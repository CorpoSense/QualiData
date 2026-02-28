// Simple E2E test for MasterDataCleaner
describe('MasterDataCleaner', () => {
  it('homepage loads correctly', () => {
    cy.visit('/')
    cy.contains('MasterDataCleaner').should('be.visible')
  })

  it('can navigate to login page', () => {
    cy.visit('/')
    cy.contains('Sign In').click()
    cy.get('input[type="email"]').should('be.visible')
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

  it('pricing page loads', () => {
    cy.visit('/pricing')
    cy.contains('Pricing').should('be.visible')
    cy.contains('Free').should('be.visible')
    cy.contains('Pro').should('be.visible')
    cy.contains('Enterprise').should('be.visible')
  })
})
