# Manual de uso - Foja

Extension para **LibreOffice Writer**: conversion de numeros a letras y barra de estado `Pag N - Lin M`.

Compatible con Linux y Windows.

---

## 1. Instalacion

### Desde el archivo `.oxt`

1. Compila el paquete (si tenes el codigo fuente):

```bash
./scripts/build_oxt.sh
```

2. En LibreOffice Writer: **Herramientas > Administrador de extensiones > Anadir**.
3. Elegi `dist/foja.oxt`.
4. Reinicia Writer.

### Actualizacion

**Herramientas > Administrador de extensiones > Buscar actualizaciones**

Si instalas a mano una version nueva, conviene quitar la anterior o reemplazarla y reiniciar Writer.

---

## 2. Donde encontrar Foja

Tras instalar y reiniciar:

| Lugar | Que ves |
|-------|---------|
| Menu **Foja** | De N a Letras |
| Barra de herramientas **Foja** | N a Letras |
| Barra de estado | Indicador `Pag N - Lin M` (pagina y linea relativa a la pagina) |

---

## 3. De N a Letras

1. Selecciona un numero en el documento.
2. Ejecuta **Foja > De N a Letras** (o el boton de la barra).
3. La seleccion se reemplaza por su escritura en espanol.

Ejemplo: `125` -> texto en letras correspondiente.

Si no hay seleccion, no hace nada.

---

## 4. Barra de estado

Muestra `Pag N - Lin M`:

- **Pag**: numero de pagina actual.
- **Lin**: linea relativa a esa pagina (no al documento entero).

Si no aparece, reinicia Writer tras instalar o verifica que la barra de estado este visible (**Ver > Barra de estado**).

---

## 5. Problemas frecuentes

| Sintoma | Que probar |
|---------|------------|
| No aparece el menu Foja | Reinstalar la extension y reiniciar Writer por completo |
| N a Letras no cambia el texto | Asegurate de tener seleccionado el numero completo |
| Barra `Pag - Lin` no se ve | Ver > Barra de estado; reiniciar Writer |

---

## 6. Requisitos

- LibreOffice Writer 4.1 o superior (recomendado una version reciente).
- Python embebido de LibreOffice (incluido en la instalacion habitual).

---

## Licencia

MIT. Ver el archivo `LICENSE` del proyecto.
