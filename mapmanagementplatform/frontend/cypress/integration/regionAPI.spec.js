describe('Region API', () => {
    it('check a random value in Region API', () => {
      cy.visit('http://localhost:8000/api/regions'); 
      cy.contains('Adelaide CBD').should('exist');
    });
  });
  