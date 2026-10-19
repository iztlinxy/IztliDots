"""Extract a wallpaper palette into css/root.css."""

import argparse
import colorsys
import os
from pathlib import Path
import tempfile

from colorthief import ColorThief


OUTPUT = Path(__file__).resolve().parents[1] / "css" / "root.css"
COLORS = (
    "bar-background",
    "bar-border",
    "media-background",
    "text-primary",
    "text-secondary",
    "text-controls",
    "text-disabled",
    "accent",
    "accent-hover",
    "on-accent",
    "badge-background",
    "badge-text",
)


def mix(first, second, amount):
    return tuple(round(a * (1 - amount) + b * amount) for a, b in zip(first, second))


def tone(rgb, saturation, lightness):
    hue, _, source_saturation = colorsys.rgb_to_hls(*(value / 255 for value in rgb))
    return tuple(round(value * 255) for value in colorsys.hls_to_rgb(hue, lightness, min(saturation, source_saturation)))


def luminance(rgb):
    channels = [value / 255 for value in rgb]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(first, second):
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def readable(color, background, minimum=4.5):
    target = max(((20, 20, 20), (255, 255, 255)), key=lambda value: contrast(value, background))
    for _ in range(32):
        if contrast(color, background) >= minimum:
            return color
        color = mix(color, target, 0.12)
    return target


def build_palette(colors):
    cool_colors = [
        rgb for rgb in colors
        if 0.42 <= colorsys.rgb_to_hls(*(value / 255 for value in rgb))[0] <= 0.68
        and colorsys.rgb_to_hls(*(value / 255 for value in rgb))[2] >= 0.16
    ]
    if cool_colors:
        dominant = max(cool_colors, key=lambda rgb: colorsys.rgb_to_hls(*(value / 255 for value in rgb))[2])
        accent_source = min(
            cool_colors,
            key=lambda rgb: abs(colorsys.rgb_to_hls(*(value / 255 for value in rgb))[0] - 0.5),
        )
    else:
        dominant = colors[0]
        accent_source = max(colors, key=lambda rgb: colorsys.rgb_to_hls(*(value / 255 for value in rgb))[2])
    background = tone(dominant, 0.18, 0.14)
    surface = tone(dominant, 0.14, 0.105)
    primary = tone(dominant, 0.08, 0.94)
    secondary = readable(tone(dominant, 0.12, 0.66), background)
    accent = readable(tone(accent_source, 0.78, 0.67), background, minimum=3.0)
    badge = tone(dominant, 0.30, 0.79)
    return {
        "bar-background": background,
        "bar-border": mix(background, secondary, 0.22),
        "media-background": surface,
        "text-primary": primary,
        "text-secondary": secondary,
        "text-controls": mix(primary, secondary, 0.2),
        "text-disabled": mix(secondary, surface, 0.48),
        "accent": accent,
        "accent-hover": mix(accent, (255, 255, 255), 0.16),
        "on-accent": readable((20, 20, 20), accent, minimum=4.5),
        "badge-background": badge,
        "badge-text": readable((20, 20, 20), badge, minimum=4.5),
    }


def render_palette(colors):
    palette = build_palette(colors)
    variables = [f"    --{name}: #{''.join(f'{value:02x}' for value in rgb)};" for name, rgb in palette.items()]
    variables.append("    --transparent: transparent;")
    return "/* Generated from wallpaper. */\n:root {\n" + "\n".join(variables) + "\n}\n"


def render(image):
    colors = ColorThief(str(image)).get_palette(color_count=len(COLORS))
    if not colors:
        raise ValueError("La imagen no contiene colores visibles")
    colors += [colors[-1]] * (len(COLORS) - len(colors))
    return render_palette(colors)


def write(path, content):
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
        os.replace(temporary, path)
        os.utime(path, None)
    finally:
        Path(temporary).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--apply", action="store_true", help="write the palette to css/root.css")
    args = parser.parse_args()
    try:
        css = render(args.image)
        if args.apply:
            write(OUTPUT, css)
            print(f"Actualizado: {OUTPUT}")
        else:
            print(css, end="")
    except (OSError, ValueError) as error:
        parser.exit(1, f"No se pudo extraer la paleta: {error}\n")


if __name__ == "__main__":
    main()
