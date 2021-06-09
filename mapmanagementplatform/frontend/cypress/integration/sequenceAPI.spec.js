describe('Sequence API', () => {
    it('check a random value in Sequence API', () => {
      cy.visit('http://localhost:8000/api/sequences/?ids=1'); 
      cy.contains('kqw1kqn8kgg20w8qx6n4qa').should('exist');
    });
  });
  