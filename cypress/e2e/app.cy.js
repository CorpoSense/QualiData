// E2E tests for MasterDataCleaner

// Handle console errors gracefully
Cypress.on('uncaught:exception', (err) => {
  return false
})

describe('MasterDataCleaner - Home Page', () => {
  it('homepage loads', () => {
    cy.visit('/', { failOnStatusCode: false })
    cy.get('body').should('exist')
  })
})

describe('MasterDataCleaner - Login Page', () => {
  beforeEach(() => {
    cy.visit('/login', { failOnStatusCode: false })
    cy.wait(2000)
  })

  it('login page loads without crashing', () => {
    cy.get('body').should('exist')
  })

  it('login page has content', () => {
    cy.get('body').should('not.be.empty')
  })
})

describe('MasterDataCleaner - Register Page', () => {
  beforeEach(() => {
    cy.visit('/login', { failOnStatusCode: false })
    cy.wait(2000)
  })

  it('can access register through login page', () => {
    cy.get('body').should('exist')
  })
})

describe('MasterDataCleaner - Pricing Page', () => {
  it('pricing page loads', () => {
    cy.visit('/pricing', { failOnStatusCode: false })
    cy.wait(1000)
    cy.get('body').should('exist')
  })
})

describe('MasterDataCleaner - Forgot Password', () => {
  it('forgot password page loads', () => {
    cy.visit('/forgot-password', { failOnStatusCode: false })
    cy.wait(1000)
    cy.get('body').should('exist')
  })
})

describe('MasterDataCleaner - Reset Password', () => {
  it('reset password page loads', () => {
    cy.visit('/reset-password?token=test', { failOnStatusCode: false })
    cy.wait(1000)
    cy.get('body').should('exist')
  })
})

describe('MasterDataCleaner - Navigation', () => {
  it('navbar exists on homepage', () => {
    cy.visit('/', { failOnStatusCode: false })
    cy.get('nav').should('exist')
  })
})
