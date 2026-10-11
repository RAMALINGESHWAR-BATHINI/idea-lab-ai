# Security

## Threat Model

IdeaLab AI handles student data, faculty records, and institutional documents. The security model addresses:

1. **Authentication** — who are you?
2. **Authorization** — what can you do?
3. **Input Validation** — what are you sending?
4. **Output Encoding** — what are we returning?
5. **Audit** — what happened?

## Authentication

### JWT (HS256)
- Access token: 720 minutes expiry
- Refresh token: stored in `localStorage`
- Algorithm: `HS256` (symmetric)
- Secret key: must be 48+ random characters

### Password Hashing
- Algorithm: bcrypt
- Minimum password length: 8 characters
- Salt per user (built-in to bcrypt)

### Registration
- Controlled by `ALLOW_REGISTRATION` flag
- Can be disabled for invite-only mode
- Invitation codes can grant specific roles

## RBAC (Role-Based Access Control)

### Default Roles (14)
| Role | Permissions |
|---|---|
| `superuser` | All permissions |
| `admin` | Content + user management |
| `faculty` | View own content, edit projects |
| `staff` | View content, limited edits |
| `student` | View public content |
| `idealab_member` | View internal content |
| `contributor` | Create content |
| `chief_mentor` | Mentor permissions |
| `faculty_coordinator` | Event coordination |
| `tech_guru` | Equipment management |
| `student_coordinator` | Student coordination |
| `student_ambassador` | Public representation |
| `public_visitor` | Public access only |
| `guest` | Minimal access |

### Default Permissions (40)
- `content.*` — Create, read, update, delete content
- `users.manage` — User management
- `roles.manage` — Role management
- `system.settings.manage` — System configuration
- `audit.read` — View audit logs
- `devices.register` — Register devices
- `devices.manage` — Manage devices
- `invitations.manage` — Manage invitation codes
- `access_grants.manage` — Manage access grants

## SSRF Protection

All external requests are guarded:
- Private IP ranges blocked (10.x, 172.16-31.x, 192.168.x, 127.x, 169.254.x, ::1, fc00::/7)
- Configurable via `SSRF_ALLOW_PRIVATE_HOSTS`
- Timeout: 15 seconds
- Max redirect: 3
- Max response size: 5MB

## Prompt Injection Defense

All LLM inputs are sanitized:
1. System prompt is fenced with `### SYSTEM` / `### END SYSTEM`
2. User input is labeled `### USER` / `### END USER`
3. Tool outputs are labeled `### TOOL OUTPUT` / `### END TOOL OUTPUT`
4. Instructions in user input are treated as data, not commands

## Rate Limiting

Uses `slowapi` with per-endpoint limits:
- Auth endpoints: 20/minute (per IP)
- Chat endpoints: 30/minute (per user)
- Default: 120/minute (per IP)

## Audit Trail

All security-relevant actions are logged:
- Login/logout
- Content creation/modification
- Permission changes
- Admin actions
- Errors

Logs are append-only and stored in `audit_logs` table.

## Security Headers

All responses include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Strict-Transport-Security` (production only)

## CORS

Configurable via `CORS_ORIGINS`:
- Default: `http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174`
- Credentials allowed
- All methods allowed