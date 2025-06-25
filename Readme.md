# local keycloak localhost:8080
docker compose up --build

# FastApi app localhost:8000
cd fastapi-backend
uvicorn main:app --reload --port 8000

# Flask app localhost:5000
cd flask-frontend
python app.py

