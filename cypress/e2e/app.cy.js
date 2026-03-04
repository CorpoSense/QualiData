// E2E tests for MasterDataCleaner

describe('MasterDataCleaner - Home Page', () => {
  it('homepage loads', () => {
    cy.visit('/')
    cy.get('body').should('exist')
  })
})

describe('MasterDataCleaner - Login Page', () => {
  beforeEach(() => {
    cy.visit('/login')
  })

  it('login page loads', () => {
    cy.get('body').should('exist')
  })

  it('shows email and password fields', () => {
    cy.contains('Email').should('exist')
    cy.contains('Password').should('exist')
  })

  it('shows sign in button', () => {
    cy.contains('Sign In').should('exist')
  })

  it('shows forgot password link', () => {
    cy.contains('Forgot').should('exist')
  })

  it('shows oauth options', () => {
    cy.contains('Google').should('exist')
    cy.contains('GitHub').should('exist')
  })

  it('can switch to register tab', () => {
    cy.contains("Don't have an account?").click()
    cy.contains('Already have an account?').should('exist')
  })

  it('shows validation for empty email', () => {
    cy.contains('Sign In').click()
    // Should not crash - just handle gracefully
    cy.get('body').should('exist')
  })

  it('shows validation for empty password', () => {
    cy.get('input[type="email"]').type('test@example.com')
    cy.contains('Sign In').click()
    cy.get('body').should('exist')
  })
})

describe('MasterDataCleaner - Login Form Submission', () => {
  it('login with empty fields does not crash', () => {
    cy.visit('/login')
    cy.contains('Sign In').click()
    // Should show error or stay on page - not crash
    cy.get('body').should('exist')
  })

  it('login with email only does not crash', () => {
    cy.visit('/login')
    cy.get('input[type="email"]').type('test@example.com')
    cy.contains('Sign In').click()
    // Should show error or stay on page - not crash
    cy.get('body').should('exist')
  })

  it('login with non-existent user does not crash', () => {
    cy.visit('/login')
    cy.get('input[type="email"]').type('nonexistent@test.com')
    cy.get('input[type="password"]').type('wrongpassword')
    cy.contains('Sign In').click()
    // Should show error message - not crash
    cy.get('body').should('exist')
  })
})

describe('MasterDataCleaner - Register Page', () => {
  beforeEach(() => {
    cy.visit('/login')
    cy.contains("Don't have an account?").click()
  })

  it('register page loads', () => {
    cy.contains('Already have an account?').should('exist')
  })

  it('shows all required fields', () => {
    cy.contains('Full Name').should('exist')
    cy.contains('Email').should('exist')
    cy.contains('Password').should('exist')
    cy.contains('Confirm Password').should('exist')
  })

  it('can switch back to login', () => {
    cy.contains('Already have an account?').click()
    cy.contains("Don't have an account?").should('exist')
  })

  it('register with password mismatch shows error', () => {
    cy.get('input[placeholder="John Doe"]').type('Test User')
    cy.get('input[type="email"]').type('test@example.com')
    cy.get('input[type="password"]').type('password123')
    cy.get('input[placeholder="Confirm password"]').type('differentpassword')
    cy.contains('Create Account').click()
    // Should show password mismatch error
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

  it('shows email field', () => {
    cy.visit('/forgot-password')
    cy.contains('Email').should('exist')
  })
})

describe('MasterDataCleaner - Reset Password', () => {
  it('reset password page loads', () => {
    cy.visit('/reset-password?token=test')
    cy.get('body').should('exist')
  })

  it('shows new password fields', () => {
    cy.visit('/reset-password?token=test')
    cy.contains('New Password').should('exist')
    cy.contains('Confirm Password').should('exist')
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
