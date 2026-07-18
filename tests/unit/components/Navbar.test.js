/**
 * Tests for Navbar component
 * Tests rendering, projects dropdown, submenu behavior, and navigation
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import Navbar from '@/components/Navbar.vue'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(() => 'test-token'),
  setItem: vi.fn(),
  removeItem: vi.fn(),
}
Object.defineProperty(globalThis, 'localStorage', { value: localStorageMock })

// Mock fetch for projects nav
const mockFetch = vi.fn()
globalThis.fetch = mockFetch

// Mock getApiUrl
vi.mock('@/utils/api', () => ({
  getApiUrl: () => 'http://localhost:8000'
}))

// Mock useProjectsNav composable
const mockReset = vi.fn()
const mockFetchProjects = vi.fn()
const mockFetchDatasets = vi.fn()

vi.mock('@/composables/useProjectsNav', () => ({
  useProjectsNav: () => ({
    projects: { value: [] },
    loading: { value: false },
    loaded: { value: false },
    fetchProjects: mockFetchProjects,
    fetchDatasets: mockFetchDatasets,
    reset: mockReset,
  })
}))

// Create a simple router for testing
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/projects', component: { template: '<div>Projects</div>' } },
    { path: '/projects/:id', component: { template: '<div>Project Detail</div>' } },
    { path: '/projects/:id/dataset/:datasetId', component: { template: '<div>Data Viewer</div>' } },
    { path: '/dashboard', component: { template: '<div>Dashboard</div>' } },
    { path: '/agents', component: { template: '<div>Agents</div>' } },
    { path: '/admin/users', component: { template: '<div>Users</div>' } },
    { path: '/profile', component: { template: '<div>Profile</div>' } },
    { path: '/login', component: { template: '<div>Login</div>' } },
  ],
})

function createWrapper(props = {}) {
  return mount(Navbar, {
    props: {
      isAuthenticated: true,
      user: { email: 'test@example.com', role: 'user' },
      unreadCount: 0,
      ...props,
    },
    global: {
      plugins: [router],
      stubs: {
        'router-link': {
          template: '<a :href="to" @click.prevent><slot /></a>',
          props: ['to'],
        },
      },
    },
  })
}

describe('Navbar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering - Unauthenticated', () => {
    it('renders public nav links when not authenticated', () => {
      const wrapper = createWrapper({ isAuthenticated: false })
      expect(wrapper.find('a[href="#features"]').exists()).toBe(true)
      expect(wrapper.find('a[href="#pricing"]').exists()).toBe(true)
    })

    it('does not render authenticated nav links when not authenticated', () => {
      const wrapper = createWrapper({ isAuthenticated: false })
      expect(wrapper.find('.projects-dropdown').exists()).toBe(false)
    })
  })

  describe('Rendering - Authenticated', () => {
    it('renders Dashboard link', () => {
      const wrapper = createWrapper()
      const links = wrapper.findAll('.nav-link')
      const dashboardLink = links.find(l => l.text().includes('Dashboard'))
      expect(dashboardLink).toBeTruthy()
    })

    it('renders Projects dropdown toggle', () => {
      const wrapper = createWrapper()
      const toggle = wrapper.find('.projects-dropdown .dropdown-toggle')
      expect(toggle.exists()).toBe(true)
      expect(toggle.text()).toContain('Projects')
    })

    it('renders AI Agents link', () => {
      const wrapper = createWrapper()
      const links = wrapper.findAll('.nav-link')
      const agentsLink = links.find(l => l.text().includes('Agents'))
      expect(agentsLink).toBeTruthy()
    })

    it('renders Users link for admin users', () => {
      const wrapper = createWrapper({ user: { email: 'admin@test.com', role: 'admin' } })
      const links = wrapper.findAll('.nav-link')
      const usersLink = links.find(l => l.text().includes('Users'))
      expect(usersLink).toBeTruthy()
    })

    it('hides Users link for non-admin users', () => {
      const wrapper = createWrapper({ user: { email: 'user@test.com', role: 'user' } })
      const links = wrapper.findAll('.nav-link')
      const usersLink = links.find(l => l.text().includes('Users'))
      expect(usersLink).toBeFalsy()
    })

    it('renders notification bell', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.bi-bell').exists()).toBe(true)
    })

    it('shows unread count badge when unreadCount > 0', () => {
      const wrapper = createWrapper({ unreadCount: 5 })
      const badge = wrapper.find('.badge.bg-danger')
      expect(badge.exists()).toBe(true)
      expect(badge.text()).toBe('5')
    })

    it('shows 9+ when unreadCount > 9', () => {
      const wrapper = createWrapper({ unreadCount: 15 })
      const badge = wrapper.find('.badge.bg-danger')
      expect(badge.text()).toBe('9+')
    })

    it('renders user dropdown with email', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.user-avatar').exists()).toBe(true)
      expect(wrapper.text()).toContain('test@example.com')
    })
  })

  describe('Projects Dropdown', () => {
    it('shows dropdown menu when toggle is clicked', async () => {
      const wrapper = createWrapper()
      const toggle = wrapper.find('.projects-dropdown .dropdown-toggle')

      await toggle.trigger('click')

      expect(wrapper.find('.projects-dropdown-menu.show').exists()).toBe(true)
    })

    it('calls fetchProjects when dropdown is opened', async () => {
      const wrapper = createWrapper()
      const toggle = wrapper.find('.projects-dropdown .dropdown-toggle')

      await toggle.trigger('click')

      expect(mockFetchProjects).toHaveBeenCalled()
    })

    it('closes dropdown when closeProjects is triggered', async () => {
      const wrapper = createWrapper()
      const toggle = wrapper.find('.projects-dropdown .dropdown-toggle')

      await toggle.trigger('click')
      expect(wrapper.find('.projects-dropdown-menu.show').exists()).toBe(true)

      // Click the "All Projects" link which calls closeProjects
      const allProjectsLink = wrapper.find('.projects-dropdown-menu .dropdown-item')
      await allProjectsLink.trigger('click')
      expect(wrapper.find('.projects-dropdown-menu.show').exists()).toBe(false)
    })

    it('shows "All Projects" link in dropdown', () => {
      const wrapper = createWrapper()
      const dropdownMenu = wrapper.find('.projects-dropdown-menu')
      expect(dropdownMenu.text()).toContain('All Projects')
    })

    it('toggles dropdown open and closed on click', async () => {
      const wrapper = createWrapper()
      const toggle = wrapper.find('.projects-dropdown .dropdown-toggle')

      await toggle.trigger('click')
      expect(wrapper.find('.projects-dropdown-menu.show').exists()).toBe(true)

      await toggle.trigger('click')
      expect(wrapper.find('.projects-dropdown-menu.show').exists()).toBe(false)
    })
  })

  describe('Events', () => {
    it('emits show-notifications when bell is clicked', async () => {
      const wrapper = createWrapper()
      const bellButton = wrapper.findAll('button').find(btn => btn.find('.bi-bell').exists())
      await bellButton.trigger('click')

      expect(wrapper.emitted('show-notifications')).toBeTruthy()
    })

    it('emits logout when logout link is clicked', async () => {
      const wrapper = createWrapper()
      const logoutLink = wrapper.find('.dropdown-item.text-danger')
      await logoutLink.trigger('click')

      expect(wrapper.emitted('logout')).toBeTruthy()
    })
  })
})
