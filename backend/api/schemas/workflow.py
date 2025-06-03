from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class WorkflowRole(str, Enum):
    OWNER = "owner"
    EDITOR = "editor"
    EXECUTOR = "executor"
    VIEWER = "viewer"
    ANALYST = "analyst"
    
    def can_view(self) -> bool:
        """Check if role can view workflow details."""
        return True  # All roles can view
    
    def can_edit(self) -> bool:
        """Check if role can modify workflow structure."""
        return self in [self.OWNER, self.EDITOR]
    
    def can_execute(self) -> bool:
        """Check if role can run workflows."""
        return self in [self.OWNER, self.EDITOR, self.EXECUTOR]
    
    def can_download(self) -> bool:
        """Check if role can download workflow results."""
        return True  # All roles can download results
    
    def can_copy(self) -> bool:
        """Check if role can create copies/forks."""
        return self in [self.OWNER, self.EDITOR, self.ANALYST]
    
    def can_delete(self) -> bool:
        """Check if role can delete workflow."""
        return self == self.OWNER
    
    def can_manage_permissions(self) -> bool:
        """Check if role can manage workflow permissions."""
        return self == self.OWNER
    
    def can_view_sensitive_data(self) -> bool:
        """Check if role can access sensitive workflow data."""
        return self in [self.OWNER, self.EDITOR, self.EXECUTOR]
    
    def get_role_hierarchy_level(self) -> int:
        """Get numeric level for role hierarchy comparison."""
        hierarchy = {
            self.OWNER: 5,
            self.EDITOR: 4,
            self.EXECUTOR: 3,
            self.ANALYST: 2,
            self.VIEWER: 1
        }
        return hierarchy.get(self, 0)

class ConfigFieldType(str, Enum):
    STRING = "string"
    FILE = "file"
    BOOLEAN = "boolean"
    RADIO = "radio"
    SELECT = "select"

class WorkflowBase(BaseModel):
    dag_id: str

class ConfigField(BaseModel):
    name: str
    value: str
    type: ConfigFieldType
    options: Optional[List[str]] = None

class WorkflowComponent(BaseModel):
    id: str
    content: str
    type: str
    subtype: str = ""
    config: List[ConfigField]
    dependencies: List[str] = []

class WorkflowAirflow(WorkflowBase):
    schedule: str = None
    start_date: str = None
    tasks: List[WorkflowComponent]

class WorkflowCollaborator(BaseModel):
    email: str
    role: WorkflowRole = WorkflowRole.VIEWER
    invited_at: Optional[str] = None
    invited_by: Optional[str] = None

class WorkflowDB(BaseModel):
    name: str
    last_edit: str
    user_id: str  # owner_id
    organization_id: Optional[str] = None  # Organization that owns this workflow
    last_run: str = None
    status: str = "Not Started"
    collaborators: List[str] = []  # List of user emails with collaboration access (legacy)
    workflow_collaborators: Optional[List[WorkflowCollaborator]] = []  # Enhanced collaborator info

class AddCollaboratorRequest(BaseModel):
    email: str
    role: WorkflowRole = WorkflowRole.VIEWER

class UpdateCollaboratorRequest(BaseModel):
    role: WorkflowRole

class WorkflowPermissions(BaseModel):
    role: WorkflowRole
    is_owner: bool
    can_view: bool
    can_edit: bool
    can_execute: bool
    can_download: bool
    can_copy: bool
    can_delete: bool
    can_manage_permissions: bool
    can_view_sensitive_data: bool

class EnhancedWorkflowPermissions(BaseModel):
    user_role: WorkflowRole
    permissions: WorkflowPermissions
    is_organization_member: bool = False
    organization_role: Optional[str] = None
