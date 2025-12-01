
import ApiClient from '@/lib/api';

// Mock fetch global
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('ApiClient', () => {
  let api: ApiClient;

  beforeEach(() => {
    mockFetch.mockClear();
    api = new ApiClient('http://test.api');
  });

  describe('request method token handling', () => {
    // We need to access the private request method, so we cast to any or verify via side effect
    // Since request is private, we'll test via a public method that uses it, like getRecipes

    it('should add Authorization header when valid token is provided', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: [] }),
      });

      await api.getRecipes(0, 10, 'valid-token');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/recipes'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer valid-token',
          }),
        })
      );
    });

    it('should NOT add Authorization header when token is empty string', async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: [] }),
        });

        await api.getRecipes(0, 10, '');

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/recipes'),
          expect.objectContaining({
            headers: expect.not.objectContaining({
              'Authorization': expect.anything(),
            }),
          })
        );
      });

    it('should NOT add Authorization header when token is only whitespace', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: [] }),
      });

      await api.getRecipes(0, 10, '   ');

      // Check the calls
      const calls = mockFetch.mock.calls;
      const headers = calls[0][1].headers;

      // If headers is Headers object or simple object, we check for Authorization key
      // Based on implementation it is a simple object
      expect(headers).not.toHaveProperty('Authorization');
    });

    it('should NOT add Authorization header when token is null/undefined', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: [] }),
      });

      await api.getRecipes(0, 10, null);

      const calls = mockFetch.mock.calls;
      const headers = calls[0][1].headers;
      expect(headers).not.toHaveProperty('Authorization');
    });
  });

  describe('uploadRecipeFile token handling', () => {
    it('should add Authorization header when valid token is provided', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      });

      const file = new File(['content'], 'test.txt', { type: 'text/plain' });
      await api.uploadRecipeFile(file, 'valid-token');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/recipes/upload'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer valid-token',
          }),
        })
      );
    });

    it('should NOT add Authorization header when token is empty/whitespace', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      });

      const file = new File(['content'], 'test.txt', { type: 'text/plain' });
      await api.uploadRecipeFile(file, '   ');

      const calls = mockFetch.mock.calls;
      const headers = calls[0][1].headers;
      expect(headers).not.toHaveProperty('Authorization');
    });
  });
});
