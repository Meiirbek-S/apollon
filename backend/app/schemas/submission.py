from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.static_analysis import RiskLevel
from app.models.submission import SubmissionStatus, SubmissionType


class FileSubmissionCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=512)
    sha256: str | None = Field(default=None, min_length=64, max_length=64)


class UrlSubmissionCreate(BaseModel):
    url: str = Field(min_length=8, max_length=2048)


class SubmissionCreateResponse(BaseModel):
    submission_id: int
    status: SubmissionStatus
    task_id: str
    deduplicated: bool = False
    reused_from_submission_id: int | None = None


class SubmissionRead(BaseModel):
    id: int
    source_type: SubmissionType
    filename: str
    target_url: str | None
    sha256: str | None
    content_type: str | None
    size_bytes: int | None
    storage_key: str | None
    reused_from_submission_id: int | None
    status: SubmissionStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class StaticAnalysisRead(BaseModel):
    submission_id: int
    original_filename: str
    md5: str
    sha256: str
    file_size: int
    mime_type: str
    extension: str
    extension_mismatch: bool
    risk_score: int
    risk_level: RiskLevel
    risk_indicators: list[str]
    verdict_reason: str

    is_pe: bool
    machine_type: str | None
    compile_timestamp: str | None
    entry_point: str | None
    image_base: str | None
    pe_sections: list[dict[str, Any]]
    imported_functions: list[str]
    suspicious_imports: list[str]
    yara_matches: list[dict[str, Any]]
    yara_rule_count: int
    yara_error: str | None

    created_at: datetime

    model_config = {"from_attributes": True}


class UrlAnalysisRead(BaseModel):
    submission_id: int
    normalized_url: str
    domain: str
    scheme: str
    hostname: str
    path: str
    query_present: bool
    port: int | None
    resolved_ip: str | None
    dns_resolved: bool
    uses_https: bool
    final_url: str | None
    redirect_count: int
    risk_score: int
    risk_level: RiskLevel
    risk_indicators: list[str]
    verdict_reason: str
    analyzed_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
