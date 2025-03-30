from datetime import datetime
import uuid

class AdminRole:
    """
    Model class for admin_roles table.
    """
    def __init__(self, id=None, name=None, description=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class AdminPermission:
    """
    Model class for admin_permissions table.
    """
    def __init__(self, id=None, name=None, description=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class AdminRolePermission:
    """
    Model class for admin_role_permissions table.
    """
    def __init__(self, role_id=None, permission_id=None, created_at=None):
        self.role_id = role_id
        self.permission_id = permission_id
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            'role_id': self.role_id,
            'permission_id': self.permission_id,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class UserAdminRole:
    """
    Model class for user_admin_roles table.
    """
    def __init__(self, user_id=None, role_id=None, assigned_by=None, created_at=None, updated_at=None):
        self.user_id = user_id
        self.role_id = role_id
        self.assigned_by = assigned_by
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'role_id': self.role_id,
            'assigned_by': self.assigned_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class AdminAuditLog:
    """
    Model class for admin_audit_logs table.
    """
    def __init__(self, id=None, admin_id=None, action=None, resource_type=None, resource_id=None, details=None, ip_address=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.admin_id = admin_id
        self.action = action
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.details = details
        self.ip_address = ip_address
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data) 