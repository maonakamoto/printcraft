#!/usr/bin/env python3
"""
Composite panoramic mural — v6 (quality push)
- Better background from both source images
- Water color matching at vehicle waterline
- Spray/splash at hull
- Sunset rim light on vehicles
- Proper depth of field
"""

from PIL import Image, ImageFilter, ImageDraw, ImageEnhance, ImageChops
import numpy as np
from rembg import remove
import io, math, random

SRC = "/home/g/Dokumente/Duschwand/7photos-edited"
OUT = "/home/g/Dokumente/Duschwand/final-scenes/mural_composite.png"

CANVAS_W, CANVAS_H = 5900, 5700
HORIZON_Y = int(CANVAS_H * 0.36)

FINAL = "/home/g/Dokumente/Duschwand/final-scenes"
SCENES = {
    'hero':       f"{FINAL}/scene1_hero_bap670.png",
    'white_amph': f"{FINAL}/scene2_white_amph.png",
    'red_amph':   f"{FINAL}/scene3_red_amph_kd.png",
    'blue_amph':  f"{FINAL}/scene4_blue_amph_abn274.png",
    'hydrofoil':  f"{FINAL}/scene5_hydrofoil_surfer.png",
    'jetranger':  f"{FINAL}/scene6_jetranger.png",
    'vv_van':     f"{FINAL}/scene7_vv_van.png",
}


def create_background():
    """
    High quality background: use BOTH bg.png and background.jpg,
    blend them, add painted water texture, horizon detail.
    """
    # Load both references
    bg1 = Image.open(f"{SRC}/bg.png").convert("RGB")
    bg2 = Image.open(f"{SRC}/background.jpg").convert("RGB")
    
    # Scale both to canvas width
    def scale_full(img):
        r = CANVAS_W / img.width
        return img.resize((CANVAS_W, int(img.height * r)), Image.LANCZOS)
    
    bg1_s = scale_full(bg1)
    bg2_s = scale_full(bg2)
    
    # Create canvas
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H))
    
    # Use bg2 (background.jpg) for the sky portion — paste it centered on horizon
    # bg2 has good warm tones
    sky_paste_y = HORIZON_Y - int(bg2_s.height * 0.45)
    canvas.paste(bg2_s, (0, sky_paste_y))
    
    # Overlay bg1 blended — it has the Lake Garda town detail
    bg1_paste_y = HORIZON_Y - int(bg1_s.height * 0.42)
    bg1_rgba = bg1_s.convert("RGBA")
    # Create blend mask — strongest at horizon
    mask = Image.new("L", bg1_s.size, 0)
    md = ImageDraw.Draw(mask)
    horizon_local = int(bg1_s.height * 0.42)
    for y in range(bg1_s.height):
        dist = abs(y - horizon_local) / (bg1_s.height * 0.4)
        md.line([(0, y), (CANVAS_W, y)], fill=int(max(0, min(255, 255 * (1 - dist)))))
    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba.paste(bg1_rgba, (0, bg1_paste_y), mask)
    canvas = canvas_rgba.convert("RGB")
    
    # Now paint proper water in the lower portion
    # Sample water colors from the blended result at horizon+100
    arr = np.array(canvas)
    
    # Add horizontal water ripple texture
    for y in range(HORIZON_Y + 100, CANVAS_H):
        depth = (y - HORIZON_Y) / (CANVAS_H - HORIZON_Y)
        # Ripple: sinusoidal brightness variation
        ripple = int(12 * math.sin(y * 0.04 + 0.5) * math.cos(y * 0.017))
        # Slight horizontal wave offset
        shift = int(3 * math.sin(y * 0.03))
        row = arr[y].astype(np.int16)
        row = np.clip(row + ripple, 0, 255).astype(np.uint8)
        # Darken water slightly as it gets closer (deeper = darker blue-green)
        darken = 1.0 - depth * 0.15
        row = np.clip(row * darken, 0, 255).astype(np.uint8)
        arr[y] = row
    
    canvas = Image.fromarray(arr)
    
    # Sun glow at horizon
    glow = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    sun_x = int(CANVAS_W * 0.5)
    sun_y = HORIZON_Y - 50
    for r in range(800, 0, -4):
        alpha = int(35 * (1 - r/800))
        gd.ellipse([(sun_x-r, sun_y-r), (sun_x+r, sun_y+r)], 
                    fill=(255, 190, 100, alpha))
    
    # Sun reflection on water — vertical streak below sun
    for r in range(400, 0, -3):
        for y_off in range(0, CANVAS_H - HORIZON_Y, 20):
            alpha = int(20 * (1 - r/400) * (1 - y_off/(CANVAS_H - HORIZON_Y)))
            if alpha > 0:
                gd.ellipse([(sun_x-r, sun_y+y_off-5), (sun_x+r, sun_y+y_off+5)],
                           fill=(255, 200, 130, alpha))
    
    canvas = Image.alpha_composite(canvas.convert("RGBA"), glow).convert("RGB")
    
    # Final painterly blur
    canvas = canvas.filter(ImageFilter.GaussianBlur(2))
    
    return canvas.convert("RGBA")


def remove_bg(img):
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return Image.open(io.BytesIO(remove(buf.getvalue()))).convert("RGBA")


def scale_to_width(img, target_w):
    ratio = target_w / img.width
    return img.resize((target_w, int(img.height * ratio)), Image.LANCZOS)


def find_content_bbox(img):
    """Return (top, bottom, left, right) of non-transparent content."""
    a = np.array(img.split()[3])
    rows = np.any(a > 30, axis=1)
    cols = np.any(a > 30, axis=0)
    if not np.any(rows):
        return (0, img.height, 0, img.width)
    return (int(np.where(rows)[0][0]), int(np.where(rows)[0][-1]),
            int(np.where(cols)[0][0]), int(np.where(cols)[0][-1]))


def submerge_with_water_color(img, canvas, pos, depth_pct=0.22):
    """
    Fade bottom of vehicle AND blend its edge pixels toward the water color beneath it.
    This prevents the harsh cutout look at the waterline.
    """
    img = img.copy()
    w, h = img.size
    r, g, b, a = img.split()
    a_arr = np.array(a, dtype=np.float32)
    rgb_arr = np.array(img)[:, :, :3].astype(np.float32)
    
    top, bottom, left, right = find_content_bbox(img)
    fade_start = int(bottom - (bottom - top) * depth_pct)
    
    # Sample water color from canvas at the position where vehicle sits
    canvas_arr = np.array(canvas)
    
    for y in range(fade_start, min(h, bottom + 20)):
        progress = (y - fade_start) / max(1, bottom - fade_start)
        # Alpha fade
        alpha_mult = max(0, 1.0 - progress ** 1.5)
        a_arr[y, :] *= alpha_mult
        
        # Color blend toward water
        canvas_y = min(pos[1] + y, CANVAS_H - 1)
        if canvas_y >= 0 and canvas_y < canvas_arr.shape[0]:
            water_color = canvas_arr[canvas_y, min(pos[0] + w//2, CANVAS_W-1), :3].astype(np.float32)
            blend = min(1.0, progress * 1.5)
            rgb_arr[y, :, :3] = rgb_arr[y, :, :3] * (1 - blend) + water_color * blend
    
    result = np.zeros((h, w, 4), dtype=np.uint8)
    result[:, :, :3] = np.clip(rgb_arr, 0, 255).astype(np.uint8)
    result[:, :, 3] = a_arr.astype(np.uint8)
    return Image.fromarray(result)


def add_spray(canvas, cx, waterline_y, width):
    """Paint small white spray/splash dots at the waterline."""
    spray = Image.new("RGBA", (width, int(width * 0.15)), (0, 0, 0, 0))
    d = ImageDraw.Draw(spray)
    random.seed(cx + waterline_y)  # deterministic
    for _ in range(int(width * 0.15)):
        x = random.randint(0, width - 1)
        y = random.randint(0, spray.height - 1)
        size = random.randint(2, 6)
        alpha = random.randint(20, 60)
        d.ellipse([(x, y), (x+size, y+size)], fill=(255, 240, 220, alpha))
    spray = spray.filter(ImageFilter.GaussianBlur(3))
    paste_x = cx - width // 2
    paste_y = waterline_y - spray.height // 2
    canvas.paste(spray, (paste_x, paste_y), spray)


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
    """Add warm rim/edge lighting from the left (sunset direction)."""
    r, g, b, a = img.split()
    a_arr = np.array(a)
    
    # Create edge mask by finding alpha edges
    a_blur = np.array(a.filter(ImageFilter.GaussianBlur(8)), dtype=np.float32)
    a_sharp = np.array(a, dtype=np.float32)
    edge = np.clip(a_blur - a_sharp * 0.7, 0, 255)
    
    # Apply warm color to edges
    rim = Image.new("RGBA", img.size, (0, 0, 0, 0))
    rim_arr = np.array(rim)
    rim_arr[:, :, 0] = np.clip(edge * 1.2, 0, 255).astype(np.uint8)  # red
    rim_arr[:, :, 1] = np.clip(edge * 0.7, 0, 255).astype(np.uint8)  # green
    rim_arr[:, :, 2] = np.clip(edge * 0.2, 0, 255).astype(np.uint8)  # blue
    rim_arr[:, :, 3] = np.clip(edge * strength * 2, 0, 200).astype(np.uint8)
    
    rim_img = Image.fromarray(rim_arr)
    return Image.alpha_composite(img, rim_img)


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
    
    # Warm tint to match sunset
    img = warm_tint(img, 0.10 + depth_factor * 0.1)
    
    # Sunset rim lighting
    img = apply_sunset_rim(img, 0.25 - depth_factor * 0.1)
    
    # Atmospheric depth
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
    
    # Calculate position BEFORE submersion (need this for water color sampling)
    top, bottom, left, right = find_content_bbox(img)
    pos_x = center_x - img.width // 2
    pos_y = waterline_y - bottom
    
    # Submerge with water color blending
    img = submerge_with_water_color(img, canvas, (pos_x, pos_y), submersion)
    
    # Shadow on water
    sw = int(scale_w * 0.6)
    sh = int(max(8, scale_w * 0.04))
    shadow = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([(0, 0), (sw, sh)], 
                                    fill=(10, 5, 0, 30 + int(25 * (1 - depth_factor))))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    canvas.paste(shadow, (center_x - sw//2, waterline_y - sh//2), shadow)
    
    # Paste vehicle
    canvas.paste(img, (pos_x, pos_y), img)
    
    # Spray at waterline
    add_spray(canvas, center_x, waterline_y, int(scale_w * 0.5))
    
    # Wake behind
    add_wake(canvas, center_x, waterline_y + 15, int(scale_w * 0.35))
    
    return (pos_x, pos_y, img.width, img.height)


def main():
    print("Creating high-quality background...")
    canvas = create_background()
    
    print("Removing backgrounds (AI)...")
    processed = {}
    for name, path in SCENES.items():
        print(f"  {name}...")
        processed[name] = remove_bg(Image.open(path))

    # SHOWER FIXTURE ZONE: x=0-1350, y=1800-3000 — KEEP EMPTY
    
    # --- FAR BACKGROUND ---
    
    print("Placing VV van...")
    place_vehicle(canvas, processed['vv_van'],
                  waterline_y=2850, center_x=2050, scale_w=750,
                  depth_factor=0.5, submersion=0.22)

    print("Placing blue Amphicar...")
    place_vehicle(canvas, processed['blue_amph'],
                  waterline_y=2700, center_x=4700, scale_w=850,
                  depth_factor=0.45, submersion=0.20)

    # --- MID BACKGROUND ---
    
    print("Placing Jetranger...")
    place_vehicle(canvas, processed['jetranger'],
                  waterline_y=4000, center_x=700, scale_w=1050,
                  depth_factor=0.3, submersion=0.22)

    print("Placing red Amphicar...")
    place_vehicle(canvas, processed['red_amph'],
                  waterline_y=3100, center_x=3300, scale_w=1050,
                  depth_factor=0.25, submersion=0.22)

    print("Placing white Amphicar...")
    place_vehicle(canvas, processed['white_amph'],
                  waterline_y=3500, center_x=5100, scale_w=1200,
                  depth_factor=0.2, submersion=0.22)

    # --- MID-FOREGROUND ---
    
    print("Placing hydrofoil surfer...")
    place_vehicle(canvas, processed['hydrofoil'],
                  waterline_y=4200, center_x=2400, scale_w=600,
                  depth_factor=0.1, submersion=0.12)

    # --- HERO ---
    
    print("Placing HERO (Roli + gf, teal B-AP 670)...")
    place_vehicle(canvas, processed['hero'],
                  waterline_y=5100, center_x=3800, scale_w=2600,
                  depth_factor=0.0, submersion=0.25)

    print(f"Saving {OUT}...")
    canvas.save(OUT, quality=95)
    
    # QC preview with annotations
    preview = canvas.copy()
    preview.thumbnail((1400, 1400), Image.LANCZOS)
    s = preview.width / CANVAS_W
    draw = ImageDraw.Draw(preview)
    draw.line([(0, int(HORIZON_Y*s)), (preview.width, int(HORIZON_Y*s))], fill=(255,255,0,120), width=1)
    draw.line([(int(2325*s), 0), (int(2325*s), preview.height)], fill=(0,255,0,120), width=1)
    draw.rectangle([(0, int(1800*s)), (int(1350*s), int(3000*s))], outline=(255,0,0), width=2)
    preview.convert("RGB").save(f"{FINAL}/mural_check.jpg", quality=90)
    
    clean = canvas.copy()
    clean.thumbnail((1400, 1400), Image.LANCZOS)
    clean.convert("RGB").save(f"{FINAL}/mural_preview.jpg", quality=92)
    
    print("Done!")


if __name__ == "__main__":
    main()
