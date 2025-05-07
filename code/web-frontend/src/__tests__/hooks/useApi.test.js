import { renderHook, act, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import useApi from '../../../hooks/useApi'; // Adjust path as necessary
import axios from 'axios';

// Mock axios to control API responses during tests
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('useApi Hook', () => {
    // Reset mocks before each test
    beforeEach(() => {
        mockedAxios.get.mockReset();
        mockedAxios.post.mockReset();
        // Reset other methods like put, delete if you add tests for them
    });

    it('initializes with correct default state', () => {
        const { result } = renderHook(() => useApi());
        expect(result.current.data).toBeNull();
        expect(result.current.error).toBeNull();
        expect(result.current.loading).toBe(false);
    });

    describe('GET requests', () => {
        it('handles successful GET request', async () => {
            const mockData = { message: 'Success!' };
            mockedAxios.get.mockResolvedValueOnce({ data: mockData });

            const { result } = renderHook(() => useApi());

            // Use act to wrap state updates
            let response;
            await act(async () => {
                response = await result.current.get('/test-endpoint');
            });

            expect(result.current.loading).toBe(false); // Should be false after completion
            expect(result.current.data).toEqual(mockData);
            expect(result.current.error).toBeNull();
            expect(response.data).toEqual(mockData);
            expect(mockedAxios.get).toHaveBeenCalledWith('/test-endpoint', undefined); // Check URL and config
        });

        it('handles GET request error', async () => {
            const errorMessage = 'Network Error';
            mockedAxios.get.mockRejectedValueOnce(new Error(errorMessage));

            const { result } = renderHook(() => useApi());
            let response;
            await act(async () => {
                response = await result.current.get('/test-endpoint');
            });
            
            // await waitFor(() => expect(result.current.loading).toBe(false)); // Wait for loading to be false

            expect(result.current.loading).toBe(false);
            expect(result.current.data).toBeNull();
            expect(result.current.error).toBeInstanceOf(Error);
            expect(result.current.error.message).toBe(errorMessage);
            expect(response).toBeInstanceOf(Error); // The hook should return the error
        });

        it('sets loading state correctly during GET request', async () => {
            mockedAxios.get.mockResolvedValueOnce({ data: { message: 'loading test' } });
            const { result } = renderHook(() => useApi());

            // Check loading state immediately after calling
            act(() => {
                 result.current.get('/test-loading');
            });
            expect(result.current.loading).toBe(true);

            // Wait for the request to complete
            await waitFor(() => expect(result.current.loading).toBe(false));
        });
    });

    describe('POST requests', () => {
        it('handles successful POST request', async () => {
            const postData = { key: 'value' };
            const mockResponseData = { message: 'Posted successfully!' };
            mockedAxios.post.mockResolvedValueOnce({ data: mockResponseData });

            const { result } = renderHook(() => useApi());
            let response;
            await act(async () => {
                response = await result.current.post('/test-post-endpoint', postData);
            });

            expect(result.current.loading).toBe(false);
            expect(result.current.data).toEqual(mockResponseData); // Or as per your hook's logic for POST data handling
            expect(result.current.error).toBeNull();
            expect(response.data).toEqual(mockResponseData);
            expect(mockedAxios.post).toHaveBeenCalledWith('/test-post-endpoint', postData, undefined);
        });

        it('handles POST request error', async () => {
            const postData = { key: 'value' };
            const errorMessage = 'POST Failed';
            mockedAxios.post.mockRejectedValueOnce(new Error(errorMessage));

            const { result } = renderHook(() => useApi());
            let response;
            await act(async () => {
                response = await result.current.post('/test-post-endpoint', postData);
            });

            expect(result.current.loading).toBe(false);
            expect(result.current.data).toBeNull();
            expect(result.current.error).toBeInstanceOf(Error);
            expect(result.current.error.message).toBe(errorMessage);
            expect(response).toBeInstanceOf(Error);
        });
    });

    // Add similar test blocks for PUT, DELETE, PATCH if your useApi hook supports them
    // Example for PUT:
    // describe('PUT requests', () => { ... });

    // Example for DELETE:
    // describe('DELETE requests', () => { ... });
});

