### Airports Data (IATA) Migration

#### Current
- `static/js/airport_iata.js` exports a large array and helpers to lookup city and country flag.

#### Target
- Convert to TypeScript module `apps/web/lib/utils/airports.ts`:
```ts
export type Airport = { code: string; city: string; country: string };
export const airports: Airport[] = [ /* deduped list migrated from current JS */ ];
export const getAirportByCode = (code?: string) => code ? airports.find(a => a.code === code) : undefined;
export const getAirportCityByCode = (code?: string) => getAirportByCode(code)?.city.replace(/\s*\([^)]*\)/g,'') ?? code ?? '';
export const getFlagUrl = (cc?: string) => cc ? `https://flagicons.lipis.dev/flags/4x3/${cc.toLowerCase()}.svg` : '';
```

#### Improvements
- Deduplicate repeated codes (e.g., `CAN` appears twice in current file).
- Optional: store airports JSON and generate TS module at build time.

#### Usage
- Replace all places rendering IATA codes with city names using `getAirportCityByCode`.


