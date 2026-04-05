# Round 9 — Unified Mural Generation

## Approach
Generate the ENTIRE mural scene as one image, instead of compositing individual scenes.
All 7 vehicles/characters described in a single prompt. No photo upload (Grok can't 
handle 7 photos at once). The individual scene images from round 08 serve as style 
reference and face-likeness verification.

## Why
Previous composite attempts (round 05) failed because:
- Photographic background + cartoon vehicles = collage effect
- Scale mismatch between individually generated vehicles
- No unified perspective or spatial logic
- Water doesn't blend at vehicle boundaries

## Key learnings for Grok prompts
- SHORT prompts (~200 chars) trigger Aurora illustration mode
- LONG prompts cause Grok to switch to text-mode photo editing
- Use `page.keyboard.type()` not JS setter — triggers React state properly
- SuperGrok "Auto" model works when prompt is short enough

## Scene Description (from BRIEF.md)
Lake Garda at golden sunset. 7 amphibious vehicles/watercraft spread across the water.
Center: Roli's TEAL Amphicar B-AP 670 (hero, largest).
Supporting cast around it in various positions.

## Prompt Used
See individual attempt files in this directory.

## Print Specs
- Two panels: 80 cm (left) + 120 cm (right) × 200 cm tall
- Minimum 150 DPI = 4,724 × 11,811 px (left) + 7,087 × 11,811 px (right)
- Total: 11,811 × 11,811 px
