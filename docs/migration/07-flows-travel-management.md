### Flow: Travel Management

#### Create Travel
- Page: `[locale]/travels/create`
- Fields:
  - Method (plane/car/bus/petTransport/other)
  - Origin & Destination (if plane, restrict to IATA selectable; else free text)
  - Ticket date (optional)
  - Estimated date
  - Vehicle plate (conditional: car)
  - Pets (multi-select from user’s pets)
- Submit:
  - POST `/travels` with payload; redirect to travel details.

#### Travel Details
- Page: `[locale]/travels/[id]`
- Sections:
  - Header: status chip, origin/destination, ticket/estimated dates, method.
  - Pets in travel (avatars, names/species).
  - Documents:
    - Two panels side-by-side:
      - Owner required documents
      - Pet documents (pet selector, then list required docs for that pet)
    - Each required doc row:
      - Name (translated)
      - Status: Not Uploaded / Uploaded / Verified (optional)
      - “Upload” button → opens upload modal
      - If uploaded: “View” (PDF viewer or image) + “Replace” (re-upload)
- Compute progress:
  - GET `/travels/:id/progress` returns percent.
- Upload:
  - POST `/documents/upload` (multipart; fields: travelId, entityType, entityId, documentType)
  - Update list via TanStack Query invalidate.

#### Admin Travel Docs Config
- Admin page `[locale]/admin/travel/[id]`:
  - Sets `requiredDocuments.owner` array via checkboxes
  - For each pet in travel, sets `requiredDocuments.pets[petId] = []`.
  - PATCH `/travels/:id/required-documents`

#### IATA Integration
- `lib/utils/airports.ts`:
  - `getAirportByCode(code)`
  - `getAirportCityByCode(code)`
  - `getFlagUrl(countryCode)`
- Use in UI to render “NYC (New York)” etc., with small flag chips if desired.

#### PDF/Image Viewer
- Use `react-pdf` for PDFs, with lazy loading.
- Images: `<Image>` with `next/image`.

#### Validation
- Zod schema for travel create/update; server class-validator mirrors it.


