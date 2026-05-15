# Deployment Guide

Deployment instructions for various platforms and environments.

## Overview

MasterDataCleaner can be deployed in multiple configurations:

| Deployment Type | Description | Best For |
|----------------|-------------|----------|
| **Docker** | Containerized deployment | Production, consistent environments |
| **Single Server** | Traditional VPS deployment | Small teams, cost-effective |
| **Cloud Platform** | PaaS deployment (Koyeb, Railway, etc.) | Easy scaling, managed infrastructure |
| **Kubernetes** | Container orchestration | Large-scale, high availability |

## Prerequisites

For all deployment types, you'll need:

- **Git** - For cloning the repository
- **Environment variables** - Configuration for database, API keys, etc.
- **Domain name** (optional) - For production access

## Docker Deployment

### Docker Compose (Recommended)

The easiest way to deploy MasterDataCleaner.

**1. Clone Repository:**
```bash
git clone https://github.com/bitsnaps/MasterDataCleaner.git
cd MasterDataCleaner
```

**2. Create Environment File:**
```bash
cp backend/.env.sample backend/.env
```

Edit `backend/.env`:
```env
# App
SECRET_KEY=<generate-random-key>
DEBUG=false
FRONTEND_URL=https://your-domain.com

# Database
DATABASE_URL=postgresql://user:password@db:5432/masterdatacleaner

# AI Providers
OPENAI_API_KEY=sk-...

# Admin
ADMIN_USER=admin@example.com
ADMIN_PASSWORD=<secure-password>
```

**3. Start Services:**
```bash
docker-compose up -d
```

**4. Verify Deployment:**
```bash
docker-compose ps
docker-compose logs -f
```

**Services:**
- **web** - Frontend (port 3000)
- **api** - Backend API (port 8000)
- **db** - PostgreSQL database (port 5432)

### Docker Production Build

**Build Images:**
```bash
docker-compose build
```

**Deploy:**
```bash
docker-compose up -d
```

**Update:**
```bash
git pull
docker-compose build
docker-compose up -d
```

### Docker Environment Variables

```yaml
# docker-compose.yml
services:
  api:
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/masterdatacleaner
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - FRONTEND_URL=${FRONTEND_URL}
  
  web:
    environment:
      - VITE_API_URL=http://api:8000
```

## Single Server Deployment

### Ubuntu/Debian Server

**1. Install Dependencies:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install pnpm
npm install -g pnpm

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Nginx
sudo apt install -y nginx
```

**2. Clone Repository:**
```bash
cd /var/www
sudo git clone https://github.com/bitsnaps/MasterDataCleaner.git
sudo chown -R $USER:$USER MasterDataCleaner
cd MasterDataCleaner
```

**3. Setup Database:**
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE masterdatacleaner;
CREATE USER masterdatacleaner_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE masterdatacleaner TO masterdatacleaner_user;
\q
```

**4. Setup Backend:**
```bash
cd backend

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.sample .env
nano .env  # Edit configuration
```

**5. Setup Frontend:**
```bash
cd ..

# Install dependencies
pnpm install

# Build for production
pnpm build
```

**6. Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/masterdatacleaner
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /var/www/MasterDataCleaner/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/masterdatacleaner /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**7. Setup Systemd Services:**

Backend service:
```bash
sudo nano /etc/systemd/system/masterdatacleaner-api.service
```

```ini
[Unit]
Description=MasterDataCleaner API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/MasterDataCleaner/backend
Environment="PATH=/var/www/MasterDataCleaner/backend/.venv/bin"
ExecStart=/var/www/MasterDataCleaner/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable masterdatacleaner-api
sudo systemctl start masterdatacleaner-api
sudo systemctl status masterdatacleaner-api
```

**8. Setup SSL (Optional but Recommended):**
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Cloud Platform Deployment

### Koyeb

**1. Create Account:**
- Sign up at https://www.koyeb.com

**2. Deploy Backend:**
- Create new service
- Connect GitHub repository
- Set build command: `pip install -r backend/requirements.txt`
- Set start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Set working directory: `backend`
- Add environment variables

**3. Deploy Frontend:**
- Create new service
- Set build command: `pnpm install && pnpm build`
- Set start command: `pnpm preview`
- Add environment variables

**4. Add Database:**
- Create managed PostgreSQL database
- Add connection string to environment variables

### Railway

**1. Create Account:**
- Sign up at https://railway.app

**2. Deploy from GitHub:**
- Connect repository
- Railway auto-detects services

**3. Configure:**
- Add environment variables
- Provision PostgreSQL database
- Deploy

### Render

**1. Create Account:**
- Sign up at https://render.com

**2. Deploy Backend:**
- Create Web Service
- Connect repository
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

**3. Deploy Frontend:**
- Create Static Site
- Root directory: `.`
- Build command: `pnpm install && pnpm build`
- Publish directory: `dist`

**4. Add Database:**
- Create PostgreSQL database
- Add connection string to environment

## Environment Variables

### Required Variables

```env
# Application
SECRET_KEY=<generate-with: openssl rand -hex 32>
DEBUG=false
FRONTEND_URL=https://your-domain.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# Admin (optional)
ADMIN_USER=admin@example.com
ADMIN_PASSWORD=<secure-password>
```

### AI Provider Variables (Optional)

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
GROQ_API_KEY=...
NVIDIA_API_KEY=...
DEEPSEEK_API_KEY=...
OPENROUTER_API_KEY=...
```

### OAuth Variables (Optional)

```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
```

## Database Setup

### PostgreSQL Configuration

**Production Settings:**
```env
DATABASE_URL=postgresql://user:password@host:5432/masterdatacleaner?sslmode=require

# Connection pool settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
```

**SSL Mode:**
- Production: `sslmode=require`
- Development: omit or `sslmode=disable`

### Database Migrations

Migrations run automatically on startup. To run manually:

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

## Security Considerations

### Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Generate secure `SECRET_KEY`
- [ ] Use strong database password
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Enable database backups
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Review rate limits

### Firewall Configuration

**Required Ports:**
- **80** - HTTP (redirect to HTTPS)
- **443** - HTTPS
- **5432** - PostgreSQL (internal only)

**UFW Configuration (Ubuntu):**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Monitoring & Logging

### Application Logs

**Backend Logs:**
```bash
# Docker
docker-compose logs -f api

# Systemd
journalctl -u masterdatacleaner-api -f
```

### Database Logs

```bash
# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Health Check

```bash
curl https://your-domain.com/api/health
```

Expected response:
```json
{
  "status": "healthy"
}
```

## Backup & Recovery

### Database Backup

**PostgreSQL:**
```bash
# Backup
pg_dump -U user -h host masterdatacleaner > backup_$(date +%Y%m%d).sql

# Restore
psql -U user -h host masterdatacleaner < backup_20240101.sql
```

**Automated Backups (Cron):**
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * pg_dump -U user masterdatacleaner > /backups/backup_$(date +\%Y\%m\%d).sql
```

### File Backups

Backup important files:
- `.env` - Configuration
- `alembic/versions/` - Database migrations
- Custom agent configurations

## Scaling

### Horizontal Scaling

**Multiple API Instances:**
```bash
# Docker Compose
docker-compose up -d --scale api=3
```

**Load Balancer Configuration:**
```nginx
upstream api_servers {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    location /api {
        proxy_pass http://api_servers;
    }
}
```

### Vertical Scaling

**Increase Resources:**
- More CPU cores
- More RAM
- Faster database

**Database Optimization:**
```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_datasets_project_id ON datasets(project_id);
```

## Troubleshooting

### Common Issues

**Database Connection Failed:**
```bash
# Check database is running
docker-compose ps db

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL
```

**API Not Starting:**
```bash
# Check logs
docker-compose logs api

# Check port is free
lsof -i :8000

# Check environment variables
docker-compose exec api env
```

**Frontend Not Loading:**
```bash
# Check build completed
ls -la dist/

# Check Nginx config
nginx -t

# Check Nginx logs
tail -f /var/log/nginx/error.log
```

### Performance Issues

**Slow Queries:**
```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();
```

**High Memory Usage:**
- Reduce batch sizes
- Limit operation history
- Optimize connection pool

## Update Procedure

### Docker Deployment

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Run migrations (if needed)
docker-compose exec api alembic upgrade head
```

### Single Server

```bash
# Pull latest changes
cd /var/www/MasterDataCleaner
git pull

# Update backend
cd backend
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# Restart service
sudo systemctl restart masterdatacleaner-api

# Update frontend (if changed)
cd ..
pnpm install
pnpm build
```

## Next Steps

- **[Architecture](../architecture/README.md)** - System architecture details
- **[Backend](../backend/README.md)** - Backend configuration
- **[Guides](../guides/README.md)** - Usage guides

---

*Part of the [MasterDataCleaner Documentation](../README.md)*
