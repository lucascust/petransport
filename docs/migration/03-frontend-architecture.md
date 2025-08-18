### Frontend Architecture (Next.js + TypeScript)

#### Directory Structure (App Router)
```
apps/web/
  app/
    [locale]/
      layout.tsx
      page.tsx                # maybe dashboard or home
      admin/
        page.tsx
      auth/
        login/page.tsx
        register/page.tsx
      users/
        [username]/page.tsx   # user main view
      travels/
        create/page.tsx
        [id]/page.tsx
  components/
    forms/
    ui/                       # shadcn/ui wrappers
    documents/
    travel/
    admin/
  lib/
    api-client.ts
    query-client.ts
    i18n/
      messages/
        en.json
        es.json
        pt.json
      index.ts
    validators/
      user.ts
      pet.ts
      travel.ts
    utils/
      airports.ts
      formatters.ts
      masks.ts
      pdf.ts
  styles/
    globals.css
  providers/
    query-provider.tsx
    theme-provider.tsx
    i18n-provider.tsx
```

#### Global Providers
- Hydrate TanStack Query, i18n, and theme in `app/[locale]/layout.tsx`.
```tsx
// app/[locale]/layout.tsx
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import QueryProvider from '@/providers/query-provider';
import ThemeProvider from '@/providers/theme-provider';
import '@/styles/globals.css';

export default async function RootLayout({ children, params: { locale } }) {
  const messages = await getMessages();
  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider messages={messages} locale={locale}>
          <ThemeProvider>
            <QueryProvider>{children}</QueryProvider>
          </ThemeProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

#### i18n
- Use `next-intl`. All labels via keys. Example messages:
```json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "edit": "Edit"
  },
  "pages": {
    "owner_registration": {
      "title": "Owner Registration",
      "owner_info": "Owner Info",
      "use_different_address": "Use a different delivery address",
      "address_map": "Address Map",
      "residential": "Residential",
      "delivery": "Delivery",
      "pets": "Pets",
      "add_pet": "Add Pet",
      "register": "Register"
    }
  },
  "enums": {
    "Pet": { "species": { "canine": "Dog", "feline": "Cat", "bird": "Bird", "rodent": "Rodent", "other": "Other" },
             "gender": { "male": "Male", "female": "Female" } },
    "Travel": { "method": { "plane": "Plane", "car": "Car", "bus": "Bus", "petTransport": "Pet Transport", "other": "Other" },
                "status": { "upcoming": "Upcoming", "completed": "Completed", "cancelled": "Cancelled" } }
  }
}
```
- Mirror keys in `es.json` and `pt.json`.

#### Forms (React Hook Form + Zod)
- Example user registration zod schema:
```ts
import { z } from 'zod';

export const phoneSchema = z.object({ e164: z.string().min(5), country: z.string().length(2).optional() });

export const addressSchema = z.object({
  formatted: z.string().min(5),
  city: z.string().min(1),
  state: z.string().min(1),
  country: z.string().min(2),
  zipCode: z.string().optional(),
  lat: z.string().optional(),
  lng: z.string().optional(),
  type: z.enum(['residential', 'delivery', 'destination'])
});

export const registerUserSchema = z.object({
  ownerName: z.string().min(2),
  username: z.string().min(3),
  email: z.string().email(),
  password: z.string().min(6),
  contactNumber: phoneSchema,
  hasCpf: z.boolean(),
  cpf: z.string().optional(),
  passportNumber: z.string().optional(),
  hasSpecialNeeds: z.boolean(),
  specialNeedsDetails: z.string().optional(),
  howDidYouKnow: z.enum(['instagram','facebook','google','youtube','recommendation','other']).optional(),
  addresses: z.object({
    residential: addressSchema,
    delivery: addressSchema.optional()
  }),
  pets: z.array(z.object({
    name: z.string().min(1),
    species: z.enum(['canine','feline','bird','rodent','other']),
    breed: z.string().min(1),
    gender: z.enum(['male','female']),
    birthDate: z.string().regex(/^(\d{2})\/(\d{2})\/(\d{4})$/),
    weight: z.string().optional(),
    microchip: z.string().max(15).optional(),
    furColor: z.string().optional(),
    photoFile: z.instanceof(File).optional()
  })).min(1)
}).refine(d => d.hasCpf ? !!d.cpf : !!d.passportNumber, { message: 'CPF or Passport required', path: ['cpf'] });
```

- Use RHF with shadcn/ui components (Input, Select, Textarea, Button, Dialog/Sheet).

#### Data Fetching
- Axios client with base URL from `NEXT_PUBLIC_API_BASE_URL`.
- Query keys per resource, mutation hooks per form.

#### IATA Airports Module
- Convert `static/js/airport_iata.js` to `lib/utils/airports.ts` with types and deduped entries. Provide search helpers and country flag resolver.

#### File Upload UI
- Use `<input type="file" />` or drag/drop (e.g., `react-dropzone`), preview via URL.createObjectURL. Submit to API with FormData.

#### PDF/Image Viewer
- `react-pdf` component + fallback `<img />` for images.

#### Masks and Formatting
- Phone formatting via `react-phone-number-input`.
- CPF/passport microchip masks via simple utilities in `lib/utils/masks.ts`.

#### Styling
- Tailwind + shadcn installed; extract a theme to `packages/ui` for reuse.


