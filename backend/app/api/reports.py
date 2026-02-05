"""
Reports API - Report generation and export endpoints

Endpoints:
- POST /api/reports/generate - Generate a report
- GET /api/reports/{id} - Download generated report
- POST /api/reports/export - Export raw data
- GET /api/reports/templates - List available report templates
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import io

from app.database import get_db
from app.services.report_generator import (
    ReportGenerator,
    get_report_generator,
    ReportConfig,
    ReportType,
    ReportFormat,
    ReportPeriod,
    GeneratedReport,
)


router = APIRouter(prefix="/api/reports", tags=["reports"])


# ============================================================================
# Request/Response Models
# ============================================================================

class GenerateReportRequest(BaseModel):
    """Generate report request"""
    report_type: ReportType = Field(..., description="Type of report")
    format: ReportFormat = Field(ReportFormat.PDF, description="Output format")
    period: ReportPeriod = Field(ReportPeriod.WEEKLY, description="Time period")
    start_date: Optional[str] = Field(None, description="Custom start date (ISO format)")
    end_date: Optional[str] = Field(None, description="Custom end date (ISO format)")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Additional filters")
    include_charts: bool = Field(True, description="Include charts")
    include_summary: bool = Field(True, description="Include summary")
    include_details: bool = Field(True, description="Include details")


class ExportDataRequest(BaseModel):
    """Export data request"""
    data_type: str = Field(..., description="Type of data (agents, tasks, executions)")
    format: ReportFormat = Field(ReportFormat.CSV, description="Export format")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Data filters")


class ReportMetadataResponse(BaseModel):
    """Report metadata response"""
    id: str
    report_type: str
    format: str
    generated_at: str
    period_start: str
    period_end: str
    file_size: int
    metadata: Dict[str, Any]


class ReportTemplateResponse(BaseModel):
    """Report template response"""
    id: str
    name: str
    description: str
    report_type: str
    default_format: str
    default_period: str
    available_formats: List[str]
    customizable_options: List[str]


# ============================================================================
# Helper Functions
# ============================================================================

def get_content_type(format: ReportFormat) -> str:
    """Get MIME content type for format"""
    if format == ReportFormat.PDF:
        return "application/pdf"
    elif format == ReportFormat.CSV:
        return "text/csv"
    elif format == ReportFormat.EXCEL:
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif format == ReportFormat.JSON:
        return "application/json"
    else:
        return "application/octet-stream"


def get_filename(report_type: ReportType, format: ReportFormat) -> str:
    """Generate filename for download"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    extension = format.value
    return f"switchboard_{report_type.value}_{timestamp}.{extension}"


# ============================================================================
# Report Generation Endpoints
# ============================================================================

@router.post("/generate", response_model=ReportMetadataResponse)
async def generate_report(
    request: GenerateReportRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a report

    Creates a report based on the specified type, format, and period.
    Returns metadata about the generated report.
    Use the report ID to download the actual file.
    """
    generator = get_report_generator(db)

    # Parse dates if provided
    start_date = None
    end_date = None
    if request.start_date:
        try:
            start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO 8601.")

    if request.end_date:
        try:
            end_date = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO 8601.")

    # Create report config
    config = ReportConfig(
        report_type=request.report_type,
        format=request.format,
        period=request.period,
        start_date=start_date,
        end_date=end_date,
        filters=request.filters,
        include_charts=request.include_charts,
        include_summary=request.include_summary,
        include_details=request.include_details
    )

    try:
        # Generate report
        report = await generator.generate_report(config)

        # Store report in memory cache (in production, use Redis or file storage)
        # For now, we'll include the ID in response but won't persist the file
        _report_cache[report.id] = report

        return ReportMetadataResponse(
            id=report.id,
            report_type=report.report_type.value,
            format=report.format.value,
            generated_at=report.generated_at.isoformat(),
            period_start=report.period_start.isoformat(),
            period_end=report.period_end.isoformat(),
            file_size=report.file_size,
            metadata=report.metadata
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/{report_id}")
async def download_report(
    report_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Download a generated report

    Returns the report file for download
    """
    # Retrieve from cache (in production, use proper storage)
    if report_id not in _report_cache:
        raise HTTPException(status_code=404, detail=f"Report with ID {report_id} not found")

    report = _report_cache[report_id]

    # Get content type and filename
    content_type = get_content_type(report.format)
    filename = get_filename(report.report_type, report.format)

    # Create streaming response
    return StreamingResponse(
        io.BytesIO(report.file_data),
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(report.file_size)
        }
    )


@router.post("/export")
async def export_data(
    request: ExportDataRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Export raw data

    Exports specific data types (agents, tasks, executions) without report formatting
    """
    generator = get_report_generator(db)

    try:
        # Export data
        file_data = await generator.export_data(
            data_type=request.data_type,
            format=request.format,
            filters=request.filters
        )

        # Get content type and filename
        content_type = get_content_type(request.format)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"switchboard_{request.data_type}_{timestamp}.{request.format.value}"

        # Return file
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(file_data))
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data export failed: {str(e)}")


@router.get("/templates/list", response_model=List[ReportTemplateResponse])
async def list_report_templates():
    """
    List available report templates

    Returns all predefined report templates with their configurations
    """
    templates = [
        ReportTemplateResponse(
            id="system_health",
            name="System Health Report",
            description="Overview of current system health, agent status, and connections",
            report_type=ReportType.SYSTEM_HEALTH.value,
            default_format=ReportFormat.PDF.value,
            default_period=ReportPeriod.DAILY.value,
            available_formats=[f.value for f in ReportFormat],
            customizable_options=["period", "format"]
        ),
        ReportTemplateResponse(
            id="performance_summary",
            name="Performance Summary Report",
            description="Performance metrics including response times, throughput, and error rates",
            report_type=ReportType.PERFORMANCE_SUMMARY.value,
            default_format=ReportFormat.PDF.value,
            default_period=ReportPeriod.WEEKLY.value,
            available_formats=[f.value for f in ReportFormat],
            customizable_options=["period", "format"]
        ),
        ReportTemplateResponse(
            id="agent_analytics",
            name="Agent Analytics Report",
            description="Detailed analytics on agent performance, task completion, and efficiency",
            report_type=ReportType.AGENT_ANALYTICS.value,
            default_format=ReportFormat.PDF.value,
            default_period=ReportPeriod.MONTHLY.value,
            available_formats=[f.value for f in ReportFormat],
            customizable_options=["period", "format", "filters"]
        ),
        ReportTemplateResponse(
            id="execution_analytics",
            name="Execution Analytics Report",
            description="Analysis of execution times, costs, and success rates",
            report_type=ReportType.EXECUTION_ANALYTICS.value,
            default_format=ReportFormat.PDF.value,
            default_period=ReportPeriod.MONTHLY.value,
            available_formats=[f.value for f in ReportFormat],
            customizable_options=["period", "format"]
        ),
        ReportTemplateResponse(
            id="comprehensive",
            name="Comprehensive Report",
            description="All-inclusive report with system health, performance, agents, and executions",
            report_type=ReportType.COMPREHENSIVE.value,
            default_format=ReportFormat.PDF.value,
            default_period=ReportPeriod.MONTHLY.value,
            available_formats=[f.value for f in ReportFormat],
            customizable_options=["period", "format"]
        )
    ]

    return templates


# ============================================================================
# Quick Export Endpoints
# ============================================================================

@router.get("/quick/agents")
async def quick_export_agents(
    format: ReportFormat = Query(ReportFormat.CSV, description="Export format"),
    status: Optional[str] = Query(None, description="Filter by status"),
    role: Optional[str] = Query(None, description="Filter by role"),
    db: AsyncSession = Depends(get_db)
):
    """
    Quick export of agents data

    Exports all agents with optional filtering
    """
    generator = get_report_generator(db)

    filters = {}
    if status:
        filters["status"] = status
    if role:
        filters["role"] = role

    file_data = await generator.export_data("agents", format, filters)

    content_type = get_content_type(format)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"agents_{timestamp}.{format.value}"

    return StreamingResponse(
        io.BytesIO(file_data),
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(len(file_data))
        }
    )


@router.get("/quick/tasks")
async def quick_export_tasks(
    format: ReportFormat = Query(ReportFormat.CSV, description="Export format"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Quick export of tasks data

    Exports all tasks with optional filtering
    """
    generator = get_report_generator(db)

    filters = {}
    if status:
        filters["status"] = status

    file_data = await generator.export_data("tasks", format, filters)

    content_type = get_content_type(format)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"tasks_{timestamp}.{format.value}"

    return StreamingResponse(
        io.BytesIO(file_data),
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(len(file_data))
        }
    )


@router.get("/quick/executions")
async def quick_export_executions(
    format: ReportFormat = Query(ReportFormat.CSV, description="Export format"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Quick export of executions data

    Exports all executions with optional filtering
    """
    generator = get_report_generator(db)

    filters = {}
    if status:
        filters["status"] = status

    file_data = await generator.export_data("executions", format, filters)

    content_type = get_content_type(format)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"executions_{timestamp}.{format.value}"

    return StreamingResponse(
        io.BytesIO(file_data),
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(len(file_data))
        }
    )


# ============================================================================
# In-memory cache for generated reports
# (In production, use Redis or file storage)
# ============================================================================

_report_cache: Dict[str, GeneratedReport] = {}
