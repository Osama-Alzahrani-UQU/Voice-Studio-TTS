"""
create_assets.py - Visual Branding Assets Generator
--------------------------------------------------
Programmatically generates high-quality icon files (app_icon.ico) and
header banner images (header_banner.png) for the application interface.
"""

import os
from PIL import Image, ImageDraw

DEFAULT_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def generate_app_assets(output_dir: str = DEFAULT_ASSETS_DIR):
    os.makedirs(output_dir, exist_ok=True)
    icon_path = os.path.join(output_dir, "app_icon.ico")
    banner_path = os.path.join(output_dir, "header_banner.png")

    # 1. Generate 256x256 Icon
    size = (256, 256)
    img = Image.new("RGBA", size, (24, 24, 37, 255))  # Dark Catppuccin Base
    draw = ImageDraw.Draw(img)

    # Draw rounded background card
    draw.rounded_rectangle(
        [12, 12, 244, 244],
        radius=36,
        fill=(30, 30, 46, 255),
        outline=(203, 166, 247, 255),
        width=4,
    )

    # Draw stylized soundwave bars
    wave_colors = ["#cba6f7", "#89b4fa", "#f5e0dc", "#89b4fa", "#cba6f7"]
    bar_heights = [60, 110, 150, 100, 50]
    bar_x = [60, 95, 130, 165, 200]

    for x, h, col in zip(bar_x, bar_heights, wave_colors):
        y_top = 128 - (h // 2)
        y_bottom = 128 + (h // 2)
        draw.rounded_rectangle([x - 10, y_top, x + 10, y_bottom], radius=10, fill=col)

    # Save as ICO (multiple sizes)
    img.save(
        icon_path,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print(f"[Assets] Icon created successfully at: {icon_path}")

    # 2. Generate Header Banner Image (800x120)
    banner_size = (800, 120)
    banner = Image.new("RGBA", banner_size, (24, 24, 37, 255))
    b_draw = ImageDraw.Draw(banner)

    # Draw subtle gradient header background
    b_draw.rectangle([0, 0, 800, 120], fill=(30, 30, 46, 255))

    # Accent decorative line at bottom
    b_draw.rectangle([0, 116, 800, 120], fill=(203, 166, 247, 255))

    # Draw mini soundwave graphics on banner
    for i in range(12):
        bx = 30 + (i * 18)
        bh = 20 + (i % 5) * 12
        by1 = 60 - (bh // 2)
        by2 = 60 + (bh // 2)
        b_draw.rounded_rectangle([bx, by1, bx + 6, by2], radius=3, fill=(137, 180, 250, 220))

    banner.save(banner_path, format="PNG")
    print(f"[Assets] Header banner created successfully at: {banner_path}")

    return icon_path, banner_path


if __name__ == "__main__":
    generate_app_assets()
