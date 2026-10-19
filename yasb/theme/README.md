# Paleta desde el wallpaper

`scripts/wallpaper_theme.py` usa [colorgram.py](https://pypi.org/project/colorgram.py/)
como backend de extracción, con Pillow para reducir la imagen a 160 píxeles.
Convierte hasta 12 colores representativos en las 12 variables de `css/root.css`.
Conserva tonos neutros y ajusta texto y acento para el fondo oscuro.

## Instalar

Desde la carpeta `yasb`, con Python 3.10 o superior:

```powershell
python -m venv scripts/.venv
./scripts/.venv/Scripts/python.exe -m pip install -r scripts/requirements.txt
```

## Ejecutar

```powershell
./scripts/.venv/Scripts/python.exe scripts/wallpaper_theme.py "C:/ruta/fondo.jpg"
./scripts/.venv/Scripts/python.exe scripts/wallpaper_theme.py "C:/ruta/fondo.jpg" --apply
```

Sin `--apply` muestra el CSS. El widget llama a `apply-wallpaper-theme.ps1` mediante
`run_after`. Solo la ruta del lanzador en `config.yaml` es absoluta.

No hay tests, configuración adicional, respaldos ni estado persistente.
La escritura es atómica y notifica a YASB para recargar sin guardar manualmente.
Si se solapan ejecuciones, prevalece la última que termina; no hay cola.
Los colores fijos en YAML siguen independientes del CSS. Los cambios de fondo
realizados desde Windows no ejecutan este generador.
