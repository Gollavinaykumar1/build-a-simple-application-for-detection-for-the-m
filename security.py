import asyncio
import jwt
from datetime import datetime, timedelta

class Security:
    def __init__(self, secret_key):
        self.secret_key = secret_key

    async def generate_token(self, user_id):
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token

    async def validate_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    async def detect_malware(self, file_path):
        # Implement malware detection logic here
        # For demonstration purposes, this function will always return True
        await asyncio.sleep(1)  # Simulate IO-bound operation
        return True