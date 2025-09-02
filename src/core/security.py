"""
Security Module for API Authentication and Authorization
"""

import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from functools import wraps
import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
import hmac
from dataclasses import dataclass
from pathlib import Path
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
JWT_SECRET_KEY = secrets.token_urlsafe(32)
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

@dataclass
class User:
    """User model for authentication"""
    username: str
    email: str
    password_hash: str
    is_premium: bool = False
    is_admin: bool = False
    created_at: datetime = None
    last_login: datetime = None
    api_key: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class SecurityManager:
    """Manages application security, authentication, and authorization"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecurityManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.api_keys: Dict[str, str] = {}  # api_key -> username
        self.rate_limits: Dict[str, List[float]] = {}  # IP -> timestamps
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Load users from database or config
        self._load_users()
        
        self._initialized = True
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for sensitive data"""
        # In production, this should be loaded from secure storage
        password = b"GermanCodeZero-Cleaner-2024"
        salt = b"salt_1234567890"
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def _load_users(self):
        """Load users from configuration or database"""
        # Default admin user (should be changed in production)
        admin_user = User(
            username="admin",
            email="admin@germancodezero.com",
            password_hash=self.hash_password("admin123"),  # Change this!
            is_admin=True,
            is_premium=True
        )
        self.users[admin_user.username] = admin_user
        
        # Generate API key for admin
        api_key = self.generate_api_key()
        admin_user.api_key = api_key
        self.api_keys[api_key] = admin_user.username
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, username: str, email: str, password: str, 
                   is_premium: bool = False) -> Optional[User]:
        """Create a new user"""
        if username in self.users:
            return None
        
        user = User(
            username=username,
            email=email,
            password_hash=self.hash_password(password),
            is_premium=is_premium
        )
        
        # Generate API key
        api_key = self.generate_api_key()
        user.api_key = api_key
        self.api_keys[api_key] = username
        
        self.users[username] = user
        return user
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        user = self.users.get(username)
        if user and self.verify_password(password, user.password_hash):
            user.last_login = datetime.utcnow()
            return user
        return None
    
    def generate_token(self, user: User) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            "username": user.username,
            "email": user.email,
            "is_premium": user.is_premium,
            "is_admin": user.is_admin,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def generate_api_key(self) -> str:
        """Generate a unique API key"""
        return f"gczc_{secrets.token_urlsafe(32)}"
    
    def verify_api_key(self, api_key: str) -> Optional[User]:
        """Verify API key and return associated user"""
        username = self.api_keys.get(api_key)
        if username:
            return self.users.get(username)
        return None
    
    def check_rate_limit(self, ip_address: str, max_requests: int = 100, 
                        window_seconds: int = 60) -> bool:
        """Check if IP address has exceeded rate limit"""
        current_time = time.time()
        
        if ip_address not in self.rate_limits:
            self.rate_limits[ip_address] = []
        
        # Remove old timestamps outside the window
        self.rate_limits[ip_address] = [
            timestamp for timestamp in self.rate_limits[ip_address]
            if current_time - timestamp < window_seconds
        ]
        
        # Check if limit exceeded
        if len(self.rate_limits[ip_address]) >= max_requests:
            return False
        
        # Add current request timestamp
        self.rate_limits[ip_address].append(current_time)
        return True
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF protection token"""
        return secrets.token_urlsafe(32)
    
    def verify_csrf_token(self, token: str, stored_token: str) -> bool:
        """Verify CSRF token"""
        return hmac.compare_digest(token, stored_token)
    
    def check_permission(self, user: User, permission: str) -> bool:
        """Check if user has specific permission"""
        permissions = {
            "admin": ["all"],
            "premium": ["advanced_scan", "ai_features", "cloud_backup", "priority_support"],
            "free": ["basic_scan", "basic_clean"]
        }
        
        if user.is_admin:
            return True
        
        user_type = "premium" if user.is_premium else "free"
        allowed_permissions = permissions.get(user_type, [])
        
        return permission in allowed_permissions or "all" in allowed_permissions
    
    def sanitize_input(self, input_str: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        # Remove potential dangerous characters
        dangerous_chars = ["<", ">", "&", '"', "'", "/", "\\", ";", "|", "$", "`"]
        sanitized = input_str
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")
        return sanitized.strip()
    
    def validate_file_path(self, file_path: str, base_path: str = None) -> bool:
        """Validate file path to prevent directory traversal attacks"""
        try:
            path = Path(file_path).resolve()
            
            if base_path:
                base = Path(base_path).resolve()
                return path.is_relative_to(base)
            
            # Check for suspicious patterns
            suspicious_patterns = ["../", "..\\", "/etc/", "C:\\Windows", "C:\\Program Files"]
            for pattern in suspicious_patterns:
                if pattern in str(path):
                    return False
            
            return True
        except Exception:
            return False
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related events"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "details": details
        }
        
        # In production, this should go to a secure logging system
        print(f"[SECURITY] {json.dumps(event)}")
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return self.sessions.get(session_id)
    
    def create_session(self, user: User) -> str:
        """Create a new session"""
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = {
            "username": user.username,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        return session_id
    
    def destroy_session(self, session_id: str):
        """Destroy a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """Remove expired sessions"""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            age = current_time - session_data["last_activity"]
            if age.total_seconds() > max_age_hours * 3600:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]

# Decorators for FastAPI routes
def require_auth(func):
    """Decorator to require authentication"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # This would be integrated with FastAPI's dependency injection
        # Example implementation
        return await func(*args, **kwargs)
    return wrapper

def require_premium(func):
    """Decorator to require premium account"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Check if user has premium access
        return await func(*args, **kwargs)
    return wrapper

def require_admin(func):
    """Decorator to require admin privileges"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Check if user is admin
        return await func(*args, **kwargs)
    return wrapper

# Singleton instance getter
def get_security_manager() -> SecurityManager:
    """Get the singleton SecurityManager instance"""
    return SecurityManager()

# Export main components
__all__ = [
    "SecurityManager",
    "get_security_manager",
    "User",
    "require_auth",
    "require_premium",
    "require_admin"
]