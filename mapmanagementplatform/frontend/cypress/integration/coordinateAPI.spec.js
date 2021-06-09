describe('Coordinate API', () => {
    it('check a random value in Coordinate API', () => {
      cy.visit('http://localhost:8000/api/coordinates/?ids=1'); 
      cy.contains('9_pk3Ly9BbAg1lkYv8qyzQ').should('exist');
    });
  });
  