### Flow: Admin Management

#### Pages
- `[locale]/admin` (list/search users, pets, and current travel status)
- `[locale]/admin/travel/[id]` (view travel details and documents, update required docs)
- `[locale]/admin/users/[username]` (compact user profile)

#### Admin Dashboard Features
- Search by tutor name, username, or pet names.
- Cards showing:
  - Owner name & `@username`
  - Current travel (status chip, origin/destination, ticket or estimated date)
  - Quick link to “View profile”
  - Pets list with thumbnails
- “View Travel” opens details with:
  - Status label
  - Origin/Destination
  - Ticket date
  - Travel method
  - Pets list with thumbnails
  - History/events (optional backlog)
  - Notes (local; a dedicated events collection can be added later)

#### Required Documents Management
- Admin sets `requiredDocuments` on a travel:
```ts
type RequiredDocumentsPayload = {
  owner: DocumentType[];
  pets: Record<string, DocumentType[]>;
}
```
- API: `PATCH /travels/:id/required-documents`
- Frontend UI:
  - Two sections: Owner docs; Per-pet docs (pet selector + checklist).
  - Persist with optimistic updates (TanStack Query).

#### Document Verification (optional enhancement)
- Extend `documents` with `status: 'pending'|'verified'|'rejected'` and `reviewNotes?`.
- Add API: `PATCH /documents/:id` for status updates.

#### Admin Auth
- Replace password-only login with email/password (role=admin).
- Guard routes on API & SSR (server components can check cookie/JWT).

#### Improvements vs current
- Fully typed data, better search, reliable doc scoping per travel, optimistic document requirements updates, status badges with accessible colors.


