### Platform Migration: Architecture Overview

#### Goals
- Rebuild the platform with:
  - Frontend: Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui, TanStack Query, React Hook Form + Zod, `next-intl` for i18n.
  - Backend: Nest.js (REST), TypeScript, Mongoose, MongoDB, Firebase Storage (file management via server-side upload).
- Everything in English in code; PT/ES/EN exposed via translations only.
- Preserve domain rules:
  - Users (0..n) Pets
  - Pets (1) User
  - Users (0..n) Travels
  - Travels (1) User, (1..n) Pets
  - Documents belong to one User OR one Pet, always scoped to one Travel

#### Suggested Repo Structure (monorepo)
- Monorepo (Turborepo) with `apps/web` (Next.js) and `apps/api` (Nest.js), plus shared packages.
```
/
  apps/
    web/                # Next.js (frontend)
    api/                # Nest.js (backend)
  packages/
    ui/                 # shared shadcn/ui wrappers, icons, themes
    config/             # ESLint, TS config, tailwind preset
    schemas/            # zod schemas shared client/server
    translations/       # base translation schemas & tooling
  docs/
  .env
  pnpm-workspace.yaml
  turbo.json
```

#### Core Tech Choices
- Internationalization: `next-intl` with EN/ES/PT locale JSON files. All user-facing text via translations. Developers write English code and keys.
- Forms: React Hook Form + Zod. Client validation mirrors server DTO validation (class-validator) using shared zod schemas.
- Data fetching: TanStack Query. Unified HTTP client with Axios; interceptors inject auth.
- UI: Tailwind CSS + shadcn/ui for cohesive UX and consistent components.
- Viewer: `react-pdf` for PDF; responsive `<img>` for images.
- Maps & Phone:
  - Google Places: `@vis.gl/react-google-maps` or `react-places-autocomplete` with Next Script to load Maps JS API.
  - Phone input: `react-phone-number-input` + libphonenumber for validation.
- File upload: Frontend -> Nest API (multipart) -> Firebase Admin uploads to Storage -> returns public URL + metadata; Document is created in Mongo.

#### Environments
- Common .env keys:
  - API: `MONGODB_URI`, `JWT_SECRET`, `FIREBASE_PROJECT_ID`, `FIREBASE_CLIENT_EMAIL`, `FIREBASE_PRIVATE_KEY`, `FIREBASE_STORAGE_BUCKET`
  - Web: `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`, `NEXT_PUBLIC_DEFAULT_LOCALE=en`

#### Authentication
- Users: email/password (bcrypt) + JWT (access/refresh). Admin is a role on `users` (role: 'admin'), not a separate concept.
- Admin Login replaces single-password page with email/password form; password-only mode can be supported via an env-guarded “admin backdoor” during migration if needed.

#### High-Level Data Flow
- Frontend forms → zod validation → submit to Nest REST endpoints → Mongoose persists → files uploaded to Firebase Storage by API → public URLs stored in `documents`.
- Admin configures required documents per Travel (owner + per-pet), stored in `travel.requiredDocuments`.


