-- Allow anyone (including anon) to upload/read from project-files bucket
-- This is for guest/unauthenticated mode in Phase 1

create policy "Anon can upload"
  on storage.objects for insert
  with check (bucket_id = 'project-files');

create policy "Anon can read"
  on storage.objects for select
  using (bucket_id = 'project-files');

create policy "Anon can update"
  on storage.objects for update
  using (bucket_id = 'project-files');

create policy "Anon can delete"
  on storage.objects for delete
  using (bucket_id = 'project-files');
