/**
 * Tests for useProjectsNav composable
 * Tests project fetching, dataset fetching, and state management
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(() => 'test-token'),
  setItem: vi.fn(),
  removeItem: vi.fn(),
}
Object.defineProperty(globalThis, 'localStorage', { value: localStorageMock })

// Mock fetch
const mockFetch = vi.fn()
globalThis.fetch = mockFetch

// Mock getApiUrl
vi.mock('@/utils/api', () => ({
  getApiUrl: () => 'http://localhost:8000'
}))

import { useProjectsNav } from './useProjectsNav'

describe('useProjectsNav', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset the composable state between tests
    const { reset } = useProjectsNav()
    reset()
  })

  describe('fetchProjects', () => {
    it('fetches projects from the API', async () => {
      const mockProjects = [
        { id: '1', name: 'Project A', datasets_count: 3 },
        { id: '2', name: 'Project B', datasets_count: 1 },
      ]
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ projects: mockProjects, total: 2 })
      })

      const { fetchProjects, projects } = useProjectsNav()
      await fetchProjects()

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/projects?page=1&page_size=50',
        { headers: { Authorization: 'Bearer test-token' } }
      )
      expect(projects.value).toEqual(mockProjects)
    })

    it('handles API error gracefully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500
      })

      const { fetchProjects, projects } = useProjectsNav()
      await fetchProjects()

      expect(projects.value).toEqual([])
    })

    it('handles network error gracefully', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      const { fetchProjects, projects } = useProjectsNav()
      await fetchProjects()

      expect(projects.value).toEqual([])
    })

    it('does not fetch if already loading', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ projects: [] })
      })

      const { fetchProjects } = useProjectsNav()
      // Call twice simultaneously
      fetchProjects()
      fetchProjects()

      // Only one fetch call should be made
      expect(mockFetch).toHaveBeenCalledTimes(1)
    })

    it('sends authorization header with token from localStorage', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ projects: [] })
      })

      const { fetchProjects } = useProjectsNav()
      await fetchProjects()

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: { Authorization: 'Bearer test-token' }
        })
      )
    })
  })

  describe('fetchDatasets', () => {
    it('fetches datasets for a project', async () => {
      const mockDatasets = [
        { id: 'ds1', name: 'Dataset 1', project_id: '1' },
        { id: 'ds2', name: 'Dataset 2', project_id: '1' },
      ]
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ datasets: mockDatasets, total: 2 })
      })

      const { fetchDatasets } = useProjectsNav()
      const result = await fetchDatasets('1')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/datasets?project_id=1&page=1&page_size=20',
        { headers: { Authorization: 'Bearer test-token' } }
      )
      expect(result).toEqual(mockDatasets)
    })

    it('returns empty array on API error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404
      })

      const { fetchDatasets } = useProjectsNav()
      const result = await fetchDatasets('1')

      expect(result).toEqual([])
    })

    it('returns empty array on network error', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      const { fetchDatasets } = useProjectsNav()
      const result = await fetchDatasets('1')

      expect(result).toEqual([])
    })
  })

  describe('reset', () => {
    it('clears projects and loaded state', async () => {
      const mockProjects = [
        { id: '1', name: 'Project A', datasets_count: 0 }
      ]
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ projects: mockProjects })
      })

      const { fetchProjects, projects, loaded, reset } = useProjectsNav()
      await fetchProjects()
      expect(projects.value).toEqual(mockProjects)
      expect(loaded.value).toBe(true)

      reset()
      expect(projects.value).toEqual([])
      expect(loaded.value).toBe(false)
    })
  })

  describe('loading state', () => {
    it('starts with loading false', () => {
      const { loading } = useProjectsNav()
      expect(loading.value).toBe(false)
    })
  })
})
