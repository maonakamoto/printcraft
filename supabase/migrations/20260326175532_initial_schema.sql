-- PrintCraft: Scene Composer for Physical Art
-- Initial schema

-- Enable pgvector for face embeddings
create extension if not exists vector;

-- Enable UUID generation
create extension if not exists "uuid-ossp" schema extensions;

-------------------------------------------------------
-- STYLES
-- Art style presets with emotional descriptions
-------------------------------------------------------
create table styles (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text not null unique,
  description text not null,
  emotional_tone text not null,
  prompt_template text not null,
  negative_prompt text,
  example_url text,
  sort_order integer not null default 0,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

-------------------------------------------------------
-- PROJECTS
-- One project = one artwork
-------------------------------------------------------
create table projects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  description text,
  style_id uuid references styles(id),
  scene_description text,
  status text not null default 'draft'
    check (status in ('draft', 'uploading', 'generating', 'composing', 'previewing', 'exported', 'printed')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-------------------------------------------------------
-- SURFACES
-- Physical output specifications
-------------------------------------------------------
create table surfaces (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  type text not null default 'canvas'
    check (type in ('glass', 'canvas', 'metal', 'paper', 'tile', 'custom')),
  panels jsonb not null default '[{"width_cm": 100, "height_cm": 70}]',
  seam_positions jsonb not null default '[]',
  dead_zones jsonb not null default '[]',
  dpi_target integer not null default 200,
  bleed_mm numeric not null default 3,
  created_at timestamptz not null default now()
);

-------------------------------------------------------
-- FIGURES
-- Each uploaded person/group
-------------------------------------------------------
create table figures (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  label text,
  original_photo_url text not null,
  extracted_url text,
  styled_url text,
  face_embedding vector(512),
  face_confidence numeric,
  position_x numeric,
  position_y numeric,
  scale numeric not null default 1.0,
  z_depth integer not null default 0,
  status text not null default 'uploaded'
    check (status in ('uploaded', 'extracting', 'extracted', 'styling', 'styled', 'verified', 'failed')),
  created_at timestamptz not null default now()
);

-------------------------------------------------------
-- COMPOSITIONS
-- Versioned scene renders
-------------------------------------------------------
create table compositions (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  version integer not null default 1,
  background_url text,
  composite_url text,
  layout jsonb,
  created_at timestamptz not null default now()
);

-------------------------------------------------------
-- EXPORTS
-- Print-ready file outputs
-------------------------------------------------------
create table exports (
  id uuid primary key default gen_random_uuid(),
  composition_id uuid not null references compositions(id) on delete cascade,
  format text not null default 'png'
    check (format in ('png', 'tiff', 'pdf')),
  dpi integer not null,
  width_px integer not null,
  height_px integer not null,
  panels jsonb not null default '[]',
  color_profile text not null default 'srgb'
    check (color_profile in ('srgb', 'cmyk', 'adobe_rgb')),
  bleed_mm numeric not null default 3,
  file_url text,
  created_at timestamptz not null default now()
);

-------------------------------------------------------
-- INDEXES
-------------------------------------------------------
create index idx_projects_user_id on projects(user_id);
create index idx_figures_project_id on figures(project_id);
create index idx_compositions_project_id on compositions(project_id);
create index idx_exports_composition_id on exports(composition_id);

-------------------------------------------------------
-- ROW LEVEL SECURITY
-------------------------------------------------------
alter table projects enable row level security;
alter table surfaces enable row level security;
alter table figures enable row level security;
alter table compositions enable row level security;
alter table exports enable row level security;
alter table styles enable row level security;

-- Users can only access their own projects
create policy "Users see own projects"
  on projects for all
  using (auth.uid() = user_id);

create policy "Users see own surfaces"
  on surfaces for all
  using (project_id in (select id from projects where user_id = auth.uid()));

create policy "Users see own figures"
  on figures for all
  using (project_id in (select id from projects where user_id = auth.uid()));

create policy "Users see own compositions"
  on compositions for all
  using (project_id in (select id from projects where user_id = auth.uid()));

create policy "Users see own exports"
  on exports for all
  using (composition_id in (
    select c.id from compositions c
    join projects p on c.project_id = p.id
    where p.user_id = auth.uid()
  ));

-- Styles are public read-only
create policy "Styles are public"
  on styles for select
  using (true);

-------------------------------------------------------
-- UPDATED_AT TRIGGER
-------------------------------------------------------
create or replace function update_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger projects_updated_at
  before update on projects
  for each row execute function update_updated_at();

-------------------------------------------------------
-- SEED: Initial art styles
-------------------------------------------------------
insert into styles (name, slug, description, emotional_tone, prompt_template, negative_prompt, sort_order) values
  ('Retro Travel Poster', 'retro-travel', 'Vintage 1960s travel poster meets European comic book. Rich painterly colors, warm golden tones, bold black outlines.', 'Warm nostalgia, golden hour, adventure', 'Vintage 1960s travel poster style. Rich painterly colors, warm golden tones, bold black outlines, slightly textured like a classic print. FACES: Must be EXACTLY recognizable.', 'blurry, low quality, distorted face, watermark, text, logo', 1),
  ('Oil Portrait', 'oil-portrait', 'Classical oil painting with rich darks, warm highlights, and visible brushwork.', 'Gravitas, permanence, legacy', 'Classical oil painting. Rich warm darks, luminous highlights, visible confident brushwork. FACES: Must be EXACTLY recognizable.', 'cartoon, flat, digital, smooth, watermark', 2),
  ('Watercolor', 'watercolor', 'Soft watercolor with bleeding edges, gentle washes, white paper showing through.', 'Gentle, dreamy, ephemeral', 'Watercolor illustration. Soft bleeding edges, gentle color washes, luminous. FACES: Must be EXACTLY recognizable.', 'hard edges, digital, cartoon, watermark', 3),
  ('Pop Art', 'pop-art', 'Bold Warhol/Lichtenstein with flat vivid colors, halftone dots, strong outlines.', 'Bold, energetic, celebration', 'Pop Art style. Bold flat colors, strong black outlines, halftone dots. FACES: Must be EXACTLY recognizable.', 'realistic, painterly, soft, muted, watermark', 4),
  ('Comic Book', 'comic-euro', 'European comic book style like Hergé/Tintin. Clean lines, flat colors with subtle shading.', 'Fun, dynamic, storytelling', 'European comic book style. Clean black outlines, flat colors with cel-shading. FACES: Must be EXACTLY recognizable.', 'realistic, painterly, blurry, watermark', 5),
  ('Renaissance', 'renaissance', 'Florentine painting with chiaroscuro lighting and golden atmosphere.', 'Sacred, eternal, reverence', 'Renaissance painting. Chiaroscuro lighting, rich warm palette, golden atmosphere. FACES: Must be EXACTLY recognizable.', 'modern, cartoon, flat, digital, watermark', 6),
  ('Impressionist', 'impressionist', 'Visible brushstrokes, dappled light, vibrant colors. Monet meets Renoir.', 'Warmth, movement, life', 'Impressionist painting. Visible brushstrokes, dappled sunlight, vibrant colors. FACES: Must be EXACTLY recognizable.', 'sharp, digital, cartoon, flat, watermark', 7),
  ('Art Deco', 'art-deco', '1920s poster art with geometric shapes, elegant lines, metallic accents.', 'Elegant, glamorous, sophisticated', 'Art Deco style. Geometric shapes, elegant lines, metallic gold accents. FACES: Must be EXACTLY recognizable.', 'realistic, painterly, soft, watermark', 8),
  ('Noir', 'noir', 'Film noir with dramatic high-contrast black and white, deep shadows.', 'Moody, mysterious, dramatic', 'Film noir style. Dramatic high-contrast black and white, deep shadows. FACES: Must be EXACTLY recognizable.', 'color, bright, cheerful, cartoon, watermark', 9);
