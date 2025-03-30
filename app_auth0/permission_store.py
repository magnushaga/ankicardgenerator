from enum import Enum
import logging
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    DECK = "deck"
    LIVE_DECK = "live_deck"
    PART = "part"
    CHAPTER = "chapter"
    TOPIC = "topic"
    CARD = "card"
    STUDY_SESSION = "study_session"
    USER = "user"

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"
    ADMIN = "admin"
    CREATE_LIVE_DECK = "create_live_deck"
    EDIT_LIVE_DECK = "edit_live_deck"
    USE_AI_FEATURES = "use_ai_features"
    USE_MEDIA = "use_media"
    USE_ANALYTICS = "use_analytics"
    USE_EXPORT = "use_export"
    USE_IMPORT = "use_import"
    USE_API = "use_api"
    USE_PRIORITY_SUPPORT = "use_priority_support"

class PermissionStore:
    def __init__(self):
        # Structure: {user_id: {resource_type:resource_id: [permissions]}}
        self._user_permissions: Dict[str, Dict[str, Set[Permission]]] = {}
        # Structure: {resource_type:resource_id: user_id}
        self._resource_owners: Dict[str, str] = {}

    @property
    def user_permissions(self) -> Dict[str, Dict[str, Set[Permission]]]:
        return self._user_permissions

    @property
    def resource_owners(self) -> Dict[str, str]:
        return self._resource_owners

    def _get_resource_key(self, resource_type: str, resource_id: str) -> str:
        """Create a unique key for a resource."""
        return f"{resource_type}:{resource_id}"

    def set_permission(self, user_id: str, resource_type: str, resource_id: str, permission: str) -> None:
        """Set a permission for a user on a resource."""
        try:
            permission_enum = Permission(permission)
            resource_key = self._get_resource_key(resource_type, resource_id)

            # Initialize user's permission dictionary if needed
            if user_id not in self._user_permissions:
                self._user_permissions[user_id] = {}

            # Initialize resource permissions set if needed
            if resource_key not in self._user_permissions[user_id]:
                self._user_permissions[user_id][resource_key] = set()

            # Add the permission
            self._user_permissions[user_id][resource_key].add(permission_enum)
            logger.info(f"Added permission {permission} for user {user_id} on {resource_key}")

        except ValueError as e:
            logger.error(f"Invalid permission value: {permission}")
            raise ValueError(f"Invalid permission value: {permission}")

    def remove_permission(self, user_id: str, resource_type: str, resource_id: str, permission: str) -> None:
        """Remove a permission for a user on a resource."""
        try:
            permission_enum = Permission(permission)
            resource_key = self._get_resource_key(resource_type, resource_id)

            if user_id in self._user_permissions and resource_key in self._user_permissions[user_id]:
                self._user_permissions[user_id][resource_key].discard(permission_enum)
                logger.info(f"Removed permission {permission} for user {user_id} on {resource_key}")

        except ValueError as e:
            logger.error(f"Invalid permission value: {permission}")
            raise ValueError(f"Invalid permission value: {permission}")

    def set_resource_owner(self, user_id: str, resource_type: str, resource_id: str) -> None:
        """Set the owner of a resource."""
        resource_key = self._get_resource_key(resource_type, resource_id)
        self._resource_owners[resource_key] = user_id
        logger.info(f"Set owner of {resource_key} to user {user_id}")

    def get_resource_owner(self, resource_type: str, resource_id: str) -> Optional[str]:
        """Get the owner of a resource."""
        resource_key = self._get_resource_key(resource_type, resource_id)
        return self._resource_owners.get(resource_key)

    def get_user_permissions(self, user_id: str, resource_type: str, resource_id: str) -> Set[Permission]:
        """Get all permissions for a user on a resource."""
        resource_key = self._get_resource_key(resource_type, resource_id)
        if user_id in self._user_permissions and resource_key in self._user_permissions[user_id]:
            return self._user_permissions[user_id][resource_key]
        return set()

    def has_permission(self, user_id: str, resource_type: str, resource_id: str, permission: Permission) -> bool:
        """Check if a user has a specific permission on a resource."""
        try:
            # Admin users have all permissions
            if self.has_permission(user_id, resource_type, resource_id, Permission.ADMIN):
                return True

            # Resource owners have all permissions on their resources
            resource_owner = self.get_resource_owner(resource_type, resource_id)
            if resource_owner == user_id:
                return True

            # Check specific permissions
            user_permissions = self.get_user_permissions(user_id, resource_type, resource_id)
            return permission in user_permissions

        except Exception as e:
            logger.error(f"Error checking permission: {str(e)}")
            return False

    def clear_permissions(self) -> None:
        """Clear all permissions and resource owners."""
        self._user_permissions.clear()
        self._resource_owners.clear()
        logger.info("Cleared all permissions and resource owners")

# Create a singleton instance
permission_store = PermissionStore() 