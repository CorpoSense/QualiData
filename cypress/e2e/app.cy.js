// E2E tests for MasterDataCleaner

describe('MasterDataCleaner - Home Page', () => {
  it('homepage loads', () => {
    cy.visit('/')
    cy.get('body').should('exist')
  })
})

describe('MasterDataCleaner - Login Page', () => {
  it('login page loads', () => {
    cy.visit('/login')
    cy.get('body').should('exist')
  })
})

describe('MasterDataCleaner - Pricing Page', () => {
  it('pricing page loads', () => {
    cy.visit('/pricing')
    cy.get('body').should('exist')
  })
})
