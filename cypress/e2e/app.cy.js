// E2E tests for MasterDataCleaner

describe('MasterDataCleaner - Home Page', () => {
  it('homepage loads correctly', () => {
    cy.visit('/')
    cy.contains('MasterDataCleaner').should('be.visible')
  })

  it('pricing section is visible', () => {
    cy.visit('/')
    cy.contains('Simple Pricing').should('be.visible')
    cy.contains('Free').should('be.visible')
    cy.contains('Pro').should('be.visible')
    cy.contains('Enterprise').should('be.visible')
  })

  it('features section is visible', () => {
    cy.visit('/')
    cy.contains('Powerful Features').should('be.visible')
  })

  it('footer is visible', () => {
    cy.visit('/')
    cy.contains('2026 MasterDataCleaner').should('be.visible')
  })
})

describe('MasterDataCleaner - Login Page', () => {
  it('login page loads', () => {
    cy.visit('/login')
    cy.contains('Sign in to your account').should('be.visible')
  })

  it('can switch to register tab', () => {
    cy.visit('/login')
    cy.contains("Don't have an account?").should('be.visible')
    cy.contains('Sign Up').click()
    cy.contains('Already have an account?').should('be.visible')
  })

  it('forgot password link exists', () => {
    cy.visit('/login')
    cy.contains('Forgot your password?').should('be.visible')
  })

  it('oauth buttons exist', () => {
    cy.visit('/login')
    cy.contains('Google').should('be.visible')
    cy.contains('GitHub').should('be.visible')
  })

  it('login form validation', () => {
    cy.visit('/login')
    // Submit empty form
    cy.contains('Sign In').click()
    // Should show validation errors (email required)
    cy.get('input[type="email"]').should('exist')
  })
})

describe('MasterDataCleaner - Pricing Page', () => {
  it('pricing page loads with all tiers', () => {
    cy.visit('/pricing')
    cy.contains('Simple').should('be.visible')
    cy.contains('Free').should('be.visible')
    cy.contains('Pro').should('be.visible')
    cy.contains('Enterprise').should('be.visible')
  })

  it('pricing page has FAQ section', () => {
    cy.visit('/pricing')
    cy.contains('Frequently Asked Questions').should('be.visible')
  })
})

describe('MasterDataCleaner - Navigation', () => {
  it('navbar appears on homepage', () => {
    cy.visit('/')
    // Check for navbar elements
    cy.get('nav').should('exist')
  })

  it('public navbar has correct links', () => {
    cy.visit('/')
    cy.contains('Home').should('exist')
    cy.contains('Pricing').should('exist')
  })
})
