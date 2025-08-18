### Migration Plan

#### Phase 0 — Prep
- Decide monorepo (Turborepo + pnpm).
- Create `apps/web` and `apps/api` scaffolds.
- Set CI, Prettier/ESLint, commit hooks (`lint-staged`).
- Add `.env` templates.

#### Phase 1 — Data Model & API
- Implement Nest.js modules:
  - `auth`, `users`, `pets`, `travels`, `documents`, `files`
- Configure Mongoose schemas matching the improved model.
- Implement Firebase Admin and `FirebaseStorageService`.
- Implement endpoints in 02-api-design.md.
- Seed admin user via script.

#### Phase 2 — Frontend Shell
- Next.js app with App Router, Tailwind + shadcn installed.
- Setup `next-intl` locales (en/es/pt) and start migrating text to keys.
- Create global providers (query, i18n, theme).
- Implement shared UI primitives and form components.

#### Phase 3 — Flows
- User Registration page:
  - RHF + Zod, Google Places, phone input, pets FieldArray, pet avatar preview
  - Wire to `/auth/register` then `/pets/:id/avatar`
- User Main View:
  - Fetch user by username, list pets, list travels by status
  - Progress bars via `/travels/:id/progress`
- Travel Create + Details:
  - Create travel with conditional fields
  - Document panels with upload modal and viewer
- Admin pages:
  - Admin list/search
  - Travel required-docs configurator

#### Phase 4 — Data Migration
- Data already in Mongo: write Node scripts to:
  - Normalize enums to English values
  - Migrate embedded addresses under `users.addresses`
  - Ensure each document has `travelId` and valid scope (user/pet for that travel)
  - Move pet avatar info from legacy locations to `pets.photo`
  - Generate `username` slugs if missing, ensure unique constraints.

#### Phase 5 — Cutover
- Deploy API (Render/Fly/Heroku/K8s) and Web (Vercel).
- Run smoke tests.
- Feature flag rollout for new flows; keep old Flask pages during transition (strangler pattern).
- Switch DNS/routes.

#### Quality & Tooling Improvements
- Add E2E tests (Playwright) for the main flows.
- Add API contract tests (Jest + supertest).
- Add Sentry for error observability.
- Lighthouse performance budgets.

#### Risks and Mitigations
- File migration: prefer server-side re-upload to Firebase on demand (lazy migration) instead of bulk, to reduce cutover risk.
- i18n completeness: enforce key coverage via CI checks.
- Enum drift: add a validation script to list “unknown” values before cutover.


