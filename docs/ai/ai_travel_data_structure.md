# Travel Data Structure Documentation

## Overview
This document outlines the structure of travel records in the system, detailing fields available after travel creation based on travel type. This is intended to be a reference for AI systems that need to understand and manage travel records.

## Common Fields (All Travel Types)
All travel records include these base fields regardless of travel method:

```json
{
  "id": "uuid-string",
  "user_id": "string",
  "username": "string",
  "origin": "string",
  "destination": "string",
  "travelingPets": ["pet-id-1", "pet-id-2"],
  "destinationAddress": {
    "formatted": "string",
    "city": "string",
    "state": "string",
    "zip_code": "string",
    "lat": "string",
    "lng": "string"
  },
  "travelMethod": "plane|bus|car|petTransport|other",
  "status": "upcoming|in_progress|completed|cancelled",
  "created_at": "datetime",
  "updated_at": "datetime",
  "required_documents": {
    "pet_docs": ["vaccinationCard", "microchipCertificate"],
    "human_docs": ["passport", "identityDocument"]
  },
  "history": [
    {
      "type": "status_change|update",
      "description": "string",
      "date": "datetime"
    }
  ]
}
```

## Travel Method Specific Fields

### Airplane Travel (`travelMethod: "plane"`)
```json
{
  "travelTicketFile": {
    "file_id": "string",
    "filename": "string",
    "path": "string",
    "file_type": "PDF|IMAGE",
    "size": "number",
    "uploaded_at": "datetime"
  },
  "travelTicketDate": "datetime",
  "estimatedDate": "string (MM/YYYY)",
  "airline": "string"
}
```

### Bus Travel (`travelMethod: "bus"`)
```json
{
  "travelTicketFile": {
    "file_id": "string",
    "filename": "string",
    "path": "string",
    "file_type": "PDF|IMAGE",
    "size": "number",
    "uploaded_at": "datetime"
  },
  "travelTicketDate": "datetime",
  "estimatedDate": "string (MM/YYYY)",
  "borderCity": "string"
}
```

### Car Travel (`travelMethod: "car"`)
```json
{
  "vehiclePlate": "string (max 7 chars, required)",
  "borderCity": "string",
  "estimatedDate": "string (MM/YYYY)"
}
```

### Pet Transport (`travelMethod: "petTransport"`)
```json
{
  "estimatedDate": "string (MM/YYYY)"
}
```

## Field Descriptions

### Common Fields
- `id`: Unique identifier for the travel record (UUID)
- `user_id`: Reference to the user who created the travel
- `username`: Username of the travel creator
- `origin`: City and country of departure
- `destination`: City and country of arrival
- `travelingPets`: Array of pet IDs that will travel
- `destinationAddress`: Structured address information for the destination
- `travelMethod`: Method of transportation (plane, bus, car, petTransport, other)
- `status`: Current status of the travel
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `required_documents`: Documents required for the travel
- `history`: Record of changes and status updates

### Method-Specific Fields
- `travelTicketFile`: File information for plane or bus tickets
- `travelTicketDate`: Exact date and time of travel from ticket
- `estimatedDate`: Month/year estimate for travel (format: MM/YYYY)
- `airline`: Airline name for plane travel
- `borderCity`: City of border crossing for bus or car travel
- `vehiclePlate`: License plate number for car travel (mandatory for car method)

## Validation Rules
1. `travelMethod` must be one of: "plane", "bus", "car", "petTransport", "other"
2. `status` must be one of: "upcoming", "in_progress", "completed", "cancelled"
3. `vehiclePlate` is required when `travelMethod` is "car" and limited to 7 characters
4. Date fields follow specific formats:
   - `travelTicketDate`: Full datetime (DD/MM/YYYY HH:MM)
   - `estimatedDate`: Month and year only (MM/YYYY)

## Travel Management Operations
1. Create: Initialize a new travel record with appropriate fields
2. Update: Modify travel details or add documents
3. Status Change: Update travel status with history recording
4. Document Upload: Add or update required documents for the travel

## Default Values
1. New travels are created with status "upcoming"
2. Default required documents:
   - Pet docs: "vaccinationCard", "microchipCertificate"
   - Human docs: "passport", "identityDocument"
3. Travel history begins with a "Viagem criada" (Travel created) entry

This documentation serves as a comprehensive reference for AI systems to understand and manipulate travel records based on their structure and type. 