### Validation: Shared Schemas (Zod ↔ class-validator)

#### Approach
- Define source-of-truth schemas in `packages/schemas` using Zod.
- Frontend imports zod directly.
- Backend derives TypeScript types for DTOs and mirrors with `class-validator` decorators for runtime validation.

#### Why not share zod runtime on server?
- Nest.js integrates best with `class-validator` + `class-transformer`. Keep types aligned and tests to ensure parity.

#### Example: User Registration
Zod (`packages/schemas/user.ts`):
```ts
import { z } from 'zod';
export const phoneSchema = z.object({ e164: z.string().min(5), country: z.string().length(2).optional() });
export const addressSchema = z.object({
  formatted: z.string().min(5), city: z.string().min(1), state: z.string().min(1), country: z.string().min(2),
  zipCode: z.string().optional(), lat: z.string().optional(), lng: z.string().optional(),
  type: z.enum(['residential','delivery','destination'])
});
export const petSchema = z.object({
  name: z.string().min(1), species: z.enum(['canine','feline','bird','rodent','other']), breed: z.string().min(1),
  gender: z.enum(['male','female']), birthDate: z.string().regex(/^(\d{2})\/(\d{2})\/(\d{4})$/),
  weight: z.string().optional(), microchip: z.string().max(15).optional(), furColor: z.string().optional()
});
export const registerUserSchema = z.object({
  ownerName: z.string().min(2), username: z.string().min(3), email: z.string().email(), password: z.string().min(6),
  contactNumber: phoneSchema, hasCpf: z.boolean(), cpf: z.string().optional(), passportNumber: z.string().optional(),
  hasSpecialNeeds: z.boolean(), specialNeedsDetails: z.string().optional(),
  howDidYouKnow: z.enum(['instagram','facebook','google','youtube','recommendation','other']).optional(),
  addresses: z.object({ residential: addressSchema, delivery: addressSchema.optional() }),
  pets: z.array(petSchema).min(1)
}).refine(d => d.hasCpf ? !!d.cpf : !!d.passportNumber, { message: 'CPF or Passport required', path: ['cpf'] });
export type RegisterUserInput = z.infer<typeof registerUserSchema>;
```

Nest DTO mirrors (`apps/api/src/auth/dto/register-user.dto.ts`):
```ts
import { IsEmail, IsString, MinLength, IsBoolean, ValidateNested, IsOptional, IsArray } from 'class-validator';
import { Type } from 'class-transformer';

class PhoneDto { @IsString() e164: string; @IsOptional() @IsString() country?: string }
class AddressDto {
  @IsString() formatted: string; @IsString() city: string; @IsString() state: string; @IsString() country: string;
  @IsOptional() @IsString() zipCode?: string; @IsOptional() @IsString() lat?: string; @IsOptional() @IsString() lng?: string;
}
class PetDto {
  @IsString() name: string; @IsString() species: string; @IsString() breed: string; @IsString() gender: string;
  @IsString() birthDate: string; @IsOptional() @IsString() weight?: string; @IsOptional() @IsString() microchip?: string;
  @IsOptional() @IsString() furColor?: string;
}
export class RegisterUserDto {
  @IsString() ownerName: string; @IsString() username: string; @IsEmail() email: string; @MinLength(6) password: string;
  @ValidateNested() @Type(() => PhoneDto) contactNumber: PhoneDto; @IsBoolean() hasCpf: boolean;
  @IsOptional() @IsString() cpf?: string; @IsOptional() @IsString() passportNumber?: string;
  @IsBoolean() hasSpecialNeeds: boolean; @IsOptional() @IsString() specialNeedsDetails?: string;
  @IsOptional() @IsString() howDidYouKnow?: string;
  @ValidateNested() @Type(() => AddressDto) addresses: { residential: AddressDto; delivery?: AddressDto };
  @IsArray() @ValidateNested({ each: true }) @Type(() => PetDto) pets: PetDto[];
}
```

#### Tests
- Contract tests assert that zod parse success/failure matches DTO validation.


