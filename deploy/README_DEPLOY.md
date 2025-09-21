# Deployment (NGINX + HTTPS)

## Prereqs
- Docker + Docker Compose on the server
- Domain pointing to server public IP

## Steps
1. Set env vars (`SECRET_KEY`, `QR_ALLOWED_DOMAINS`, `DATABASE_URL` if external DB)
2. Start services:
```bash
docker compose up -d --build
```
3. Run NGINX reverse proxy on the same host (as another container or host install):
```bash
# Example (host install)
sudo apt update && sudo apt install -y nginx
sudo cp deploy/nginx.conf /etc/nginx/nginx.conf
sudo systemctl restart nginx
```
4. HTTPS with Let's Encrypt (Certbot):
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your.domain
```

## Notes
- Proxy terminates TLS and forwards to backend on port 8000.
- Increase `client_max_body_size` if larger uploads are needed.
- Rotate `SECRET_KEY` and move credentials into a secure store.





