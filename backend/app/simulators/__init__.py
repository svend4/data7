"""
Professional Simulator Framework

Paradigm 2: Professional Simulator
Transforms MMO mechanics into professional training and simulation.

Domains:
- Logistics and Transport (Delivery, Routing, Fleet Management)
- Retail and Service (Customer Service, Sales, Inventory)
- Manufacturing and Production (Assembly Lines, Quality Control)
- Healthcare and Medical (Diagnosis, Treatment, Patient Care)
"""

from .base import (
    ProfessionalSimulator,
    SimulationScenario,
    ProfessionalRole,
    Task,
    Location,
    Resource,
    PerformanceMetrics
)

from .logistics_simulator import (
    LogisticsSimulator,
    DeliveryDriver,
    DeliveryTask,
    Warehouse,
    Vehicle,
    Route
)

from .retail_simulator import (
    RetailSimulator,
    ServiceAgent,
    ServiceTask,
    Customer,
    Product,
    Store,
    Shift
)

from .manufacturing_simulator import (
    ManufacturingSimulator,
    ManufacturingWorker,
    ProductionTask,
    Factory,
    Machine,
    ProductionShift
)

from .healthcare_simulator import (
    HealthcareSimulator,
    HealthcareWorker,
    MedicalTask,
    Patient,
    Hospital,
    MedicalEquipment,
    MedicalShift
)

__all__ = [
    # Base classes
    "ProfessionalSimulator",
    "SimulationScenario",
    "ProfessionalRole",
    "Task",
    "Location",
    "Resource",
    "PerformanceMetrics",

    # Logistics
    "LogisticsSimulator",
    "DeliveryDriver",
    "DeliveryTask",
    "Warehouse",
    "Vehicle",
    "Route",

    # Retail
    "RetailSimulator",
    "ServiceAgent",
    "ServiceTask",
    "Customer",
    "Product",
    "Store",
    "Shift",

    # Manufacturing
    "ManufacturingSimulator",
    "ManufacturingWorker",
    "ProductionTask",
    "Factory",
    "Machine",
    "ProductionShift",

    # Healthcare
    "HealthcareSimulator",
    "HealthcareWorker",
    "MedicalTask",
    "Patient",
    "Hospital",
    "MedicalEquipment",
    "MedicalShift",
]
