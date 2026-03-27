-- Make bucket public so images can be served directly via public URLs.
-- Simplest approach for Phase 1.
update storage.buckets set public = true where id = 'project-files';
