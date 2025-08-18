### Flow: User Registration

#### Page
- `[locale]/auth/register`

#### Requirements covered
- Google Places for addresses (residential, optional delivery)
- International phone input with country selector
- Toggle CPF vs Passport (hasCpf)
- Multiple pets with dynamic add/remove
- Microchip mask, birth date (DD/MM/YYYY)
- Pet image upload with preview (avatar stored on Pet record, not in Documents)
- Client-side zod validation; server-side DTO validation
- All text via i18n keys (EN/ES/PT)

#### Implementation Notes
- Use React Hook Form with zod resolver.
- For Places autocomplete:
  - Load Maps JS API with Next `<Script>`
  - Use `react-places-autocomplete` OR a simple custom autocomplete binding to `google.maps.places.Autocomplete` via a reusable hook.
- For phone:
  - `react-phone-number-input` storing E.164 in `contactNumber.e164`.
- Pets:
  - RHF FieldArray for `pets[]`.
  - For photo avatar: keep `File` in RHF state; on submit, upload via a dedicated pet-avatar endpoint that stores file metadata on Pet (not a `documents` record).

#### Submit Flow
1. Validate form (zod).
2. Call `POST /auth/register` creating the user and pets atomically (or: create user then loop pets).
3. For each pet with `photoFile`, upload via `POST /pets/:id/avatar` (multipart) and persist returned `{ path, publicUrl, size }` on the pet.

#### UX
- Debounced validation for address fields when typing.
- Badge to switch Residential/Delivery map marker (mirrors current UI but cleaner).
- Loading states and error toasts using shadcn/ui `useToast`.

#### Sample RHF snippet (pets array)
```tsx
const { control, register } = useForm({ resolver: zodResolver(registerUserSchema) });
const { fields, append, remove } = useFieldArray({ control, name: 'pets' });

<Button onClick={() => append({ name: '', species: 'canine', breed: '', gender: 'male', birthDate: '' })}>
  {t('pages.owner_registration.add_pet')}
  </Button>

{fields.map((field, i) => (
  <div key={field.id}>
    <Input {...register(`pets.${i}.name`)} />
    {/* Selects for species/gender (shadcn/ui) */}
    {/* File input for photoFile with preview */}
    <Button variant="ghost" onClick={() => remove(i)} disabled={fields.length <= 1}>
      {t('common.remove')}
    </Button>
  </div>
))}
```


