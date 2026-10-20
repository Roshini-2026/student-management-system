# Task 13: File Uploads
- Students can have a profile photo (JPG/PNG, max 2 MB) and a supporting document (PDF, max 5 MB).
- Files are checked by extension, real content (Pillow for images, "%PDF-" header for PDFs) and size.
- Files get random names, so the client's filename is never trusted. Replaced or removed files are deleted from disk.
- Photos are saved in media/ and served at /media/. Documents are saved in private_media/ and only served through a view that checks the user's permission.
- Development vs production: in development Django serves media from local folders. In production the web server (or cloud storage such as S3 with private buckets and signed URLs) should serve files, and the private folder must never be public.
- Errors and fixes: none.