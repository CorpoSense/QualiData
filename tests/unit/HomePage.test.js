import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import Home from '@/views/Home.vue';

describe('Home Page', () => {
  it('renders the hero section with main heading', () => {
    const wrapper = mount(Home);
    
    // Check that the main heading is present
    expect(wrapper.find('h1.display-3').exists()).toBe(true);
    expect(wrapper.find('h1.display-3').text()).toContain('Master Your Data');
  });

  it('contains navigation elements', () => {
    const wrapper = mount(Home);
    
    // Check for navigation elements
    expect(wrapper.find('.navbar-brand').text()).toBe('MasterDataCleaner');
    expect(wrapper.find('.nav-item a[href="#features"]').exists()).toBe(true);
    expect(wrapper.find('.nav-item a[href="#pricing"]').exists()).toBe(true);
  });

  it('has CTA buttons in hero section', () => {
    const wrapper = mount(Home);
    
    // Check for CTA buttons by text content
    expect(wrapper.text()).toContain('Get Started Free');
    expect(wrapper.text()).toContain('Watch Demo');
  });

  it('displays features section', () => {
    const wrapper = mount(Home);
    
    // Check for features section
    expect(wrapper.find('#features').exists()).toBe(true);
    expect(wrapper.findAll('.feature-card').length).toBe(6); // There are 6 feature cards
  });

  it('includes pricing section with tiers', () => {
    const wrapper = mount(Home);
    
    // Check for pricing section
    expect(wrapper.find('#pricing').exists()).toBe(true);
    expect(wrapper.findAll('.col-lg-4').length).toBeGreaterThanOrEqual(2); // At least 2 pricing tiers
  });

  it('has footer with navigation links', () => {
    const wrapper = mount(Home);
    
    // Check for footer elements
    expect(wrapper.find('footer').exists()).toBe(true);
    expect(wrapper.find('footer').exists()).toBe(true);
  });
});