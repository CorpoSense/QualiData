<template>
  <div>
    <b-navbar type="is-white" :fixed-top="true" :mobile-burger="true" wrapper-class="container">
      <template #brand>
        <b-navbar-item tag="router-link" :to="{ path: '/' }" class="logo-item">
          <b-icon icon="alpha-m-box" size="is-medium" type="is-primary"></b-icon>
          <span class="logo-text">MasterDataCleaner</span>
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
            <b-button type="is-light">
              Log In
            </b-button>
            <b-button type="is-primary" class="has-shadow">
              <strong>Sign Up Free</strong>
            </b-button>
          </div>
        </b-navbar-item>
      </template>
    </b-navbar>

    <main>
      <router-view />
    </main>

    <footer class="footer">
      <div class="content has-text-centered">
        <p>
          <strong>MasterDataCleaner</strong> by <a href="https://yourcompany.com">YourCompany</a>. The source code is licensed
          <a href="http://opensource.org/licenses/mit-license.php">MIT</a>.
        </p>
        <p>&copy; 2024 YourCompany, Inc. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
// Script remains clean as navigation is handled by Buefy's component
</script>

<style>
/* General app styling */
html {
  scroll-behavior: smooth;
}

body {
  background-color: #f8f9fa; /* Light grey background for the whole app */
}

/* Navbar styling */
.navbar {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 0.5rem 0;
}

.logo-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-text {
  font-weight: 600;
  font-size: 1.1rem;
}

.navbar-item {
  font-weight: 500;
  color: #4a4a4a;
}

.navbar-item.is-active,
.navbar-item:hover {
  color: #3273dc; /* Bulma's primary blue */
}

.navbar .buttons .button.is-primary {
  background-color: #667eea;
}

.navbar .buttons .button.is-primary:hover {
  background-color: #5a6ed0;
}

/* Add a subtle shadow to primary buttons */
.button.has-shadow {
  box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
}

/* Main content area */
main {
  padding-top: 52px; /* Height of the navbar */
}

/* Footer styling */
.footer {
  background-color: #ffffff;
  padding: 3rem 1.5rem 3rem;
  border-top: 1px solid #e0e0e0;
}
</style>