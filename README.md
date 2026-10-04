# RefundOS Frontend

Premium React + TypeScript + Tailwind CSS frontend for the banking refund assessment system.

## Stack

- React + TypeScript
- Vite
- Tailwind CSS
- React Router
- Axios
- Lucide React

## Run

```bash
cp .env.example .env
npm install
npm run dev
```

Frontend: http://localhost:3000

Backend expected at:

`http://localhost:8000/api/v1`

## Expected API contract

### Auth

- `POST /auth/login`
- `POST /auth/signup`

Expected response:

```json
{
  "access_token": "jwt",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "Jane",
    "role": "CUSTOMER"
  }
}
```

### Customer

- `GET /refunds?page=1&page_size=10`
- `POST /refunds`
- `POST /chat`

### Admin

- `GET /admin/refunds?page=1&page_size=10&refund_id=&status=&created_date=`
- `GET /admin/refunds/summary`

Expected summary response:

```json
{
  "created": 128,
  "approved": 72,
  "rejected": 31,
  "escalated": 9
}
```

### Developer

- `GET /developer/audit-logs?page=1&page_size=15&created_date=`

## Roles

The frontend supports:

- CUSTOMER → `/dashboard`, `/refunds`
- ADMIN → `/admin`
- DEVELOPER → `/developer`

Authorization is enforced in the frontend for user experience, but the backend must remain the source of truth for security.

## Important backend alignment

The current backend role enum must include:

```python
class Role(str, Enum):
    CUSTOMER = "CUSTOMER"
    SUPPORT = "SUPPORT"
    ADMIN = "ADMIN"
    DEVELOPER = "DEVELOPER"
```

Admin and developer endpoints must also enforce their roles server-side.

## Chat

The widget sends:

```json
POST /api/v1/chat
{
  "message": "Where is my refund?"
}
```

Expected response:

```json
{
  "message": "Your refund is currently being reviewed."
}
```

## Design

The interface uses a mature banking-style palette:

- deep navy for trust and primary actions
- teal for active/successful operational states
- slate neutrals for information hierarchy
- restrained gold/amber for attention
- white surfaces and generous spacing

The UI is intentionally operational rather than playful.
