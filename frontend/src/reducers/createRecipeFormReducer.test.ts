/**
 * Tests for createRecipeFormReducer
 */

import {
  createRecipeFormReducer,
  getInitialCreateRecipeFormState,
  selectIsTitleValid,
  selectValidIngredients,
  selectHasValidIngredients,
  selectCanSubmit,
  selectCreateRecipeRequest,
  selectTotalTime,
  selectHasDietaryTag,
  selectIngredientCount,
  selectValidIngredientCount,
  type CreateRecipeFormState,
  type CreateRecipeFormAction,
} from './createRecipeFormReducer'

describe('createRecipeFormReducer', () => {
  describe('getInitialCreateRecipeFormState', () => {
    it('should return initial state', () => {
      const state = getInitialCreateRecipeFormState()
      expect(state.title).toBe('')
      expect(state.ingredients).toEqual([''])
      expect(state.instructions).toBe('')
      expect(state.prepTime).toBeUndefined()
      expect(state.cookTime).toBeUndefined()
      expect(state.servings).toBe(2)
      expect(state.dietaryTags).toEqual([])
      expect(state.success).toBe(false)
    })
  })

  describe('USER_CHANGED_TITLE action', () => {
    it('should update title', () => {
      const initialState = getInitialCreateRecipeFormState()
      const action: CreateRecipeFormAction = {
        type: 'USER_CHANGED_TITLE',
        payload: 'Chocolate Cake',
      }

      const newState = createRecipeFormReducer(initialState, action)

      expect(newState.title).toBe('Chocolate Cake')
    })
  })

  describe('USER_CHANGED_INSTRUCTIONS action', () => {
    it('should update instructions', () => {
      const initialState = getInitialCreateRecipeFormState()
      const action: CreateRecipeFormAction = {
        type: 'USER_CHANGED_INSTRUCTIONS',
        payload: 'Mix ingredients and bake',
      }

      const newState = createRecipeFormReducer(initialState, action)

      expect(newState.instructions).toBe('Mix ingredients and bake')
    })
  })

  describe('USER_CHANGED_PREP_TIME action', () => {
    it('should update prep time', () => {
      const initialState = getInitialCreateRecipeFormState()
      const action: CreateRecipeFormAction = {
        type: 'USER_CHANGED_PREP_TIME',
        payload: 15,
      }

      const newState = createRecipeFormReducer(initialState, action)

      expect(newState.prepTime).toBe(15)
    })

    it('should accept undefined', () => {
      const initialState: CreateRecipeFormState = {
        ...getInitialCreateRecipeFormState(),
        prepTime: 15,
      }
      const action: CreateRecipeFormAction = {
        type: 'USER_CHANGED_PREP_TIME',
        payload: undefined,
      }

      const newState = createRecipeFormReducer(initialState, action)

      expect(newState.prepTime).toBeUndefined()
    })
  })

  describe('USER_CHANGED_COOK_TIME action', () => {
    it('should update cook time', () => {
      const initialState = getInitialCreateRecipeFormState()
      const action: CreateRecipeFormAction = {
        type: 'USER_CHANGED_COOK_TIME',
        payload: 30,
      }

      const newState = createRecipeFormReducer(initialState, action)

      expect(newState.cookTime).toBe(30)
    })
  })

  describe('USER_CHANGED_SERVINGS action', () => {
    it('should update servings', () => {
      const initialState = getInitialCreateRecipeFormState()
      const action: CreateRecipeFormAction = {
        type: 'USER_CHANGED_SERVINGS',
        payload: 4,
      }

      const newState = createRecipeFormReducer(initialState, action)

      expect(newState.servings).toBe(4)
    })
  })

  describe('USER_CHANGED_INGREDIENT action', () => {
    it('should update ingredient at specific index', () => {
      const initialState: CreateRecipeFormState = {
        ...getInitialCreateRecipeFormState(),
        ingredients: ['flour', 'sugar', 'eggs'],
      }
      const action: CreateRecipeFormAction = {
        type: 'USER_CHANGED_INGREDIENT',
        payload: { index: 1, value: 'brown sugar' },
      }

      const newState = createRecipeFormReducer(initialState, action)

      expect(newState.ingredients).toEqual(['flour', 'brown sugar', 'eggs'])
    })
  })

  describe('USER_ADDED_INGREDIENT action', () => {
    it('should add empty ingredient to list', () => {
      const initialState: CreateRecipeFormState = {
        ...getInitialCreateRecipeFormState(),
        ingredients: ['flour'],
      }
      const action: CreateRecipeFormAction = {
        type: 'USER_ADDED_INGREDIENT',
      }

      const newState = createRecipeFormReducer(initialState, action)

      expect(newState.ingredients).toEqual(['flour', ''])
    })
  })

  describe('USER_REMOVED_INGREDIENT action', () => {
    it('should remove ingredient at specific index', () => {
      const initialState: CreateRecipeFormState = {
        ...getInitialCreateRecipeFormState(),
        ingredients: ['flour', 'sugar', 'eggs'],
      }
      const action: CreateRecipeFormAction = {
        type: 'USER_REMOVED_INGREDIENT',
        payload: { index: 1 },
      }

      const newState = createRecipeFormReducer(initialState, action)

      expect(newState.ingredients).toEqual(['flour', 'eggs'])
    })

    it('should not remove last ingredient', () => {
      const initialState: CreateRecipeFormState = {
        ...getInitialCreateRecipeFormState(),
        ingredients: ['flour'],
      }
      const action: CreateRecipeFormAction = {
        type: 'USER_REMOVED_INGREDIENT',
        payload: { index: 0 },
      }

      const newState = createRecipeFormReducer(initialState, action)

      expect(newState.ingredients).toEqual(['flour'])
    })
  })

  describe('USER_TOGGLED_DIETARY_TAG action', () => {
    it('should add dietary tag if not present', () => {
      const initialState = getInitialCreateRecipeFormState()
      const action: CreateRecipeFormAction = {
        type: 'USER_TOGGLED_DIETARY_TAG',
        payload: 'vegan',
      }

      const newState = createRecipeFormReducer(initialState, action)

      expect(newState.dietaryTags).toContain('vegan')
    })

    it('should remove dietary tag if already present', () => {
      const initialState: CreateRecipeFormState = {
        ...getInitialCreateRecipeFormState(),
        dietaryTags: ['vegan', 'gluten-free'],
      }
      const action: CreateRecipeFormAction = {
        type: 'USER_TOGGLED_DIETARY_TAG',
        payload: 'vegan',
      }

      const newState = createRecipeFormReducer(initialState, action)

      expect(newState.dietaryTags).toEqual(['gluten-free'])
    })
  })

  describe('RECIPE_CREATED_SUCCESSFULLY action', () => {
    it('should set success flag', () => {
      const initialState = getInitialCreateRecipeFormState()
      const action: CreateRecipeFormAction = {
        type: 'RECIPE_CREATED_SUCCESSFULLY',
      }

      const newState = createRecipeFormReducer(initialState, action)

      expect(newState.success).toBe(true)
    })
  })

  describe('FORM_RESET action', () => {
    it('should reset to initial state', () => {
      const initialState: CreateRecipeFormState = {
        title: 'Chocolate Cake',
        ingredients: ['flour', 'sugar', 'eggs'],
        instructions: 'Mix and bake',
        prepTime: 15,
        cookTime: 30,
        servings: 8,
        dietaryTags: ['vegetarian'],
        success: true,
      }
      const action: CreateRecipeFormAction = {
        type: 'FORM_RESET',
      }

      const newState = createRecipeFormReducer(initialState, action)

      expect(newState).toEqual(getInitialCreateRecipeFormState())
    })
  })

  describe('Selectors', () => {
    describe('selectIsTitleValid', () => {
      it('should return true for non-empty title', () => {
        const state: CreateRecipeFormState = {
          ...getInitialCreateRecipeFormState(),
          title: 'Chocolate Cake',
        }
        expect(selectIsTitleValid(state)).toBe(true)
      })

      it('should return false for empty title', () => {
        const state = getInitialCreateRecipeFormState()
        expect(selectIsTitleValid(state)).toBe(false)
      })

      it('should return false for whitespace-only title', () => {
        const state: CreateRecipeFormState = {
          ...getInitialCreateRecipeFormState(),
          title: '   ',
        }
        expect(selectIsTitleValid(state)).toBe(false)
      })
    })

    describe('selectValidIngredients', () => {
      it('should return only non-empty ingredients', () => {
        const state: CreateRecipeFormState = {
          ...getInitialCreateRecipeFormState(),
          ingredients: ['flour', '', 'sugar', '   ', 'eggs'],
        }

        const validIngredients = selectValidIngredients(state)

        expect(validIngredients).toEqual(['flour', 'sugar', 'eggs'])
      })
    })

    describe('selectHasValidIngredients', () => {
      it('should return true when has valid ingredients', () => {
        const state: CreateRecipeFormState = {
          ...getInitialCreateRecipeFormState(),
          ingredients: ['flour', '', 'sugar'],
        }
        expect(selectHasValidIngredients(state)).toBe(true)
      })

      it('should return false when no valid ingredients', () => {
        const state: CreateRecipeFormState = {
          ...getInitialCreateRecipeFormState(),
          ingredients: ['', '  '],
        }
        expect(selectHasValidIngredients(state)).toBe(false)
      })
    })

    describe('selectCanSubmit', () => {
      it('should return true when title and ingredients are valid', () => {
        const state: CreateRecipeFormState = {
          ...getInitialCreateRecipeFormState(),
          title: 'Chocolate Cake',
          ingredients: ['flour', 'sugar'],
        }
        expect(selectCanSubmit(state)).toBe(true)
      })

      it('should return false when title is missing', () => {
        const state: CreateRecipeFormState = {
          ...getInitialCreateRecipeFormState(),
          title: '',
          ingredients: ['flour', 'sugar'],
        }
        expect(selectCanSubmit(state)).toBe(false)
      })

      it('should return false when no valid ingredients', () => {
        const state: CreateRecipeFormState = {
          ...getInitialCreateRecipeFormState(),
          title: 'Chocolate Cake',
          ingredients: ['', '  '],
        }
        expect(selectCanSubmit(state)).toBe(false)
      })
    })

    describe('selectCreateRecipeRequest', () => {
      it('should return formatted request data', () => {
        const state: CreateRecipeFormState = {
          title: 'Chocolate Cake',
          ingredients: ['flour', '', 'sugar'],
          instructions: 'Mix and bake',
          prepTime: 15,
          cookTime: 30,
          servings: 8,
          dietaryTags: ['vegetarian', 'gluten-free'],
          success: false,
        }

        const request = selectCreateRecipeRequest(state)

        expect(request.title).toBe('Chocolate Cake')
        expect(request.ingredients).toEqual(['flour', 'sugar'])
        expect(request.instructions).toBe('Mix and bake')
        expect(request.prep_time).toBe(15)
        expect(request.cook_time).toBe(30)
        expect(request.servings).toBe(8)
        expect(request.dietary_tags).toEqual(['vegetarian', 'gluten-free'])
      })

      it('should omit dietary_tags when empty', () => {
        const state: CreateRecipeFormState = {
          ...getInitialCreateRecipeFormState(),
          title: 'Chocolate Cake',
          ingredients: ['flour'],
        }

        const request = selectCreateRecipeRequest(state)

        expect(request.dietary_tags).toBeUndefined()
      })
    })

    describe('selectTotalTime', () => {
      it('should return sum of prep and cook time', () => {
        const state: CreateRecipeFormState = {
          ...getInitialCreateRecipeFormState(),
          prepTime: 15,
          cookTime: 30,
        }
        expect(selectTotalTime(state)).toBe(45)
      })

      it('should handle only prep time', () => {
        const state: CreateRecipeFormState = {
          ...getInitialCreateRecipeFormState(),
          prepTime: 15,
        }
        expect(selectTotalTime(state)).toBe(15)
      })

      it('should handle only cook time', () => {
        const state: CreateRecipeFormState = {
          ...getInitialCreateRecipeFormState(),
          cookTime: 30,
        }
        expect(selectTotalTime(state)).toBe(30)
      })

      it('should return undefined when both are undefined', () => {
        const state = getInitialCreateRecipeFormState()
        expect(selectTotalTime(state)).toBeUndefined()
      })
    })

    describe('selectHasDietaryTag', () => {
      it('should return true when tag is present', () => {
        const state: CreateRecipeFormState = {
          ...getInitialCreateRecipeFormState(),
          dietaryTags: ['vegan', 'gluten-free'],
        }
        expect(selectHasDietaryTag(state, 'vegan')).toBe(true)
      })

      it('should return false when tag is not present', () => {
        const state: CreateRecipeFormState = {
          ...getInitialCreateRecipeFormState(),
          dietaryTags: ['vegan'],
        }
        expect(selectHasDietaryTag(state, 'gluten-free')).toBe(false)
      })
    })

    describe('selectIngredientCount', () => {
      it('should return total ingredient count', () => {
        const state: CreateRecipeFormState = {
          ...getInitialCreateRecipeFormState(),
          ingredients: ['flour', '', 'sugar'],
        }
        expect(selectIngredientCount(state)).toBe(3)
      })
    })

    describe('selectValidIngredientCount', () => {
      it('should return count of non-empty ingredients', () => {
        const state: CreateRecipeFormState = {
          ...getInitialCreateRecipeFormState(),
          ingredients: ['flour', '', 'sugar', '  '],
        }
        expect(selectValidIngredientCount(state)).toBe(2)
      })
    })
  })
})
