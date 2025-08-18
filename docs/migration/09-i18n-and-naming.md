### i18n and Naming Conventions

#### Goals
- All code (identifiers, filenames, enums) in English.
- All UI text in translations, supporting EN, ES, PT.

#### Recommended Stack
- Frontend: `next-intl` with App Router and static messages per locale.
- Backend: return machine-friendly enum values in English; map to display text on the client via i18n.

#### Translation Files Structure
```
lib/i18n/messages/
  en.json
  es.json
  pt.json
```
Keys follow namespaces:
- `common.*` small shared words: save, cancel, edit
- `pages.*` page-specific labels
- `enums.*` enum value maps
- `errors.*` error messages

#### Enforcement
- ESLint rule/check: disallow hard-coded strings in components except for test ids, aria labels that are purely structural (prefer i18n anyway).
- PR checklist: new UI must add keys for EN/ES/PT.

#### Naming
- Use lowerCamelCase for object keys, PascalCase for types/classes, SCREAMING_CASE for env vars.
- Prefer explicit nouns/verbs: `ownerName`, `travelMethod`, `requiredDocuments`.
- Enum values are kebab-like lowercase strings persisted in DB (e.g., `plane`, `upcoming`).

#### Date/Number Formatting
- Use `Intl.DateTimeFormat` and `Intl.NumberFormat` client-side based on active locale.


