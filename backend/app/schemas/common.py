"""
Common Pydantic Schemas
Shared schemas for API requests and responses
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Value Object Schemas
# ============================================================================


class Vector3Schema(BaseModel):
    """3D vector coordinates"""
    x: float
    y: float
    z: float

    class Config:
        json_schema_extra = {
            "example": {"x": 0.0, "y": 1.5, "z": 0.0}
        }


class ColorSchema(BaseModel):
    """RGB Color"""
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)
    a: float = Field(default=1.0, ge=0.0, le=1.0)

    @field_validator('r', 'g', 'b')
    @classmethod
    def validate_rgb(cls, v: int) -> int:
        if not 0 <= v <= 255:
            raise ValueError('RGB values must be 0-255')
        return v

    class Config:
        json_schema_extra = {
            "example": {"r": 212, "g": 175, "b": 55, "a": 1.0}
        }


class AgentCapabilitySchema(BaseModel):
    """Agent capability definition"""
    name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    level: int = Field(ge=1, le=5, default=1)
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "text_analysis",
                "category": "analysis",
                "level": 3,
                "description": "Analyze text content for sentiment and entities"
            }
        }


class PerformanceMetricsSchema(BaseModel):
    """Agent performance metrics"""
    avg_response_time: float = Field(default=0.0, ge=0.0)
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    total_tasks: int = Field(default=0, ge=0)
    current_load: float = Field(default=0.0, ge=0.0, le=1.0)

    class Config:
        json_schema_extra = {
            "example": {
                "avg_response_time": 1.25,
                "success_rate": 0.94,
                "total_tasks": 127,
                "current_load": 0.35
            }
        }


# ============================================================================
# Response Wrappers
# ============================================================================


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": "abc123"}
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Resource not found",
                "details": {"resource_id": "abc123"}
            }
        }


class PaginatedResponse(BaseModel):
    """Paginated list response"""
    items: List[Any]
    total: int
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_pages: int

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 50,
                "page": 1,
                "page_size": 20,
                "total_pages": 3
            }
        }
