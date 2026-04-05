#!/usr/bin/env python3
"""
Composite panoramic mural — v7 (new v3 cartoon images)
Uses the retro cartoon v3 Grok outputs + original red Amphicar.
"""

from PIL import Image, ImageFilter, ImageDraw, ImageEnhance, ImageChops
import numpy as np
from rembg import remove
import io, math, random

SRC = "/home/g/Dokumente/Duschwand/7photos-edited"
FINAL = "/home/g/Dokumente/Duschwand/final-scenes"
OUT = f"{FINAL}/mural_composite_v3.png"

CANVAS_W, CANVAS_H = 5900, 5700
HORIZON_Y = int(CANVAS_H * 0.36)

# New v3 cartoon images
SCENES = {
    'hero':       f"{SRC}/grok_1_hero_v3.jpg",
    'white_amph': f"{SRC}/grok_2_white_v3.jpg",
    'red_amph':   f"{SRC}/grok_3_red_amph.png",      # original master — already good
    'blue_amph':  f"{SRC}/grok_4_blue_v3.jpg",
    'hydrofoil':  f"{SRC}/grok_5_hydrofoil_v3.jpg",
    'jetranger':  f"{SRC}/grok_6_jetranger_v3.jpg",
    'vv_van':     f"{SRC}/grok_7_vv_van_v3.jpg",
}


def create_background():
    """Lake Garda sunset background from reference images."""
    bg1 = Image.open(f"{SRC}/bg.png").convert("RGB")
    bg2 = Image.open(f"{SRC}/background.jpg").convert("RGB")
    
    def scale_full(img):
        r = CANVAS_W / img.width
        return img.resize((CANVAS_W, int(img.height * r)), Image.LANCZOS)
    
    bg1_s = scale_full(bg1)
    bg2_s = scale_full(bg2)
    
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H))
    sky_paste_y = HORIZON_Y - int(bg2_s.height * 0.45)
    canvas.paste(bg2_s, (0, sky_paste_y))
    
    bg1_rgba = bg1_s.convert("RGBA")
    mask = Image.new("L", bg1_s.size, 0)
    md = ImageDraw.Draw(mask)
    horizon_local = int(bg1_s.height * 0.42)
    for y in range(bg1_s.height):
        dist = abs(y - horizon_local) / (bg1_s.height * 0.4)
        md.line([(0, y), (CANVAS_W, y)], fill=int(max(0, min(255, 255 * (1 - dist)))))
    bg1_paste_y = HORIZON_Y - int(bg1_s.height * 0.42)
    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba.paste(bg1_rgba, (0, bg1_paste_y), mask)
    canvas = canvas_rgba.convert("RGB")
    
    arr = np.array(canvas)
    for y in range(HORIZON_Y + 100, CANVAS_H):
        depth = (y - HORIZON_Y) / (CANVAS_H - HORIZON_Y)
        ripple = int(12 * math.sin(y * 0.04 + 0.5) * math.cos(y * 0.017))
        row = arr[y].astype(np.int16)
        row = np.clip(row + ripple, 0, 255).astype(np.uint8)
        darken = 1.0 - depth * 0.15
        row = np.clip(row * darken, 0, 255).astype(np.uint8)
        arr[y] = row
    canvas = Image.fromarray(arr)
    
    # Sun glow
    glow = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    sun_x = int(CANVAS_W * 0.5)
    sun_y = HORIZON_Y - 50
    for r in range(800, 0, -4):
        alpha = int(35 * (1 - r/800))
        gd.ellipse([(sun_x-r, sun_y-r), (sun_x+r, sun_y+r)], fill=(255, 190, 100, alpha))
    for r in range(400, 0, -3):
        for y_off in range(0, CANVAS_H - HORIZON_Y, 20):
            alpha = int(20 * (1 - r/400) * (1 - y_off/(CANVAS_H - HORIZON_Y)))
            if alpha > 0:
                gd.ellipse([(sun_x-r, sun_y+y_off-5), (sun_x+r, sun_y+y_off+5)],
                           fill=(255, 200, 130, alpha))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), glow).convert("RGB")
    canvas = canvas.filter(ImageFilter.GaussianBlur(2))
    return canvas.convert("RGBA")


def remove_bg(img):
    """Remove background using rembg AI."""
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return Image.open(io.BytesIO(remove(buf.getvalue()))).convert("RGBA")


def scale_to_width(img, target_w):
    ratio = target_w / img.width
    return img.resize((target_w, int(img.height * ratio)), Image.LANCZOS)


def find_content_bbox(img):
    a = np.array(img.split()[3])
    rows = np.any(a > 30, axis=1)
    cols = np.any(a > 30, axis=0)
    if not np.any(rows):
        return (0, img.height, 0, img.width)
    return (int(np.where(rows)[0][0]), int(np.where(rows)[0][-1]),
            int(np.where(cols)[0][0]), int(np.where(cols)[0][-1]))


def submerge_with_water_color(img, canvas, pos, depth_pct=0.22):
    img = img.copy()
    w, h = img.size
    r, g, b, a = img.split()
    a_arr = np.array(a, dtype=np.float32)
    rgb_arr = np.array(img)[:, :, :3].astype(np.float32)
    top, bottom, left, right = find_content_bbox(img)
    fade_start = int(bottom - (bottom - top) * depth_pct)
    canvas_arr = np.array(canvas)
    
    for y in range(fade_start, min(h, bottom + 20)):
        progress = (y - fade_start) / max(1, bottom - fade_start)
        alpha_mult = max(0, 1.0 - progress ** 1.5)
        a_arr[y, :] *= alpha_mult
        canvas_y = min(pos[1] + y, CANVAS_H - 1)
        if 0 <= canvas_y < canvas_arr.shape[0]:
            water_color = canvas_arr[canvas_y, min(pos[0] + w//2, CANVAS_W-1), :3].astype(np.float32)
            blend = min(1.0, progress * 1.5)
            rgb_arr[y, :, :3] = rgb_arr[y, :, :3] * (1 - blend) + water_color * blend
    
    result = np.zeros((h, w, 4), dtype=np.uint8)
    result[:, :, :3] = np.clip(rgb_arr, 0, 255).astype(np.uint8)
    result[:, :, 3] = a_arr.astype(np.uint8)
    return Image.fromarray(result)


def add_spray(canvas, cx, waterline_y, width):
    spray = Image.new("RGBA", (width, int(width * 0.15)), (0, 0, 0, 0))
    d = ImageDraw.Draw(spray)
    random.seed(cx + waterline_y)
    for _ in range(int(width * 0.15)):
        x = random.randint(0, width - 1)
        y = random.randint(0, spray.height - 1)
        size = random.randint(2, 6)
        alpha = random.randint(20, 60)
        d.ellipse([(x, y), (x+size, y+size)], fill=(255, 240, 220, alpha))
    spray = spray.filter(ImageFilter.GaussianBlur(3))
    canvas.paste(spray, (cx - width // 2, waterline_y - spray.height // 2), spray)


def add_wake(canvas, cx, cy, width):
    wake = Image.new("RGBA", (width * 2, int(width * 0.4)), (0, 0, 0, 0))
    d = ImageDraw.Draw(wake)
    mid = width
    h = wake.height
    for i in range(6):
        off = i * 15
        alpha = max(8, 35 - i * 6)
        w_line = 2 + i
        d.line([(mid, 0), (mid - width//2 - off, h)], fill=(255, 230, 190, alpha), width=w_line)
        d.line([(mid, 0), (mid + width//2 + off, h)], fill=(255, 230, 190, alpha), width=w_line)
    wake = wake.filter(ImageFilter.GaussianBlur(12))
    canvas.paste(wake, (cx - width, cy), wake)


def apply_sunset_rim(img, strength=0.3):
    r, g, b, a = img.split()
    a_blur = np.array(a.filter(ImageFilter.GaussianBlur(8)), dtype=np.float32)
    a_sharp = np.array(a, dtype=np.float32)
    edge = np.clip(a_blur - a_sharp * 0.7, 0, 255)
    rim_arr = np.zeros((*img.size[::-1], 4), dtype=np.uint8)
    rim_arr[:, :, 0] = np.clip(edge * 1.2, 0, 255).astype(np.uint8)
    rim_arr[:, :, 1] = np.clip(edge * 0.7, 0, 255).astype(np.uint8)
    rim_arr[:, :, 2] = np.clip(edge * 0.2, 0, 255).astype(np.uint8)
    rim_arr[:, :, 3] = np.clip(edge * strength * 2, 0, 200).astype(np.uint8)
    return Image.alpha_composite(img, Image.fromarray(rim_arr))


def warm_tint(img, strength=0.12):
    r, g, b, a = img.split()
    ra = np.clip(np.array(r, dtype=np.float32) * (1 + strength * 0.35), 0, 255)
    ga = np.clip(np.array(g, dtype=np.float32) * (1 + strength * 0.1), 0, 255)
    ba = np.clip(np.array(b, dtype=np.float32) * (1 - strength * 0.25), 0, 255)
    return Image.merge("RGBA", (Image.fromarray(ra.astype(np.uint8)),
                                 Image.fromarray(ga.astype(np.uint8)),
                                 Image.fromarray(ba.astype(np.uint8)), a))


def place_vehicle(canvas, img, waterline_y, center_x, scale_w,
                  depth_factor=0.0, submersion=0.22):
    img = scale_to_width(img, scale_w)
    img = warm_tint(img, 0.10 + depth_factor * 0.1)
    img = apply_sunset_rim(img, 0.25 - depth_factor * 0.1)
    
    if depth_factor > 0:
        r, g, b, a = img.split()
        rgb = Image.merge("RGB", (r, g, b))
        rgb = ImageEnhance.Color(rgb).enhance(1.0 - depth_factor * 0.3)
        rgb = ImageEnhance.Brightness(rgb).enhance(1.0 + depth_factor * 0.1)
        if depth_factor > 0.25:
            rgb = rgb.filter(ImageFilter.GaussianBlur(max(1, depth_factor * 2)))
        r, g, b = rgb.split()
        img = Image.merge("RGBA", (r, g, b, a))
    
    # Feather edges
    r, g, b, a = img.split()
    a = a.filter(ImageFilter.GaussianBlur(2.5))
    img = Image.merge("RGBA", (r, g, b, a))
    
    top, bottom, left, right = find_content_bbox(img)
    pos_x = center_x - img.width // 2
    pos_y = waterline_y - bottom
    
    img = submerge_with_water_color(img, canvas, (pos_x, pos_y), submersion)
    
    # Shadow
    sw = int(scale_w * 0.6)
    sh = int(max(8, scale_w * 0.04))
    shadow = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([(0, 0), (sw, sh)],
                                    fill=(10, 5, 0, 30 + int(25 * (1 - depth_factor))))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    canvas.paste(shadow, (center_x - sw//2, waterline_y - sh//2), shadow)
    
    canvas.paste(img, (pos_x, pos_y), img)
    add_spray(canvas, center_x, waterline_y, int(scale_w * 0.5))
    add_wake(canvas, center_x, waterline_y + 15, int(scale_w * 0.35))
    return (pos_x, pos_y, img.width, img.height)


def main():
    print("Creating background...")
    canvas = create_background()
    
    print("Removing backgrounds (AI)...")
    processed = {}
    for name, path in SCENES.items():
        print(f"  {name}: {path}")
        processed[name] = remove_bg(Image.open(path))

    # LAYOUT (from PROJECT.md):
    # Left panel: 0-2325px (77.5cm), Right panel: 2325-5900px (119.5cm)
    # Panel seam dead zone: 2100-2550px (70-85cm)
    # Shower fixture: x=0-1350, y=4560-5700 (lower-left, avoid)
    # Hero on RIGHT panel, slightly left of center
    
    # --- FAR BACKGROUND (small, faded) ---
    
    print("Placing VV van (far background)...")
    place_vehicle(canvas, processed['vv_van'],
                  waterline_y=2850, center_x=1600, scale_w=750,
                  depth_factor=0.5, submersion=0.22)

    print("Placing blue Amphicar (far background)...")
    place_vehicle(canvas, processed['blue_amph'],
                  waterline_y=2700, center_x=4700, scale_w=850,
                  depth_factor=0.45, submersion=0.20)

    # --- MID BACKGROUND ---
    
    print("Placing Jetranger (mid-left)...")
    place_vehicle(canvas, processed['jetranger'],
                  waterline_y=3600, center_x=800, scale_w=1050,
                  depth_factor=0.3, submersion=0.22)

    print("Placing red Amphicar (mid-center)...")
    place_vehicle(canvas, processed['red_amph'],
                  waterline_y=3100, center_x=3300, scale_w=1050,
                  depth_factor=0.25, submersion=0.22)

    print("Placing white Amphicar (mid-right)...")
    place_vehicle(canvas, processed['white_amph'],
                  waterline_y=3500, center_x=5100, scale_w=1200,
                  depth_factor=0.2, submersion=0.22)

    # --- MID-FOREGROUND ---
    
    print("Placing hydrofoil surfer (left panel)...")
    place_vehicle(canvas, processed['hydrofoil'],
                  waterline_y=4500, center_x=1800, scale_w=700,
                  depth_factor=0.1, submersion=0.12)

    # --- HERO (largest, foreground) ---
    
    print("Placing HERO teal Amphicar B-AP 670...")
    place_vehicle(canvas, processed['hero'],
                  waterline_y=5100, center_x=3800, scale_w=2600,
                  depth_factor=0.0, submersion=0.25)

    # Save full res
    print(f"Saving full-res: {OUT}")
    canvas.save(OUT, quality=95)
    
    # QC preview with layout annotations
    preview = canvas.copy()
    preview.thumbnail((1400, 1400), Image.LANCZOS)
    s = preview.width / CANVAS_W
    draw = ImageDraw.Draw(preview)
    # Horizon
    draw.line([(0, int(HORIZON_Y*s)), (preview.width, int(HORIZON_Y*s))], fill=(255,255,0,120), width=1)
    # Panel seam
    draw.line([(int(2325*s), 0), (int(2325*s), preview.height)], fill=(0,255,0,120), width=2)
    # Shower fixture zone
    draw.rectangle([(0, int(4560*s)), (int(1350*s), int(5700*s))], outline=(255,0,0), width=2)
    preview.convert("RGB").save(f"{FINAL}/mural_check_v3.jpg", quality=90)
    
    # Clean preview
    clean = canvas.copy()
    clean.thumbnail((1400, 1400), Image.LANCZOS)
    clean.convert("RGB").save(f"{FINAL}/mural_preview_v3.jpg", quality=92)
    
    print("Done! Files:")
    print(f"  Full: {OUT}")
    print(f"  Preview: {FINAL}/mural_preview_v3.jpg")
    print(f"  QC: {FINAL}/mural_check_v3.jpg")


if __name__ == "__main__":
    main()
