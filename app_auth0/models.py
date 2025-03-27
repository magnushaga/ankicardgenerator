from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User:
    def __init__(self, id, email, username, auth0_id=None):
        self.id = id or str(uuid.uuid4())
        self.email = email
        self.username = username
        self.auth0_id = auth0_id
        self.created_at = datetime.utcnow()
        self.last_login = datetime.utcnow()

    @staticmethod
    def from_auth0_claims(claims):
        return User(
            id=None,  # Supabase will generate this
            email=claims['email'],
            username=claims.get('nickname', claims['email'].split('@')[0]),
            auth0_id=claims['sub']
        )

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'auth0_id': self.auth0_id,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat()
        } 