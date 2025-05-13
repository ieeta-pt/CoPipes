from pydantic import BaseModel
from typing import List

class WorkflowBase(BaseModel):
    dag_id: str

class ConfigField(BaseModel):
    name: str
    value: str

class WorkflowComponent(BaseModel):
    id: str
    content: str
    type: str
    subtype: str = None
    config: List[ConfigField]
    dependencies: List[str] = None

class WorkflowAirflow(WorkflowBase):
    schedule_interval: str = None
    start_date: str = None
    tasks: List[WorkflowComponent]

class WorkflowDB(BaseModel):
    created_at: str
    name: str
    last_edit: str
    last_run: str = None
    last_run_status: str = "Not Started"
    people: List[str] = None
