### Flow: User Main View

#### Page
- `[locale]/users/[username]`

#### Top Section
- Greeting + user summary.
- Pets list with mini cards:
  - Thumbnail (pet avatar if exists) or initial.
  - Species chip, breed, gender, fur color.
  - “Edit” opens modal to edit pet (prefill; submit PATCH /pets/:id).

#### Bottom Section: Travels
- Tabs:
  - “In Progress” (status=upcoming)
  - “Completed”
- Table columns:
  - Destination (show city for IATA via `airports.ts` helper)
  - Estimated date and ticket date (if exists)
  - Pets (avatars with tooltip on hover)
  - Method (badge)
  - Docs progress bar (computed: GET `/travels/:id/progress`)
  - Actions: “View Details”

#### Improvements vs current
- Table virtualization for performance if needed.
- Translated enum values from i18n.
- Unified airport code-to-city mapping and country flags (optional in UI).


