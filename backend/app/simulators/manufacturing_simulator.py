"""
Manufacturing and Production Professional Simulator

Domain: Assembly, Production, Quality Control
Status: 0% → 40%

Maps manufacturing operations to MMO mechanics:
- Assembly Line Worker → MMO Crafter (builds items)
- Production Task → MMO Crafting Quest
- Factory Floor → MMO Workshop/Forge
- Tool/Machine → MMO Crafting Tool
- Quality Control → MMO Item Inspection
- Shift → MMO Dungeon Run

Simulates realistic manufacturing scenarios with quality tracking.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import random

from .base import (
    ProfessionalSimulator,
    SimulationScenario,
    ProfessionalRole,
    Task,
    TaskType,
    TaskStatus,
    Location,
    Resource,
    ResourceType,
    PerformanceMetrics
)


class WorkerRole(Enum):
    """Manufacturing worker roles"""
    ASSEMBLER = "assembler"
    MACHINE_OPERATOR = "machine_operator"
    QUALITY_INSPECTOR = "quality_inspector"
    MAINTENANCE_TECH = "maintenance_tech"
    SUPERVISOR = "supervisor"


class ProductionTaskType(Enum):
    """Types of production tasks"""
    ASSEMBLY = "assembly"
    MACHINING = "machining"
    QUALITY_CHECK = "quality_check"
    PACKAGING = "packaging"
    MAINTENANCE = "maintenance"
    SETUP = "setup"


class QualityStatus(Enum):
    """Quality control status"""
    PASS = "pass"
    FAIL = "fail"
    REWORK = "rework"
    PENDING = "pending"


@dataclass
class Machine(Resource):
    """
    Manufacturing machine (maps to MMO Crafting Station)

    Attributes:
    - production_rate: Units per hour
    - maintenance_required: Needs maintenance
    - downtime_hours: Hours of downtime
    """

    def __init__(
        self,
        id: str,
        name: str,
        machine_type: str = "assembly",
        production_rate: float = 10.0,  # units/hour
        reliability: float = 0.95  # 0-1
    ):
        super().__init__(
            id=id,
            name=name,
            resource_type=ResourceType.EQUIPMENT,
            capacity=1.0
        )
        self.machine_type = machine_type
        self.production_rate = production_rate
        self.reliability = reliability
        self.is_operational = True
        self.hours_since_maintenance = 0.0
        self.metadata.update({
            "machine_type": machine_type,
            "production_rate": production_rate,
            "reliability": reliability,
            "total_units_produced": 0,
            "total_downtime_hours": 0.0
        })

    def operate(self, hours: float) -> int:
        """Operate machine for specified hours"""
        self.hours_since_maintenance += hours

        # Check if breakdown occurs
        breakdown_chance = 0.01 * (self.hours_since_maintenance / 100.0)
        if random.random() < breakdown_chance:
            self.is_operational = False
            return 0

        # Calculate production
        units = int(self.production_rate * hours * self.reliability)
        self.metadata["total_units_produced"] += units
        return units

    def perform_maintenance(self):
        """Perform maintenance on machine"""
        self.hours_since_maintenance = 0.0
        self.is_operational = True
        self.reliability = min(0.99, self.reliability + 0.05)

    def needs_maintenance(self) -> bool:
        """Check if machine needs maintenance"""
        return self.hours_since_maintenance > 160.0  # ~1 month


@dataclass
class Factory(Location):
    """
    Factory location (maps to MMO Guild Hall/Workshop)
    """

    def __init__(
        self,
        id: str,
        name: str,
        coordinates: tuple,
        floor_space: int = 10000,  # square meters
        shift_hours: Tuple[int, int, int] = (8, 8, 8)  # 3 shifts
    ):
        super().__init__(
            id=id,
            name=name,
            location_type="factory",
            coordinates=coordinates,
            capacity=floor_space
        )
        self.shift_hours = shift_hours
        self.metadata.update({
            "floor_space": floor_space,
            "shift_hours": shift_hours,
            "total_production": 0,
            "quality_rate": 0.0,
            "operational_efficiency": 0.0
        })


@dataclass
class ProductionTask(Task):
    """
    Production task (maps to MMO Crafting Quest)

    Attributes:
    - assembly_steps: List of steps to complete
    - target_quantity: Number of units to produce
    - quality_standard: Minimum quality score (0-1)
    - machine_required: Machine needed for task
    """

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        production_type: ProductionTaskType,
        factory: Factory,
        target_quantity: int = 1,
        quality_standard: float = 0.95,
        machine_id: Optional[str] = None,
        priority: int = 1
    ):
        super().__init__(
            id=id,
            name=name,
            description=description,
            task_type=TaskType.PRODUCTION,
            location=factory,
            priority=priority
        )
        self.production_type = production_type
        self.target_quantity = target_quantity
        self.quality_standard = quality_standard
        self.machine_id = machine_id

        # Production tracking
        self.units_produced = 0
        self.units_passed = 0
        self.units_failed = 0
        self.defects: List[str] = []

        # Assembly steps (for assembly tasks)
        self.assembly_steps: List[str] = []
        self.completed_steps: List[str] = []

        # Quality tracking
        self.quality_score = 0.0
        self.quality_status = QualityStatus.PENDING

        self.metadata.update({
            "production_type": production_type.value,
            "target_quantity": target_quantity,
            "quality_standard": quality_standard,
            "actual_quality": 0.0
        })

    def add_assembly_step(self, step: str):
        """Add assembly step"""
        self.assembly_steps.append(step)

    def complete_step(self, step: str):
        """Mark assembly step as completed"""
        if step in self.assembly_steps and step not in self.completed_steps:
            self.completed_steps.append(step)

    def is_complete(self) -> bool:
        """Check if production task is complete"""
        steps_complete = len(self.completed_steps) == len(self.assembly_steps)
        quantity_complete = self.units_produced >= self.target_quantity
        return steps_complete and quantity_complete

    def calculate_quality_score(self) -> float:
        """Calculate quality score based on defects"""
        if self.units_produced == 0:
            return 0.0

        return self.units_passed / self.units_produced

    def perform_quality_check(self, inspector_skill: float = 0.8) -> QualityStatus:
        """Perform quality check on produced units"""
        # Quality influenced by inspector skill
        detected_quality = self.quality_score * (0.5 + inspector_skill * 0.5)

        if detected_quality >= self.quality_standard:
            self.quality_status = QualityStatus.PASS
        elif detected_quality >= self.quality_standard * 0.8:
            self.quality_status = QualityStatus.REWORK
        else:
            self.quality_status = QualityStatus.FAIL

        return self.quality_status


@dataclass
class ManufacturingWorker(ProfessionalRole):
    """
    Manufacturing worker (maps to MMO Crafter)

    Specializations:
    - Assembler: Manual assembly work
    - Machine Operator: Operates machines
    - Quality Inspector: Checks quality
    - Maintenance Tech: Maintains equipment
    """

    def __init__(
        self,
        id: str,
        name: str,
        role: WorkerRole,
        factory: Factory,
        shift_number: int = 1  # 1, 2, or 3
    ):
        super().__init__(
            id=id,
            name=name,
            role_type="manufacturing_worker"
        )
        self.worker_role = role
        self.factory = factory
        self.shift_number = shift_number

        # Add role-specific skills
        self._initialize_skills_for_role(role)

        # Production tracking
        self.units_produced_today = 0
        self.defects_found_today = 0
        self.machines_maintained_today = 0

        self.metadata.update({
            "worker_role": role.value,
            "factory_id": factory.id,
            "shift_number": shift_number,
            "specialization": role.value
        })

    def _initialize_skills_for_role(self, role: WorkerRole):
        """Initialize skills based on worker role"""
        if role == WorkerRole.ASSEMBLER:
            self.add_skill("manual_dexterity", level=3)
            self.add_skill("assembly", level=3)
            self.add_skill("attention_to_detail", level=2)
        elif role == WorkerRole.MACHINE_OPERATOR:
            self.add_skill("machine_operation", level=3)
            self.add_skill("troubleshooting", level=2)
            self.add_skill("process_optimization", level=2)
        elif role == WorkerRole.QUALITY_INSPECTOR:
            self.add_skill("quality_inspection", level=4)
            self.add_skill("attention_to_detail", level=4)
            self.add_skill("measurement", level=3)
        elif role == WorkerRole.MAINTENANCE_TECH:
            self.add_skill("equipment_maintenance", level=4)
            self.add_skill("troubleshooting", level=3)
            self.add_skill("electrical", level=2)
        elif role == WorkerRole.SUPERVISOR:
            self.add_skill("leadership", level=3)
            self.add_skill("planning", level=3)
            self.add_skill("quality_management", level=2)

    def produce_units(
        self,
        task: ProductionTask,
        machine: Optional[Machine] = None,
        hours: float = 1.0
    ) -> int:
        """Produce units for task"""
        if machine and not machine.is_operational:
            return 0

        # Calculate production based on worker skill and machine
        base_rate = 5.0  # units/hour for manual work

        if machine:
            base_rate = machine.production_rate

        # Apply skill multiplier
        skill_multiplier = 1.0
        if self.worker_role == WorkerRole.ASSEMBLER:
            skill_multiplier = 0.5 + (self.get_skill_level("assembly") * 0.1)
        elif self.worker_role == WorkerRole.MACHINE_OPERATOR:
            skill_multiplier = 0.5 + (self.get_skill_level("machine_operation") * 0.1)

        units = int(base_rate * skill_multiplier * hours)

        # Calculate quality
        quality_skill = self.get_skill_level("attention_to_detail") / 5.0
        quality = min(1.0, 0.7 + quality_skill * 0.3 + random.uniform(-0.05, 0.05))

        # Update task
        task.units_produced += units
        if quality >= task.quality_standard:
            task.units_passed += units
        else:
            task.units_failed += units
            task.defects.append(f"Quality below standard: {quality:.2f}")

        task.quality_score = task.calculate_quality_score()

        # Track worker production
        self.units_produced_today += units

        return units

    def inspect_quality(self, task: ProductionTask) -> QualityStatus:
        """Inspect quality of produced units"""
        if self.worker_role != WorkerRole.QUALITY_INSPECTOR:
            return task.quality_status

        inspector_skill = self.get_skill_level("quality_inspection") / 5.0
        status = task.perform_quality_check(inspector_skill)

        # Track defects found
        if status == QualityStatus.FAIL:
            self.defects_found_today += task.units_failed

        return status

    def maintain_machine(self, machine: Machine):
        """Perform maintenance on machine"""
        if self.worker_role != WorkerRole.MAINTENANCE_TECH:
            return

        machine.perform_maintenance()
        self.machines_maintained_today += 1

        # Gain XP for maintenance
        self.metrics.experience_points += 10.0


@dataclass
class ProductionShift:
    """
    Production shift (maps to MMO Dungeon Run/Raid)
    """
    id: str
    shift_number: int  # 1, 2, or 3
    start_hour: int  # 0-23
    duration: int  # hours
    workers: List[ManufacturingWorker] = field(default_factory=list)
    tasks: List[ProductionTask] = field(default_factory=list)
    machines: List[Machine] = field(default_factory=list)

    # Shift metrics
    total_units_produced: int = 0
    total_units_passed: int = 0
    total_defects: int = 0
    efficiency_score: float = 0.0
    quality_rate: float = 0.0

    def add_worker(self, worker: ManufacturingWorker):
        """Add worker to shift"""
        self.workers.append(worker)

    def add_task(self, task: ProductionTask):
        """Add production task to shift"""
        self.tasks.append(task)

    def add_machine(self, machine: Machine):
        """Add machine to shift"""
        self.machines.append(machine)

    def calculate_metrics(self):
        """Calculate shift performance metrics"""
        self.total_units_produced = sum(t.units_produced for t in self.tasks)
        self.total_units_passed = sum(t.units_passed for t in self.tasks)
        self.total_defects = sum(t.units_failed for t in self.tasks)

        if self.total_units_produced > 0:
            self.quality_rate = self.total_units_passed / self.total_units_produced

        # Calculate efficiency (actual vs. target)
        target_units = sum(t.target_quantity for t in self.tasks)
        if target_units > 0:
            self.efficiency_score = min(1.0, self.total_units_produced / target_units)


class ManufacturingSimulator(ProfessionalSimulator):
    """
    Manufacturing operations simulator

    Simulates:
    - Assembly line production
    - Machine operations
    - Quality control
    - Shift management
    - Maintenance scheduling
    """

    def __init__(self):
        super().__init__(domain="manufacturing")
        self.factories: Dict[str, Factory] = {}
        self.machines: Dict[str, Machine] = {}
        self.shifts: Dict[str, ProductionShift] = {}

    def create_manufacturing_scenario(
        self,
        name: str,
        description: str,
        num_workers: int = 10,
        num_machines: int = 5,
        production_target: int = 500,
        factory_type: str = "electronics"
    ) -> SimulationScenario:
        """
        Create manufacturing scenario

        Args:
            name: Scenario name
            description: Scenario description
            num_workers: Number of workers
            num_machines: Number of machines
            production_target: Target units to produce
            factory_type: Type of factory (electronics, automotive, etc.)

        Returns:
            SimulationScenario with workers, machines, and tasks
        """
        scenario = self.create_scenario(
            name=name,
            description=description,
            scenario_type="manufacturing"
        )

        # Create factory
        factory = Factory(
            id=f"factory_001",
            name=f"{factory_type.title()} Manufacturing Plant",
            coordinates=(random.uniform(-90, 90), random.uniform(-180, 180)),
            floor_space=10000
        )
        scenario.add_location(factory)
        self.factories[factory.id] = factory

        # Create machines
        machine_types = ["assembly", "welding", "testing", "packaging"]
        for i in range(num_machines):
            machine = Machine(
                id=f"machine_{i:03d}",
                name=f"{machine_types[i % len(machine_types)].title()} Machine {i+1}",
                machine_type=machine_types[i % len(machine_types)],
                production_rate=random.uniform(8.0, 15.0),
                reliability=random.uniform(0.90, 0.98)
            )
            self.machines[machine.id] = machine

        # Create workers with different roles
        worker_roles = [
            WorkerRole.ASSEMBLER,
            WorkerRole.MACHINE_OPERATOR,
            WorkerRole.QUALITY_INSPECTOR,
            WorkerRole.MAINTENANCE_TECH
        ]

        for i in range(num_workers):
            # Distribute roles (more assemblers/operators, fewer inspectors/maintenance)
            if i < num_workers * 0.4:
                role = WorkerRole.ASSEMBLER
            elif i < num_workers * 0.7:
                role = WorkerRole.MACHINE_OPERATOR
            elif i < num_workers * 0.85:
                role = WorkerRole.QUALITY_INSPECTOR
            else:
                role = WorkerRole.MAINTENANCE_TECH

            shift_number = (i % 3) + 1  # Distribute across 3 shifts

            worker = ManufacturingWorker(
                id=f"worker_{i:03d}",
                name=f"Worker {i+1}",
                role=role,
                factory=factory,
                shift_number=shift_number
            )
            scenario.add_professional(worker)

        # Create production tasks
        task_types = [
            ProductionTaskType.ASSEMBLY,
            ProductionTaskType.MACHINING,
            ProductionTaskType.QUALITY_CHECK,
            ProductionTaskType.PACKAGING
        ]

        tasks_per_type = production_target // len(task_types)

        for i, task_type in enumerate(task_types):
            task = ProductionTask(
                id=f"task_{i:03d}",
                name=f"{task_type.value.title()} Task {i+1}",
                description=f"Produce {tasks_per_type} units via {task_type.value}",
                production_type=task_type,
                factory=factory,
                target_quantity=tasks_per_type,
                quality_standard=0.95,
                machine_id=self.machines[f"machine_{i:03d}"].id if i < num_machines else None,
                priority=random.randint(1, 3)
            )

            # Add assembly steps for assembly tasks
            if task_type == ProductionTaskType.ASSEMBLY:
                task.add_assembly_step("Prepare components")
                task.add_assembly_step("Assemble main unit")
                task.add_assembly_step("Install fasteners")
                task.add_assembly_step("Connect wiring")
                task.add_assembly_step("Final assembly")

            scenario.add_task(task)

        # Store scenario
        self.scenarios[scenario.id] = scenario

        return scenario

    def assign_tasks_to_shift(
        self,
        scenario: SimulationScenario,
        shift_number: int
    ) -> ProductionShift:
        """
        Assign tasks to workers in a shift

        Args:
            scenario: Simulation scenario
            shift_number: Shift number (1, 2, or 3)

        Returns:
            ProductionShift with assigned workers and tasks
        """
        shift_hours = [8, 8, 8]  # 8-hour shifts
        start_hours = [6, 14, 22]  # 6 AM, 2 PM, 10 PM

        shift = ProductionShift(
            id=f"shift_{shift_number}",
            shift_number=shift_number,
            start_hour=start_hours[shift_number - 1],
            duration=shift_hours[shift_number - 1]
        )

        # Add workers from this shift
        shift_workers = [
            p for p in scenario.professionals
            if isinstance(p, ManufacturingWorker) and p.shift_number == shift_number
        ]

        for worker in shift_workers:
            shift.add_worker(worker)

        # Assign tasks based on worker roles
        for task in scenario.tasks:
            production_task = task
            if isinstance(production_task, ProductionTask):
                shift.add_task(production_task)

        # Add machines
        for machine_id, machine in self.machines.items():
            shift.add_machine(machine)

        self.shifts[shift.id] = shift

        return shift

    def simulate_production_shift(
        self,
        scenario: SimulationScenario,
        shift_number: int = 1,
        shift_duration: int = 8
    ) -> Dict[str, Any]:
        """
        Simulate a production shift

        Args:
            scenario: Simulation scenario
            shift_number: Which shift (1, 2, or 3)
            shift_duration: Shift duration in hours

        Returns:
            Dictionary with shift results
        """
        # Create shift
        shift = self.assign_tasks_to_shift(scenario, shift_number)

        # Simulate production hour by hour
        for hour in range(shift_duration):
            # Assign workers to tasks
            for worker in shift.workers:
                if isinstance(worker, ManufacturingWorker):
                    # Find suitable task for worker
                    suitable_task = None

                    if worker.worker_role == WorkerRole.QUALITY_INSPECTOR:
                        # Inspectors check completed tasks
                        for task in shift.tasks:
                            if isinstance(task, ProductionTask) and task.units_produced > 0:
                                suitable_task = task
                                break
                    elif worker.worker_role == WorkerRole.MAINTENANCE_TECH:
                        # Maintenance techs maintain machines
                        for machine in shift.machines:
                            if machine.needs_maintenance():
                                worker.maintain_machine(machine)
                                break
                    else:
                        # Assemblers and operators produce units
                        for task in shift.tasks:
                            if isinstance(task, ProductionTask) and not task.is_complete():
                                suitable_task = task
                                break

                    if suitable_task:
                        # Find machine for task
                        machine = None
                        if suitable_task.machine_id:
                            machine = next(
                                (m for m in shift.machines if m.id == suitable_task.machine_id),
                                None
                            )

                        if worker.worker_role == WorkerRole.QUALITY_INSPECTOR:
                            # Perform quality inspection
                            worker.inspect_quality(suitable_task)
                        else:
                            # Produce units
                            units = worker.produce_units(suitable_task, machine, hours=1.0)

                            # Award XP based on production
                            xp_gain = units * 2.0
                            worker.metrics.experience_points += xp_gain
                            worker.metrics.tasks_completed += 1

        # Calculate shift metrics
        shift.calculate_metrics()

        # Update scenario performance metrics
        for worker in shift.workers:
            worker.metrics.update_efficiency(shift.efficiency_score)
            worker.metrics.update_quality(shift.quality_rate)

        return {
            "shift_number": shift_number,
            "duration": shift_duration,
            "workers": len(shift.workers),
            "tasks": {
                "total": len(shift.tasks),
                "completed": len([t for t in shift.tasks if t.status == TaskStatus.COMPLETED]),
                "in_progress": len([t for t in shift.tasks if t.status == TaskStatus.IN_PROGRESS])
            },
            "production": {
                "total_units": shift.total_units_produced,
                "passed_units": shift.total_units_passed,
                "failed_units": shift.total_defects,
                "quality_rate": shift.quality_rate
            },
            "efficiency": shift.efficiency_score,
            "machines_operational": len([m for m in shift.machines if m.is_operational]),
            "machines_needing_maintenance": len([m for m in shift.machines if m.needs_maintenance()])
        }

    def get_performance_report(self, scenario: SimulationScenario) -> Dict[str, Any]:
        """
        Generate performance report for manufacturing scenario

        Args:
            scenario: Simulation scenario

        Returns:
            Dictionary with performance metrics
        """
        total_units = sum(
            t.units_produced for t in scenario.tasks if isinstance(t, ProductionTask)
        )
        total_passed = sum(
            t.units_passed for t in scenario.tasks if isinstance(t, ProductionTask)
        )
        total_failed = sum(
            t.units_failed for t in scenario.tasks if isinstance(t, ProductionTask)
        )

        quality_rate = total_passed / total_units if total_units > 0 else 0.0

        target_units = sum(
            t.target_quantity for t in scenario.tasks if isinstance(t, ProductionTask)
        )
        completion_score = min(1.0, total_units / target_units) if target_units > 0 else 0.0

        # Worker statistics
        worker_stats = []
        for professional in scenario.professionals:
            if isinstance(professional, ManufacturingWorker):
                worker_stats.append({
                    "id": professional.id,
                    "name": professional.name,
                    "role": professional.worker_role.value,
                    "shift": professional.shift_number,
                    "units_produced": professional.units_produced_today,
                    "defects_found": professional.defects_found_today,
                    "machines_maintained": professional.machines_maintained_today,
                    "level": professional.metrics.level,
                    "experience": professional.metrics.experience_points,
                    "efficiency": professional.metrics.efficiency_score,
                    "quality": professional.metrics.quality_score
                })

        return {
            "scenario_id": scenario.id,
            "scenario_name": scenario.name,
            "completion_score": completion_score,
            "production": {
                "total_units": total_units,
                "passed_units": total_passed,
                "failed_units": total_failed,
                "target_units": target_units,
                "quality_rate": quality_rate
            },
            "workers": worker_stats,
            "machines": {
                "total": len(self.machines),
                "operational": len([m for m in self.machines.values() if m.is_operational]),
                "needing_maintenance": len([m for m in self.machines.values() if m.needs_maintenance()])
            },
            "shifts_completed": len(self.shifts)
        }
