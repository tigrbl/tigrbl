# Forms, Multipart, and Uploads

## Current public surface

The framework now closes the request-body operator surface for:

- `application/x-www-form-urlencoded`
- `multipart/form-data`
- uploaded files through `Request.files`

## Request APIs

- `await request.form()`
- `request.form_sync()`
- `request.files`
- `UploadedFile.filename`
- `UploadedFile.content_type`
- `UploadedFile.body`
- `UploadedFile.text()`

## Notes

The Phase 7 operator tests verify a multipart submission with scalar fields plus an uploaded text file and confirm that the request model round-trips the parsed values correctly.
