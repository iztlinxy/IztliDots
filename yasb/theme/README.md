# Tema desde el wallpaper

Generador de una paleta oscura para YASB en Windows. Mantiene seis colores base
y deriva las **12 variables** que utiliza actualmente `css/root.css`.
Los colores candidatos extraídos (`palette_size`) no son el número de variables.

Las seis bases son: fondo de barra, superficie de widgets, texto principal,
texto secundario, acento y fondo de notificaciones. Bordes, estados hover,
controles y textos sobre acentos se derivan de ellas.

El acento combina frecuencia y saturación para evitar que un detalle diminuto
domine el tema. Los wallpapers grises mantienen tonos neutros. Los textos activos
y el acento tienen contraste mínimo 4.5:1 sobre barra y superficie de widgets;
el texto desactivado se atenúa deliberadamente.

## Preparación

Desde la carpeta `yasb`, con Python 3.10 o posterior instalado:

```powershell
python -m venv scripts/.venv
./scripts/.venv/Scripts/python.exe -m pip install -r scripts/requirements.txt
```

## Uso

Vista previa, sin modificar archivos:

```powershell
./scripts/.venv/Scripts/python.exe scripts/wallpaper_theme.py "C:/Users/saura/Pictures/wallpapers/fondo.jpg"
```

Aplicar y conservar una copia de la paleta anterior:

```powershell
./scripts/.venv/Scripts/python.exe scripts/wallpaper_theme.py "C:/Users/saura/Pictures/wallpapers/fondo.jpg" --apply
```

Restaurar:

```powershell
./scripts/.venv/Scripts/python.exe scripts/wallpaper_theme.py --restore
```

Las rutas en `settings.json` son relativas a la ubicación de ese archivo.
`fixed_accent` permite proponer un acento `#RRGGBB`; se aclara si necesita
contraste. Los originales de los wallpapers nunca se modifican.

## Actualización automática

- Vista previa por defecto; escritura atómica y respaldo al usar `--apply`.
- Tras reemplazar el CSS se actualiza su fecha de modificación para que el
  observador de YASB reciba un evento `modified`. También se notifica al restaurar
  o volver a aplicar la misma paleta; no hace falta guardar manualmente el CSS.
- Textos principales y acentos ajustados para contraste sobre el fondo oscuro.
- `config.yaml` conecta `run_after` con `scripts/apply-wallpaper-theme.ps1`.
  El lanzador encuentra Python y el generador desde su propia carpeta.
  Cada cambio desde el widget pasa `{image}` al generador con `--apply`.
  Solo la ruta del lanzador en `run_after` necesita actualizarse si mueves el repositorio.
  Recrea también el entorno virtual después de moverlo.
  No detecta cambios realizados desde la configuración de Windows.
- No modifica los colores escritos directamente en `config.yaml`.
- Un bloqueo de Windows serializa escritura y respaldo. Una revisión por solicitud
  impide que una extracción antigua sobrescriba una actualización más reciente.
  El orden se determina al iniciar los procesos, no al hacer clic en la galería.
- Una paleta idéntica no reescribe el CSS ni sustituye el respaldo.
- YASB tiene `watch_stylesheet: true`; al aplicar se recarga la paleta CSS.

La automatización requiere instalar las dependencias del entorno indicado arriba.
Los colores literales de YAML siguen siendo independientes de la paleta CSS.
Actualmente son el acento de la galería, el borde del menú Media y el color del
artista en el HTML de Media. Las variables de `root.css` solo se resuelven en CSS;
no se sustituyen automáticamente dentro de YAML o HTML. No se reescribe la
configuración al cambiar el fondo, para evitar recargas completas de los widgets.

## Verificación

```powershell
./scripts/.venv/Scripts/python.exe -m unittest discover -s scripts -p 'test_*.py'
```

Las pruebas comprueban las 12 variables y su contraste, extracción de una imagen,
vista previa sin escritura, aplicación, respaldo, restauración y rechazo de
imágenes inexistentes o totalmente transparentes. También cubren tonos grises,
selección ponderada del acento, procesos simultáneos, resultados antiguos,
configuración inválida y fallos de escritura. Usan archivos temporales;
no cambian el tema activo.
