"""
ZENALTO OAuth Setup and Configuration Guide

This guide explains how to set up OAuth 2.0 authentication for social media platforms
and configure the ZENALTO platform for production use.
"""

# Environment Variables Configuration

The ZENALTO platform requires API credentials for each social media platform you want to integrate.
Set up the following environment variables:

## Twitter/X API v2.0
```bash
export TWITTER_CLIENT_ID="your_twitter_client_id"
export TWITTER_CLIENT_SECRET="your_twitter_client_secret"
export TWITTER_REDIRECT_URI="http://localhost:8501/oauth/twitter"
```

To get Twitter API credentials:
1. Go to https://developer.twitter.com/
2. Create a new app in the Twitter Developer Portal
3. Enable OAuth 2.0 with PKCE
4. Set redirect URI to match your application
5. Copy the Client ID and Client Secret

## LinkedIn API v2.0
```bash
export LINKEDIN_CLIENT_ID="your_linkedin_client_id"
export LINKEDIN_CLIENT_SECRET="your_linkedin_client_secret"
export LINKEDIN_REDIRECT_URI="http://localhost:8501/oauth/linkedin"
```

To get LinkedIn API credentials:
1. Go to https://developer.linkedin.com/
2. Create a new LinkedIn app
3. Request access to required permissions
4. Configure OAuth 2.0 redirect URLs
5. Copy Client ID and Client Secret

## Instagram Basic Display API
```bash
export INSTAGRAM_CLIENT_ID="your_instagram_app_id"
export INSTAGRAM_CLIENT_SECRET="your_instagram_app_secret"
export INSTAGRAM_REDIRECT_URI="http://localhost:8501/oauth/instagram"
```

For Instagram:
1. Go to https://developers.facebook.com/
2. Create a new Facebook App
3. Add Instagram Basic Display product
4. Configure OAuth redirect URIs
5. Get App ID and App Secret

## Facebook Graph API
```bash
export FACEBOOK_CLIENT_ID="your_facebook_app_id"
export FACEBOOK_CLIENT_SECRET="your_facebook_app_secret"
export FACEBOOK_REDIRECT_URI="http://localhost:8501/oauth/facebook"
```

For Facebook:
1. Use the same Facebook App from Instagram setup
2. Add permissions for page management
3. Set up webhook if needed for real-time updates

## YouTube Data API v3.0
```bash
export GOOGLE_CLIENT_ID="your_google_oauth_client_id"
export GOOGLE_CLIENT_SECRET="your_google_oauth_client_secret"
export GOOGLE_REDIRECT_URI="http://localhost:8501/oauth/youtube"
```

For YouTube:
1. Go to https://console.developers.google.com/
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials
5. Set authorized redirect URIs

## Security Configuration

### Encryption Key (Production)
```bash
export ZENALTO_ENCRYPTION_KEY="base64_encoded_32_byte_key"
```

Generate a secure key:
```python
from cryptography.fernet import Fernet
import base64
key = Fernet.generate_key()
print(base64.b64encode(key).decode())
```

### Production Database (Optional)
```bash
export DATABASE_URL="postgresql://user:pass@localhost/zenalto"
export REDIS_URL="redis://localhost:6379"
```

## Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (create a .env file):
```bash
# Copy the variables above into .env file
```

3. Start the application:
```bash
python deepcode.py
```

4. Access OAuth flows at:
- Twitter: http://localhost:8501/oauth/twitter
- LinkedIn: http://localhost:8501/oauth/linkedin
- Instagram: http://localhost:8501/oauth/instagram
- Facebook: http://localhost:8501/oauth/facebook
- YouTube: http://localhost:8501/oauth/youtube

## Testing OAuth Flow

```python
import asyncio
from tools.social_media_server import SocialMediaServer

async def test_oauth():
    server = SocialMediaServer()
    
    # Initiate OAuth flow
    result = await server.oauth_manager.initiate_oauth_flow(
        platform="twitter", 
        user_id="test_user_123"
    )
    
    print(f"Visit this URL to authorize: {result['auth_url']}")
    
    # After user authorizes, handle callback
    # callback_result = await server.oauth_manager.handle_oauth_callback(
    #     platform="twitter",
    #     authorization_code="code_from_callback",
    #     state=result["state"]
    # )

asyncio.run(test_oauth())
```

## Production Deployment

1. **Environment Variables**: Set all required API credentials
2. **HTTPS**: Use HTTPS in production, update redirect URIs accordingly
3. **Database**: Configure PostgreSQL or MongoDB for storing user data
4. **Redis**: Set up Redis for session management and caching
5. **Load Balancer**: Configure load balancer for high availability
6. **Monitoring**: Set up logging and monitoring for OAuth flows

## API Rate Limits

Each platform has different rate limits:

- **Twitter**: 300 requests per 15 minutes
- **LinkedIn**: 100 requests per hour  
- **Instagram**: 200 requests per hour
- **Facebook**: 200 requests per hour
- **YouTube**: 10,000 units per day

The platform automatically handles rate limiting and will wait when limits are reached.

## Security Best Practices

1. **Token Encryption**: All OAuth tokens are encrypted before storage
2. **State Parameter**: CSRF protection using secure random state
3. **PKCE**: Twitter and YouTube use PKCE for additional security
4. **Token Refresh**: Automatic token refresh when possible
5. **Scope Limitation**: Request only necessary permissions
6. **Secure Storage**: Tokens stored with restrictive file permissions

## Troubleshooting

### Common Issues:

1. **"Invalid redirect URI"**: 
   - Check that redirect URI in app settings matches exactly
   - Include http/https and port number

2. **"Invalid client credentials"**:
   - Verify CLIENT_ID and CLIENT_SECRET environment variables
   - Check if app is in development vs production mode

3. **"Insufficient permissions"**:
   - Review requested scopes in app settings
   - Some platforms require manual approval for certain permissions

4. **"Token expired"**:
   - Tokens are automatically refreshed when possible
   - Some platforms don't support refresh tokens (Instagram Basic Display)

### Support:

For additional support:
1. Check platform-specific developer documentation
2. Review API error responses in logs
3. Test OAuth flow in browser developer tools
4. Verify webhook endpoints if using real-time features