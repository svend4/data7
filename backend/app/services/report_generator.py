"""
ReportGenerator Service - PDF and export generation

Provides:
- PDF report generation (system health, performance, analytics)
- CSV/Excel export for data analysis
- Scheduled reports with email delivery
- Customizable report templates
- Data aggregation and visualization
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
import io
import csv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.database import (
    AgentModel,
    TaskModel,
    ExecutionModel,
    ConnectionModel,
)
from app.services.metrics_collector import MetricsCollector


class ReportFormat(str, Enum):
    """Supported report formats"""
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"


class ReportType(str, Enum):
    """Predefined report types"""
    SYSTEM_HEALTH = "system_health"
    PERFORMANCE_SUMMARY = "performance_summary"
    AGENT_ANALYTICS = "agent_analytics"
    EXECUTION_ANALYTICS = "execution_analytics"
    COMPREHENSIVE = "comprehensive"
    CUSTOM = "custom"


class ReportPeriod(str, Enum):
    """Report time periods"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


@dataclass
class ReportConfig:
    """Report generation configuration"""
    report_type: ReportType
    format: ReportFormat
    period: ReportPeriod
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    include_charts: bool = True
    include_summary: bool = True
    include_details: bool = True


@dataclass
class ReportSection:
    """Report section data"""
    title: str
    data: Dict[str, Any]
    charts: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class GeneratedReport:
    """Generated report metadata"""
    id: str
    report_type: ReportType
    format: ReportFormat
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    file_size: int  # bytes
    file_data: bytes
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScheduledReport:
    """Scheduled report configuration"""
    id: str
    name: str
    report_config: ReportConfig
    schedule: str  # Cron expression
    enabled: bool
    recipients: List[str]  # Email addresses
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class ReportGenerator:
    """
    Report generation service

    Features:
    - Multiple format support (PDF, CSV, Excel, JSON)
    - Predefined report templates
    - Custom report building
    - Data aggregation and formatting
    - Chart and table generation
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.metrics_collector = MetricsCollector(db)

    async def generate_report(self, config: ReportConfig) -> GeneratedReport:
        """Generate a report based on configuration"""
        # Set default date range if not specified
        if not config.end_date:
            config.end_date = datetime.utcnow()
        if not config.start_date:
            config.start_date = self._calculate_start_date(config.period, config.end_date)

        # Collect report data based on type
        if config.report_type == ReportType.SYSTEM_HEALTH:
            sections = await self._generate_system_health_report(config)
        elif config.report_type == ReportType.PERFORMANCE_SUMMARY:
            sections = await self._generate_performance_report(config)
        elif config.report_type == ReportType.AGENT_ANALYTICS:
            sections = await self._generate_agent_analytics_report(config)
        elif config.report_type == ReportType.EXECUTION_ANALYTICS:
            sections = await self._generate_execution_analytics_report(config)
        elif config.report_type == ReportType.COMPREHENSIVE:
            sections = await self._generate_comprehensive_report(config)
        else:
            sections = []

        # Generate output in requested format
        if config.format == ReportFormat.PDF:
            file_data = self._generate_pdf(sections, config)
        elif config.format == ReportFormat.CSV:
            file_data = self._generate_csv(sections, config)
        elif config.format == ReportFormat.EXCEL:
            file_data = self._generate_excel(sections, config)
        elif config.format == ReportFormat.JSON:
            file_data = self._generate_json(sections, config)
        else:
            raise ValueError(f"Unsupported format: {config.format}")

        # Create report metadata
        report_id = f"{config.report_type.value}_{int(datetime.utcnow().timestamp())}"

        return GeneratedReport(
            id=report_id,
            report_type=config.report_type,
            format=config.format,
            generated_at=datetime.utcnow(),
            period_start=config.start_date,
            period_end=config.end_date,
            file_size=len(file_data),
            file_data=file_data,
            metadata={
                "period": config.period.value,
                "filters": config.filters,
                "sections_count": len(sections)
            }
        )

    def _calculate_start_date(self, period: ReportPeriod, end_date: datetime) -> datetime:
        """Calculate start date based on period"""
        if period == ReportPeriod.HOURLY:
            return end_date - timedelta(hours=1)
        elif period == ReportPeriod.DAILY:
            return end_date - timedelta(days=1)
        elif period == ReportPeriod.WEEKLY:
            return end_date - timedelta(weeks=1)
        elif period == ReportPeriod.MONTHLY:
            return end_date - timedelta(days=30)
        else:
            return end_date - timedelta(days=7)  # Default to week

    async def _generate_system_health_report(self, config: ReportConfig) -> List[ReportSection]:
        """Generate system health report sections"""
        sections = []

        # Current system health
        health = await self.metrics_collector.get_system_health()

        sections.append(ReportSection(
            title="System Health Overview",
            data={
                "total_agents": health.total_agents,
                "agents_idle": health.agents_idle,
                "agents_busy": health.agents_busy,
                "agents_error": health.agents_error,
                "total_connections": health.total_connections,
                "active_connections": health.active_connections,
                "error_rate": f"{health.error_rate * 100:.2f}%",
                "avg_response_time": f"{health.avg_response_time:.2f}s",
                "active_executions": health.active_executions
            },
            tables=[{
                "title": "Agent Status Distribution",
                "headers": ["Status", "Count", "Percentage"],
                "rows": [
                    ["Idle", health.agents_idle, f"{(health.agents_idle / max(health.total_agents, 1)) * 100:.1f}%"],
                    ["Busy", health.agents_busy, f"{(health.agents_busy / max(health.total_agents, 1)) * 100:.1f}%"],
                    ["Error", health.agents_error, f"{(health.agents_error / max(health.total_agents, 1)) * 100:.1f}%"]
                ]
            }]
        ))

        return sections

    async def _generate_performance_report(self, config: ReportConfig) -> List[ReportSection]:
        """Generate performance report sections"""
        sections = []

        # Performance metrics
        perf_metrics = await self.metrics_collector.get_performance_metrics(
            timeframe=config.end_date - config.start_date
        )

        sections.append(ReportSection(
            title="Performance Summary",
            data={
                "avg_response_time": f"{perf_metrics.avg_response_time:.2f}s",
                "p50_response_time": f"{perf_metrics.p50_response_time:.2f}s",
                "p95_response_time": f"{perf_metrics.p95_response_time:.2f}s",
                "p99_response_time": f"{perf_metrics.p99_response_time:.2f}s",
                "total_requests": perf_metrics.total_requests,
                "requests_per_second": f"{perf_metrics.requests_per_second:.2f}",
                "success_rate": f"{perf_metrics.success_rate * 100:.2f}%",
                "error_rate": f"{perf_metrics.error_rate * 100:.2f}%"
            },
            tables=[{
                "title": "Response Time Percentiles",
                "headers": ["Percentile", "Time (seconds)"],
                "rows": [
                    ["P50 (Median)", f"{perf_metrics.p50_response_time:.2f}"],
                    ["P95", f"{perf_metrics.p95_response_time:.2f}"],
                    ["P99", f"{perf_metrics.p99_response_time:.2f}"],
                    ["Average", f"{perf_metrics.avg_response_time:.2f}"]
                ]
            }]
        ))

        return sections

    async def _generate_agent_analytics_report(self, config: ReportConfig) -> List[ReportSection]:
        """Generate agent analytics report sections"""
        sections = []

        # Agent analytics
        timeframe_days = (config.end_date - config.start_date).days or 7
        agent_analytics = await self.metrics_collector.get_agent_analytics(
            timeframe=timedelta(days=timeframe_days)
        )

        # Top performers
        top_agents = sorted(
            agent_analytics,
            key=lambda a: a.success_rate,
            reverse=True
        )[:10]

        sections.append(ReportSection(
            title="Top Performing Agents",
            data={
                "total_agents": len(agent_analytics),
                "agents_analyzed": len(agent_analytics)
            },
            tables=[{
                "title": "Top 10 Agents by Success Rate",
                "headers": ["Agent ID", "Role", "Tasks Completed", "Success Rate", "Avg Time (s)"],
                "rows": [
                    [
                        agent.agent_id,
                        agent.role,
                        agent.total_tasks_completed,
                        f"{agent.success_rate * 100:.1f}%",
                        f"{agent.avg_execution_time:.2f}"
                    ]
                    for agent in top_agents
                ]
            }]
        ))

        return sections

    async def _generate_execution_analytics_report(self, config: ReportConfig) -> List[ReportSection]:
        """Generate execution analytics report sections"""
        sections = []

        # Execution analytics
        timeframe = config.end_date - config.start_date
        exec_analytics = await self.metrics_collector.get_execution_analytics(timeframe=timeframe)

        sections.append(ReportSection(
            title="Execution Analytics",
            data={
                "total_executions": exec_analytics.total_executions,
                "successful_executions": exec_analytics.successful_executions,
                "failed_executions": exec_analytics.failed_executions,
                "avg_execution_time": f"{exec_analytics.avg_execution_time:.2f}s",
                "total_cost": f"${exec_analytics.total_cost:.4f}",
                "avg_cost": f"${exec_analytics.avg_cost:.4f}"
            },
            tables=[{
                "title": "Execution Status Distribution",
                "headers": ["Status", "Count", "Percentage"],
                "rows": [
                    [
                        "Successful",
                        exec_analytics.successful_executions,
                        f"{(exec_analytics.successful_executions / max(exec_analytics.total_executions, 1)) * 100:.1f}%"
                    ],
                    [
                        "Failed",
                        exec_analytics.failed_executions,
                        f"{(exec_analytics.failed_executions / max(exec_analytics.total_executions, 1)) * 100:.1f}%"
                    ]
                ]
            }]
        ))

        return sections

    async def _generate_comprehensive_report(self, config: ReportConfig) -> List[ReportSection]:
        """Generate comprehensive report with all sections"""
        sections = []

        # Combine all report types
        sections.extend(await self._generate_system_health_report(config))
        sections.extend(await self._generate_performance_report(config))
        sections.extend(await self._generate_agent_analytics_report(config))
        sections.extend(await self._generate_execution_analytics_report(config))

        return sections

    def _generate_pdf(self, sections: List[ReportSection], config: ReportConfig) -> bytes:
        """Generate PDF report (placeholder - requires reportlab)"""
        # In production, use reportlab to generate professional PDFs
        # For now, return a simple text-based representation

        output = io.StringIO()
        output.write("=" * 80 + "\n")
        output.write(f"Meta-Orchestrator Switchboard Report\n")
        output.write(f"Report Type: {config.report_type.value}\n")
        output.write(f"Period: {config.start_date.strftime('%Y-%m-%d')} to {config.end_date.strftime('%Y-%m-%d')}\n")
        output.write(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        output.write("=" * 80 + "\n\n")

        for section in sections:
            output.write(f"\n{section.title}\n")
            output.write("-" * len(section.title) + "\n\n")

            # Write section data
            for key, value in section.data.items():
                output.write(f"{key.replace('_', ' ').title()}: {value}\n")

            # Write tables
            for table in section.tables:
                output.write(f"\n{table['title']}\n")
                output.write("-" * len(table['title']) + "\n")

                # Headers
                header_line = " | ".join(str(h) for h in table['headers'])
                output.write(header_line + "\n")
                output.write("-" * len(header_line) + "\n")

                # Rows
                for row in table['rows']:
                    row_line = " | ".join(str(cell) for cell in row)
                    output.write(row_line + "\n")

                output.write("\n")

        output.write("\n" + "=" * 80 + "\n")
        output.write("End of Report\n")

        return output.getvalue().encode('utf-8')

    def _generate_csv(self, sections: List[ReportSection], config: ReportConfig) -> bytes:
        """Generate CSV export"""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Meta-Orchestrator Switchboard Report"])
        writer.writerow([f"Report Type: {config.report_type.value}"])
        writer.writerow([f"Period: {config.start_date.strftime('%Y-%m-%d')} to {config.end_date.strftime('%Y-%m-%d')}"])
        writer.writerow([f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"])
        writer.writerow([])

        # Write sections
        for section in sections:
            writer.writerow([section.title])
            writer.writerow([])

            # Write section data as key-value pairs
            for key, value in section.data.items():
                writer.writerow([key.replace('_', ' ').title(), value])

            writer.writerow([])

            # Write tables
            for table in section.tables:
                writer.writerow([table['title']])
                writer.writerow(table['headers'])
                for row in table['rows']:
                    writer.writerow(row)
                writer.writerow([])

        return output.getvalue().encode('utf-8')

    def _generate_excel(self, sections: List[ReportSection], config: ReportConfig) -> bytes:
        """Generate Excel export (placeholder - requires openpyxl)"""
        # In production, use openpyxl to create Excel workbooks
        # For now, return CSV format
        return self._generate_csv(sections, config)

    def _generate_json(self, sections: List[ReportSection], config: ReportConfig) -> bytes:
        """Generate JSON export"""
        import json

        report_data = {
            "metadata": {
                "report_type": config.report_type.value,
                "format": config.format.value,
                "period_start": config.start_date.isoformat(),
                "period_end": config.end_date.isoformat(),
                "generated_at": datetime.utcnow().isoformat()
            },
            "sections": [
                {
                    "title": section.title,
                    "data": section.data,
                    "tables": section.tables,
                    "charts": section.charts
                }
                for section in sections
            ]
        }

        return json.dumps(report_data, indent=2).encode('utf-8')

    async def export_data(
        self,
        data_type: str,
        format: ReportFormat,
        filters: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Export raw data in specified format"""
        # This method allows exporting specific data types (agents, tasks, executions)
        # without the full report structure

        if data_type == "agents":
            data = await self._export_agents(filters or {})
        elif data_type == "tasks":
            data = await self._export_tasks(filters or {})
        elif data_type == "executions":
            data = await self._export_executions(filters or {})
        else:
            raise ValueError(f"Unknown data type: {data_type}")

        if format == ReportFormat.CSV:
            return self._data_to_csv(data)
        elif format == ReportFormat.JSON:
            return self._data_to_json(data)
        elif format == ReportFormat.EXCEL:
            return self._data_to_excel(data)
        else:
            raise ValueError(f"Unsupported format for data export: {format}")

    async def _export_agents(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Export agent data"""
        query = select(AgentModel)

        # Apply filters
        if "status" in filters:
            query = query.where(AgentModel.status == filters["status"])
        if "role" in filters:
            query = query.where(AgentModel.role == filters["role"])

        result = await self.db.execute(query)
        agents = result.scalars().all()

        return [
            {
                "id": agent.id,
                "role": agent.role,
                "status": agent.status,
                "model": agent.model,
                "temperature": agent.temperature,
                "max_tokens": agent.max_tokens,
                "total_tasks_completed": agent.total_tasks_completed,
                "created_at": agent.created_at.isoformat()
            }
            for agent in agents
        ]

    async def _export_tasks(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Export task data"""
        query = select(TaskModel)

        # Apply filters
        if "status" in filters:
            query = query.where(TaskModel.status == filters["status"])
        if "priority" in filters:
            query = query.where(TaskModel.priority == filters["priority"])

        result = await self.db.execute(query)
        tasks = result.scalars().all()

        return [
            {
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "agent_id": task.agent_id,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            for task in tasks
        ]

    async def _export_executions(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Export execution data"""
        query = select(ExecutionModel)

        # Apply filters
        if "status" in filters:
            query = query.where(ExecutionModel.status == filters["status"])

        result = await self.db.execute(query)
        executions = result.scalars().all()

        return [
            {
                "id": execution.id,
                "task_id": execution.task_id,
                "agent_id": execution.agent_id,
                "status": execution.status,
                "execution_time": execution.execution_time,
                "tokens_used": execution.tokens_used,
                "cost": execution.cost,
                "created_at": execution.created_at.isoformat()
            }
            for execution in executions
        ]

    def _data_to_csv(self, data: List[Dict[str, Any]]) -> bytes:
        """Convert data to CSV"""
        if not data:
            return b""

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

        return output.getvalue().encode('utf-8')

    def _data_to_json(self, data: List[Dict[str, Any]]) -> bytes:
        """Convert data to JSON"""
        import json
        return json.dumps(data, indent=2).encode('utf-8')

    def _data_to_excel(self, data: List[Dict[str, Any]]) -> bytes:
        """Convert data to Excel (placeholder)"""
        # In production, use openpyxl
        return self._data_to_csv(data)


# Singleton instance
_report_generator_instance: Optional[ReportGenerator] = None


def get_report_generator(db: AsyncSession) -> ReportGenerator:
    """Get or create ReportGenerator singleton"""
    global _report_generator_instance
    if _report_generator_instance is None:
        _report_generator_instance = ReportGenerator(db)
    return _report_generator_instance
