# Authenticity Validator for Academia (Jharkhand)

Run locally (Docker):

```bash
docker compose up -d --build
# App: http://localhost:8000/
# Admin UI: http://localhost:8000/admin-ui (admin/admin123)
# Metrics: http://localhost:8000/metrics
```

Demo dataset:
- Import via Admin UI bulk upload or use Postman collection under `postman/`.
- File: `data/demo_certificates.csv`.

Environment:
- `SECRET_KEY` (required in prod)
- `DATABASE_URL` (defaults to SQLite; compose uses Postgres)
- `QR_ALLOWED_DOMAINS` for QR URL allowlist

Deployment (NGINX reverse proxy):
- Terminate TLS at NGINX, proxy to `backend:8000`.
- Add rate limiting and size limits at proxy (e.g., `limit_req`, `client_max_body_size`).

Next:
- Replace demo admin with user store, rotate keys, and add proper RBAC.





