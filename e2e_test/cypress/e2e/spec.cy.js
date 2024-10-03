
describe('Test Spec', function() {

  before(() => {
    const username = new Date().getTime().toString();
    const email = username + '@gmail.com';
    const password = "myasdjflks123"
    cy.wrap(username).as('username')
    cy.wrap(email).as('email')
    cy.wrap(password).as('password')
    cy.visit('/')
  })

  it("it should register a new user", function() {
    cy.get('a[href="/accounts/register-v1/"]').click({ force: true })
    cy.get('input[name="username"]').type(this.username)
    cy.get('input[name="email"]').type(this.email)
    cy.get('input[name="password1"]').type(this.password)
    cy.get('input[name="password2"]').type(this.password)
    cy.get('button[type="submit"').contains('Sign up').click()

    // assertion login page
    cy.get('h3').contains('Login').should('be.visible')
    cy.get('input[name="username"]').should('be.visible')
    cy.get('input[name="password"]').should('be.visible')
    cy.get('button[type="submit"').should('be.visible')
  })

  it('it should log in with the registered user', function() {
    cy.login(this.username, this.password, this.username)
    cy.visit('/')
  })

  it('it should update the fullname of user', function() {
    cy.login(this.username, this.password, this.username)
    cy.visit('/')
    cy.get('.drp-user > a').should('be.visible').click({ force: true })
    cy.get('.profile-notification > .pro-body > li > a[href="/users/profile/"]').click()
    cy.get('a[href="#user-set-information"]').click({ force: true })
    cy.get('input[name="full_name"]').type('updated', { force: true })
    cy.get('button[type="submit"]').contains('Update Profile').click()
    cy.get('p').contains('Profile updated successfully')
  })

  it('it data in database should be updated', function() {
    cy.login(this.username, this.password, this.username)
    cy.visit('/users/profile')
    cy.task("getUserProfile", this.email).as('getProfile')
    cy.get('@getProfile').its('full_name').should('eq', 'updated')
  })

  it('it should logout', function () {
    cy.login(this.username, this.password, this.username)
    cy.visit('/')
    cy.get('.drp-user > a').should('be.visible').click()
    cy.get('a[href="/accounts/logout/"]').click()
  })

  it('it should redirect to login page when access the profile page', () => {
    cy.visit('/users/profile').its('location.pathname').should('eq', 
"/accounts/login-v1/")
  });
})
