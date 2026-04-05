#!/usr/bin/env python3
"""
GIMP 3.0 Python-Fu headless mural composite.
Run via: gimp -i --batch-interpreter python-fu-eval -b "exec(open('THIS_FILE').read())"
"""
import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gegl', '0.4')
from gi.repository import Gimp, Gegl, GLib
import os, sys

BASE = "/home/g/Dokumente/Duschwand"
V4 = f"{BASE}/07-grok-v4-retro-poster"
OUT_DIR = f"{BASE}/05-composites"

CANVAS_W = 5900
CANVAS_H = 5700

# Best picks from v4 retro-poster (most consistent style)
SCENES = {
    "bild1_hero":  f"{V4}/bild1_hero_teal_bap670.jpg",
    "bild2_white": f"{V4}/bild2_white_italian.jpg",
    "bild3_teal":  f"{V4}/bild3_teal_kd.jpg",
    "bild4_blue":  f"{V4}/bild4_blue_abn274.jpg",
    "bild5_hydro": f"{V4}/bild5_hydrofoil_dog.jpg",
    "bild6_jet":   f"{V4}/bild6_jetranger.jpg",
    "bild7_vw":    f"{V4}/bild7_vw_van.jpg",
}

# Layout: (center_x, waterline_y, target_width, depth)
# depth 0=foreground, 1=mid, 2=far
LAYOUT = {
    "bild1_hero":  (3800, 4800, 2400, 0),
    "bild2_white": (4900, 3700, 1100, 1),
    "bild3_teal":  (3200, 3400, 1000, 1),
    "bild4_blue":  (4400, 3200, 950, 1),
    "bild5_hydro": (1200, 4200, 800, 1),
    "bild6_jet":   (900, 2900, 800, 2),
    "bild7_vw":    (1600, 2700, 750, 2),
}

# Render order: back to front
RENDER_ORDER = ["bild7_vw", "bild6_jet", "bild4_blue", "bild3_teal",
                "bild2_white", "bild5_hydro", "bild1_hero"]

print("=== GIMP 3.0 Mural Composite ===")

# Verify files
for name, path in SCENES.items():
    if not os.path.exists(path):
        print(f"MISSING: {path}")
        sys.exit(1)
print(f"All {len(SCENES)} scene files found.")

# Create canvas
img = Gimp.Image.new(CANVAS_W, CANVAS_H, Gimp.ImageBaseType.RGB)
print(f"Canvas created: {CANVAS_W}x{CANVAS_H}")

# Background gradient layer (sunset sky + water)
bg = Gimp.Layer.new(img, "background", CANVAS_W, CANVAS_H,
                    Gimp.ImageType.RGB_IMAGE, 100.0, Gimp.LayerMode.NORMAL)
img.insert_layer(bg, None, -1)

# Fill with warm sunset orange as base
color_fg = Gimp.RGB()
color_fg.set(255/255, 160/255, 60/255)
Gimp.context_set_foreground(color_fg)
bg.edit_fill(Gimp.FillType.FOREGROUND)

# Now add gradient overlay: dark blue top -> warm orange at horizon -> dark teal water bottom
gradient_layer = Gimp.Layer.new(img, "sky_gradient", CANVAS_W, CANVAS_H,
                                Gimp.ImageType.RGBA_IMAGE, 100.0, Gimp.LayerMode.NORMAL)
img.insert_layer(gradient_layer, None, -1)

# Use built-in gradient
horizon_y = int(CANVAS_H * 0.36)

# Sky portion: deep blue-purple at top, warm at horizon
sky_layer = Gimp.Layer.new(img, "sky", CANVAS_W, horizon_y,
                           Gimp.ImageType.RGBA_IMAGE, 80.0, Gimp.LayerMode.MULTIPLY)
img.insert_layer(sky_layer, None, -1)
color_sky = Gimp.RGB()
color_sky.set(40/255, 30/255, 80/255)
Gimp.context_set_foreground(color_sky)
sky_layer.edit_fill(Gimp.FillType.FOREGROUND)

# Water portion: darker, more blue-green
water_layer = Gimp.Layer.new(img, "water_tint", CANVAS_W, CANVAS_H - horizon_y,
                             Gimp.ImageType.RGBA_IMAGE, 40.0, Gimp.LayerMode.MULTIPLY)
img.insert_layer(water_layer, None, -1)
water_layer.set_offsets(0, horizon_y)
color_water = Gimp.RGB()
color_water.set(20/255, 60/255, 80/255)
Gimp.context_set_foreground(color_water)
water_layer.edit_fill(Gimp.FillType.FOREGROUND)

print(f"Background created (horizon at y={horizon_y})")

# Place each scene
for name in RENDER_ORDER:
    path = SCENES[name]
    cx, wy, tw, depth = LAYOUT[name]
    
    print(f"Loading {name}...")
    
    # Load as layer
    scene_layer = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, img, 
                                        GLib.file_new_for_path(path))
    img.insert_layer(scene_layer, None, -1)
    scene_layer.set_name(name)
    
    # Scale to target width
    orig_w = scene_layer.get_width()
    orig_h = scene_layer.get_height()
    scale = tw / orig_w
    new_h = int(orig_h * scale)
    scene_layer.scale(tw, new_h, False)
    
    # Position: center at cx, bottom at waterline
    pos_x = cx - tw // 2
    pos_y = wy - new_h
    scene_layer.set_offsets(pos_x, pos_y)
    
    print(f"  Placed at ({pos_x}, {pos_y}), size {tw}x{new_h}")
    
    # Depth effects
    if depth == 2:
        # Far background: desaturate, reduce opacity, slight blur
        scene_layer.set_opacity(70.0)
        Gimp.drawable_desaturate(scene_layer, Gimp.DesaturateMode.LUMINOSITY_601)
        # Re-colorize with warm tint
        Gimp.drawable_color_balance(scene_layer, Gimp.ColorRange.MIDTONES, True, 15, 0, -20)
    elif depth == 1:
        # Mid-ground: slightly reduced
        scene_layer.set_opacity(85.0)
        Gimp.drawable_color_balance(scene_layer, Gimp.ColorRange.MIDTONES, True, 8, 0, -10)
    else:
        # Foreground hero: full opacity, warm
        scene_layer.set_opacity(100.0)
        Gimp.drawable_color_balance(scene_layer, Gimp.ColorRange.MIDTONES, True, 5, 0, -5)
    
    # Add layer mask for bottom fade (water submersion)
    mask = scene_layer.create_mask(Gimp.AddMaskType.WHITE)
    scene_layer.add_mask(mask)
    
    # Draw gradient on mask: white (visible) at top, fading to black (invisible) at bottom 20%
    color_white = Gimp.RGB()
    color_white.set(1.0, 1.0, 1.0)
    color_black = Gimp.RGB()
    color_black.set(0.0, 0.0, 0.0)
    Gimp.context_set_foreground(color_white)
    Gimp.context_set_background(color_black)
    
    # The mask gradient goes from visible to invisible in the bottom portion
    fade_start_y = pos_y + int(new_h * 0.75)
    fade_end_y = pos_y + new_h + 20
    
    # Use GIMP's gradient tool on the mask
    Gimp.context_set_opacity(100.0)
    mask.edit_gradient_fill(Gimp.GradientType.LINEAR,
                           0.0,  # offset
                           Gimp.RepeatMode.NONE,
                           False,  # reverse
                           Gimp.GradientSegmentType.LINEAR,
                           0.0,  # supersample
                           True,  # dither
                           0, fade_start_y,  # x1, y1
                           0, fade_end_y)    # x2, y2
    
    # Create reflection layer
    if depth < 2:  # Only for foreground and mid-ground
        reflect = scene_layer.copy()
        img.insert_layer(reflect, None, -1)
        reflect.set_name(f"{name}_reflection")
        
        # Flip vertically
        reflect.transform_flip_simple(Gimp.OrientationType.VERTICAL, True, 0)
        
        # Position below the original
        reflect.set_offsets(pos_x, wy)
        reflect.set_opacity(25.0 - depth * 8)
        reflect.set_mode(Gimp.LayerMode.SCREEN)
        
        # Mask the reflection to fade out
        rmask = reflect.create_mask(Gimp.AddMaskType.WHITE)
        reflect.add_mask(rmask)
        Gimp.context_set_foreground(color_white)
        Gimp.context_set_background(color_black)
        rmask.edit_gradient_fill(Gimp.GradientType.LINEAR,
                                0.0, Gimp.RepeatMode.NONE, False,
                                Gimp.GradientSegmentType.LINEAR, 0.0, True,
                                0, wy, 0, wy + int(new_h * 0.4))

print("All scenes placed.")

# --- Global color unification ---
print("Flattening and applying global color correction...")
flat = img.flatten()

# Warm color balance on the whole image
Gimp.drawable_color_balance(flat, Gimp.ColorRange.MIDTONES, True, 10, 0, -15)
Gimp.drawable_color_balance(flat, Gimp.ColorRange.HIGHLIGHTS, True, 5, 3, -8)

# Slight contrast via curves
Gimp.curves_spline(flat, Gimp.HistogramChannel.VALUE, [0, 0, 64, 45, 128, 132, 192, 215, 255, 255])

# --- Export ---
out_full = f"{OUT_DIR}/mural_gimp_v1.png"
out_preview = f"{OUT_DIR}/mural_gimp_v1_preview.jpg"

print(f"Exporting full res: {out_full}")
# GIMP 3.0 export API
Gimp.file_overwrite(Gimp.RunMode.NONINTERACTIVE, img, flat, GLib.file_new_for_path(out_full))

# Scale for preview
img_preview = img.duplicate()
img_preview.scale_full(1400, 1353, Gimp.InterpolationType.LANCZOS)
flat_preview = img_preview.flatten()
print(f"Exporting preview: {out_preview}")
Gimp.file_overwrite(Gimp.RunMode.NONINTERACTIVE, img_preview, flat_preview, GLib.file_new_for_path(out_preview))

img_preview.delete()
img.delete()

print("\n✅ DONE!")
print(f"  Full: {out_full}")
print(f"  Preview: {out_preview}")

Gimp.quit()
