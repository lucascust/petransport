### Monorepo Setup (Turborepo + pnpm)

#### Why
- Keep web (Next.js) and api (Nest.js) in one repo, share types, schemas, and UI.

#### Steps
1. Initialize pnpm workspace:
```
pnpm init -y
```
2. Add `pnpm-workspace.yaml`:
```
packages:
  - 'apps/*'
  - 'packages/*'
```
3. Add Turborepo `turbo.json`:
```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": { "dependsOn": ["^build"], "outputs": ["dist/**", ".next/**"] },
    "lint": {},
    "test": {}
  }
}
```
4. Scaffold apps:
```
pnpm dlx create-next-app@latest apps/web --ts --eslint --tailwind --app --src-dir=false --import-alias @/*
pnpm dlx @nestjs/cli new apps/api --package-manager pnpm
```
5. Create shared packages:
```
mkdir -p packages/{schemas,ui,config,translations}
```
6. Configure Tailwind preset in `packages/config/tailwind-preset.js` and consume in web.
7. Install shadcn/ui in web and generate components.
8. Setup `next-intl` in web.
9. Setup Mongoose + Firebase Admin in api.

#### Scripts (root package.json)
```json
{
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "lint": "turbo run lint",
    "test": "turbo run test"
  }
}
```


