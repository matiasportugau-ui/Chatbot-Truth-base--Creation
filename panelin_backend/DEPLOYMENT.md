# Production Deployment Guide

## Option 1: Render.com (Recommended - Easy)

### Steps

1. **Create Render Account**
   - Sign up at [render.com](https://render.com)

2. **Create PostgreSQL Database**
   - Go to Dashboard → New → PostgreSQL
   - Name: `panelin-conversations-db`
   - Region: Choose closest to your users
   - Plan: Starter ($7/month)
   - Save the Internal Database URL

3. **Create Web Service**
   - Go to Dashboard → New → Web Service
   - Connect your GitHub repository
   - Name: `panelin-backend`
   - Region: Same as database
   - Branch: `main`
   - Root Directory: Leave empty
   - Runtime: Python 3
   - Build Command: `pip install -r panelin_backend/requirements.txt`
   - Start Command: `uvicorn panelin_backend.main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**
   - `DATABASE_URL`: Use Internal Database URL from step 2
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `PANELIN_ASSISTANT_ID`: Your assistant ID

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Your API will be available at: `https://panelin-backend.onrender.com`

6. **Update Chat Script**
   - Set `PANELIN_BACKEND_URL=https://panelin-backend.onrender.com` in your environment

### Cost
- PostgreSQL: $7/month
- Web Service: $7-25/month (depending on usage)
- **Total: ~$15-30/month**

---

## Option 2: DigitalOcean App Platform

### Steps

1. **Create DigitalOcean Account**
   - Sign up at [digitalocean.com](https://www.digitalocean.com/)

2. **Create App from GitHub**
   - Go to Apps → Create App
   - Select GitHub repository
   - Select branch and directory

3. **Add PostgreSQL Database Component**
   - Click "Add Component" → Database
   - Type: PostgreSQL
   - Plan: Basic ($7/month)

4. **Configure App**
   - Build Command: `pip install -r panelin_backend/requirements.txt`
   - Run Command: `uvicorn panelin_backend.main:app --host 0.0.0.0 --port $PORT`

5. **Add Environment Variables**
   - Same as Render.com

6. **Deploy**

### Cost
- Database: $7/month
- App: $12/month
- **Total: ~$20/month**

---

## Option 3: AWS (Scalable)

### Components

- **ECS Fargate**: For Docker containers
- **RDS PostgreSQL**: For database
- **ALB**: Load balancer

### Steps

1. **Create RDS PostgreSQL**
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier panelin-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username panelin \
     --master-user-password <strong-password> \
     --allocated-storage 20
   ```

2. **Push Docker Image to ECR**
   ```bash
   aws ecr create-repository --repository-name panelin-backend
   docker build -t panelin-backend ./panelin_backend
   docker tag panelin-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/panelin-backend:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/panelin-backend:latest
   ```

3. **Create ECS Cluster and Service**
   - Use AWS Console or CloudFormation
   - Configure task definition with environment variables
   - Set up ALB for load balancing

### Cost
- RDS PostgreSQL (t3.micro): ~$15/month
- ECS Fargate: ~$30/month
- ALB: ~$20/month
- **Total: ~$65-100/month**

---

## Option 4: Self-Hosted VPS

### Recommended Providers
- DigitalOcean Droplets
- Linode
- Vultr

### Steps

1. **Provision Ubuntu VPS**
   - Ubuntu 22.04 LTS
   - 2GB RAM minimum
   - $10-20/month

2. **Install Docker and Docker Compose**
   ```bash
   # SSH into VPS
   ssh root@your-vps-ip
   
   # Update system
   apt update && apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Install Docker Compose
   apt install docker-compose -y
   ```

3. **Clone Repository**
   ```bash
   git clone https://github.com/your-repo/Chatbot-Truth-base--Creation.git
   cd Chatbot-Truth-base--Creation
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your values
   ```

5. **Start Services**
   ```bash
   docker-compose up -d
   ```

6. **Setup Nginx Reverse Proxy (Optional)**
   ```nginx
   server {
       listen 80;
       server_name api.yourdomain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

7. **Setup SSL with Let's Encrypt**
   ```bash
   apt install certbot python3-certbot-nginx
   certbot --nginx -d api.yourdomain.com
   ```

### Cost
- VPS: $10-20/month
- **Total: ~$10-20/month**

---

## Security Best Practices

### 1. Use Strong Passwords
```bash
# Generate strong database password
openssl rand -base64 32
```

### 2. Enable SSL/TLS
- Use HTTPS for all API endpoints
- Configure SSL certificates (Let's Encrypt is free)

### 3. Firewall Configuration
```bash
# Allow only necessary ports
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

### 4. Regular Backups
```bash
# Automated PostgreSQL backups
docker-compose exec postgres pg_dump -U panelin panelin_conversations > backup.sql
```

### 5. Environment Variables
- Never commit `.env` files
- Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)

---

## Monitoring and Maintenance

### Health Checks
```bash
# Check API health
curl https://your-api-url/health

# Check database
docker-compose exec postgres pg_isready -U panelin
```

### Logs
```bash
# View backend logs
docker-compose logs -f backend

# View database logs
docker-compose logs -f postgres
```

### Updates
```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose down
docker-compose up -d --build
```

---

## Scaling Considerations

### When to Scale

- **Database**: When queries slow down (>100ms)
- **API**: When response times increase (>500ms)
- **Storage**: Monitor disk usage

### Horizontal Scaling

1. **Database**: Use read replicas
2. **API**: Add more backend instances behind load balancer
3. **Caching**: Add Redis for frequently accessed data

### Vertical Scaling

- Upgrade VPS/instance sizes
- Increase database resources
- Add more CPU/RAM

---

## Cost Comparison Summary

| Option | Monthly Cost | Complexity | Best For |
|--------|-------------|------------|----------|
| Render.com | $15-30 | Low | Quick deployment |
| DigitalOcean App | $20 | Low | Balanced option |
| AWS | $65-100 | High | Enterprise/Scale |
| Self-Hosted VPS | $10-20 | Medium | Cost-conscious |

---

## Support

For deployment issues:
1. Check logs: `docker-compose logs`
2. Verify environment variables
3. Test database connection
4. Check firewall rules

For production support, consider:
- Uptime monitoring (UptimeRobot, Pingdom)
- Error tracking (Sentry)
- Log aggregation (Papertrail, LogDNA)
