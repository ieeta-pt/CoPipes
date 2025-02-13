from pydantic import BaseModel

class CreateDAG(BaseModel):
    dag_id: str
    schedule_interval: str | None
    start_date: str
    tasks: list