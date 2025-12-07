# Authentication Setup

## Development Mode (Mock API)

The UI Shell includes mock API endpoints for development without running the Python backend.

### Quick Start

1. **Environment Setup**
   ```bash
   cd serp/ui-shell
   cp .env.local.example .env.local  # Already created as .env.local
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

3. **Login Credentials**
   - **Username**: `testuser`
   - **Password**: `testpass123`

### Mock API Endpoints

The following endpoints are available at `http://localhost:3000/api`:

- `POST /api/auth/login` - Login with username/password
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user info
- `GET /api/health` - Health check

### Mock User Data

The mock authentication returns a test user with:
- **ID**: 1
- **Username**: testuser
- **Email**: test@example.com
- **Full Name**: Test User
- **Role**: Admin
- **Permissions**: Full access to users and CRM modules

## Production Mode (Real Backend)

To connect to the real Python backend:

1. **Update `.env.local`**
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

2. **Start Backend API**
   ```bash
   cd serp
   uv run uvicorn serp_shell.main:app --reload
   ```

3. **Backend expects snake_case**
   The Python backend returns:
   - `access_token` (not `accessToken`)
   - `refresh_token` (not `refreshToken`)
   
   The frontend API client handles the transformation automatically.

## Troubleshooting

### "Network error" on login

**Cause**: The API endpoint is not responding.

**Solutions**:
1. **Using Mock API**: Ensure `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:3000`
2. **Using Real Backend**: Ensure backend is running on port 8000
3. Check browser console for actual error messages
4. Verify no CORS issues (backend should allow localhost:3000)

### Login succeeds but user not authenticated

**Cause**: Token storage or validation issue.

**Solutions**:
1. Clear localStorage: `localStorage.clear()`
2. Check browser DevTools → Application → Local Storage
3. Verify token is saved under key `serp_auth_token`

### Redirects to login after successful authentication

**Cause**: `/api/auth/me` endpoint failing.

**Solutions**:
1. Check Network tab for 401 errors
2. Verify Authorization header is sent: `Bearer <token>`
3. Ensure token hasn't expired

## API Response Format

All API endpoints follow this format:

### Success Response
```json
{
  "data": {
    // Response data here
  }
}
```

### Error Response
```json
{
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE",
    "status": 400,
    "details": {}
  }
}
```

## Next Steps

Once logged in, you can:
1. Navigate to `/dashboard` - Main dashboard
2. Load CRM module UI at `/crm/*` routes
3. Access user management at `/users`
4. View available modules at `/modules`
