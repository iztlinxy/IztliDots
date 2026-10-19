# Tema desde el wallpaper

Generador inicial de una paleta oscura para YASB. Mantiene seis colores base
y deriva las **12 variables** que utiliza actualmente `css/root.css`.
Los colores candidatos extraídos (`palette_size`) no son el número de variables.

Las seis bases son: fondo de barra, superficie de widgets, texto principal,
texto secundario, acento y fondo de notificaciones. Bordes, estados hover,
controles y textos sobre acentos se derivan de ellas.

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

## Alcance de esta primera versión

- Vista previa por defecto; escritura atómica y respaldo al usar `--apply`.
- Tras reemplazar el CSS se actualiza su fecha de modificación para que el
  observador de YASB reciba un evento `modified`. También se notifica al restaurar
  o volver a aplicar la misma paleta; no hace falta guardar manualmente el CSS.
- Textos principales y acentos ajustados para contraste sobre el fondo oscuro.
- `config.yaml` conecta `run_after` de Wallpapers con el Python de `scripts/.venv`.
  Cada cambio desde el widget pasa `{image}` al generador con `--apply`.
  Las rutas son absolutas: actualízalas si mueves este repositorio.
  No detecta cambios realizados desde la configuración de Windows.
- No modifica los colores escritos directamente en `config.yaml`.
- Ejecutar de forma secuencial: la coordinación de cambios rápidos queda pendiente.
- YASB tiene `watch_stylesheet: true`; al aplicar se recarga la paleta CSS.

La automatización requiere instalar las dependencias del entorno indicado arriba.
Los colores literales de YAML siguen siendo independientes de la paleta CSS.

## Verificación

```powershell
./scripts/.venv/Scripts/python.exe -m unittest discover -s scripts -p 'test_*.py'
```

Las pruebas comprueban las 12 variables y su contraste, extracción de una imagen,
vista previa sin escritura, aplicación, respaldo, restauración y rechazo de
imágenes inexistentes o totalmente transparentes. Usan archivos temporales;
no cambian el tema activo.
