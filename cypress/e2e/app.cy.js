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
  beforeEach(() => {
    cy.visit('/login')
    // Wait for the app to load
    cy.wait(1000)
  })

  it('login page loads', () => {
    cy.get('input[type="email"]').should('exist')
  })

  it('can switch to register tab', () => {
    // Wait for page to be ready
    cy.get('input[type="email"]').should('exist')
    // Click the Sign Up tab button
    cy.get('button').contains('Sign Up').click()
    cy.contains('Already have an account?').should('be.visible')
  })

  it('forgot password link exists', () => {
    cy.get('input[type="email"]').should('exist')
    cy.contains('Forgot').should('exist')
  })

  it('oauth buttons exist', () => {
    cy.get('input[type="email"]').should('exist')
    cy.contains('Google').should('exist')
    cy.contains('GitHub').should('exist')
  })
})

describe('MasterDataCleaner - Pricing Page', () => {
  it('pricing page loads with all tiers', () => {
    cy.visit('/pricing')
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
    cy.get('nav').should('exist')
  })

  it('public navbar has correct links', () => {
    cy.visit('/')
    cy.contains('Home').should('exist')
    cy.contains('Pricing').should('exist')
  })
})
