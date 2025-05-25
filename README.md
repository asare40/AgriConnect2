# AgriConnect

## Backend (FastAPI)

1. Install dependencies:
   ```
   pip install -r backend/requirements.txt
   ```

2. Place your trained ML model (`your_model.joblib`) in the `backend/` directory.

3. Start the backend:
   ```
   uvicorn backend.api:app --reload
   ```

## Frontend (React)

1. Go to the frontend folder:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the frontend:
   ```
   npm start
   ```

The React app will run at [http://localhost:3000](http://localhost:3000) and will communicate with the FastAPI backend at [http://localhost:8000](http://localhost:8000).