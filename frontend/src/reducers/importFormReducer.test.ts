/**
 * Tests for importFormReducer
 */

import {
  importFormReducer,
  getInitialImportFormState,
  selectIsUrlValid,
  selectHasFile,
  selectFileInfo,
  selectCanSubmitUrl,
  selectCanSubmitFile,
  selectImportRequest,
  selectHasSuccess,
  type ImportFormState,
  type ImportFormAction,
} from './importFormReducer'

describe('importFormReducer', () => {
  describe('getInitialImportFormState', () => {
    it('should return initial state', () => {
      const state = getInitialImportFormState()
      expect(state.url).toBe('')
      expect(state.sourceType).toBe('html')
      expect(state.selectedFile).toBeNull()
      expect(state.urlImportSuccess).toBe(false)
      expect(state.fileUploadSuccess).toBe(false)
    })
  })

  describe('USER_CHANGED_URL action', () => {
    it('should update URL', () => {
      const initialState = getInitialImportFormState()
      const action: ImportFormAction = {
        type: 'USER_CHANGED_URL',
        payload: 'https://example.com/recipe',
      }

      const newState = importFormReducer(initialState, action)

      expect(newState.url).toBe('https://example.com/recipe')
    })

    it('should reset success flag when URL changes', () => {
      const initialState: ImportFormState = {
        ...getInitialImportFormState(),
        urlImportSuccess: true,
      }
      const action: ImportFormAction = {
        type: 'USER_CHANGED_URL',
        payload: 'https://example.com/new-recipe',
      }

      const newState = importFormReducer(initialState, action)

      expect(newState.urlImportSuccess).toBe(false)
    })
  })

  describe('USER_SELECTED_SOURCE_TYPE action', () => {
    it('should update source type', () => {
      const initialState = getInitialImportFormState()
      const action: ImportFormAction = {
        type: 'USER_SELECTED_SOURCE_TYPE',
        payload: 'api',
      }

      const newState = importFormReducer(initialState, action)

      expect(newState.sourceType).toBe('api')
    })
  })

  describe('USER_SELECTED_FILE action', () => {
    it('should set selected file', () => {
      const initialState = getInitialImportFormState()
      const mockFile = new File(['content'], 'recipe.html', { type: 'text/html' })
      const action: ImportFormAction = {
        type: 'USER_SELECTED_FILE',
        payload: mockFile,
      }

      const newState = importFormReducer(initialState, action)

      expect(newState.selectedFile).toBe(mockFile)
    })

    it('should reset success flag when file changes', () => {
      const initialState: ImportFormState = {
        ...getInitialImportFormState(),
        fileUploadSuccess: true,
      }
      const mockFile = new File(['content'], 'recipe.html', { type: 'text/html' })
      const action: ImportFormAction = {
        type: 'USER_SELECTED_FILE',
        payload: mockFile,
      }

      const newState = importFormReducer(initialState, action)

      expect(newState.fileUploadSuccess).toBe(false)
    })
  })

  describe('USER_CLEARED_FILE action', () => {
    it('should clear selected file', () => {
      const mockFile = new File(['content'], 'recipe.html', { type: 'text/html' })
      const initialState: ImportFormState = {
        ...getInitialImportFormState(),
        selectedFile: mockFile,
      }
      const action: ImportFormAction = {
        type: 'USER_CLEARED_FILE',
      }

      const newState = importFormReducer(initialState, action)

      expect(newState.selectedFile).toBeNull()
      expect(newState.fileUploadSuccess).toBe(false)
    })
  })

  describe('URL_IMPORT_SUCCEEDED action', () => {
    it('should set success flag and clear URL', () => {
      const initialState: ImportFormState = {
        ...getInitialImportFormState(),
        url: 'https://example.com/recipe',
      }
      const action: ImportFormAction = {
        type: 'URL_IMPORT_SUCCEEDED',
      }

      const newState = importFormReducer(initialState, action)

      expect(newState.urlImportSuccess).toBe(true)
      expect(newState.url).toBe('')
    })
  })

  describe('FILE_UPLOAD_SUCCEEDED action', () => {
    it('should set success flag and clear file', () => {
      const mockFile = new File(['content'], 'recipe.html', { type: 'text/html' })
      const initialState: ImportFormState = {
        ...getInitialImportFormState(),
        selectedFile: mockFile,
      }
      const action: ImportFormAction = {
        type: 'FILE_UPLOAD_SUCCEEDED',
      }

      const newState = importFormReducer(initialState, action)

      expect(newState.fileUploadSuccess).toBe(true)
      expect(newState.selectedFile).toBeNull()
    })
  })

  describe('FORM_RESET action', () => {
    it('should reset to initial state', () => {
      const initialState: ImportFormState = {
        url: 'https://example.com/recipe',
        sourceType: 'api',
        selectedFile: new File(['content'], 'recipe.html', { type: 'text/html' }),
        urlImportSuccess: true,
        fileUploadSuccess: false,
      }
      const action: ImportFormAction = {
        type: 'FORM_RESET',
      }

      const newState = importFormReducer(initialState, action)

      expect(newState).toEqual(getInitialImportFormState())
    })
  })

  describe('Selectors', () => {
    describe('selectIsUrlValid', () => {
      it('should return true for non-empty URL', () => {
        const state: ImportFormState = {
          ...getInitialImportFormState(),
          url: 'https://example.com/recipe',
        }
        expect(selectIsUrlValid(state)).toBe(true)
      })

      it('should return false for empty URL', () => {
        const state = getInitialImportFormState()
        expect(selectIsUrlValid(state)).toBe(false)
      })

      it('should return false for whitespace-only URL', () => {
        const state: ImportFormState = {
          ...getInitialImportFormState(),
          url: '   ',
        }
        expect(selectIsUrlValid(state)).toBe(false)
      })
    })

    describe('selectHasFile', () => {
      it('should return true when file is selected', () => {
        const state: ImportFormState = {
          ...getInitialImportFormState(),
          selectedFile: new File(['content'], 'recipe.html', { type: 'text/html' }),
        }
        expect(selectHasFile(state)).toBe(true)
      })

      it('should return false when no file selected', () => {
        const state = getInitialImportFormState()
        expect(selectHasFile(state)).toBe(false)
      })
    })

    describe('selectFileInfo', () => {
      it('should return file info when file is selected', () => {
        const mockFile = new File(['a'.repeat(2048)], 'recipe.html', { type: 'text/html' })
        const state: ImportFormState = {
          ...getInitialImportFormState(),
          selectedFile: mockFile,
        }

        const fileInfo = selectFileInfo(state)

        expect(fileInfo).not.toBeNull()
        expect(fileInfo?.name).toBe('recipe.html')
        expect(fileInfo?.sizeKB).toBe(2)
      })

      it('should return null when no file selected', () => {
        const state = getInitialImportFormState()
        const fileInfo = selectFileInfo(state)
        expect(fileInfo).toBeNull()
      })
    })

    describe('selectCanSubmitUrl', () => {
      it('should return true when URL is valid', () => {
        const state: ImportFormState = {
          ...getInitialImportFormState(),
          url: 'https://example.com/recipe',
        }
        expect(selectCanSubmitUrl(state)).toBe(true)
      })

      it('should return false when URL is empty', () => {
        const state = getInitialImportFormState()
        expect(selectCanSubmitUrl(state)).toBe(false)
      })
    })

    describe('selectCanSubmitFile', () => {
      it('should return true when file is selected', () => {
        const state: ImportFormState = {
          ...getInitialImportFormState(),
          selectedFile: new File(['content'], 'recipe.html', { type: 'text/html' }),
        }
        expect(selectCanSubmitFile(state)).toBe(true)
      })

      it('should return false when no file selected', () => {
        const state = getInitialImportFormState()
        expect(selectCanSubmitFile(state)).toBe(false)
      })
    })

    describe('selectImportRequest', () => {
      it('should return formatted import request', () => {
        const state: ImportFormState = {
          ...getInitialImportFormState(),
          url: '  https://example.com/recipe  ',
          sourceType: 'api',
        }

        const request = selectImportRequest(state)

        expect(request.url).toBe('https://example.com/recipe')
        expect(request.source_type).toBe('api')
      })
    })

    describe('selectHasSuccess', () => {
      it('should return true when URL import succeeded', () => {
        const state: ImportFormState = {
          ...getInitialImportFormState(),
          urlImportSuccess: true,
        }
        expect(selectHasSuccess(state)).toBe(true)
      })

      it('should return true when file upload succeeded', () => {
        const state: ImportFormState = {
          ...getInitialImportFormState(),
          fileUploadSuccess: true,
        }
        expect(selectHasSuccess(state)).toBe(true)
      })

      it('should return false when no success', () => {
        const state = getInitialImportFormState()
        expect(selectHasSuccess(state)).toBe(false)
      })
    })
  })
})
