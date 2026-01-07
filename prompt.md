Extract all contact information from the provided business card image with high precision.

### RULES:
- **STRICTLY ONLY** extract text that is clearly visible in the image.
- **NEVER** invent, assume, or hallucinate data that is not present.
- **DO NOT TRANSLATE** any text. Keep the original text exactly as it appears (including Vietnamese or other languages).
- **CLEAN VALUES**: Remove labels or icons such as "M:", "P:", "E:", "Tel:", or phone icons. Extract only the actual data.
- **ACCURACY**: Pay close attention to numbers and special characters in emails and websites.
- If a field is not found or is illegible, set it to `null`.
- Return **ONLY** a valid JSON object.

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
