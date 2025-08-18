### API Design (Nest.js + REST)

Base URL: `/api`

Auth:
- POST `/auth/register`
- POST `/auth/login` → { accessToken, refreshToken }
- POST `/auth/refresh`
- POST `/auth/logout`

Users:
- GET `/users/:id`
- GET `/users/by-username/:username`
- GET `/users` (admin; filters: q, page, limit)
- POST `/users` (admin create)
- PATCH `/users/:id`
- DELETE `/users/:id` (admin)
- GET `/users/:id/pets`
- GET `/users/:id/travels`

Pets:
- GET `/pets/:id`
- POST `/pets` // body: { ownerId, ... }
- PATCH `/pets/:id`
- DELETE `/pets/:id`
- POST `/pets/:id/avatar` (multipart: file) → stores avatar on Pet record (not a document)
- DELETE `/pets/:id/avatar`

Travels:
- GET `/travels/:id`
- GET `/travels` (filters: username, status, page, limit)
- POST `/travels` // user or admin
- PATCH `/travels/:id`
- DELETE `/travels/:id`
- PATCH `/travels/:id/required-documents` (admin)
- GET `/travels/:id/progress` → { total, completed, percent, breakdown }

Documents:
- GET `/documents/:id`
- GET `/travels/:travelId/documents?entityType=user|pet&entityId=...`
- POST `/documents/upload` (multipart)
  - fields: `travelId`, `entityType`, `entityId`, `documentType`, `file`
  - server uploads to Firebase Storage via Admin SDK, returns created document record
- DELETE `/documents/:id`

Admin:
- GET `/admin/dashboard` (stats: users count, pets count, travels by status)
- GET `/admin/users` (search by ownerName, username, pet name)
- GET `/admin/travel/:id` (admin enriched view)

#### DTOs and Validation
- Use `class-validator` (Nest) mirroring zod on client:
  - RegisterUserDto, LoginDto
  - CreatePetDto, UpdatePetDto
  - CreateTravelDto, UpdateTravelDto
  - UpdateRequiredDocumentsDto
  - UploadDocumentDto (non-file fields)
- For uploads: Nest `@UseInterceptors(FileInterceptor('file'))` + Multer memory storage.

#### Firebase Storage
- Server-side only. `FirebaseStorageService`:
  - `uploadFile(buffer: Buffer, contentType: string, destPath: string): Promise<{ publicUrl, path, size }>`
  - `deleteFile(path: string)`
  - `getPublicUrl(path: string)`

#### Error Model
```json
{ "error": { "code": "VALIDATION_ERROR", "message": "Invalid email", "fieldErrors": { "email": "Invalid" } } }
```

#### Pagination
- Standard: `?page=1&limit=20`
- Response: `{ data: [...], page, limit, total, hasNext }`

#### Security
- JWT for protected routes.
- Role guard for admin endpoints.
- Rate limit for uploads.
- Validate file type/size on server.


