# CVstractor API Specification

## Overview
API that receives a CV document in `.docx` or `.odt` format and extracts structured information using regular expressions, returning a JSON object.

## Languages
- **Node.js** (Express.js) - API endpoint and document processing
- **Python** - Regular expression extraction using `re` library

## API Endpoints

### POST `/api/extract`
Extract structured data from a CV document.

**Request:**
- `multipart/form-data` with field `cv` containing the `.docx` or `.odt` file

**Response:**
```json
{
  "personal": {
    "name": "string",
    "email": "string",
    "phone": "string",
    "address": "string"
  },
  "contact": {
    "github": "string",
    "linkedin": "string",
    "website": "string"
  },
  "education": [
    {
      "institution": "string",
      "degree": "string",
      "graduation_year": "number"
    }
  ],
  "experience": [
    {
      "company": "string",
      "position": "string",
      "start_date": "string",
      "end_date": "string",
      "description": "string"
    }
  ],
  "skills": ["string"],
  "summary": "string"
}
```

## Extraction Logic

### Node.js (`src/`)
- Receives uploaded file via Express.js
- Converts `.docx`/`.odt` to XML using `unzip` library
- Parses XML to extract plain text content
- Triggers Python regex extraction pipeline

### Python (`python/`)
- Uses `re` module for pattern matching
- Defined regex patterns for:
  - Name: `^[A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*$`
  - Email: `\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}\\b`
  - Phone: `\\(?\\d{3}\\)?\\s?-?\\d{3}\\s?-?\\d{4}`
  - GitHub: `github\\/([A-Za-z0-9-]+)`
  - LinkedIn: `linkedin\\.com\\/in\\/([A-Za-z0-9-]+)`
- Returns structured JSON output

## Data Formats
- Input: `.docx` or `.odt` (MIME types: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `application/vnd.oasis.opendocument.text`)
- Output: JSON with extracted personal information, contact details, education, experience, skills, and summary