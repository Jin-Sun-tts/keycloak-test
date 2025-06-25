local keycloak localhost:8080
```bash
docker compose up --build
```

FastApi app localhost:8000
```bash
cd fastapi-backend
uvicorn main:app --reload --port 8000
```

Flask app localhost:5000
```bash
cd flask-frontend
python app.py
```

