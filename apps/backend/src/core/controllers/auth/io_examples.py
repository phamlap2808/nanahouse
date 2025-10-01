register_examples = {
    "default": {
        "summary": "Register new user",
        "description": "Register a new user account",
        "value": {
            "email": "user@example.com",
            "password": "SecurePass123!",
            "name": "John Doe",
        },
    },
    "minimal": {
        "summary": "Register with minimal data",
        "description": "Register with only required fields",
        "value": {
            "email": "minimal@example.com",
            "password": "SecurePass123!",
        },
    },
}

login_examples = {
    "default": {
        "summary": "User login",
        "description": "Login with email and password",
        "value": {
            "email": "user@example.com",
            "password": "SecurePass123!",
        },
    },
}

me_update_examples = {
    "default": {
        "summary": "Update user profile",
        "description": "Update current user's name",
        "value": {
            "name": "Updated Name",
        },
    },
    "clear_name": {
        "summary": "Clear user name",
        "description": "Remove user's name by setting to null",
        "value": {
            "name": None,
        },
    },
}
