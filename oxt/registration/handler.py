# -*- coding: utf-8 -*-
"""Foja ProtocolHandler: toolbar actions + page/line statusbar."""

from __future__ import annotations

import os
import sys
import threading
import time
import traceback

_EXT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_PYTHONPATH = os.path.join(_EXT_ROOT, "pythonpath")
if _PYTHONPATH not in sys.path:
    sys.path.insert(0, _PYTHONPATH)

import uno
import unohelper
from com.sun.star.frame import FeatureStateEvent, XDispatch, XDispatchProvider
from com.sun.star.lang import XInitialization, XServiceInfo
from com.sun.star.view import XSelectionChangeListener

from foja.actions import run_action
from foja.page_line_calc import UNKNOWN_LABEL, status_text_for_document

IMPLEMENTATION_NAME = "org.foja.writer.ProtocolHandler"
SERVICE_NAMES = ("com.sun.star.frame.ProtocolHandler",)
PROTOCOL = "vnd.foja"
PROTOCOL_PREFIX = PROTOCOL + ":"
STATUS_COMMAND = PROTOCOL_PREFIX + "status"
THROTTLE_SECONDS = 0.15

ACTIONS = {
    "nro_letras",
    "status",
}


class ActionDispatch(unohelper.Base, XDispatch):
    def __init__(self, ctx, frame, action):
        self.ctx = ctx
        self.frame = frame
        self.action = action

    def dispatch(self, url, arguments):
        try:
            run_action(self.ctx, self.frame, self.action)
        except Exception:
            traceback.print_exc()

    def addStatusListener(self, listener, url):
        event = FeatureStateEvent()
        event.Source = self
        event.FeatureURL = url
        event.IsEnabled = True
        event.Requery = False
        event.State = True
        try:
            listener.statusChanged(event)
        except Exception:
            pass

    def removeStatusListener(self, listener, url):
        return


class StatusDispatch(unohelper.Base, XDispatch, XSelectionChangeListener):
    def __init__(self, ctx, frame, url):
        self.ctx = ctx
        self.frame = frame
        self.url = url
        self._listeners = []
        self._listeners_lock = threading.Lock()
        self._selection_attached = False
        self._last_text = UNKNOWN_LABEL
        self._last_notify_at = 0.0
        self._pending_timer = None
        self._timer_lock = threading.Lock()
        self._disposed = False
        self._updating = False

    def dispatch(self, url, arguments):
        self._refresh_and_notify(force=True)

    def addStatusListener(self, listener, url):
        with self._listeners_lock:
            self._listeners.append((listener, url))
        self._attach_selection_listener()
        self._refresh_and_notify(force=True, only_listener=(listener, url))

    def removeStatusListener(self, listener, url):
        with self._listeners_lock:
            self._listeners = [pair for pair in self._listeners if pair[0] != listener]
            empty = not self._listeners
        if empty:
            self._detach_selection_listener()

    def selectionChanged(self, event):
        if self._updating:
            return
        self._schedule_refresh()

    def disposing(self, event):
        self._disposed = True
        self._detach_selection_listener()
        with self._listeners_lock:
            self._listeners = []
        with self._timer_lock:
            if self._pending_timer is not None:
                self._pending_timer.cancel()
                self._pending_timer = None

    def _controller(self):
        if self.frame is None:
            return None
        try:
            return self.frame.getController()
        except Exception:
            return None

    def _document(self):
        controller = self._controller()
        if controller is None:
            return None
        try:
            return controller.getModel()
        except Exception:
            return None

    def _attach_selection_listener(self):
        if self._selection_attached:
            return
        controller = self._controller()
        if controller is None:
            return
        try:
            controller.addSelectionChangeListener(self)
            self._selection_attached = True
        except Exception:
            traceback.print_exc()

    def _detach_selection_listener(self):
        if not self._selection_attached:
            return
        controller = self._controller()
        if controller is not None:
            try:
                controller.removeSelectionChangeListener(self)
            except Exception:
                pass
        self._selection_attached = False

    def _schedule_refresh(self):
        if self._disposed:
            return
        now = time.monotonic()
        elapsed = now - self._last_notify_at
        if elapsed >= THROTTLE_SECONDS:
            self._refresh_and_notify(force=True)
            return
        delay = max(0.01, THROTTLE_SECONDS - elapsed)

        def _fire():
            self._refresh_and_notify(force=True)
            with self._timer_lock:
                self._pending_timer = None

        with self._timer_lock:
            if self._pending_timer is not None:
                self._pending_timer.cancel()
            self._pending_timer = threading.Timer(delay, _fire)
            self._pending_timer.daemon = True
            self._pending_timer.start()

    def _refresh_and_notify(self, force=False, only_listener=None):
        if self._disposed:
            return
        document = self._document()
        self._updating = True
        try:
            if document is None:
                text = UNKNOWN_LABEL
            else:
                try:
                    if not document.supportsService("com.sun.star.text.TextDocument"):
                        text = UNKNOWN_LABEL
                    else:
                        text = status_text_for_document(document)
                except Exception:
                    traceback.print_exc()
                    text = UNKNOWN_LABEL
        finally:
            self._updating = False

        if not force and text == self._last_text:
            return
        self._last_text = text
        self._last_notify_at = time.monotonic()
        if only_listener is not None:
            self._notify_one(only_listener[0], only_listener[1], text)
            return
        with self._listeners_lock:
            listeners = list(self._listeners)
        for listener, url in listeners:
            self._notify_one(listener, url, text)

    def _notify_one(self, listener, url, text):
        try:
            event = FeatureStateEvent()
            event.Source = self
            event.FeatureURL = url
            event.IsEnabled = True
            event.Requery = False
            event.State = text
            listener.statusChanged(event)
        except Exception:
            traceback.print_exc()


class ProtocolHandler(unohelper.Base, XDispatchProvider, XInitialization, XServiceInfo):
    def __init__(self, ctx):
        self.ctx = ctx
        self.frame = None
        self._dispatches = {}

    def initialize(self, args):
        for arg in args:
            frame = self._coerce_frame(arg)
            if frame is not None:
                self.frame = frame
                return

    @staticmethod
    def _coerce_frame(arg):
        if arg is None:
            return None
        try:
            if hasattr(arg, "Name") and getattr(arg, "Name", None) == "Frame":
                return arg.Value
        except Exception:
            pass
        try:
            if hasattr(arg, "getController"):
                return arg
        except Exception:
            pass
        return None

    def queryDispatch(self, url, target_frame_name, search_flags):
        if self.frame is None:
            self.frame = self._frame_from_desktop()

        complete = getattr(url, "Complete", "") or ""
        protocol = getattr(url, "Protocol", "") or ""
        path = getattr(url, "Path", "") or ""

        matches = complete.startswith(PROTOCOL_PREFIX) or protocol.rstrip(":") == PROTOCOL
        if not matches:
            return None

        action = path or complete.split(":", 1)[-1]
        action = action.split("?")[0].strip()
        if action not in ACTIONS:
            return None

        key = PROTOCOL_PREFIX + action
        dispatch = self._dispatches.get(key)
        if action == "status":
            if dispatch is None:
                dispatch = StatusDispatch(self.ctx, self.frame, url)
                self._dispatches[key] = dispatch
            else:
                dispatch.frame = self.frame
        else:
            if dispatch is None:
                dispatch = ActionDispatch(self.ctx, self.frame, action)
                self._dispatches[key] = dispatch
            else:
                dispatch.frame = self.frame
        return dispatch

    def queryDispatches(self, requests):
        return tuple(
            self.queryDispatch(req.URL, req.FrameName, req.SearchFlags) for req in requests
        )

    def _frame_from_desktop(self):
        try:
            desktop = self.ctx.ServiceManager.createInstanceWithContext(
                "com.sun.star.frame.Desktop", self.ctx
            )
            component = desktop.getCurrentComponent()
            if component is None:
                return None
            return component.getCurrentController().getFrame()
        except Exception:
            return None

    def getImplementationName(self):
        return IMPLEMENTATION_NAME

    def supportsService(self, name):
        return name in SERVICE_NAMES

    def getSupportedServiceNames(self):
        return SERVICE_NAMES


def createInstance(ctx, *args):
    handler = ProtocolHandler(ctx)
    if args:
        handler.initialize(args)
    return handler


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    createInstance,
    IMPLEMENTATION_NAME,
    SERVICE_NAMES,
)
