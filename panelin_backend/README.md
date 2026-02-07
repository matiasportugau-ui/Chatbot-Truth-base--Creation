# Panelin Conversation Logging System

Complete conversation logging and management system for Panelin GPT.

## Features

- ✅ Full conversation logging (all messages stored)
- ✅ User and sales agent tracking
- ✅ Real-time message capture
- ✅ Analytics and reporting
- ✅ Export capabilities (JSON/CSV)
- ✅ RESTful API
- ✅ Docker deployment ready

## Quick Start

### 1. Setup Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 2. Start Services

```bash
docker-compose up -d
```

### 3. Initialize Database

Database will auto-initialize from schema.sql on first run.

### 4. Test API

```bash
curl http://localhost:8000/health
```

### 5. Use with chat_with_panelin.py

```bash
export PANELIN_BACKEND_URL=http://localhost:8000
python chat_with_panelin.py
```

## API Endpoints

### Conversations

- `POST /api/conversations` - Create new conversation
- `GET /api/conversations` - List conversations (with filters)
- `GET /api/conversations/{id}/messages` - Get conversation messages
- `GET /api/conversations/{id}/export` - Export conversation

### Analytics

- `GET /api/analytics/summary` - Get analytics summary

## Database Access

View conversations directly:

```bash
docker-compose exec postgres psql -U panelin -d panelin_conversations

# List all conversations
SELECT * FROM conversations ORDER BY created_at DESC LIMIT 10;

# View messages for a conversation
SELECT * FROM messages WHERE thread_id = 'thread_xxx' ORDER BY created_at;
```

## Environment Variables

Required environment variables:

- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key
- `PANELIN_BACKEND_URL` - Backend API URL (for chat integration)
- `DB_PASSWORD` - Database password

## Development

### Install Dependencies

```bash
cd panelin_backend
pip install -r requirements.txt
```

### Run Locally

```bash
export DATABASE_URL="postgresql://panelin:changeme@localhost:5432/panelin_conversations"
uvicorn panelin_backend.main:app --reload
```

### Run Tests

```bash
pytest panelin_backend/tests/
```

## Production Deployment

See `DEPLOYMENT.md` for production setup instructions.

## Architecture

```
┌─────────────────┐
│ chat_with_      │
│ panelin.py      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ FastAPI Backend │
│ (REST API)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PostgreSQL DB   │
│ (Conversations) │
└─────────────────┘
```

## Troubleshooting

### Database Connection Issues

1. Ensure PostgreSQL is running: `docker-compose ps`
2. Check database credentials in `.env`
3. Verify DATABASE_URL format

### API Connection Issues

1. Check backend is running: `curl http://localhost:8000/health`
2. Verify PANELIN_BACKEND_URL in environment
3. Check logs: `docker-compose logs backend`

## License

See main repository LICENSE file.
