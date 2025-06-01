from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

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

class WorkflowDB(BaseModel):
    name: str
    last_edit: str
    user_id: str  # owner_id
    last_run: str = None
    status: str = "Not Started"
    collaborators: List[str] = []  # List of user emails with collaboration access

class WorkflowCollaborator(BaseModel):
    email: str

class WorkflowPermissions(BaseModel):
    is_owner: bool
    can_edit: bool
    can_execute: bool
    can_download: bool
    can_delete: bool
    can_manage_collaborators: bool
