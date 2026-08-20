# Foja para LibreOffice Writer

Extension notarial para Writer: formatos de foja, herramientas, copia simple, impresion, lectura TTS y barra de estado `Pag N - Lin M`.

## Instalar

```bash
./scripts/build_oxt.sh
```

En LibreOffice: **Herramientas > Administrador de extensiones > Anadir** y elegi `dist/foja.oxt`. Reinicia Writer.

## Uso

Menu / toolbar **Foja**:

- Formatos: Prot.(Anv/Rev), Inter.(Anv/Rev), A4, Legal, Boletos, paginas simetricas, copia simple
- Herramientas: CUIT, N a Letras, Entrelinear, Leer, Parametros
- Imprimir: vista previa, impar/par, vigente, imprimir

Atajos Writer:

| Tecla | Accion |
|-------|--------|
| F11 | Protocolo anverso |
| Ctrl+F11 | Protocolo reverso |
| F12 | Intervencion anverso |
| Ctrl+F12 | Intervencion reverso |
| F5 | Buscar comodin |
| F9 | Generar CUIT |

Parametros se guardan en `~/.config/foja-writer/params.json`.

## Leer (TTS)

- Linux: `spd-say` o `espeak-ng`
- Windows: SAPI via PowerShell

## Actualizar

**Herramientas > Administrador de extensiones > Buscar actualizaciones**

Release:

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Licencia

MIT. Ver [LICENSE](LICENSE).
