import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { createRouter, createMemoryHistory } from 'vue-router'
import Breadcrumb from '@/components/Breadcrumb.vue'

function createRouterInstance() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div>Home</div>' } },
      { path: '/projects', component: { template: '<div>Projects</div>' } },
      { path: '/projects/:id', component: { template: '<div>Project</div>' } },
      { path: '/settings', component: { template: '<div>Settings</div>' } },
      { path: '/:pathMatch(.*)*', component: { template: '<div>Catch-all</div>' } },
    ],
  })
}

function mountBreadcrumb(items: Array<{ label: string; path?: string; icon?: string }>) {
  const router = createRouterInstance()
  const wrapper = mount(Breadcrumb, {
    props: { items },
    global: {
      plugins: [router],
    },
  })
  return { wrapper, router }
}

describe('Breadcrumb.vue', () => {
  describe('Rendering', () => {
    it('renders nav element with aria-label', () => {
      const { wrapper } = mountBreadcrumb([{ label: 'Home', path: '/' }])
      const nav = wrapper.find('nav')
      expect(nav.exists()).toBe(true)
      expect(nav.attributes('aria-label')).toBe('breadcrumb')
    })

    it('renders ordered list with breadcrumb class', () => {
      const { wrapper } = mountBreadcrumb([{ label: 'Home', path: '/' }])
      const ol = wrapper.find('ol.breadcrumb')
      expect(ol.exists()).toBe(true)
      expect(ol.classes()).toContain('mb-0')
    })

    it('renders empty list when items array is empty', () => {
      const { wrapper } = mountBreadcrumb([])
      const items = wrapper.findAll('li.breadcrumb-item')
      expect(items).toHaveLength(0)
    })

    it('renders single item as active with span', () => {
      const { wrapper } = mountBreadcrumb([{ label: 'Home', path: '/' }])
      const items = wrapper.findAll('li.breadcrumb-item')
      expect(items).toHaveLength(1)
      expect(items[0].classes()).toContain('active')
      expect(items[0].find('span').exists()).toBe(true)
      expect(items[0].find('span').text()).toBe('Home')
      expect(items[0].find('a').exists()).toBe(false)
    })

    it('renders multiple items with last one active', () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'Home', path: '/' },
        { label: 'Projects', path: '/projects' },
        { label: 'Project X' },
      ])
      const items = wrapper.findAll('li.breadcrumb-item')
      expect(items).toHaveLength(3)

      // First two should have router-link
      expect(items[0].find('a').exists()).toBe(true)
      expect(items[1].find('a').exists()).toBe(true)

      // Last should be active with span
      expect(items[2].classes()).toContain('active')
      expect(items[2].find('span').exists()).toBe(true)
      expect(items[2].find('a').exists()).toBe(false)
    })

    it('renders correct labels for all items', () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'Home', path: '/' },
        { label: 'Projects', path: '/projects' },
        { label: 'Dataset A' },
      ])
      const items = wrapper.findAll('li.breadcrumb-item')
      expect(items[0].text()).toBe('Home')
      expect(items[1].text()).toBe('Projects')
      expect(items[2].text()).toBe('Dataset A')
    })
  })

  describe('Router Links', () => {
    it('renders router-link for non-last items with path', () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'Home', path: '/' },
        { label: 'Projects', path: '/projects' },
        { label: 'Current' },
      ])
      const links = wrapper.findAllComponents({ name: 'RouterLink' })
      expect(links).toHaveLength(2)
    })

    it('does not render router-link for the last item even with path', () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'Home', path: '/' },
        { label: 'Current', path: '/current' },
      ])
      const items = wrapper.findAll('li.breadcrumb-item')
      // Last item should use span, not router-link
      expect(items[1].find('a').exists()).toBe(false)
      expect(items[1].find('span').exists()).toBe(true)
    })

    it('renders span instead of router-link when item has no path', () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'Home', path: '/' },
        { label: 'No Path' },
      ])
      const items = wrapper.findAll('li.breadcrumb-item')
      // Second item has no path, should use span
      expect(items[1].find('span').exists()).toBe(true)
      expect(items[1].find('a').exists()).toBe(false)
    })

    it('sets correct to prop on router-links', () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'Home', path: '/' },
        { label: 'Projects', path: '/projects' },
        { label: 'Current' },
      ])
      const links = wrapper.findAllComponents({ name: 'RouterLink' })
      expect(links[0].props('to')).toBe('/')
      expect(links[1].props('to')).toBe('/projects')
    })
  })

  describe('Icons', () => {
    it('renders icon in router-link when icon is provided for non-last item', () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'Home', path: '/', icon: 'bi bi-house' },
        { label: 'Current' },
      ])
      const items = wrapper.findAll('li.breadcrumb-item')
      const icon = items[0].find('i')
      expect(icon.exists()).toBe(true)
      expect(icon.classes()).toContain('bi')
      expect(icon.classes()).toContain('bi-house')
      expect(icon.classes()).toContain('me-1')
    })

    it('renders icon in span when icon is provided for last item', () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'Home', path: '/' },
        { label: 'Current', icon: 'bi bi-folder' },
      ])
      const items = wrapper.findAll('li.breadcrumb-item')
      const icon = items[1].find('i')
      expect(icon.exists()).toBe(true)
      expect(icon.classes()).toContain('bi')
      expect(icon.classes()).toContain('bi-folder')
      expect(icon.classes()).toContain('me-1')
    })

    it('does not render icon element when icon is not provided', () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'Home', path: '/' },
        { label: 'Current' },
      ])
      const icons = wrapper.findAll('i')
      expect(icons).toHaveLength(0)
    })

    it('renders icons for all items when provided', () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'Home', path: '/', icon: 'bi bi-house' },
        { label: 'Projects', path: '/projects', icon: 'bi bi-folder' },
        { label: 'Dataset', icon: 'bi bi-table' },
      ])
      const icons = wrapper.findAll('i')
      expect(icons).toHaveLength(3)
    })
  })

  describe('Active State', () => {
    it('applies active class only to the last item', () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'Home', path: '/' },
        { label: 'Projects', path: '/projects' },
        { label: 'Current' },
      ])
      const items = wrapper.findAll('li.breadcrumb-item')
      expect(items[0].classes()).not.toContain('active')
      expect(items[1].classes()).not.toContain('active')
      expect(items[2].classes()).toContain('active')
    })

    it('applies active class to single item', () => {
      const { wrapper } = mountBreadcrumb([{ label: 'Only Item' }])
      const items = wrapper.findAll('li.breadcrumb-item')
      expect(items).toHaveLength(1)
      expect(items[0].classes()).toContain('active')
    })
  })

  describe('Reactivity', () => {
    it('updates rendered items when props change', async () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'Home', path: '/' },
        { label: 'Projects', path: '/projects' },
      ])
      expect(wrapper.findAll('li.breadcrumb-item')).toHaveLength(2)

      await wrapper.setProps({
        items: [
          { label: 'Home', path: '/' },
          { label: 'Projects', path: '/projects' },
          { label: 'Dataset A' },
        ],
      })
      await nextTick()

      expect(wrapper.findAll('li.breadcrumb-item')).toHaveLength(3)
      const items = wrapper.findAll('li.breadcrumb-item')
      expect(items[2].text()).toBe('Dataset A')
      expect(items[2].classes()).toContain('active')
    })

    it('updates from items with icons to items without icons', async () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'Home', path: '/', icon: 'bi bi-house' },
        { label: 'Current', icon: 'bi bi-folder' },
      ])
      expect(wrapper.findAll('i')).toHaveLength(2)

      await wrapper.setProps({
        items: [
          { label: 'Home', path: '/' },
          { label: 'Current' },
        ],
      })
      await nextTick()

      expect(wrapper.findAll('i')).toHaveLength(0)
    })
  })

  describe('Edge Cases', () => {
    it('handles item with path as last item (renders as span, not link)', () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'Current', path: '/current' },
      ])
      const items = wrapper.findAll('li.breadcrumb-item')
      expect(items[0].classes()).toContain('active')
      expect(items[0].find('span').exists()).toBe(true)
      expect(items[0].find('a').exists()).toBe(false)
    })

    it('handles item without path as non-last item (renders as span)', () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'No Path' },
        { label: 'Current' },
      ])
      const items = wrapper.findAll('li.breadcrumb-item')
      // First item has no path, should use span
      expect(items[0].find('span').exists()).toBe(true)
      expect(items[0].find('a').exists()).toBe(false)
    })

    it('handles all items without paths', () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'Step 1' },
        { label: 'Step 2' },
        { label: 'Step 3' },
      ])
      const links = wrapper.findAllComponents({ name: 'RouterLink' })
      expect(links).toHaveLength(0)
      const spans = wrapper.findAll('li.breadcrumb-item span')
      expect(spans).toHaveLength(3)
    })

    it('handles all items with paths (only last rendered as span)', () => {
      const { wrapper } = mountBreadcrumb([
        { label: 'Home', path: '/' },
        { label: 'Projects', path: '/projects' },
        { label: 'Settings', path: '/settings' },
      ])
      const links = wrapper.findAllComponents({ name: 'RouterLink' })
      expect(links).toHaveLength(2)
      const items = wrapper.findAll('li.breadcrumb-item')
      expect(items[2].find('span').exists()).toBe(true)
    })

    it('renders correct number of breadcrumb items', () => {
      const items = Array.from({ length: 5 }, (_, i) => ({
        label: `Item ${i + 1}`,
        path: i < 4 ? `/path-${i + 1}` : undefined,
      }))
      const { wrapper } = mountBreadcrumb(items)
      expect(wrapper.findAll('li.breadcrumb-item')).toHaveLength(5)
    })
  })
})
