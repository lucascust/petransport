### Data Model (Improved)

All collections: `users`, `pets`, `travels`, `documents`. Addresses are embedded in `users` and (optionally) in `travels` (destination). All text keys, enums, filenames, fields are English.

#### Shared Enums (TypeScript)
```ts
export enum TravelMethod { Plane='plane', Bus='bus', Car='car', PetTransport='petTransport', Other='other' }
export enum TravelStatus { Upcoming='upcoming', Completed='completed', Cancelled='cancelled' }
export enum PetSpecies { Canine='canine', Feline='feline', Bird='bird', Rodent='rodent', Other='other' }
export enum Gender { Male='male', Female='female' }
export enum DocumentType {
  VaccinationCard='vaccinationCard',
  MicrochipCertificate='microchipCertificate',
  RabiesSerologyReport='rabiesSerologyReport',
  LeishmaniasisSerologyReport='leishmaniasisSerologyReport',
  ImportPermit='importPermit',
  PetPassport='petPassport',
  CVI='cvi',
  ExportAuthorization='exportAuthorization',
  ArrivalNotice='arrivalNotice',
  EndorsedCvi='endorsedCvi',
  AwbCargo='awbCargo',
  PetFacilities='petFacilities',
  IdentityDocument='identityDocument',
  CviIssuanceAuthorization='cviIssuanceAuthorization',
  Passport='passport',
  TravelTicket='travelTicket',
  TravelAuthorization='travelAuthorization',
  CarDocument='carDocument',
  AddressProof='addressProof',
  Other='other',
}
```

#### Embedded Types
```ts
export type Address = {
  formatted?: string
  city?: string
  state?: string
  country?: string
  zipCode?: string
  lat?: string
  lng?: string
  type: 'residential' | 'delivery' | 'destination'
};

export type Phone = {
  e164: string  // +5511999999999
  country?: string // ISO-2
};
```

#### users
- `_id`
- `username`: string (slug)
- `ownerName`: string
- `email`: string (unique)
- `passwordHash`: string
- `contactNumber`: `Phone`
- `hasCpf`: boolean
- `cpf?`: string
- `passportNumber?`: string
- `hasSpecialNeeds`: boolean
- `specialNeedsDetails?`: string
- `howDidYouKnow?`: 'instagram' | 'facebook' | 'google' | 'youtube' | 'recommendation' | 'other'
- `addresses`: { residential: Address; delivery?: Address }
- `lastAccess`: date
- `petIds`: ObjectId[]
- `documentIds`: Record<string, ObjectId> // optional quick-access map
- `role`: 'user' | 'admin'
- `createdAt`, `updatedAt`

Indexes:
- `email` unique
- `username` unique

#### pets
- `_id`
- `ownerId`: ObjectId (users._id)
- `name`, `species`, `breed`, `gender`
- `birthDate`: date
- `microchip?`: string
- `weight?`: string
- `furColor?`: string
- `photo?`: { path: string; publicUrl?: string; size?: number } // pet avatar not travel-scoped
- `createdAt`, `updatedAt`

Indexes:
- `{ ownerId: 1, name: 1 }` unique per owner

#### travels
- `_id`
- `userId`: ObjectId
- `username`: string (denormalized to simplify queries)
- `status`: TravelStatus
- `origin`: string (IATA or free text)
- `destination`: string (IATA or free text)
- `destinationAddress?`: Address
- `borderCity?`: string
- `travelMethod`: TravelMethod
- `vehiclePlate?`: string
- `ticketDocumentId?`: ObjectId (documents._id)
- `ticketDate?`: date
- `estimatedDate?`: string (kept string to match your usage; can be date if consistent)
- `petIds`: ObjectId[]
- `documentIds`: Record<string, ObjectId> // uploaded docs shortcut
- `requiredDocuments`:
```ts
{
  owner: DocumentType[];          // required for the user
  pets: Record<string, DocumentType[]>; // per petId
}
```
- `createdAt`, `updatedAt`

Indexes:
- `{ userId: 1, status: 1 }`
- `{ username: 1, status: 1 }`

#### documents
- `_id`
- `travelId`: ObjectId (required)
- `entityType`: 'user' | 'pet'
- `entityId`: ObjectId (users._id or pets._id)
- `documentType`: DocumentType
- `filename`: string
- `path`: string // storage path (folder/filename.ext)
- `fileType`: 'image' | 'pdf'
- `size`: number
- `description?`: string
- `publicUrl?`: string
- `storageType`: 'firebase'
- `firebasePath?`: string
- `petId?`: ObjectId (if entityType is 'pet', mirrors `entityId` for clarity)
- `createdAt`, `updatedAt`

Indexes:
- `{ travelId: 1, entityType: 1, entityId: 1, documentType: 1 }` unique

#### Improvements from current
- Enforce `travelId` on every `document`.
- Embed `addresses` in `users` and `destinationAddress` in `travels`.
- Consolidate enums and types in English; use translations for UI labels.
- Add role to `users` for admin features.
- Store pet avatar outside `documents` (keeps `documents` strictly travel-scoped).


