#!/usr/bin/env python3
"""
GIMP 3.0 headless mural composite via Script-Fu batch commands.
Generates a .sf script then runs it through GIMP.

Strategy: Use GIMP's real compositing engine — layer modes, masks,
Curves, Gaussian blur, reflections — instead of Pillow pixel math.
"""

import subprocess, os, sys, json

BASE = "/home/g/Dokumente/Duschwand"
V4 = f"{BASE}/07-grok-v4-retro-poster"
SRC_PHOTOS = f"{BASE}/00-source-photos"
OUT_DIR = f"{BASE}/05-composites"
SCRIPT_PATH = f"{BASE}/06-scripts/_composite_batch.sf"

# Canvas: 197cm x 190cm @ 150 DPI (half of 300 to keep RAM sane, upscale at end)
# 150 DPI: 11634 x 11220 px — still huge. Let's go 100 DPI first for iteration.
# 100 DPI: 7756 x 7480 px
# Or keep the existing 5900x5700 for now and upgrade later.
CANVAS_W = 5900
CANVAS_H = 5700
HORIZON_Y = int(CANVAS_H * 0.36)  # 2052

# Panel seam at 77.5cm from left = 77.5/197 * 5900 = 2321px
SEAM_X = 2321
# Dead zone: 70-85cm = 2094-2545px
DEAD_LEFT = 2094
DEAD_RIGHT = 2545

# Best picks from v4 (retro-poster style — most consistent)
SCENES = {
    "bild1_hero": f"{V4}/bild1_hero_teal_bap670.jpg",
    "bild2_white": f"{V4}/bild2_white_italian.jpg",
    "bild3_teal": f"{V4}/bild3_teal_kd.jpg",
    "bild4_blue": f"{V4}/bild4_blue_abn274.jpg",
    "bild5_hydro": f"{V4}/bild5_hydrofoil_dog.jpg",
    "bild6_jet": f"{V4}/bild6_jetranger.jpg",
    "bild7_vw": f"{V4}/bild7_vw_van.jpg",
}

# Layout: (center_x, waterline_y, target_width, depth_layer)
# depth_layer: 0=foreground, 1=mid, 2=background
LAYOUT = {
    "bild1_hero":  (3800, 4800, 2400, 0),   # Main image, right panel, large
    "bild2_white": (4900, 3700, 1100, 1),    # Near hero, mid-right
    "bild3_teal":  (3200, 3400, 1000, 1),    # Near hero, mid-center
    "bild4_blue":  (4400, 3200, 950, 1),     # Near hero, mid-right-back
    "bild5_hydro": (1200, 4200, 800, 1),     # Left panel
    "bild6_jet":   (900, 2900, 800, 2),      # Background, small
    "bild7_vw":    (1600, 2700, 750, 2),     # Background, small
}

def generate_script():
    """Generate Script-Fu commands for GIMP batch processing."""
    lines = []
    
    # Helper: escape path for Script-Fu
    def sf_path(p):
        return p.replace("\\", "/")
    
    lines.append(f'; Auto-generated GIMP composite script')
    lines.append(f'; Canvas: {CANVAS_W}x{CANVAS_H}')
    lines.append(f'')
    
    # Create canvas
    lines.append(f'(let* (')
    lines.append(f'  (canvas (car (gimp-image-new {CANVAS_W} {CANVAS_H} RGB)))')
    lines.append(f'  (bg-layer (car (gimp-layer-new canvas {CANVAS_W} {CANVAS_H} RGBA-IMAGE "Background" 100 LAYER-MODE-NORMAL)))')
    lines.append(f'  )')
    lines.append(f'  (gimp-image-insert-layer canvas bg-layer 0 -1)')
    
    # Fill background with sunset gradient (warm orange to deep blue)
    lines.append(f'  ; Sunset gradient background')
    lines.append(f'  (gimp-context-set-foreground \'(255 160 60))')
    lines.append(f'  (gimp-context-set-background \'(20 40 80))')
    lines.append(f'  (gimp-drawable-edit-fill bg-layer FILL-FOREGROUND)')
    
    # Apply gradient: warm sky at horizon, darker at top and bottom (water)
    lines.append(f'  (gimp-context-set-opacity 100)')
    lines.append(f'  (gimp-gradient-select "FG to BG (RGB)")')
    lines.append(f'  (gimp-drawable-edit-gradient-fill bg-layer GRADIENT-LINEAR 0 REPEAT-NONE 0 FALSE 0 0 TRUE 0 0 0 {CANVAS_H})')
    
    # Load each scene as a layer (back to front)
    render_order = ["bild7_vw", "bild6_jet", "bild4_blue", "bild3_teal", 
                    "bild2_white", "bild5_hydro", "bild1_hero"]
    
    for name in render_order:
        path = sf_path(SCENES[name])
        cx, wy, tw, depth = LAYOUT[name]
        
        lines.append(f'')
        lines.append(f'  ; --- {name} ---')
        # Load as layer
        lines.append(f'  (let* (')
        lines.append(f'    (scene-layer (car (gimp-file-load-layer RUN-NONINTERACTIVE canvas "{path}")))')
        lines.append(f'    )')
        lines.append(f'    (gimp-image-insert-layer canvas scene-layer 0 -1)')
        lines.append(f'    (gimp-layer-set-name scene-layer "{name}")')
        
        # Scale to target width
        lines.append(f'    (let* (')
        lines.append(f'      (orig-w (car (gimp-drawable-get-width scene-layer)))')
        lines.append(f'      (orig-h (car (gimp-drawable-get-height scene-layer)))')
        lines.append(f'      (scale-factor (/ {tw}.0 orig-w))')
        lines.append(f'      (new-h (inexact->exact (round (* orig-h scale-factor))))')
        lines.append(f'      )')
        lines.append(f'      (gimp-layer-scale scene-layer {tw} new-h FALSE)')
        
        # Position: center_x - width/2, waterline_y - height (bottom of vehicle at waterline)
        lines.append(f'      (let* (')
        lines.append(f'        (pos-x (- {cx} (/ {tw} 2)))')
        lines.append(f'        (pos-y (- {wy} new-h))')
        lines.append(f'        )')
        lines.append(f'        (gimp-layer-set-offsets scene-layer pos-x pos-y)')
        
        # Depth effects: background scenes get desaturated + slightly blurred
        if depth == 2:
            lines.append(f'        (gimp-drawable-desaturate scene-layer DESATURATE-AVERAGE)')
            lines.append(f'        (gimp-drawable-color-balance scene-layer COLOR-RANGE-MIDTONES TRUE -10 0 -20)')
            lines.append(f'        (gimp-layer-set-opacity scene-layer 75)')
            lines.append(f'        (plug-in-gauss RUN-NONINTERACTIVE canvas scene-layer 3 3 0)')
        elif depth == 1:
            lines.append(f'        (gimp-layer-set-opacity scene-layer 90)')
            lines.append(f'        (gimp-drawable-color-balance scene-layer COLOR-RANGE-MIDTONES TRUE -5 0 -10)')
        
        # Add layer mask for bottom fade (water submersion)
        lines.append(f'        (let* (')
        lines.append(f'          (mask (car (gimp-layer-create-mask scene-layer ADD-MASK-WHITE)))')
        lines.append(f'          )')
        lines.append(f'          (gimp-layer-add-mask scene-layer mask)')
        lines.append(f'          ; Gradient on mask: fade bottom 20% to transparent')
        lines.append(f'          (gimp-context-set-foreground \'(255 255 255))')
        lines.append(f'          (gimp-context-set-background \'(0 0 0))')
        lines.append(f'          (let* (')
        lines.append(f'            (layer-h (car (gimp-drawable-get-height scene-layer)))')
        lines.append(f'            (layer-offY (car (cdr (gimp-drawable-get-offsets scene-layer))))')
        lines.append(f'            (fade-start (+ layer-offY (inexact->exact (round (* layer-h 0.8)))))')
        lines.append(f'            (fade-end (+ layer-offY layer-h))')
        lines.append(f'            )')
        lines.append(f'            (gimp-drawable-edit-gradient-fill mask GRADIENT-LINEAR 0 REPEAT-NONE 0 FALSE 0 0 TRUE 0 fade-start 0 fade-end)')
        lines.append(f'          )')
        lines.append(f'        )')
        lines.append(f'      )')  # close pos let
        lines.append(f'    )')  # close scale let
        lines.append(f'  )')  # close scene let
    
    # Flatten and warm-tint the whole image
    lines.append(f'')
    lines.append(f'  ; --- Global color unification ---')
    lines.append(f'  (gimp-image-flatten canvas)')
    lines.append(f'  (let* (')
    lines.append(f'    (flat (car (gimp-image-get-active-drawable canvas)))')
    lines.append(f'    )')
    lines.append(f'    ; Warm color balance')
    lines.append(f'    (gimp-drawable-color-balance flat COLOR-RANGE-MIDTONES TRUE 8 0 -12)')
    lines.append(f'    (gimp-drawable-color-balance flat COLOR-RANGE-HIGHLIGHTS TRUE 5 0 -8)')
    lines.append(f'    ; Slight contrast boost')
    lines.append(f'    (gimp-curves-spline flat HISTOGRAM-VALUE 10 #(0 0 64 40 128 135 192 220 255 255))')
    lines.append(f'  )')
    
    # Export
    out_path = sf_path(f"{OUT_DIR}/mural_gimp_v1.png")
    preview_path = sf_path(f"{OUT_DIR}/mural_gimp_v1_preview.jpg")
    
    lines.append(f'')
    lines.append(f'  ; Export full res')
    lines.append(f'  (file-png-save RUN-NONINTERACTIVE canvas (car (gimp-image-get-active-drawable canvas)) "{out_path}" "mural" 0 9 1 1 1 1 1)')
    
    # Scale for preview
    lines.append(f'  (gimp-image-scale-full canvas 1400 1353 INTERPOLATION-LANCZOS)')
    lines.append(f'  (file-jpeg-save RUN-NONINTERACTIVE canvas (car (gimp-image-get-active-drawable canvas)) "{preview_path}" "preview" 0.92 0 0 0 "" 0 1 0 2 0)')
    
    lines.append(f'  (gimp-image-delete canvas)')
    lines.append(f')')  # close outermost let*
    
    return "\n".join(lines)


def main():
    # Verify all source files exist
    missing = [n for n, p in SCENES.items() if not os.path.exists(p)]
    if missing:
        print(f"Missing files: {missing}")
        sys.exit(1)
    
    print("All 7 scene files found.")
    print("Generating Script-Fu composite script...")
    
    script = generate_script()
    with open(SCRIPT_PATH, 'w') as f:
        f.write(script)
    print(f"Script written to: {SCRIPT_PATH}")
    
    print("Running GIMP headless composite...")
    print("(This may take a few minutes on your machine)")
    
    # GIMP 3.0 requires --batch-interpreter
    with open(SCRIPT_PATH, 'r') as f:
        script_content = f.read()
    
    result = subprocess.run(
        ["gimp", "-i", "--batch-interpreter", "plug-in-script-fu-eval",
         "-b", script_content, "-b", "(gimp-quit 0)"],
        capture_output=True, text=True, timeout=600
    )
    
    print("STDOUT:", result.stdout[-500:] if result.stdout else "(none)")
    print("STDERR:", result.stderr[-500:] if result.stderr else "(none)")
    print("Return code:", result.returncode)
    
    out_file = f"{OUT_DIR}/mural_gimp_v1.png"
    preview_file = f"{OUT_DIR}/mural_gimp_v1_preview.jpg"
    if os.path.exists(out_file):
        size_mb = os.path.getsize(out_file) / 1024 / 1024
        print(f"\n✅ Full res: {out_file} ({size_mb:.1f} MB)")
    if os.path.exists(preview_file):
        print(f"✅ Preview: {preview_file}")
    else:
        print("\n❌ Output not found — check GIMP errors above")


if __name__ == "__main__":
    main()
