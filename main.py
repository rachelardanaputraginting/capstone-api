import secrets

# Generate a 32-character random string
secret_key = secrets.token_hex(32)
print("JWT_SECRET_KEY:", secret_key)