# Secure Coding Guidelines for Contributors

Essential security practices for all contributors to the Panelin chatbot project.

## 🎯 Overview

This document outlines secure coding practices to prevent vulnerabilities and maintain the security posture of the application.

---

## 🔒 Core Security Principles

### 1. Defense in Depth
Implement multiple layers of security controls.

### 2. Principle of Least Privilege
Grant minimum necessary permissions.

### 3. Fail Securely
System should default to secure state on errors.

### 4. Don't Trust User Input
Always validate and sanitize all inputs.

### 5. Keep Security Simple
Complex security is harder to maintain and audit.

---

## 🛡️ Input Validation and Sanitization

### Always Validate User Input

```python
# ❌ Bad - No validation
def process_user_data(user_input):
    return eval(user_input)  # NEVER use eval() on user input!

# ✅ Good - Proper validation
def process_user_data(user_input: str) -> dict:
    # Validate input type
    if not isinstance(user_input, str):
        raise ValueError("Input must be a string")
    
    # Validate length
    if len(user_input) > 1000:
        raise ValueError("Input exceeds maximum length")
    
    # Sanitize and parse safely
    try:
        data = json.loads(user_input)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")
    
    return data
```

### Sanitize Output

```python
import html

# ❌ Bad - XSS vulnerability
def display_user_comment(comment):
    return f"<p>{comment}</p>"

# ✅ Good - Escaped output
def display_user_comment(comment):
    safe_comment = html.escape(comment)
    return f"<p>{safe_comment}</p>"
```

### Validate File Uploads

```python
import os
from pathlib import Path

# ✅ Good - Secure file handling
ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_upload(file_path: str, file_size: int) -> bool:
    """Validate uploaded file."""
    
    # Check file extension
    ext = Path(file_path).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type {ext} not allowed")
    
    # Check file size
    if file_size > MAX_FILE_SIZE:
        raise ValueError("File too large")
    
    # Sanitize filename
    filename = os.path.basename(file_path)
    safe_filename = "".join(c for c in filename if c.isalnum() or c in '._-')
    
    return True
```

---

## 🔐 Authentication and Authorization

### Secure Password Handling

```python
import bcrypt

# ❌ Bad - Storing plain text passwords
def create_user(username, password):
    users_db[username] = password  # NEVER store passwords in plain text!

# ✅ Good - Hashing passwords
def create_user(username: str, password: str):
    # Hash password with bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    users_db[username] = hashed

def verify_password(username: str, password: str) -> bool:
    stored_hash = users_db.get(username)
    if not stored_hash:
        return False
    return bcrypt.checkpw(password.encode(), stored_hash)
```

### API Key Security

```python
import os
from typing import Optional

# ✅ Good - Secure API key handling
def get_api_key() -> str:
    """Get API key from environment."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Validate format (basic check)
    if not api_key.startswith('sk-'):
        raise ValueError("Invalid API key format")
    
    return api_key

def make_api_request(prompt: str) -> str:
    """Make API request without exposing key in logs."""
    api_key = get_api_key()
    
    # ✅ Log without exposing key
    logger.info("Making API request", extra={'prompt_length': len(prompt)})
    
    # ❌ Never do this:
    # logger.info(f"Using API key: {api_key}")
    
    response = openai_client.create_completion(
        api_key=api_key,
        prompt=prompt
    )
    
    return response
```

### Session Management

```python
import secrets
from datetime import datetime, timedelta

# ✅ Good - Secure session handling
SESSION_TIMEOUT = timedelta(hours=1)

def create_session(user_id: str) -> str:
    """Create secure session token."""
    # Generate cryptographically secure token
    token = secrets.token_urlsafe(32)
    
    sessions[token] = {
        'user_id': user_id,
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + SESSION_TIMEOUT
    }
    
    return token

def validate_session(token: str) -> Optional[str]:
    """Validate session and return user_id if valid."""
    session = sessions.get(token)
    
    if not session:
        return None
    
    # Check expiration
    if datetime.utcnow() > session['expires_at']:
        del sessions[token]
        return None
    
    return session['user_id']
```

---

## 💉 Injection Prevention

### SQL Injection Prevention

```python
import sqlite3

# ❌ Bad - SQL injection vulnerability
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)  # Vulnerable!

# ✅ Good - Parameterized queries
def get_user(username: str):
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    return cursor.fetchone()
```

### NoSQL Injection Prevention (MongoDB)

```python
from pymongo import MongoClient

# ❌ Bad - NoSQL injection vulnerability
def find_user(username):
    return db.users.find_one({"username": username})  # Vulnerable if username is dict

# ✅ Good - Type validation
def find_user(username: str):
    # Ensure username is a string, not a dict
    if not isinstance(username, str):
        raise ValueError("Username must be a string")
    
    return db.users.find_one({"username": username})
```

### Command Injection Prevention

```python
import subprocess
import shlex

# ❌ Bad - Command injection vulnerability
def process_file(filename):
    os.system(f"cat {filename}")  # Vulnerable!

# ✅ Good - Safe subprocess usage
def process_file(filename: str):
    # Validate filename
    if not filename.isalnum():
        raise ValueError("Invalid filename")
    
    # Use subprocess with list (not shell)
    result = subprocess.run(
        ['cat', filename],
        shell=False,  # IMPORTANT: shell=False prevents injection
        capture_output=True,
        text=True
    )
    return result.stdout
```

### Path Traversal Prevention

```python
from pathlib import Path

# ❌ Bad - Path traversal vulnerability
def read_file(filename):
    with open(f"data/{filename}") as f:
        return f.read()

# ✅ Good - Validate and normalize paths
def read_file(filename: str) -> str:
    # Define allowed directory
    base_dir = Path("/app/data").resolve()
    
    # Resolve the requested file path
    file_path = (base_dir / filename).resolve()
    
    # Ensure the file is within the allowed directory
    if not file_path.is_relative_to(base_dir):
        raise ValueError("Path traversal attempt detected")
    
    # Additional validation
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {filename}")
    
    with open(file_path) as f:
        return f.read()
```

---

## 🔑 Secrets and Sensitive Data

### Never Hardcode Secrets

```python
# ❌ Bad - Hardcoded secrets
OPENAI_API_KEY = "sk-proj-abc123..."
DB_PASSWORD = "my_password"

# ✅ Good - Environment variables
import os
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DB_PASSWORD = os.getenv('DB_PASSWORD')
```

### Secure Logging

```python
import logging

# ❌ Bad - Logging sensitive data
logging.info(f"User logged in with password: {password}")
logging.info(f"API key: {api_key}")

# ✅ Good - Safe logging
logging.info(f"User logged in: {username}")
logging.info("API key loaded successfully")
logging.info(f"Request payload length: {len(data)}")
```

### Redact Sensitive Data in Errors

```python
# ❌ Bad - Exposing sensitive data in errors
def connect_to_api(api_key):
    try:
        client = API(api_key=api_key)
    except Exception as e:
        raise Exception(f"Connection failed with key {api_key}: {e}")

# ✅ Good - Redacted error messages
def connect_to_api(api_key: str):
    try:
        client = API(api_key=api_key)
    except Exception as e:
        # Log error details securely (not to user)
        logger.error("API connection failed", exc_info=True)
        # User-facing error (no sensitive data)
        raise Exception("Failed to connect to API service")
```

---

## 🌐 API Security

### Rate Limiting

```python
from datetime import datetime, timedelta
from collections import defaultdict

# ✅ Simple rate limiter
class RateLimiter:
    def __init__(self, max_requests: int = 100, window: int = 3600):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window)
        self.requests = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        now = datetime.utcnow()
        cutoff = now - self.window
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff
        ]
        
        # Check limit
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Record new request
        self.requests[identifier].append(now)
        return True

# Usage
limiter = RateLimiter(max_requests=100, window=3600)

def api_endpoint(user_id: str):
    if not limiter.is_allowed(user_id):
        raise Exception("Rate limit exceeded. Please try again later.")
    
    # Process request
    return process_request()
```

### Request Validation

```python
from typing import Optional
from pydantic import BaseModel, validator

# ✅ Good - Use Pydantic for validation
class QuotationRequest(BaseModel):
    customer_name: str
    items: list
    quantity: int
    
    @validator('customer_name')
    def validate_name(cls, v):
        if len(v) > 100:
            raise ValueError('Name too long')
        if not v.isprintable():
            raise ValueError('Invalid characters in name')
        return v
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v < 1 or v > 10000:
            raise ValueError('Quantity out of range')
        return v

def create_quotation(request_data: dict):
    # Validate with Pydantic
    try:
        request = QuotationRequest(**request_data)
    except ValueError as e:
        raise ValueError(f"Invalid request: {e}")
    
    # Process validated data
    return process_quotation(request)
```

### CORS Configuration

```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# ❌ Bad - Allow all origins
CORS(app, resources={r"/*": {"origins": "*"}})

# ✅ Good - Specific origins only
ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com"
]

CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

---

## 🔍 Error Handling

### Secure Error Messages

```python
# ❌ Bad - Exposing internal details
def get_user_data(user_id):
    try:
        data = db.query(f"SELECT * FROM users WHERE id={user_id}")
    except Exception as e:
        return f"Database error: {e}"  # Exposes DB structure!

# ✅ Good - Generic error messages
def get_user_data(user_id: int):
    try:
        data = db.query("SELECT * FROM users WHERE id=?", (user_id,))
        return data
    except Exception as e:
        # Log detailed error server-side
        logger.error(f"Database error for user {user_id}", exc_info=True)
        # Return generic error to client
        return {"error": "Unable to retrieve user data"}
```

### Avoid Information Disclosure

```python
# ❌ Bad - Different errors reveal information
def login(username, password):
    user = db.get_user(username)
    if not user:
        return "Username not found"
    if not verify_password(user, password):
        return "Incorrect password"
    return "Login successful"

# ✅ Good - Generic error message
def login(username: str, password: str):
    user = db.get_user(username)
    if not user or not verify_password(user, password):
        # Same error for both cases
        return {"error": "Invalid username or password"}
    
    return {"success": True, "token": create_session(user.id)}
```

---

## 📦 Dependency Security

### Keep Dependencies Updated

```bash
# Check for vulnerabilities
pip-audit

# Update dependencies
pip install --upgrade -r requirements.txt

# Use Dependabot for automatic updates (already configured)
```

### Pin Dependency Versions

```python
# requirements.txt
# ✅ Good - Pinned versions
openai==1.12.0
pymongo==4.6.1
python-dotenv==1.0.0

# ❌ Bad - Unpinned versions
# openai
# pymongo
# python-dotenv
```

### Verify Package Integrity

```bash
# Generate hashes for requirements
pip-compile --generate-hashes requirements.in

# Install with hash verification
pip install --require-hashes -r requirements.txt
```

---

## 🧪 Security Testing

### Unit Tests for Security

```python
import pytest

def test_input_validation():
    """Test that invalid input is rejected."""
    with pytest.raises(ValueError):
        process_user_data("'; DROP TABLE users; --")

def test_path_traversal_prevention():
    """Test that path traversal is blocked."""
    with pytest.raises(ValueError):
        read_file("../../etc/passwd")

def test_rate_limiting():
    """Test that rate limiting works."""
    limiter = RateLimiter(max_requests=5, window=60)
    
    # Allow first 5 requests
    for i in range(5):
        assert limiter.is_allowed("user1") == True
    
    # Block 6th request
    assert limiter.is_allowed("user1") == False
```

### Security Checklist Before Commit

- [ ] No hardcoded secrets or API keys
- [ ] All user input is validated
- [ ] SQL/NoSQL queries use parameterization
- [ ] File operations check for path traversal
- [ ] Errors don't expose sensitive information
- [ ] Logging doesn't include secrets or PII
- [ ] Dependencies are up to date
- [ ] New code has security tests
- [ ] Code reviewed for security issues

---

## 🚨 Common Vulnerabilities to Avoid

### OWASP Top 10 (2021)

1. **Broken Access Control** - Validate user permissions
2. **Cryptographic Failures** - Use strong encryption
3. **Injection** - Sanitize all inputs
4. **Insecure Design** - Security by design
5. **Security Misconfiguration** - Secure defaults
6. **Vulnerable Components** - Keep dependencies updated
7. **Authentication Failures** - Implement MFA, secure sessions
8. **Data Integrity Failures** - Validate data integrity
9. **Logging Failures** - Log security events
10. **SSRF** - Validate and sanitize URLs

---

## 📚 Additional Resources

- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [OpenAI Safety Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)
- [CWE Top 25 Most Dangerous Software Weaknesses](https://cwe.mitre.org/top25/)

---

**Last Updated:** 2026-01-31  
**Maintainer:** @matiasportugau-ui
