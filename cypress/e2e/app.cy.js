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
  
  it('pricing shows free tier', () => {
    cy.visit('/pricing')
    cy.get('body').should('contain', 'Free')
  })
  
  it('pricing shows pro tier', () => {
    cy.visit('/pricing')
    cy.get('body').should('contain', 'Pro')
  })
  
  it('pricing shows enterprise tier', () => {
    cy.visit('/pricing')
    cy.get('body').should('contain', 'Enterprise')
  })
})

describe('MasterDataCleaner - Forgot Password', () => {
  it('forgot password page loads', () => {
    cy.visit('/forgot-password')
    cy.get('body').should('exist')
  })
})

describe('MasterDataCleaner - Reset Password', () => {
  it('reset password page loads', () => {
    cy.visit('/reset-password?token=test')
    cy.get('body').should('exist')
  })
})

describe('MasterDataCleaner - Navigation', () => {
  it('navbar exists on homepage', () => {
    cy.visit('/')
    cy.get('nav').should('exist')
  })
  
  it('navbar exists on login page', () => {
    cy.visit('/login')
    cy.get('nav').should('exist')
  })
  
  it('navbar exists on pricing page', () => {
    cy.visit('/pricing')
    cy.get('nav').should('exist')
  })
})
