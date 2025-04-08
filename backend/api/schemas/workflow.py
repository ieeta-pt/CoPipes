from pydantic import BaseModel
from typing import List

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

class WorkflowRequest(BaseModel):
    dag_id: str
    schedule_interval: str = None
    start_date: str = None
    tasks: List[WorkflowComponent]