# Self-Hosted Deployment — Knowledge OS Core v1

This guide covers deploying Knowledge OS Core on a self-hosted server using Docker Compose and Caddy.

## Prerequisites

- Docker Engine 24.0+
- Docker Compose v2.20+
- A domain name (optional, for HTTPS)
- 2GB RAM minimum (4GB recommended)
- 20GB disk space

## Quick Start

### 1. Clone or extract the project

```bash
git clone https://github.com/your-repo/knowledge-os.git
cd knowledge-os
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set POSTGRES_PASSWORD to a strong value
```

### 3. Start the stack

```bash
docker-compose up -d
```

### 4. Verify services

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs -f app-api
docker-compose logs -f worker-runtime

# Test API health
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"0.1.0"}

# Test Caddy routing
curl http://localhost/api/health
# Expected: same as above
```

### 5. Run database migrations

```bash
docker-compose exec app-api alembic upgrade head
```

## Services

### app-api (FastAPI)
- **Port**: 8000 (internal), routed via Caddy
- **Health**: `GET /health`
- **API**: `GET /api/*`
- **Logs**: `docker-compose logs -f app-api`

### worker-runtime (Background Jobs)
- **Processes**: Job queue consumers
- **Scaling**: Run `docker-compose up -d --scale worker-runtime=2` for multiple workers
- **Logs**: `docker-compose logs -f worker-runtime`

### postgres (PostgreSQL 16 + pgvector)
- **Port**: 5432 (exposed, change in production)
- **Database**: knowledge_os
- **Extensions**: pgvector, pg_trgm, unaccent

### caddy (Reverse Proxy)
- **HTTP**: Port 80
- **HTTPS**: Port 443 (automatic Let's Encrypt)
- **HTTP/3**: Port 443/udp

## Production Deployment

### 1. Domain and DNS

Point your domain's A record to your server's IP address:

```
A记录的名称 @
值 YOUR_SERVER_IP
```

### 2. Update Caddyfile

Edit `Caddyfile` and uncomment the production block:

```caddy
:443, your-domain.com {
    reverse_proxy /api/* app-api:8000
    reverse_proxy /sse/* app-api:8000
    reverse_proxy /* app-api:8000

    tls {
        dns cloudflare {env.CLOUDFLARE_API_TOKEN}
    }

    # ... rest of production config
}
```

### 3. Enable HTTPS

Caddy automatically obtains and renews Let's Encrypt certificates using the Cloudflare DNS challenge.

Set `CLOUDFLARE_API_TOKEN` in your `.env` file.

### 4. Secure the database

```bash
# Change the postgres password
docker-compose exec postgres psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'your_strong_password'"

# Update .env
POSTGRES_PASSWORD=your_strong_password
```

### 5. Firewall configuration

```bash
# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 443/udp  # HTTP/3

# If exposing SSH
ufw allow 22/tcp
```

### 6. Backup strategy

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres knowledge_os > backup_$(date +%Y%m%d).sql

# Backup workspace
tar -czf workspace_backup_$(date +%Y%m%d).tar.gz workspace/
```

## Scaling

### Multiple workers

```bash
# Scale to 3 workers
docker-compose up -d --scale worker-runtime=3
```

Workers automatically claim jobs from the shared Postgres queue — no additional coordination needed.

### Horizontal API scaling

```bash
# Scale to 2 API instances (requires load balancer)
docker-compose up -d --scale app-api=2
```

Note: Currently only one API instance should run Alembic migrations.

## Troubleshooting

### API returns 502

```bash
# Check if app-api is running
docker-compose ps app-api

# Check app-api logs
docker-compose logs app-api

# Check health endpoint directly
curl http://localhost:8000/health
```

### Worker not processing jobs

```bash
# Check worker logs
docker-compose logs worker-runtime

# Check for errors
docker-compose logs worker-runtime | grep ERROR

# Verify database connection
docker-compose exec worker-runtime python -c "import asyncio; from src.db.database import engine; asyncio.run(engine.connect())"
```

### Database connection errors

```bash
# Check postgres is running
docker-compose ps postgres

# Check postgres logs
docker-compose logs postgres

# Verify connection from app-api
docker-compose exec app-api python -c "import asyncio; from src.db.database import engine; asyncio.run(engine.connect())"
```

### Caddy not routing HTTPS

```bash
# Check Caddy logs
docker-compose logs caddy

# Validate Caddyfile
docker-compose exec caddy caddy validate --config /etc/caddy/Caddyfile

# Check port bindings
ss -tlnp | grep -E '80|443'
```

## Updating

```bash
# Pull latest changes
git pull

# Rebuild images
docker-compose build

# Restart services
docker-compose up -d

# Run any new migrations
docker-compose exec app-api alembic upgrade head
```

## Uninstall

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: destroys all data)
docker-compose down -v

# Remove images
docker-compose rmi
```
