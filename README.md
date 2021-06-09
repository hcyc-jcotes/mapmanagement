# Map Management - Team 03 

## To verify test results
Refer to Appendix A - Test report in Documentation/Testing plan_Team 03.pdf
- For Defect/Unit Testing and Integration Testing in Django: test cases can be found in mapmanagementplatform/backend/tests.py. To execute the tests, in the `mapmangementplatform` directory, run the command  `python manage.py test` in the terminal (after activating the virtual environment). The 9 tests will be executed and result "OK" will be returned. 
- For Defect/Unit Testing in React: test cases can be found in mapmanagementplatform/frontend/src/App.test.js. To execute the tests, in the `mapmangementplatform/frontend` directory, run the command  `npm run test` in the terminal. The 6 tests will be executed and 6 tests passed. 
- For Integration Testing in React: test cases can be found in mapmanagementplatform/frontend/cypress/integration. To execute the tests, in the `mapmangementplatform/frontend` directory, run the command  `npm run e2e` in the terminal. The 3 tests will be executed and all specs passed. 

## To Setup the Django server

In the `mapmangementplatform` directory, run the following commands to start the server (backend - Django):
### `python3 -m venv venv` (for MacOS/Linux) or `python -m venv venv` (for Windows)

### `source venv/bin/activate` (for MacOS/Linux) or `venv\Scripts\activate` (for Windows)

### `pip install -r requirements.txt`

## To Run the Django server

### `python manage.py runserver`

Runs the app in the development mode.\
Open http://127.0.0.1:8000/ to view it in the browser.
The page will reload if you make edits.\

## For administration purposes

Run the app 
Open http://127.0.0.1:8000/admin to view it in the browser.
Login in with user: `admin` pass: `MCIproject`

## To update the frontend

If any changes are made to frontend, in order to reflect the changes on the backend server, in the `mapmangementplatform/frontend` directory, run the following command to compile the main.js file:
### `npm run dev`



## To Download the images

Run job under jobscheduler. The destination folder is: `mapmanagementplatform/backend/static/Images`

## QuadTree based nearest nighbors algorithm in action

Algorithm inserts and searches in O(k*Log<sub>4</sub>(n)) where k is the number of neighbors in domain.
![Nearest nighbours](https://github.cs.adelaide.edu.au/MCI-Projects-2021/Team-03/blob/New-Layers/nearest_neighbours.png)


