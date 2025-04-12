Running the Prompt Sentinel Dashboard
To run an example.
export PYTHONPATH=.

Enter the venv
source .sentinel/bin/activate

This document outlines the steps to start both the backend (server) and the frontend (client) for the Prompt Sentinel
# Running the Prompt Sentinel Dashboard

This document provides instructions on how to start the backend (server) and frontend (client) components of the Prompt Sentinel Dashboard.

## Starting the Server (Backend)

The backend is a FastAPI application that serves the API endpoints and interacts with the SQLite database.

1.  **Navigate to the Project Root:**
    *   Open your terminal.
    *   Change the directory to the root of your project (where `main.py` is located).

2.  **Install Dependencies:**
    *   Run the following command to install the required Python libraries:
bash pip install -r requirements.txt

3.  **Start the Server:**
    *   Execute the following command to start the FastAPI server:
bash uvicorn main:app --reload




*   This will start the server on `http://localhost:8000`. The `--reload` flag enables automatic reloading when you make changes to the code.

4. **Setting up the environment variable**
    * If you want to use postgres instead of sqlite, set the `DATABASE_URL` environment variable. example: `DATABASE_URL="postgresql://user:password@localhost/prompt_sentinel_db"`

## Starting the Client (Frontend)

The frontend is a React application that provides the user interface for the dashboard.

1.  **Navigate to the Frontend Directory:**
    *   In your terminal, navigate to the `frontend` directory:
    bash cd frontend


2.  **Install Dependencies:**
    *   Run the following command to install the required Node.js packages:
    npm install

3.  **Start the Development Server:**
    *   Execute the following command to start the React development server:
*   This will start the server, and the app will open in your browser (usually at `http://localhost:3000`).

bash npm start


## Accessing the Dashboard

Once both the server and the client are running, you can access the dashboard by opening your web browser and going to `http://localhost:3000`.

## Notes

*   Make sure you start the server before starting the client.
*   If you make changes to the backend code, the server will automatically reload because of the `--reload` flag.
*   If you make changes to the frontend code, the browser will automatically reload.
