"""
Professional Simulator API Endpoints

Provides REST API for professional training simulations.

Endpoints:
- POST /api/simulator/logistics/scenario - Create logistics scenario
- POST /api/simulator/logistics/optimize - Optimize routes with TSP
- POST /api/simulator/logistics/simulate - Simulate full day
- GET /api/simulator/logistics/report/{scenario_id} - Get performance report
- GET /api/simulator/domains - List available domains
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

from app.simulators.logistics_simulator import (
    LogisticsSimulator,
    DeliveryDriver,
    DeliveryTask,
    Warehouse,
    Vehicle,
    Route
)


# ============================================================================
# Router
# ============================================================================

router = APIRouter(
    prefix="/api/simulator",
    tags=["Professional Simulator"]
)


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateLogisticsScenarioRequest(BaseModel):
    """Request to create logistics scenario"""
    name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")
    num_drivers: int = Field(3, ge=1, le=20, description="Number of delivery drivers")
    num_deliveries: int = Field(20, ge=1, le=100, description="Number of delivery tasks")


class LogisticsScenarioResponse(BaseModel):
    """Response with logistics scenario details"""
    scenario_id: str
    name: str
    description: str
    num_drivers: int
    num_deliveries: int
    num_warehouses: int
    objectives: List[Dict[str, Any]]
    status: str


class OptimizeRoutesRequest(BaseModel):
    """Request to optimize routes"""
    scenario_id: str = Field(..., description="Scenario ID")
    algorithm: str = Field("cluster_first_route_second", description="TSP algorithm")


class RouteInfo(BaseModel):
    """Route information"""
    id: str
    driver_name: str
    num_deliveries: int
    total_distance: float
    estimated_time: float
    status: str


class OptimizationResponse(BaseModel):
    """Response with optimized routes"""
    scenario_id: str
    total_routes: int
    total_distance: float
    total_time: float
    max_time: float
    avg_route_load: float
    load_variance: float
    routes: List[RouteInfo]
    suggestions: List[Dict[str, Any]]


class SimulateDayRequest(BaseModel):
    """Request to simulate delivery day"""
    scenario_id: str = Field(..., description="Scenario ID")


class SimulationResponse(BaseModel):
    """Response with simulation results"""
    scenario_id: str
    scenario_name: str
    completion_score: float
    total_performance: float
    tasks: Dict[str, int]
    professionals: List[Dict[str, Any]]
    logistics_metrics: Dict[str, float]


class DomainInfo(BaseModel):
    """Domain information"""
    id: str
    name: str
    description: str
    status: str
    completion_percentage: int


# ============================================================================
# Global State
# ============================================================================

# Store simulators in memory (in production, use database)
logistics_simulators: Dict[str, LogisticsSimulator] = {}


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/logistics/scenario", response_model=LogisticsScenarioResponse)
async def create_logistics_scenario(request: CreateLogisticsScenarioRequest):
    """
    Create new logistics scenario

    Creates a delivery scenario with drivers, vehicles, warehouse, and delivery tasks.
    Uses TSP algorithms for route optimization.

    Example:
    ```json
    {
        "name": "Monday Deliveries",
        "description": "Regular Monday delivery route",
        "num_drivers": 3,
        "num_deliveries": 20
    }
    ```
    """
    # Create simulator
    simulator = LogisticsSimulator()

    # Create scenario
    scenario = simulator.create_logistics_scenario(
        name=request.name,
        description=request.description,
        num_drivers=request.num_drivers,
        num_deliveries=request.num_deliveries
    )

    # Store simulator
    logistics_simulators[scenario.id] = simulator

    return LogisticsScenarioResponse(
        scenario_id=scenario.id,
        name=scenario.name,
        description=scenario.description,
        num_drivers=len(scenario.professionals),
        num_deliveries=len(scenario.tasks),
        num_warehouses=len([l for l in scenario.locations if l.location_type == "warehouse"]),
        objectives=scenario.objectives,
        status="created"
    )


@router.post("/logistics/optimize", response_model=OptimizationResponse)
async def optimize_routes(request: OptimizeRoutesRequest):
    """
    Optimize delivery routes using TSP

    Uses Multi-depot TSP to optimize routes for all drivers.
    Returns optimized routes with distances, times, and suggestions.

    Example:
    ```json
    {
        "scenario_id": "logistics_0",
        "algorithm": "cluster_first_route_second"
    }
    ```
    """
    # Get simulator
    if request.scenario_id not in logistics_simulators:
        raise HTTPException(status_code=404, detail="Scenario not found")

    simulator = logistics_simulators[request.scenario_id]
    scenario = simulator.scenarios[request.scenario_id]

    # Optimize routes
    optimization = simulator.optimize_assignments(scenario)

    return OptimizationResponse(
        scenario_id=request.scenario_id,
        total_routes=optimization["total_routes"],
        total_distance=optimization["total_distance"],
        total_time=optimization["total_time"],
        max_time=optimization["max_time"],
        avg_route_load=optimization["avg_route_load"],
        load_variance=optimization["load_variance"],
        routes=[
            RouteInfo(
                id=r["id"],
                driver_name=r["driver"],
                num_deliveries=r["num_deliveries"],
                total_distance=r["distance"],
                estimated_time=r["estimated_time"],
                status="optimized"
            )
            for r in optimization["routes"]
        ],
        suggestions=optimization["suggestions"]
    )


@router.post("/logistics/simulate", response_model=SimulationResponse)
async def simulate_delivery_day(request: SimulateDayRequest):
    """
    Simulate full delivery day

    Simulates execution of all delivery routes, tracks performance,
    and generates comprehensive report.

    Example:
    ```json
    {
        "scenario_id": "logistics_0"
    }
    ```
    """
    # Get simulator
    if request.scenario_id not in logistics_simulators:
        raise HTTPException(status_code=404, detail="Scenario not found")

    simulator = logistics_simulators[request.scenario_id]
    scenario = simulator.scenarios[request.scenario_id]

    # Simulate day
    report = simulator.simulate_day(scenario)

    return SimulationResponse(
        scenario_id=report["scenario_id"],
        scenario_name=report["scenario_name"],
        completion_score=report["completion_score"],
        total_performance=report["total_performance"],
        tasks=report["tasks"],
        professionals=report["professionals"],
        logistics_metrics=report["logistics_metrics"]
    )


@router.get("/logistics/report/{scenario_id}")
async def get_performance_report(scenario_id: str):
    """
    Get performance report for scenario

    Returns detailed performance metrics for completed scenario.
    """
    # Get simulator
    if scenario_id not in logistics_simulators:
        raise HTTPException(status_code=404, detail="Scenario not found")

    simulator = logistics_simulators[scenario_id]
    scenario = simulator.scenarios[scenario_id]

    # Generate report
    report = simulator.get_performance_report(scenario)

    return report


@router.get("/domains", response_model=List[DomainInfo])
async def list_domains():
    """
    List available professional simulator domains

    Returns all available domains with their implementation status.
    """
    domains = [
        DomainInfo(
            id="logistics",
            name="Logistics and Transport",
            description="Delivery, routing, and fleet management simulation",
            status="operational",
            completion_percentage=60
        ),
        DomainInfo(
            id="retail",
            name="Retail and Service",
            description="Customer service, sales, and inventory management",
            status="planned",
            completion_percentage=0
        ),
        DomainInfo(
            id="manufacturing",
            name="Manufacturing and Production",
            description="Assembly lines, quality control, and production optimization",
            status="planned",
            completion_percentage=0
        ),
        DomainInfo(
            id="healthcare",
            name="Healthcare and Medical",
            description="Diagnosis, treatment, and patient care simulation",
            status="planned",
            completion_percentage=0
        ),
    ]

    return domains


@router.get("/")
async def simulator_info():
    """
    Get Professional Simulator information

    Returns general information about the simulator and its capabilities.
    """
    return {
        "name": "Professional Simulator",
        "version": "1.0",
        "paradigm": "Paradigm 2 - Professional Simulator",
        "description": "Transform MMO mechanics into professional training simulations",
        "domains": {
            "logistics": {
                "status": "operational",
                "completion": "60%",
                "features": [
                    "Multi-depot TSP optimization",
                    "Vehicle routing",
                    "Performance tracking",
                    "Real-time simulation"
                ]
            },
            "retail": {
                "status": "planned",
                "completion": "0%"
            },
            "manufacturing": {
                "status": "planned",
                "completion": "0%"
            },
            "healthcare": {
                "status": "planned",
                "completion": "0%"
            }
        },
        "use_cases": [
            "Employee training",
            "Process optimization",
            "Performance evaluation",
            "Scenario planning"
        ],
        "mappings": {
            "mmo_character": "Professional Role",
            "mmo_quest": "Professional Task",
            "mmo_location": "Work Location",
            "mmo_item": "Resource/Tool",
            "mmo_xp": "Performance Metrics"
        }
    }


# ============================================================================
# Retail Simulator Endpoints
# ============================================================================

# Import retail simulator
from app.simulators.retail_simulator import (
    RetailSimulator,
    ServiceAgent,
    Customer,
    Product,
    Store
)


class CreateRetailScenarioRequest(BaseModel):
    """Request to create retail scenario"""
    name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")
    num_agents: int = Field(3, ge=1, le=20, description="Number of service agents")
    num_customers: int = Field(30, ge=1, le=200, description="Number of customers")
    num_products: int = Field(20, ge=5, le=100, description="Number of products")
    store_type: str = Field("retail", description="Type of store")


class RetailScenarioResponse(BaseModel):
    """Response with retail scenario details"""
    scenario_id: str
    name: str
    description: str
    num_agents: int
    num_customers: int
    num_products: int
    store_type: str
    objectives: List[Dict[str, Any]]
    status: str


class SimulateShiftRequest(BaseModel):
    """Request to simulate retail shift"""
    scenario_id: str = Field(..., description="Scenario ID")
    shift_duration: int = Field(480, ge=60, le=720, description="Shift duration in minutes")


class RetailSimulationResponse(BaseModel):
    """Response with retail simulation results"""
    scenario_id: str
    scenario_name: str
    completion_score: float
    total_performance: float
    tasks: Dict[str, int]
    professionals: List[Dict[str, Any]]
    retail_metrics: Dict[str, float]


# Global state for retail simulators
retail_simulators: Dict[str, RetailSimulator] = {}


@router.post("/retail/scenario", response_model=RetailScenarioResponse)
async def create_retail_scenario(request: CreateRetailScenarioRequest):
    """
    Create new retail scenario

    Creates a retail scenario with service agents, customers, products, and store.
    Simulates customer service, sales, and inventory management.

    Example:
    ```json
    {
        "name": "Monday Shift",
        "description": "Regular Monday retail operations",
        "num_agents": 3,
        "num_customers": 30,
        "num_products": 20,
        "store_type": "retail"
    }
    ```
    """
    # Create simulator
    simulator = RetailSimulator()

    # Create scenario
    scenario = simulator.create_retail_scenario(
        name=request.name,
        description=request.description,
        num_agents=request.num_agents,
        num_customers=request.num_customers,
        num_products=request.num_products,
        store_type=request.store_type
    )

    # Store simulator
    retail_simulators[scenario.id] = simulator

    return RetailScenarioResponse(
        scenario_id=scenario.id,
        name=scenario.name,
        description=scenario.description,
        num_agents=len(scenario.professionals),
        num_customers=len(simulator.customers),
        num_products=len(simulator.products),
        store_type=request.store_type,
        objectives=scenario.objectives,
        status="created"
    )


@router.post("/retail/simulate", response_model=RetailSimulationResponse)
async def simulate_retail_shift(request: SimulateShiftRequest):
    """
    Simulate retail shift

    Simulates a complete retail shift with customer service, sales,
    and performance tracking.

    Example:
    ```json
    {
        "scenario_id": "retail_0",
        "shift_duration": 480
    }
    ```
    """
    # Get simulator
    if request.scenario_id not in retail_simulators:
        raise HTTPException(status_code=404, detail="Scenario not found")

    simulator = retail_simulators[request.scenario_id]
    scenario = simulator.scenarios[request.scenario_id]

    # Simulate shift
    report = simulator.simulate_shift(scenario, request.shift_duration)

    return RetailSimulationResponse(
        scenario_id=report["scenario_id"],
        scenario_name=report["scenario_name"],
        completion_score=report["completion_score"],
        total_performance=report["total_performance"],
        tasks=report["tasks"],
        professionals=report["professionals"],
        retail_metrics=report["retail_metrics"]
    )


@router.get("/retail/report/{scenario_id}")
async def get_retail_performance_report(scenario_id: str):
    """
    Get performance report for retail scenario

    Returns detailed performance metrics for completed retail scenario.
    """
    # Get simulator
    if scenario_id not in retail_simulators:
        raise HTTPException(status_code=404, detail="Scenario not found")

    simulator = retail_simulators[scenario_id]
    scenario = simulator.scenarios[scenario_id]

    # Generate report
    report = simulator.get_performance_report(scenario)

    # Add retail-specific metrics if available
    if simulator.customers:
        report["customer_metrics"] = {
            "total_customers": len(simulator.customers),
            "avg_satisfaction": sum(c.satisfaction for c in simulator.customers) / len(simulator.customers),
            "happy_customers": sum(1 for c in simulator.customers if c.satisfaction > 0.8),
            "unhappy_customers": sum(1 for c in simulator.customers if c.satisfaction < 0.5)
        }

    if simulator.products:
        report["product_metrics"] = {
            "total_products": len(simulator.products),
            "products_sold": sum(p.metadata["sales_count"] for p in simulator.products),
            "total_revenue": sum(p.metadata["revenue"] for p in simulator.products),
            "best_seller": max(simulator.products, key=lambda p: p.metadata["sales_count"]).name
        }

    return report


# Update domains endpoint to include retail
@router.get("/domains", response_model=List[DomainInfo])
async def list_domains():
    """
    List available professional simulator domains

    Returns all available domains with their implementation status.
    """
    domains = [
        DomainInfo(
            id="logistics",
            name="Logistics and Transport",
            description="Delivery, routing, and fleet management simulation",
            status="operational",
            completion_percentage=60
        ),
        DomainInfo(
            id="retail",
            name="Retail and Service",
            description="Customer service, sales, and inventory management",
            status="operational",
            completion_percentage=40
        ),
        DomainInfo(
            id="manufacturing",
            name="Manufacturing and Production",
            description="Assembly lines, quality control, and production optimization",
            status="planned",
            completion_percentage=0
        ),
        DomainInfo(
            id="healthcare",
            name="Healthcare and Medical",
            description="Diagnosis, treatment, and patient care simulation",
            status="planned",
            completion_percentage=0
        ),
    ]

    return domains


# Update simulator info endpoint
@router.get("/")
async def simulator_info():
    """
    Get Professional Simulator information

    Returns general information about the simulator and its capabilities.
    """
    return {
        "name": "Professional Simulator",
        "version": "1.0",
        "paradigm": "Paradigm 2 - Professional Simulator",
        "description": "Transform MMO mechanics into professional training simulations",
        "domains": {
            "logistics": {
                "status": "operational",
                "completion": "60%",
                "features": [
                    "Multi-depot TSP optimization",
                    "Vehicle routing",
                    "Performance tracking",
                    "Real-time simulation"
                ]
            },
            "retail": {
                "status": "operational",
                "completion": "40%",
                "features": [
                    "Customer service simulation",
                    "Sales and inventory tracking",
                    "Queue management",
                    "Satisfaction metrics"
                ]
            },
            "manufacturing": {
                "status": "planned",
                "completion": "0%"
            },
            "healthcare": {
                "status": "planned",
                "completion": "0%"
            }
        },
        "use_cases": [
            "Employee training",
            "Process optimization",
            "Performance evaluation",
            "Scenario planning"
        ],
        "mappings": {
            "mmo_character": "Professional Role",
            "mmo_quest": "Professional Task",
            "mmo_location": "Work Location",
            "mmo_item": "Resource/Tool",
            "mmo_xp": "Performance Metrics"
        }
    }
