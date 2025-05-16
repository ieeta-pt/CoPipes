from pydantic import BaseModel
from typing import List, Optional

class WorkflowBase(BaseModel):
    dag_id: str

class ConfigField(BaseModel):
    name: str
    value: str
    type: str = "string" or "file"

class WorkflowComponent(BaseModel):
    id: str
    content: str
    type: str
    subtype: str = ""
    config: List[ConfigField]
    dependencies: List[str] = []

class WorkflowAirflow(WorkflowBase):
    schedule_interval: str = None
    start_date: str = None
    tasks: List[WorkflowComponent]

class WorkflowDB(BaseModel):
    name: str
    last_edit: str
    last_run: str = None
    last_run_status: str = "Not Started"
    people: List[str] = None
    user_id: Optional[str] = None  # ID of the user who owns this workflow
