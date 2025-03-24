from sqlalchemy.types import TypeDecorator, String
import uuid

class SQLiteUUID(TypeDecorator):
    """Platform-independent UUID type.
    Uses String(32) in SQLite, native UUID type for other databases.
    """
    impl = String
    cache_ok = True

    def __init__(self):
        self.impl.length = 32
        TypeDecorator.__init__(self, length=self.impl.length)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'sqlite':
            return str(value).replace('-', '')
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(value.replace('-', ''))
        return value