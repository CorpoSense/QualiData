// E2E tests for MasterDataCleaner

// Listen for console errors
Cypress.on('uncaught:exception', (err, runnable) => {
  // Don't fail tests on console errors
  return false
})

describe('MasterDataCleaner - Home Page', () => {
  it('homepage loads correctly', () => {
    cy.visit('/', { failOnStatusCode: false })
    cy.contains('MasterDataCleaner').should('exist')
  })

  it('pricing section is visible', () => {
    cy.visit('/', { failOnStatusCode: false })
    cy.contains('Simple Pricing').should('exist')
  })

  it('footer is visible', () => {
    cy.visit('/', { failOnStatusCode: false })
    cy.contains('2026').should('exist')
  })
})

describe('MasterDataCleaner - Login Page', () => {
  it('login page loads', () => {
    cy.visit('/login', { failOnStatusCode: false })
    // Wait for page to be ready
    cy.wait(2000)
    // Check that we have some content in #app
    cy.get('#app').should('not.be.empty')
  })

  it('login page has email field', () => {
    cy.visit('/login', { failOnStatusCode: false })
    cy.wait(2000)
    // Look for email-related content
    cy.get('body').should('contain', 'Email')
  })
})

describe('MasterDataCleaner - Pricing Page', () => {
  it('pricing page loads', () => {
    cy.visit('/pricing', { failOnStatusCode: false })
    cy.wait(1000)
    cy.get('body').should('contain', 'Free')
  })
})

describe('MasterDataCleaner - Navigation', () => {
  it('navbar exists on homepage', () => {
    cy.visit('/', { failOnStatusCode: false })
    cy.get('nav').should('exist')
  })
})
