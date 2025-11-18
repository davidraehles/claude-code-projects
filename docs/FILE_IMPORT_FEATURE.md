# File-Based Recipe Import Feature

**Date:** 2025-11-18
**Status:** ✅ COMPLETE & TESTED
**Feature:** Import recipes from HTML and PDF files

---

## Overview

Users can now upload recipe files (HTML or PDF) directly to import recipes into their library. The system automatically extracts:
- Recipe title
- Ingredient list
- Step-by-step instructions
- Cooking times (if present)
- Servings (if present)

---

## Architecture

### Backend Components

**1. File Parser Module** (`app/agents/file_parser.py`)
- `FileRecipeParser.parse_html_file()` - Extracts recipe data from HTML files
- `FileRecipeParser.parse_pdf_file()` - Extracts recipe data from PDF files
- Smart parsing with fallback heuristics for various HTML structures

**2. API Endpoint** (`app/api/v1/recipes.py`)
- `POST /api/v1/recipes/upload` - File upload endpoint
- Validates file types: `.html`, `.htm`, `.pdf`
- Max file size: 10MB
- Checks for duplicates using existing recipe comparison logic
- Creates recipe immediately in database
- Publishes `RECIPE_HARVEST_COMPLETED` event

**3. Dependencies** (`requirements.txt`)
- Added `pdfplumber==0.10.3` for PDF text extraction
- Uses existing `beautifulsoup4` for HTML parsing

### Frontend Components

**1. Upload Hook** (`meal-planner-ui/src/hooks/queries/useFileUpload.ts`)
- React Query mutation for file uploads
- Client-side validation (file type and size)
- Auto-invalidates recipe cache on success

**2. API Client Method** (`src/lib/api.ts`)
- `uploadRecipeFile(file: File, token: string)`
- FormData-based multipart upload
- Proper JWT authentication

**3. UI Component** (`meal-planner-ui/src/app/import/page.tsx`)
- File input with drag-and-drop ready styling
- Shows selected file name and size
- Upload progress with loading state
- Success/error messaging
- Auto-redirect to dashboard on success

---

## How It Works

### User Flow

1. User navigates to `/import` page
2. Clicks "Or Upload a File" section
3. Selects an HTML or PDF file
4. Clicks "📄 Upload File" button
5. System extracts recipe data
6. Checks for duplicates
7. Creates recipe in database
8. Redirects to dashboard

### Data Extraction

**HTML Files:**
- Looks for `<h1>` tag for title (fallback: `<title>`)
- Scans for ingredient-like patterns:
  - `class*="ingredient"`
  - List items with cooking units (cup, tbsp, tsp, oz, lb, g, ml)
- Extracts instructions from:
  - Containers with `class*="instruction/direction/step"`
  - Fallback: paragraphs in the content
- Parses cooking times using regex: `prep time: (\d+) minutes?`
- Extracts servings from text patterns

**PDF Files:**
- Extracts all text from PDF pages
- Parses as plain text recipe (similar to above)
- Looks for "Ingredients:" and "Instructions:" sections
- Falls back to unit-based ingredient detection

---

## Technical Details

### API Response

**Success (202 Accepted):**
```json
{
  "success": true,
  "message": "Recipe 'Delicious Chocolate Chip Cookies' successfully imported from file",
  "recipe": {
    "id": 1,
    "title": "Delicious Chocolate Chip Cookies",
    "ingredients": ["2 cups all-purpose flour", ...],
    "instructions": "Preheat oven...",
    "prep_time": null,
    "cook_time": null,
    "servings": 4,
    "source_type": "file_upload",
    "source_url": "file://test_recipe.html",
    ...
  },
  "is_duplicate": false,
  "duplicate_of_id": null
}
```

**Duplicate Detection:**
```json
{
  "success": false,
  "message": "Recipe 'Delicious Chocolate Chip Cookies' already exists in your library",
  "recipe": null,
  "is_duplicate": true,
  "duplicate_of_id": 5
}
```

**Error (400/500):**
```json
{
  "detail": "Unsupported file type: .docx. Supported: .html, .htm, .pdf"
}
```

### Database Changes

- `Recipe.source_type` now includes `'file_upload'` as a value
- `Recipe.source_url` stores `file://filename.html` or `file://filename.pdf`
- Uses existing duplicate detection with `find_duplicate_recipe()`

### Frontend State

```typescript
// File upload state
const [selectedFile, setSelectedFile] = useState<File | null>(null)
const [uploadSuccess, setUploadSuccess] = useState(false)
const { mutate: uploadFile, isPending: isUploading, error: uploadError } = useFileUpload()

// Handlers
const handleFileChange = (e) => setSelectedFile(e.target.files?.[0])
const handleFileUpload = () => uploadFile(selectedFile, { onSuccess: ... })
```

---

## Testing

**Test Case 1: HTML File Upload**
```bash
curl -X POST http://localhost:8000/api/v1/recipes/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_recipe.html"

# Response: 202 Accepted with recipe data
```

**Test Case 2: PDF File Upload**
```bash
curl -X POST http://localhost:8000/api/v1/recipes/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@recipe.pdf"

# Response: 202 Accepted with recipe data
```

**Test Case 3: Duplicate Detection**
```bash
# Upload same file twice
# Second upload returns: is_duplicate=true, duplicate_of_id=<original_id>
```

**Test Case 4: Invalid File Type**
```bash
curl -X POST http://localhost:8000/api/v1/recipes/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.docx"

# Response: 400 Bad Request
# detail: "Unsupported file type: .docx..."
```

---

## Supported File Formats

| Format | Extension | Parser | Status |
|--------|-----------|--------|--------|
| HTML | `.html`, `.htm` | BeautifulSoup4 | ✅ Working |
| PDF | `.pdf` | pdfplumber | ✅ Working |
| Word | `.docx` | - | ❌ Not supported |
| Text | `.txt` | - | ❌ Not supported |

---

## Error Handling

### Frontend Validation
- File type check (only .html, .htm, .pdf allowed)
- File size limit (10MB max)
- User-friendly error messages

### Backend Validation
- File extension validation
- UTF-8 decoding for HTML
- PDF file parsing with try/catch
- Duplicate detection before DB insert
- Event publishing with proper error handling

### User Feedback
- Loading spinner during upload
- Success message with auto-redirect
- Error alert with detailed message
- File size display before upload

---

## Commits

| Commit | Message | Status |
|--------|---------|--------|
| 8cf25c9 | feat: Add file-based recipe import (HTML and PDF support) | ✅ |
| 0bc033a | fix: Correct find_duplicate_recipe function call | ✅ |
| a227917 | fix: Correct event payload for RecipeHarvestCompletedEvent | ✅ |

---

## Known Limitations

1. **HTML Parsing**: Complex websites with dynamic content may not parse correctly
2. **PDF OCR**: Scanned PDF images (no text) won't work - text must be extractable
3. **Ingredient Parsing**: Heuristics based on common cooking units (may miss unusual patterns)
4. **Cooking Times**: Only extracts if explicitly labeled "prep time" or "cook time"
5. **Nutrition Info**: Not extracted (would require external API)

---

## Future Enhancements

1. **OCR Support**: Add optical character recognition for scanned PDFs
2. **Recipe Schema**: Use structured data (Recipe JSON-LD) if available in HTML
3. **Nutrition Extraction**: Integrate with nutrition API for extracted recipes
4. **Batch Upload**: Allow uploading multiple files at once
5. **Manual Editing**: Allow users to edit extracted recipe data before saving

---

## Deployment Status

- ✅ Backend: Railway (auto-deployed)
- ✅ Frontend: Vercel (auto-deployed)
- ✅ Both deployments completed and tested
- ✅ JWT exception fix included
- ✅ End-to-end testing passed

---

**Last Updated:** 2025-11-18
**Feature Status:** Production Ready
