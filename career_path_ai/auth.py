import json
import os
from typing import Dict, Optional, List

USERS_FILE = "data/users.json"

def load_users() -> List[Dict]:
    """Load users from JSON file"""
    if not os.path.exists(USERS_FILE):
        return []
    
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_users(users: List[Dict]) -> None:
    """Save users to JSON file"""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def validate_email(email: str) -> bool:
    """Basic email validation"""
    return '@' in email and '.' in email.split('@')[-1]

def validate_phone(phone: str) -> bool:
    """Basic phone validation"""
    return phone.isdigit() and len(phone) >= 10

def user_exists(email: str) -> bool:
    """Check if user with given email exists"""
    users = load_users()
    return any(user.get('email') == email for user in users)

def register_user(name: str, email: str, phone: str, password: str) -> tuple[bool, str]:
    """Register a new user"""
    # Validation
    if not name.strip():
        return False, "Name cannot be empty"
    
    if not validate_email(email):
        return False, "Invalid email format"
    
    if not validate_phone(phone):
        return False, "Phone number must be at least 10 digits"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if user_exists(email):
        return False, "User with this email already exists"
    
    # Create new user
    new_user = {
        "name": name.strip(),
        "email": email.lower().strip(),
        "phone": phone,
        "password": password,  # Note: In production, use proper hashing
        "created_at": str(datetime.datetime.now())
    }
    
    # Save user
    users = load_users()
    users.append(new_user)
    save_users(users)
    
    return True, "Registration successful!"

def authenticate_user(email: str, password: str) -> tuple[bool, Optional[Dict]]:
    """Authenticate user login"""
    if not validate_email(email):
        return False, None
    
    users = load_users()
    for user in users:
        if user.get('email') == email.lower().strip() and user.get('password') == password:
            return True, user
    
    return False, None

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    users = load_users()
    for user in users:
        if user.get('email') == email.lower().strip():
            return user
    return None

import datetime
