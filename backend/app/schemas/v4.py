from datetime import datetime
from pydantic import BaseModel


# ---- V4 Continue ----

class V4ContinueRequest(BaseModel):
    user_intent: str = ""
    style_note: str = ""
    target_length: int | None = None
    emotion_target: str | None = None
    pace_target: str | None = None
    planner_input: dict | None = None


class V4ContinueResponse(BaseModel):
    generation_id: int
    ai_output: str
    workflow_status: dict | None = None


# ---- Story Graph ----

class GraphNode(BaseModel):
    id: str
    label: str
    node_type: str  # character / event / location / faction / foreshadowing
    properties: dict = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    edge_type: str
    properties: dict = {}


class GraphDataResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


# ---- Consistency ----

class ConsistencyIssue(BaseModel):
    severity: str  # critical / major / minor
    category: str  # character / power / timeline / world_rule
    description: str
    suggestion: str


class ConsistencyReportResponse(BaseModel):
    passed: bool
    issues: list[ConsistencyIssue]
    overall_score: float
    check_type: str = ""  # pre / post


class ConsistencyHistoryResponse(BaseModel):
    reports: list[ConsistencyReportResponse]


# ---- Workflow Status ----

class V4WorkflowStatus(BaseModel):
    current_step: str
    progress: float  # 0.0 - 1.0
    steps: list[str]
    step_results: dict = {}
    generated_text: str | None = None
    generation_id: int | None = None
    error: str | None = None
