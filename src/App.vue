<template>
  <div class="app-layout">
    <b-navbar 
      type="is-white" 
      :fixed-top="true" 
      :mobile-burger="true" 
      wrapper-class="container"
      class="app-navbar"
    >
      <template #brand>
        <b-navbar-item tag="router-link" :to="{ path: '/' }" class="logo-item px-4">
          <div class="logo-icon mr-2">
            <b-icon icon="alpha-m-box" size="is-medium" type="is-primary"></b-icon>
          </div>
          <span class="logo-text has-text-weight-black is-size-5">MasterDataCleaner</span>
        </b-navbar-item>
      </template>

      <template #start>
        <b-navbar-item tag="router-link" to="/">
          Home
        </b-navbar-item>
        <b-navbar-item href="#features">
          Features
        </b-navbar-item>
        <b-navbar-item href="#pricing">
          Pricing
        </b-navbar-item>
        <b-navbar-item href="#docs">
          Docs
        </b-navbar-item>
      </template>

      <template #end>
        <b-navbar-item tag="div">
          <div class="buttons">
            <b-button type="is-light" class="has-text-weight-semibold">
              Log In
            </b-button>
            <b-button type="is-primary" class="has-text-weight-bold shadow-sm">
              Sign Up Free
            </b-button>
          </div>
        </b-navbar-item>
      </template>
    </b-navbar>

    <main class="main-content">
      <router-view />
    </main>

    <footer class="footer bg-white pt-6 pb-6">
      <div class="container">
        <div class="columns is-multiline mb-6">
          <div class="column is-4">
            <div class="footer-brand mb-4">
              <span class="logo-text has-text-weight-black is-size-5">MasterDataCleaner</span>
            </div>
            <p class="has-text-grey is-size-6 mb-4 max-w-sm">
              The modern data quality platform for engineers. Clean, unify, and trust your data at scale.
            </p>
            <div class="social-links">
              <a href="#" class="mr-3 has-text-grey-light hover-primary"><b-icon icon="twitter"></b-icon></a>
              <a href="#" class="mr-3 has-text-grey-light hover-primary"><b-icon icon="github"></b-icon></a>
              <a href="#" class="mr-3 has-text-grey-light hover-primary"><b-icon icon="linkedin"></b-icon></a>
            </div>
          </div>
          
          <div class="column is-2 is-offset-2">
            <h4 class="title is-6 mb-4">Product</h4>
            <ul class="footer-links">
              <li><a href="#">Features</a></li>
              <li><a href="#">Integrations</a></li>
              <li><a href="#">Security</a></li>
              <li><a href="#">Pricing</a></li>
            </ul>
          </div>
          
          <div class="column is-2">
            <h4 class="title is-6 mb-4">Resources</h4>
            <ul class="footer-links">
              <li><a href="#">Documentation</a></li>
              <li><a href="#">API Reference</a></li>
              <li><a href="#">Community</a></li>
              <li><a href="#">Blog</a></li>
            </ul>
          </div>
          
          <div class="column is-2">
            <h4 class="title is-6 mb-4">Company</h4>
            <ul class="footer-links">
              <li><a href="#">About Us</a></li>
              <li><a href="#">Careers</a></li>
              <li><a href="#">Contact</a></li>
              <li><a href="#">Privacy Policy</a></li>
            </ul>
          </div>
        </div>
        
        <div class="footer-bottom pt-5 border-top flex align-center justify-between">
          <p class="is-size-7 has-text-grey">
            &copy; 2026 MasterDataCleaner Inc. All rights reserved. Made with ❤️ for data teams.
          </p>
          <div class="footer-meta flex gap-4">
            <span class="tag is-success is-light is-small">System Status: Operational</span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
// Script remains clean as navigation is handled by Buefy's component
</script>

<style>
/* Global SaaS Styles */
html {
  scroll-behavior: smooth;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: #ffffff;
  color: #1a202c;
  -webkit-font-smoothing: antialiased;
}

/* Utils */
.flex { display: flex; }
.align-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-4 { gap: 1rem; }
.mb-4 { margin-bottom: 1rem !important; }
.mb-6 { margin-bottom: 3rem !important; }
.mr-2 { margin-right: 0.5rem !important; }
.mr-3 { margin-right: 0.75rem !important; }
.px-4 { padding-left: 1rem !important; padding-right: 1rem !important; }
.pt-6 { padding-top: 3rem !important; }
.pb-6 { padding-bottom: 3rem !important; }
.border-top { border-top: 1px solid #edf2f7; }
.bg-white { background-color: #ffffff !important; }
.max-w-sm { max-width: 24rem; }

/* Navbar */
.app-navbar {
  border-bottom: 1px solid #f7fafc;
  height: 72px;
}

.logo-item:hover {
  background-color: transparent !important;
}

.logo-icon {
  background: #ebf4ff;
  border-radius: 8px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.navbar-item {
  font-weight: 500;
  font-size: 0.95rem;
  transition: color 0.2s ease;
}

.navbar-item:hover {
  color: #667eea !important;
}

/* Buttons */
.button.is-primary {
  background-color: #667eea;
  border-color: transparent;
}

.button.is-primary:hover {
  background-color: #5a6ed0;
}

.shadow-sm {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

/* Main */
.main-content {
  min-height: calc(100vh - 72px);
}

/* Footer */
.footer-links {
  list-style: none;
  margin: 0;
  padding: 0;
}

.footer-links li {
  margin-bottom: 0.75rem;
}

.footer-links a {
  color: #718096;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.footer-links a:hover {
  color: #667eea;
  padding-left: 4px;
}

.hover-primary:hover {
  color: #667eea !important;
}

@media (max-width: 768px) {
  .footer-bottom {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
  }
}
</style>
