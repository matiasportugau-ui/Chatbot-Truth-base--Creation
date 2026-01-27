# Panelin Configuration Guide

This document describes the environment variables used by the Panelin system.

## Setup

1. Copy `.env.example` to `.env`.
2. Fill in the required values.
3. The system uses `python-dotenv` to load these variables at runtime.

## Environment Variables

### AI Providers

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key. | Yes |
| `OPENAI_ASSISTANT_ID` | The ID of the OpenAI Assistant to use. | Yes (for Assistant API) |
| `ANTHROPIC_API_KEY` | Your Anthropic API key (for Claude models). | No |
| `GOOGLE_API_KEY` | Your Google AI API key (for Gemini models). | No |

### Google Sheets Integration

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_SHEETS_CREDENTIALS` | Path to the service account JSON credentials file. | Yes (for Sheets sync) |

### Persistence

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_CONNECTION_STRING` | Connection string for MongoDB. | `mongodb://localhost:27017` |
| `MONGODB_DATABASE_NAME` | Name of the database to use. | `panelin` |

### Social Media APIs

#### Facebook
| Variable | Description |
|----------|-------------|
| `FACEBOOK_APP_ID` | Facebook App ID. |
| `FACEBOOK_APP_SECRET` | Facebook App Secret. |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | Access token for the Facebook Page. |
| `FACEBOOK_PAGE_ID` | ID of the Facebook Page. |
| `FACEBOOK_API_VERSION` | Version of the Facebook Graph API (default: `v18.0`). |

#### Instagram
| Variable | Description |
|----------|-------------|
| `INSTAGRAM_APP_ID` | Instagram App ID. |
| `INSTAGRAM_APP_SECRET` | Instagram App Secret. |
| `INSTAGRAM_ACCESS_TOKEN` | Access token for the Instagram account. |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | ID of the Instagram Business Account. |
| `INSTAGRAM_API_VERSION` | Version of the Instagram API (default: `v18.0`). |

#### MercadoLibre
| Variable | Description |
|----------|-------------|
| `MERCADOLIBRE_ACCESS_TOKEN` | Access token for MercadoLibre API. |
| `MERCADOLIBRE_USER_ID` | Your MercadoLibre User ID. |

### Project Paths

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECT_ROOT` | Absolute path to the root of the project. | `.` (Current directory) |
| `KB_PATH` | Path to the Knowledge Base files directory. | `Files` |

## Validation

The system performs basic validation of critical variables on startup. Ensure that at least `OPENAI_API_KEY` is set for the core functionality to work.
