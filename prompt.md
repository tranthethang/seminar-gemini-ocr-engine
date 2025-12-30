Extract contact information from this business card image.

### RULES:
- **ONLY** extract text visible in the image.
- **NEVER** invent or assume data (no hallucinations).
- If a field is not found, set it to `null`.
- Return **ONLY** a JSON object.

### JSON Structure:
{
  "company_name": "string or null",
  "person_name": "string or null",
  "position": "string or null",
  "contact": {
    "mobile": ["string"] or null,
    "work_phone": ["string"] or null,
    "email": ["string"] or null,
    "website": ["string"] or null
  },
  "address": "string or null"
}
