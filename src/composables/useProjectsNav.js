// Composable for navbar projects dropdown
import { ref, readonly } from 'vue'
import { getApiUrl } from '@/utils/api'

const projects = ref([])
const loading = ref(false)
const loaded = ref(false)

export function useProjectsNav() {
  const apiUrl = getApiUrl()

  async function fetchProjects() {
    if (loading.value) return
    loading.value = true
    try {
      const res = await fetch(`${apiUrl}/api/projects?page=1&page_size=50`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      if (res.ok) {
        const data = await res.json()
        projects.value = data.projects || []
        loaded.value = true
      }
    } catch (e) {
      console.error('Failed to fetch projects for navbar:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchDatasets(projectId) {
    try {
      const res = await fetch(`${apiUrl}/api/datasets?project_id=${projectId}&page=1&page_size=20`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      if (res.ok) {
        const data = await res.json()
        return data.datasets || []
      }
    } catch (e) {
      console.error('Failed to fetch datasets for navbar:', e)
    }
    return []
  }

  function reset() {
    projects.value = []
    loaded.value = false
  }

  return {
    projects,
    loading: readonly(loading),
    loaded: readonly(loaded),
    fetchProjects,
    fetchDatasets,
    reset,
  }
}
