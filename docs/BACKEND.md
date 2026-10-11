# Backend API

## Running

```powershell
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Access points:
- API: `http://127.0.0.1:8000/api`
- Health: `http://127.0.0.1:8000/health`
- Ready: `http://127.0.0.1:8000/health/ready`
- Docs (debug only): `http://127.0.0.1:8000/docs`

## API Endpoints

### Auth (`/api/auth`)
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/register` | None | Create account (if `ALLOW_REGISTRATION=true`) |
| POST | `/login` | None | Authenticate, returns JWT |
| POST | `/refresh` | None | Refresh access token |
| GET | `/me` | Bearer | Current user profile |

### Content (`/api/content`)
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/events` | Optional | List events (published only if no token) |
| GET | `/events/{id}` | Optional | Single event |
| POST | `/events` | Bearer | Create event |
| PATCH | `/events/{id}` | Bearer | Update event |
| DELETE | `/events/{id}` | Bearer | Delete event |
| POST | `/events/{id}/register` | Optional | Register for event |
| GET | `/projects` | Optional | List projects |
| GET | `/projects/{id}` | Optional | Single project |
| POST | `/projects` | Bearer | Create project |
| PATCH | `/projects/{id}` | Bearer | Update project |
| DELETE | `/projects/{id}` | Bearer | Delete project |
| GET | `/faculty` | Optional | List faculty |
| GET | `/faculty/{id}` | Optional | Single faculty |
| GET | `/staff` | Optional | List staff |
| GET | `/idealab-members` | Optional | List IdeaLab members |
| GET | `/equipment` | Optional | List active equipment |
| GET | `/equipment/{id}` | Optional | Single equipment |
| GET | `/documents` | Optional | List public documents |
| GET | `/documents/{id}` | Optional | Single document |
| GET | `/departments` | Bearer | List departments |
| GET | `/search?q=...` | Optional | Keyword search |

### AI Chat (`/api/ai`)
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/chat` | Optional | Send message, get AI response |

Request body:
```json
{
  "message": "What projects are working on computer vision?",
  "conversation_id": null,
  "use_search": true,
  "channel": "text"
}
```

Response:
```json
{
  "content": "Based on the IdeaLab projects...",
  "sources": [{"url": "...", "title": "..."}],
  "tool_calls": [],
  "conversation_id": "abc-123",
  "ai_available": true
}
```

### Admin (`/api/admin`)
| Method | Path | Permission | Description |
|---|---|---|---|
| GET | `/users` | `users.manage` | List all users |
| GET | `/users/{id}` | `users.manage` | Single user |
| PATCH | `/users/{id}` | `users.manage` | Update user |
| POST | `/users/{id}/reset-password` | `users.manage` | Reset password |
| GET | `/roles` | `roles.manage` | List roles |
| GET | `/roles/{id}` | `roles.manage` | Single role |
| POST | `/roles/{id}/permissions` | `roles.manage` | Assign permissions |
| GET | `/permissions` | `roles.manage` | List permissions |
| GET | `/audit-logs` | `audit.read` | Audit log |
| GET | `/settings` | `system.settings.manage` | System settings |
| PATCH | `/settings/{key}` | `system.settings.manage` | Update setting |

### Devices (`/api/devices`)
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/register` | Device token | ESP32 robot registration |
| POST | `/status` | Device token | Robot status update |
| POST | `/ping` | Device token | Robot heartbeat |
| POST | `/chat` | Device token | Voice chat via robot |
| POST | `/config` | Device token | Robot configuration |

## Configuration

All settings in `backend/.env`:

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | change-me | JWT signing key (generate random) |
| `DATABASE_URL` | postgresql+asyncpg://... | Database connection |
| `GEMINI_API_KEY` | (empty) | Google Gemini API key |
| `OLLAMA_BASE_URL` | http://127.0.0.1:11434 | Ollama server URL |
| `EMBEDDING_PROVIDER` | ollama | ollama or gemini |
| `ALLOW_REGISTRATION` | true | Enable self-signup |
| `CORS_ORIGINS` | localhost:5173,... | Allowed origins |
| `RATE_LIMIT_AUTH` | 20/minute | Auth endpoint limit |
| `RATE_LIMIT_CHAT` | 30/minute | Chat endpoint limit |

## Testing

```powershell
cd backend
python -m pytest
```

56 tests covering: health, auth, content, admin, security, password reset.