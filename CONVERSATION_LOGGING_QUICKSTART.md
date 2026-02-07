# Panelin Conversation Logging System - Quick Start

This guide will help you get the Panelin Conversation Logging System up and running in minutes.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- Panelin Assistant ID

### Step 1: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
# Required variables:
# - OPENAI_API_KEY=your-openai-api-key
# - PANELIN_ASSISTANT_ID=asst_your_assistant_id
# - DB_PASSWORD=your_secure_database_password
```

### Step 2: Start the System

```bash
# Start all services (PostgreSQL + Backend API)
docker-compose up -d

# Wait for services to be ready (about 10 seconds)
docker-compose ps

# Check health
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

### Step 3: Test the Chat Integration

```bash
# Set backend URL (if not in .env)
export PANELIN_BACKEND_URL=http://localhost:8000

# Start chatting with Panelin
python chat_with_panelin.py
```

The chat will now:
- ✅ Log every conversation to the database
- ✅ Record all messages (user and assistant)
- ✅ Track user information
- ✅ Enable full conversation history access

### Step 4: View Conversations

#### Via API

List all conversations:
```bash
curl http://localhost:8000/api/conversations
```

Get messages for a specific conversation:
```bash
# Replace {conversation_id} with actual ID from list
curl http://localhost:8000/api/conversations/{conversation_id}/messages
```

Export a conversation:
```bash
curl http://localhost:8000/api/conversations/{conversation_id}/export?format=json
```

Get analytics:
```bash
curl http://localhost:8000/api/analytics/summary
```

#### Via Database

Connect directly to PostgreSQL:
```bash
docker-compose exec postgres psql -U panelin -d panelin_conversations

# List recent conversations
SELECT id, thread_id, user_name, created_at, status 
FROM conversations 
ORDER BY created_at DESC 
LIMIT 10;

# View messages for a conversation
SELECT role, content, created_at 
FROM messages 
WHERE thread_id = 'thread_xxx' 
ORDER BY created_at;

# Exit psql
\q
```

## 📊 API Endpoints Reference

### Conversations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/conversations` | Create new conversation |
| GET | `/api/conversations` | List all conversations |
| GET | `/api/conversations/{id}/messages` | Get conversation messages |
| GET | `/api/conversations/{id}/export` | Export conversation (JSON/CSV) |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/summary` | Get analytics summary |
| GET | `/health` | Health check |

### Query Parameters

**List conversations** (`GET /api/conversations`):
- `user_type` - Filter by user type (customer/sales_agent)
- `status` - Filter by status (active/completed/archived)
- `limit` - Max results (default: 50)
- `offset` - Pagination offset (default: 0)

## 🔧 Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Port 8000 already in use
docker-compose down
sudo lsof -i :8000  # Find what's using port 8000
# Kill that process or change port in docker-compose.yml

# 2. Database connection issues
docker-compose logs postgres
# Ensure PostgreSQL is healthy before backend starts
```

### Database connection errors

```bash
# Verify database is running
docker-compose exec postgres pg_isready -U panelin

# If not ready, restart services
docker-compose restart postgres
docker-compose restart backend
```

### Chat doesn't log conversations

```bash
# 1. Check backend is accessible
curl http://localhost:8000/health

# 2. Verify environment variable
echo $PANELIN_BACKEND_URL

# 3. Check backend logs for errors
docker-compose logs -f backend
```

## 🛠️ Development

### Run Backend Locally (without Docker)

```bash
# Install dependencies
pip install -r panelin_backend/requirements.txt

# Set DATABASE_URL
export DATABASE_URL="postgresql://panelin:changeme@localhost:5432/panelin_conversations"

# Run with auto-reload
uvicorn panelin_backend.main:app --reload
```

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx==0.24.1

# Run all tests
pytest panelin_backend/tests/ -v

# Run specific test file
pytest panelin_backend/tests/test_api.py -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
```

## 📈 Production Deployment

See [DEPLOYMENT.md](panelin_backend/DEPLOYMENT.md) for detailed production deployment guides covering:

- **Render.com** (Easiest, $15-30/month)
- **DigitalOcean App Platform** ($20/month)
- **AWS** (Most scalable, $65-100/month)
- **Self-Hosted VPS** (Most economical, $10-20/month)

## 🔒 Security Best Practices

1. **Use strong database passwords**
   ```bash
   # Generate secure password
   openssl rand -base64 32
   ```

2. **Never commit .env files**
   ```bash
   # Ensure .env is in .gitignore
   echo ".env" >> .gitignore
   ```

3. **Use HTTPS in production**
   - Configure SSL/TLS certificates
   - Use reverse proxy (Nginx, Traefik)

4. **Regular backups**
   ```bash
   # Backup database
   docker-compose exec postgres pg_dump -U panelin panelin_conversations > backup.sql
   
   # Restore from backup
   docker-compose exec -T postgres psql -U panelin panelin_conversations < backup.sql
   ```

## 📝 Example Usage

### Create Conversation via API

```bash
curl -X POST http://localhost:8000/api/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "thread_abc123",
    "assistant_id": "asst_xyz789",
    "user_name": "John Doe",
    "user_type": "customer"
  }'
```

### Add Message via API

```bash
curl -X POST http://localhost:8000/api/conversations/{conversation_id}/messages \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "thread_abc123",
    "message_id": "msg_123",
    "role": "user",
    "content": "Hello, I need a quote for BMC panels",
    "created_at": "2024-01-01T12:00:00"
  }'
```

## 🎯 Next Steps

1. **Customize the system**
   - Modify database schema for your needs
   - Add custom analytics
   - Implement export to PDF/CSV

2. **Add authentication**
   - Implement JWT tokens
   - Add API key validation
   - Secure endpoints

3. **Build a dashboard**
   - Create web UI for viewing conversations
   - Add search and filtering
   - Visualize analytics

4. **Integrate with other systems**
   - Connect to CRM
   - Send notifications
   - Generate reports

## 📚 Additional Resources

- [README.md](panelin_backend/README.md) - Full documentation
- [DEPLOYMENT.md](panelin_backend/DEPLOYMENT.md) - Production deployment guide
- [OpenAI Assistants API](https://platform.openai.com/docs/assistants/overview) - Official docs

## 💬 Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review [Troubleshooting](#-troubleshooting) section
3. Run tests: `pytest panelin_backend/tests/`
4. Open an issue on GitHub

---

**🎉 Congratulations!** You now have a complete conversation logging system for Panelin GPT with full API access and database persistence.
