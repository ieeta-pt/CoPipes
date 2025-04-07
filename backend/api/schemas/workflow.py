from pydantic import BaseModel
from typing import List

class ConfigField(BaseModel):
    name: str
    value: str
    type: str

class WorkflowComponent(BaseModel):
    id: str
    content: str
    type: str
    config: List[ConfigField]

class WorkflowRequest(BaseModel):
    components: List[WorkflowComponent]
    input: str
    output: str