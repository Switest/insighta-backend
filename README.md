# Insighta Backend

A Flask-based REST API backend for the Insighta Labs+ application, providing authentication, user management, and data export functionality.

## Features

- **GitHub OAuth Authentication**: Secure login using GitHub OAuth with JWT tokens
- **Role-Based Access Control (RBAC)**: Support for different user roles (analyst, admin)
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **CORS Support**: Cross-origin resource sharing for web clients
- **Data Export**: CSV export functionality for user profiles
- **Pagination**: Support for paginated API responses

## API Endpoints

### Authentication
- `GET /api/v1/auth/callback` - GitHub OAuth callback endpoint

### Profiles
- `GET /api/v1/profiles` - Get user profiles (requires analyst role)
  - Query parameters: `page`, `limit`
- `GET /api/v1/profiles/export` - Export profiles as CSV (requires admin role)

## Setup Instructions

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd insighta-backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install flask flask-cors flask-limiter PyJWT requests pandas
   ```

5. **Configure GitHub OAuth**:
   - Update `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` in `app.py` with your GitHub OAuth app credentials
   - For development, you can use placeholder values, but for production, register an OAuth app on GitHub

6. **Run the application**:
   ```bash
   python app.py
   ```

The server will start on `http://127.0.0.1:5000` in debug mode.

## Configuration

### Environment Variables
The application uses the following configuration (currently hardcoded for development):

- `GITHUB_CLIENT_ID`: Your GitHub OAuth app client ID
- `GITHUB_CLIENT_SECRET`: Your GitHub OAuth app client secret
- `SECRET_KEY`: JWT signing secret (should be changed for production)

### CORS Origins
Currently configured to allow requests from:
- `http://localhost:8000`
- `http://127.0.0.1:8000`
- `http://127.0.0.1:5500`
- `http://localhost:5500`

## Authentication Flow

1. **Initiate Login**: Redirect users to GitHub OAuth authorization URL
2. **Callback**: GitHub redirects to `/api/v1/auth/callback` with authorization code
3. **Token Exchange**: Backend exchanges code for access token and retrieves user info
4. **JWT Generation**: Creates access and refresh tokens
5. **Cookie Setting**: Sets HTTP-only cookie with access token for web clients
6. **Response**: Returns tokens for CLI clients or redirects for web clients

## API Usage

### Making Authenticated Requests

**Web Clients**: Include the access token as an HTTP-only cookie (automatically handled by browser)

**CLI Clients**: Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### Example API Calls

```bash
# Get profiles (requires authentication)
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" http://127.0.0.1:5000/api/v1/profiles

# Export profiles (requires admin role)
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" http://127.0.0.1:5000/api/v1/profiles/export -o profiles.csv
```

## Security Features

- **JWT Tokens**: Short-lived access tokens (15 minutes) and refresh tokens (7 days)
- **Rate Limiting**: 200 requests/day, 50 requests/hour per IP
- **CORS Protection**: Restricted to specific origins
- **Role-Based Access**: Different endpoints require different permission levels
- **HTTP-Only Cookies**: Prevents XSS attacks on web clients

## Development

### Project Structure
```
insighta-backend/
├── app.py              # Main Flask application
├── venv/               # Virtual environment (created during setup)
└── README.md           # This file
```

### Running in Production
For production deployment:
1. Set `debug=False` in `app.run()`
2. Use environment variables for secrets instead of hardcoding
3. Use a production WSGI server (gunicorn, uWSGI)
4. Set up proper logging and monitoring

### Dependencies
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Flask-Limiter**: Rate limiting
- **PyJWT**: JSON Web Token handling
- **Requests**: HTTP client for GitHub API
- **Pandas**: Data manipulation for CSV export

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure all dependencies are installed in the virtual environment
2. **GitHub OAuth Errors**: Verify client ID and secret are correct
3. **CORS Errors**: Check that the requesting origin is in the allowed origins list
4. **Authentication Failures**: Ensure tokens are valid and not expired

### Debug Mode
The application runs in debug mode by default, which provides detailed error messages and automatic reloading on code changes.

## Contributing

1. Follow the existing code style and structure
2. Add appropriate error handling and logging
3. Update this README for any new features or configuration changes
4. Test authentication and authorization thoroughly

## License

[Add license information here]</content>
<parameter name="filePath">c:\Users\HP\Downloads\insighta-backend\README.md