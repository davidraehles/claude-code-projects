/**
 * Import Form Reducer - Implements Action/Intent Layer (ARCH-004)
 *
 * Manages the recipe import form state for URL and file upload.
 * Actions express user intent and create traceable state transitions.
 */

/**
 * Source type for recipe import
 */
export type SourceType = 'html' | 'api' | 'rss'

/**
 * State interface
 */
export interface ImportFormState {
  // URL import
  url: string
  sourceType: SourceType

  // File upload
  selectedFile: File | null

  // Status flags
  urlImportSuccess: boolean
  fileUploadSuccess: boolean
}

/**
 * Action types - Describe user intents
 */
export type ImportFormAction =
  | { type: 'USER_CHANGED_URL'; payload: string }
  | { type: 'USER_SELECTED_SOURCE_TYPE'; payload: SourceType }
  | { type: 'USER_SELECTED_FILE'; payload: File }
  | { type: 'USER_CLEARED_FILE' }
  | { type: 'URL_IMPORT_SUCCEEDED' }
  | { type: 'FILE_UPLOAD_SUCCEEDED' }
  | { type: 'FORM_RESET' }

/**
 * Initial state factory
 */
export function getInitialImportFormState(): ImportFormState {
  return {
    url: '',
    sourceType: 'html',
    selectedFile: null,
    urlImportSuccess: false,
    fileUploadSuccess: false,
  }
}

/**
 * Pure reducer function - All state transitions are traceable
 */
export function importFormReducer(
  state: ImportFormState,
  action: ImportFormAction
): ImportFormState {
  // Log actions in development for debugging
  if (process.env.NODE_ENV === 'development') {
    console.log('[ImportFormReducer]', action.type, action)
  }

  switch (action.type) {
    case 'USER_CHANGED_URL':
      return {
        ...state,
        url: action.payload,
        urlImportSuccess: false, // Reset success state when URL changes
      }

    case 'USER_SELECTED_SOURCE_TYPE':
      return {
        ...state,
        sourceType: action.payload,
      }

    case 'USER_SELECTED_FILE':
      return {
        ...state,
        selectedFile: action.payload,
        fileUploadSuccess: false, // Reset success state when file changes
      }

    case 'USER_CLEARED_FILE':
      return {
        ...state,
        selectedFile: null,
        fileUploadSuccess: false,
      }

    case 'URL_IMPORT_SUCCEEDED':
      return {
        ...state,
        urlImportSuccess: true,
        url: '', // Clear URL after successful import
      }

    case 'FILE_UPLOAD_SUCCEEDED':
      return {
        ...state,
        fileUploadSuccess: true,
        selectedFile: null, // Clear file after successful upload
      }

    case 'FORM_RESET':
      return getInitialImportFormState()

    default:
      return state
  }
}

/**
 * Selector: Check if URL is valid for import
 */
export function selectIsUrlValid(state: ImportFormState): boolean {
  return state.url.trim().length > 0
}

/**
 * Selector: Check if file is selected
 */
export function selectHasFile(state: ImportFormState): boolean {
  return state.selectedFile !== null
}

/**
 * Selector: Get file info for display
 */
export function selectFileInfo(state: ImportFormState): {
  name: string
  sizeKB: number
} | null {
  if (!state.selectedFile) return null
  return {
    name: state.selectedFile.name,
    sizeKB: Math.round((state.selectedFile.size / 1024) * 10) / 10,
  }
}

/**
 * Selector: Check if URL import can be submitted
 */
export function selectCanSubmitUrl(state: ImportFormState): boolean {
  return selectIsUrlValid(state)
}

/**
 * Selector: Check if file upload can be submitted
 */
export function selectCanSubmitFile(state: ImportFormState): boolean {
  return selectHasFile(state)
}

/**
 * Selector: Get import request data for API
 */
export function selectImportRequest(state: ImportFormState): {
  url: string
  source_type: SourceType
} {
  return {
    url: state.url.trim(),
    source_type: state.sourceType,
  }
}

/**
 * Selector: Check if any operation succeeded
 */
export function selectHasSuccess(state: ImportFormState): boolean {
  return state.urlImportSuccess || state.fileUploadSuccess
}
