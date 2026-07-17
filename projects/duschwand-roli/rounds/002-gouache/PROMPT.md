# Grok v2 — Gouache Style (Mar 31)

## Approach
Used `grok_3_red_amph.png` as the master style reference. Uploaded style ref + original photo to Grok for each scene.
Automated via browser control script (`grok_gen_v4.py`).

## Prompt Template (same for all 6 scenes, with vehicle-specific details swapped)

```
Recreate this photo in EXACTLY the same art style as the attached reference image (the red Amphicar illustration).

Match the style PRECISELY: semi-realistic digital painting mimicking traditional gouache, smooth controlled strokes, NO black outlines (form defined by color transitions), warm golden-hour palette (peach, amber, honey), high saturation foreground fading to desaturated background, glossy reflective vehicle paint with chrome specularity, stylized-realistic water with horizontal color bands and dynamic wake splash, gradated sunset sky with soft-edged clouds.

Subject: [VEHICLE-SPECIFIC DESCRIPTION]

BLACK BACKGROUND above the waterline/horizon. No text, no watermarks. This will be composited into a larger scene later.
```

### Vehicle-specific subjects:
1. **Hero (Bild 1):** A TEAL/TURQUOISE Amphicar 770 with license plate B-AP 670 cruising on a lake at golden hour. Three people aboard — keep their exact faces, expressions, hair, clothing, poses, and accessories from the photo. Gold chrome stripes, chrome bumpers, distinctive tail fins.
2. **White (Bild 2):** A WHITE Amphicar 770 with red stripe accents and Italian flag, cruising on a lake. Two people aboard (one wearing stripy pants).
3. **Blue (Bild 4):** A LIGHT BLUE/PASTEL BLUE Amphicar 770 with license plate AB-N 274. Two people in Titanic-like pose.
4. **Hydrofoil (Bild 5):** Person on a hydrofoil board on a lake at golden hour, with a golden retriever/dog.
5. **JetRanger (Bild 6):** A BLUE amphibious vehicle/truck marked "66568 JETRANGER" with Dutch flag. Man with arms spread wide.
6. **VW Van (Bild 7):** A WHITE amphibious VW-type van on water. Woman sitting on roof in a chair, couple inside.

## Results
- Scenes 1-4: Decent style match (6-9/10)
- Scenes 5-7: Too photographic, gouache style didn't hold (3-6/10)
- Grok rendered hero car as RED (copied style ref color) instead of teal — had to emphasize color more
