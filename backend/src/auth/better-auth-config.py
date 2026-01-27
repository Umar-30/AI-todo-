"""
Better Auth Configuration for Todo AI Chatbot
"""

from better_auth import Auth, BuiltinProviders
from better_auth.contrib.oauth.github import github_oauth
from better_auth.contrib.oauth.google import google_oauth
import os

# Get secret from environment variable or use a default (not for production!)
secret = os.getenv("AUTH_SECRET", "todo-ai-chatbot-dev-secret-change-in-production")

# Configure the auth instance
auth = Auth(
    secret=secret,
    # Use the same database as the main app if possible
    # For now, using a simple configuration
    rate_limit={
        "enabled": True,
        "window": 60,  # 60 seconds
        "max": 10,     # 10 requests per window
    },
    email_config={
        "from_email": os.getenv("SMTP_FROM_EMAIL", "noreply@todo-ai-chatbot.com"),
        "from_name": "Todo AI Chatbot",
        # Add SMTP configuration if needed
    },
    providers=[
        BuiltinProviders.EMAIL_PASSWORD,  # Enable email/password authentication
        # Uncomment below to add social login providers
        # github_oauth(
        #     client_id=os.getenv("GITHUB_CLIENT_ID"),
        #     client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
        # ),
        # google_oauth(
        #     client_id=os.getenv("GOOGLE_CLIENT_ID"),
        #     client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        # ),
    ],
    # Session configuration
    session_config={
        "cookie_name": "better-auth.session",
        "expires_in": 7 * 24 * 60 * 60,  # 7 days
        "anonymous_session_enabled": False,
    },
    # Database configuration would go here
    # For now using default configuration
)