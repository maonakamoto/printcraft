import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gegl', '0.4')
from gi.repository import Gimp, Gegl, GLib, Gio

BASE = "/home/g/Dokumente/Duschwand"
V4 = f"{BASE}/07-grok-v4-retro-poster"
OUT_DIR = f"{BASE}/05-composites"

CANVAS_W = 5900
CANVAS_H = 5700

SCENES = {
    "bild1_hero":  f"{V4}/bild1_hero_teal_bap670.jpg",
    "bild2_white": f"{V4}/bild2_white_italian.jpg",
    "bild3_teal":  f"{V4}/bild3_teal_kd.jpg",
    "bild4_blue":  f"{V4}/bild4_blue_abn274.jpg",
    "bild5_hydro": f"{V4}/bild5_hydrofoil_dog.jpg",
    "bild6_jet":   f"{V4}/bild6_jetranger.jpg",
    "bild7_vw":    f"{V4}/bild7_vw_van.jpg",
}

LAYOUT = {
    "bild1_hero":  (3800, 4800, 2400, 0),
    "bild2_white": (4900, 3700, 1100, 1),
    "bild3_teal":  (3200, 3400, 1000, 1),
    "bild4_blue":  (4400, 3200, 950, 1),
    "bild5_hydro": (1200, 4200, 800, 1),
    "bild6_jet":   (900, 2900, 800, 2),
    "bild7_vw":    (1600, 2700, 750, 2),
}

RENDER_ORDER = ["bild7_vw", "bild6_jet", "bild4_blue", "bild3_teal",
                "bild2_white", "bild5_hydro", "bild1_hero"]

def make_color(r, g, b):
    return Gegl.Color.new(f"rgb({r/255.0}, {g/255.0}, {b/255.0})")

print("=== GIMP 3.0 Mural Composite v3 ===")

import os
for name, path in SCENES.items():
    if not os.path.exists(path):
        print(f"MISSING: {path}")
        raise SystemExit(1)
print(f"All {len(SCENES)} scenes found.")

# Create canvas
img = Gimp.Image.new(CANVAS_W, CANVAS_H, Gimp.ImageBaseType.RGB)

# Background: warm sunset orange
bg = Gimp.Layer.new(img, "background", CANVAS_W, CANVAS_H,
                    Gimp.ImageType.RGB_IMAGE, 100.0, Gimp.LayerMode.NORMAL)
img.insert_layer(bg, None, -1)
Gimp.context_set_foreground(make_color(255, 160, 60))
bg.edit_fill(Gimp.FillType.FOREGROUND)

# Sky darkening layer (multiply)
horizon_y = int(CANVAS_H * 0.36)
sky = Gimp.Layer.new(img, "sky_dark", CANVAS_W, horizon_y,
                     Gimp.ImageType.RGBA_IMAGE, 60.0, Gimp.LayerMode.MULTIPLY)
img.insert_layer(sky, None, -1)
Gimp.context_set_foreground(make_color(40, 30, 80))
sky.edit_fill(Gimp.FillType.FOREGROUND)

# Water layer
water = Gimp.Layer.new(img, "water", CANVAS_W, CANVAS_H - horizon_y,
                       Gimp.ImageType.RGBA_IMAGE, 45.0, Gimp.LayerMode.MULTIPLY)
img.insert_layer(water, None, -1)
water.set_offsets(0, horizon_y)
Gimp.context_set_foreground(make_color(20, 60, 90))
water.edit_fill(Gimp.FillType.FOREGROUND)

print(f"Background done (horizon={horizon_y})")

# Place scenes
for name in RENDER_ORDER:
    path = SCENES[name]
    cx, wy, tw, depth = LAYOUT[name]
    print(f"Loading {name}...")
    
    scene = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, img,
                                  Gio.File.new_for_path(path))
    img.insert_layer(scene, None, -1)
    scene.set_name(name)
    
    # Scale
    orig_w = scene.get_width()
    orig_h = scene.get_height()
    scale = tw / orig_w
    new_h = int(orig_h * scale)
    scene.scale(tw, new_h, False)
    
    # Position
    pos_x = cx - tw // 2
    pos_y = wy - new_h
    scene.set_offsets(pos_x, pos_y)
    print(f"  Placed ({pos_x},{pos_y}) {tw}x{new_h}")
    
    # Depth effects via color balance
    if depth == 2:
        scene.set_opacity(72.0)
        Gimp.drawable_desaturate(scene, Gimp.DesaturateMode.LUMINOSITY_601)
        Gimp.drawable_color_balance(scene, Gimp.ColorRange.MIDTONES, True, 15, 0, -20)
    elif depth == 1:
        scene.set_opacity(87.0)
        Gimp.drawable_color_balance(scene, Gimp.ColorRange.MIDTONES, True, 8, 0, -10)
    else:
        scene.set_opacity(100.0)
        Gimp.drawable_color_balance(scene, Gimp.ColorRange.MIDTONES, True, 5, 0, -5)
    
    # Layer mask for bottom fade
    mask = scene.create_mask(Gimp.AddMaskType.WHITE)
    scene.add_mask(mask)
    
    Gimp.context_set_foreground(make_color(255, 255, 255))
    Gimp.context_set_background(make_color(0, 0, 0))
    
    fade_start = pos_y + int(new_h * 0.78)
    fade_end = pos_y + new_h + 30
    
    mask.edit_gradient_fill(Gimp.GradientType.LINEAR,
                           0.0, Gimp.RepeatMode.NONE, False,
                           Gimp.GradientSegmentType.LINEAR, 0.0, True,
                           0, fade_start, 0, fade_end)
    
    # Water reflection (foreground + mid only)
    if depth < 2:
        refl = scene.copy()
        img.insert_layer(refl, None, -1)
        refl.set_name(f"{name}_refl")
        refl.transform_flip_simple(Gimp.OrientationType.VERTICAL, True, 0)
        refl.set_offsets(pos_x, wy)
        refl.set_opacity(20.0 - depth * 7)
        refl.set_mode(Gimp.LayerMode.SCREEN)
        
        rmask = refl.create_mask(Gimp.AddMaskType.WHITE)
        refl.add_mask(rmask)
        Gimp.context_set_foreground(make_color(255, 255, 255))
        Gimp.context_set_background(make_color(0, 0, 0))
        rmask.edit_gradient_fill(Gimp.GradientType.LINEAR,
                                0.0, Gimp.RepeatMode.NONE, False,
                                Gimp.GradientSegmentType.LINEAR, 0.0, True,
                                0, wy, 0, wy + int(new_h * 0.35))

print("All scenes placed.")

# Flatten + global color correction
print("Flattening + color correction...")
flat = img.flatten()
Gimp.drawable_color_balance(flat, Gimp.ColorRange.MIDTONES, True, 10, 0, -15)
Gimp.drawable_color_balance(flat, Gimp.ColorRange.HIGHLIGHTS, True, 5, 3, -8)
Gimp.curves_spline(flat, Gimp.HistogramChannel.VALUE, [0, 0, 64, 45, 128, 132, 192, 215, 255, 255])

# Export full
out_full = f"{OUT_DIR}/mural_gimp_v1.png"
print(f"Exporting: {out_full}")
Gimp.file_overwrite(Gimp.RunMode.NONINTERACTIVE, img, flat, Gio.File.new_for_path(out_full))

# Export preview
img2 = img.duplicate()
img2.scale_full(1400, 1353, Gimp.InterpolationType.LANCZOS)
flat2 = img2.flatten()
out_prev = f"{OUT_DIR}/mural_gimp_v1_preview.jpg"
print(f"Exporting: {out_prev}")
Gimp.file_overwrite(Gimp.RunMode.NONINTERACTIVE, img2, flat2, Gio.File.new_for_path(out_prev))

img2.delete()
img.delete()
print("DONE!")
Gimp.quit()
