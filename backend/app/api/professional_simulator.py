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

from app.simulators.manufacturing_simulator import (
    ManufacturingSimulator,
    ManufacturingWorker,
    ProductionTask,
    Factory,
    Machine,
    ProductionShift
)

from app.simulators.healthcare_simulator import (
    HealthcareSimulator,
    HealthcareWorker,
    MedicalTask,
    Patient,
    Hospital,
    MedicalEquipment,
    MedicalShift
)

from app.simulators.social_domestic_simulator import (
    SocialDomesticSimulator,
    ServiceWorker,
    ServiceTask,
    Client,
    ServiceLocation,
    ServiceShift
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
            status="operational",
            completion_percentage=40
        ),
        DomainInfo(
            id="healthcare",
            name="Healthcare and Medical",
            description="Diagnosis, treatment, and patient care simulation",
            status="operational",
            completion_percentage=40
        ),
        DomainInfo(
            id="social_services",
            name="Social & Domestic Services",
            description="Legal, social work, domestic, and home care services",
            status="operational",
            completion_percentage=40
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
                "status": "operational",
                "completion": "40%",
                "features": [
                    "Assembly line simulation",
                    "Quality control system",
                    "Machine maintenance tracking",
                    "Shift-based production"
                ]
            },
            "healthcare": {
                "status": "operational",
                "completion": "40%",
                "features": [
                    "Patient diagnosis and treatment",
                    "Multi-role healthcare workers",
                    "Vital signs monitoring",
                    "Treatment outcome tracking"
                ]
            },
            "social_services": {
                "status": "operational",
                "completion": "40%",
                "features": [
                    "Legal services (lawyer, social law specialist)",
                    "Social work and case management",
                    "Domestic services (housekeeper, estate manager)",
                    "Home care (caregiver, home health aide)",
                    "Client satisfaction tracking"
                ]
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


# ============================================================================
# Manufacturing Simulator Endpoints
# ============================================================================

class CreateManufacturingScenarioRequest(BaseModel):
    """Request to create manufacturing scenario"""
    name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")
    num_workers: int = Field(10, ge=1, le=50, description="Number of workers")
    num_machines: int = Field(5, ge=1, le=20, description="Number of machines")
    production_target: int = Field(500, ge=10, le=10000, description="Target units to produce")
    factory_type: str = Field("electronics", description="Type of factory")


class SimulateProductionShiftRequest(BaseModel):
    """Request to simulate production shift"""
    scenario_id: str = Field(..., description="Scenario ID")
    shift_number: int = Field(1, ge=1, le=3, description="Shift number (1, 2, or 3)")
    shift_duration: int = Field(8, ge=1, le=12, description="Shift duration in hours")


class ManufacturingScenarioResponse(BaseModel):
    """Response for manufacturing scenario creation"""
    scenario_id: str
    name: str
    description: str
    num_workers: int
    num_machines: int
    production_target: int
    factory_type: str
    message: str = "Manufacturing scenario created successfully"


class ProductionShiftResponse(BaseModel):
    """Response for production shift simulation"""
    shift_number: int
    duration: int
    workers: int
    tasks: Dict[str, int]
    production: Dict[str, Any]
    efficiency: float
    machines_operational: int
    machines_needing_maintenance: int


class ManufacturingReportResponse(BaseModel):
    """Response for manufacturing performance report"""
    scenario_id: str
    scenario_name: str
    completion_score: float
    production: Dict[str, Any]
    workers: List[Dict[str, Any]]
    machines: Dict[str, int]
    shifts_completed: int


# In-memory storage for manufacturing simulators
manufacturing_simulators: Dict[str, ManufacturingSimulator] = {}


@router.post("/manufacturing/scenario", response_model=ManufacturingScenarioResponse)
async def create_manufacturing_scenario(request: CreateManufacturingScenarioRequest):
    """
    Create a new manufacturing scenario

    Creates a factory with workers, machines, and production tasks.
    Workers are assigned to different shifts and roles (assembler, operator, inspector, maintenance).
    """
    try:
        simulator = ManufacturingSimulator()
        scenario = simulator.create_manufacturing_scenario(
            name=request.name,
            description=request.description,
            num_workers=request.num_workers,
            num_machines=request.num_machines,
            production_target=request.production_target,
            factory_type=request.factory_type
        )

        # Store simulator for later use
        manufacturing_simulators[scenario.id] = simulator

        return ManufacturingScenarioResponse(
            scenario_id=scenario.id,
            name=scenario.name,
            description=scenario.description,
            num_workers=len(scenario.professionals),
            num_machines=request.num_machines,
            production_target=request.production_target,
            factory_type=request.factory_type
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating manufacturing scenario: {str(e)}")


@router.post("/manufacturing/simulate", response_model=ProductionShiftResponse)
async def simulate_production_shift(request: SimulateProductionShiftRequest):
    """
    Simulate a production shift

    Simulates workers performing production tasks over a shift period.
    Workers produce units, perform quality checks, and maintain machines.
    """
    if request.scenario_id not in manufacturing_simulators:
        raise HTTPException(status_code=404, detail="Manufacturing scenario not found")

    try:
        simulator = manufacturing_simulators[request.scenario_id]
        scenario = simulator.scenarios[request.scenario_id]

        # Simulate shift
        report = simulator.simulate_production_shift(
            scenario=scenario,
            shift_number=request.shift_number,
            shift_duration=request.shift_duration
        )

        return ProductionShiftResponse(**report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating production shift: {str(e)}")


@router.get("/manufacturing/report/{scenario_id}", response_model=ManufacturingReportResponse)
async def get_manufacturing_report(scenario_id: str):
    """
    Get manufacturing performance report

    Returns comprehensive report including:
    - Production metrics (units produced, quality rate)
    - Worker performance (by role and shift)
    - Machine status (operational, needing maintenance)
    - Overall efficiency and completion score
    """
    if scenario_id not in manufacturing_simulators:
        raise HTTPException(status_code=404, detail="Manufacturing scenario not found")

    try:
        simulator = manufacturing_simulators[scenario_id]
        scenario = simulator.scenarios[scenario_id]

        report = simulator.get_performance_report(scenario)

        return ManufacturingReportResponse(**report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


# ============================================================================
# Healthcare Simulator Endpoints
# ============================================================================

class CreateHealthcareScenarioRequest(BaseModel):
    """Request to create healthcare scenario"""
    name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")
    num_doctors: int = Field(3, ge=1, le=20, description="Number of doctors")
    num_nurses: int = Field(6, ge=1, le=40, description="Number of nurses")
    num_patients: int = Field(20, ge=1, le=100, description="Number of patients")
    hospital_type: str = Field("general", description="Type of hospital")


class SimulateMedicalShiftRequest(BaseModel):
    """Request to simulate medical shift"""
    scenario_id: str = Field(..., description="Scenario ID")
    shift_number: int = Field(1, ge=1, le=3, description="Shift number (1, 2, or 3)")
    shift_duration: int = Field(8, ge=1, le=12, description="Shift duration in hours")


class HealthcareScenarioResponse(BaseModel):
    """Response for healthcare scenario creation"""
    scenario_id: str
    name: str
    description: str
    num_workers: int
    num_patients: int
    hospital_type: str
    message: str = "Healthcare scenario created successfully"


class MedicalShiftResponse(BaseModel):
    """Response for medical shift simulation"""
    shift_number: int
    duration: int
    workers: int
    patients: Dict[str, int]
    treatments: Dict[str, Any]
    average_quality: float
    tasks_completed: int


class HealthcareReportResponse(BaseModel):
    """Response for healthcare performance report"""
    scenario_id: str
    scenario_name: str
    completion_score: float
    success_rate: float
    patients: Dict[str, Any]
    workers: List[Dict[str, Any]]
    equipment: Dict[str, int]
    shifts_completed: int


# In-memory storage for healthcare simulators
healthcare_simulators: Dict[str, HealthcareSimulator] = {}


@router.post("/healthcare/scenario", response_model=HealthcareScenarioResponse)
async def create_healthcare_scenario(request: CreateHealthcareScenarioRequest):
    """
    Create a new healthcare scenario

    Creates a hospital with doctors, nurses, and patients.
    Patients have various conditions and require diagnosis and treatment.
    """
    try:
        simulator = HealthcareSimulator()
        scenario = simulator.create_healthcare_scenario(
            name=request.name,
            description=request.description,
            num_doctors=request.num_doctors,
            num_nurses=request.num_nurses,
            num_patients=request.num_patients,
            hospital_type=request.hospital_type
        )

        # Store simulator for later use
        healthcare_simulators[scenario.id] = simulator

        total_workers = len(scenario.professionals)

        return HealthcareScenarioResponse(
            scenario_id=scenario.id,
            name=scenario.name,
            description=scenario.description,
            num_workers=total_workers,
            num_patients=request.num_patients,
            hospital_type=request.hospital_type
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating healthcare scenario: {str(e)}")


@router.post("/healthcare/simulate", response_model=MedicalShiftResponse)
async def simulate_medical_shift(request: SimulateMedicalShiftRequest):
    """
    Simulate a medical shift

    Simulates doctors and nurses treating patients over a shift period.
    Doctors diagnose and treat, nurses monitor vitals and administer medication.
    """
    if request.scenario_id not in healthcare_simulators:
        raise HTTPException(status_code=404, detail="Healthcare scenario not found")

    try:
        simulator = healthcare_simulators[request.scenario_id]
        scenario = simulator.scenarios[request.scenario_id]

        # Simulate shift
        report = simulator.simulate_medical_shift(
            scenario=scenario,
            shift_number=request.shift_number,
            shift_duration=request.shift_duration
        )

        return MedicalShiftResponse(**report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating medical shift: {str(e)}")


@router.get("/healthcare/report/{scenario_id}", response_model=HealthcareReportResponse)
async def get_healthcare_report(scenario_id: str):
    """
    Get healthcare performance report

    Returns comprehensive report including:
    - Treatment success rates
    - Patient outcomes (by condition)
    - Healthcare worker performance (by role)
    - Equipment status
    - Overall quality metrics
    """
    if scenario_id not in healthcare_simulators:
        raise HTTPException(status_code=404, detail="Healthcare scenario not found")

    try:
        simulator = healthcare_simulators[scenario_id]
        scenario = simulator.scenarios[scenario_id]

        report = simulator.get_performance_report(scenario)

        return HealthcareReportResponse(**report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


# ============================================================================
# Social & Domestic Services Simulator Endpoints
# ============================================================================

class CreateSocialServiceScenarioRequest(BaseModel):
    """Request to create social/domestic service scenario"""
    name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")
    service_type: str = Field("mixed", description="Service type: legal, social_work, domestic, home_care, mixed")
    num_workers: int = Field(5, ge=1, le=20, description="Number of service workers")
    num_clients: int = Field(15, ge=1, le=50, description="Number of clients")


class SimulateServiceShiftRequest(BaseModel):
    """Request to simulate service shift"""
    scenario_id: str = Field(..., description="Scenario ID")
    shift_type: str = Field("office_hours", description="Shift type: office_hours, home_visit, on_call")
    shift_duration: int = Field(8, ge=1, le=12, description="Shift duration in hours")


class SocialServiceScenarioResponse(BaseModel):
    """Response for social/domestic service scenario creation"""
    scenario_id: str
    name: str
    description: str
    service_type: str
    num_workers: int
    num_clients: int
    message: str = "Social/Domestic service scenario created successfully"


class ServiceShiftResponse(BaseModel):
    """Response for service shift simulation"""
    shift_type: str
    duration: int
    workers: int
    clients: Dict[str, int]
    outcomes: Dict[str, Any]
    average_satisfaction: float
    tasks_completed: int


class SocialServiceReportResponse(BaseModel):
    """Response for social/domestic service performance report"""
    scenario_id: str
    scenario_name: str
    completion_score: float
    success_rate: float
    clients: Dict[str, Any]
    workers: List[Dict[str, Any]]
    shifts_completed: int


# In-memory storage for social/domestic service simulators
social_service_simulators: Dict[str, SocialDomesticSimulator] = {}


@router.post("/social_services/scenario", response_model=SocialServiceScenarioResponse)
async def create_social_service_scenario(request: CreateSocialServiceScenarioRequest):
    """
    Create a new social/domestic service scenario

    Creates a service center with workers (lawyers, social workers, housekeepers, caregivers)
    and clients needing various services.
    """
    try:
        simulator = SocialDomesticSimulator()
        scenario = simulator.create_service_scenario(
            name=request.name,
            description=request.description,
            service_type=request.service_type,
            num_workers=request.num_workers,
            num_clients=request.num_clients
        )

        # Store simulator for later use
        social_service_simulators[scenario.id] = simulator

        return SocialServiceScenarioResponse(
            scenario_id=scenario.id,
            name=scenario.name,
            description=scenario.description,
            service_type=request.service_type,
            num_workers=len(scenario.professionals),
            num_clients=request.num_clients
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating social service scenario: {str(e)}")


@router.post("/social_services/simulate", response_model=ServiceShiftResponse)
async def simulate_service_shift(request: SimulateServiceShiftRequest):
    """
    Simulate a service shift

    Simulates service workers providing services to clients over a shift period.
    Lawyers provide legal advice, social workers coordinate services,
    housekeepers maintain properties, caregivers provide home care.
    """
    if request.scenario_id not in social_service_simulators:
        raise HTTPException(status_code=404, detail="Social service scenario not found")

    try:
        simulator = social_service_simulators[request.scenario_id]
        scenario = simulator.scenarios[request.scenario_id]

        # Simulate shift
        report = simulator.simulate_service_shift(
            scenario=scenario,
            shift_type=request.shift_type,
            shift_duration=request.shift_duration
        )

        return ServiceShiftResponse(**report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating service shift: {str(e)}")


@router.get("/social_services/report/{scenario_id}", response_model=SocialServiceReportResponse)
async def get_social_service_report(scenario_id: str):
    """
    Get social/domestic service performance report

    Returns comprehensive report including:
    - Client satisfaction and progress
    - Service outcomes by worker role
    - Worker performance metrics
    - Overall service quality
    """
    if scenario_id not in social_service_simulators:
        raise HTTPException(status_code=404, detail="Social service scenario not found")

    try:
        simulator = social_service_simulators[scenario_id]
        scenario = simulator.scenarios[scenario_id]

        report = simulator.get_performance_report(scenario)

        return SocialServiceReportResponse(**report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


# Update domains endpoint to include all five domains
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
            status="operational",
            completion_percentage=40
        ),
        DomainInfo(
            id="healthcare",
            name="Healthcare and Medical",
            description="Diagnosis, treatment, and patient care simulation",
            status="operational",
            completion_percentage=40
        ),
        DomainInfo(
            id="social_services",
            name="Social & Domestic Services",
            description="Legal, social work, domestic, and home care services",
            status="operational",
            completion_percentage=40
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
                "status": "operational",
                "completion": "40%",
                "features": [
                    "Assembly line simulation",
                    "Quality control system",
                    "Machine maintenance tracking",
                    "Shift-based production"
                ]
            },
            "healthcare": {
                "status": "operational",
                "completion": "40%",
                "features": [
                    "Patient diagnosis and treatment",
                    "Multi-role healthcare workers",
                    "Vital signs monitoring",
                    "Treatment outcome tracking"
                ]
            },
            "social_services": {
                "status": "operational",
                "completion": "40%",
                "features": [
                    "Legal services (lawyer, social law specialist)",
                    "Social work and case management",
                    "Domestic services (housekeeper, estate manager)",
                    "Home care (caregiver, home health aide)",
                    "Client satisfaction tracking"
                ]
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
