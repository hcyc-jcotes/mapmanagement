# Map Management - Team 03 

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

## To install the ReactJS server

To install the frontend and run it locally. Go in the `mapmangementplatform/frontend` directory and run:
### `npm install`

## To update the ReactJS server

If any changes are made to frontend, in order to reflect the changes on the backend server, in the `mapmangementplatform/frontend` directory, run the following command to compile the main.js file:
### `npm run dev`

## For administration purposes

Run the app 
Open http://127.0.0.1:8000/admin to view it in the browser.
Login in with user: `admin` pass: `MCIproject`

## To Fetch information from Mapillary

Run job under jobscheduler in http://127.0.0.1:8000/admin. Be sure to have added a region before, the job will perform the following activities in order:
1. Fetch the users and sequences.
2. Calculate the direction for all the points.
3. Populate the neighbours.
4. Download the images.


