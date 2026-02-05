"""
Base Classes for Professional Simulator Framework

Provides foundational classes for building professional training simulations
that map to MMO RPG mechanics.

Paradigm 2 Mapping:
- MMO Character → Professional Role
- MMO Quest → Professional Task
- MMO Location → Work Location
- MMO Item → Resource/Tool
- MMO XP/Level → Performance Metrics
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class TaskType(Enum):
    """Types of professional tasks"""
    DELIVERY = "delivery"
    SERVICE = "service"
    PRODUCTION = "production"
    DIAGNOSIS = "diagnosis"
    ASSEMBLY = "assembly"
    QUALITY_CHECK = "quality_check"
    CUSTOMER_INTERACTION = "customer_interaction"
    MAINTENANCE = "maintenance"


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResourceType(Enum):
    """Types of resources"""
    VEHICLE = "vehicle"
    TOOL = "tool"
    EQUIPMENT = "equipment"
    INVENTORY = "inventory"
    INFORMATION = "information"


@dataclass
class Location:
    """
    Professional location (maps to MMO Location)

    Examples:
    - Warehouse (MMO: City)
    - Customer Address (MMO: Quest Location)
    - Factory Floor (MMO: Dungeon)
    - Hospital Room (MMO: Instance)
    """
    id: str
    name: str
    location_type: str  # warehouse, customer, factory, hospital, etc.
    coordinates: tuple  # (latitude, longitude) or (x, y)
    address: Optional[str] = None
    capacity: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Resource:
    """
    Professional resource (maps to MMO Item/Equipment)

    Examples:
    - Delivery Truck (MMO: Mount)
    - Scanner (MMO: Tool)
    - Medical Equipment (MMO: Weapon/Armor)
    - Inventory Items (MMO: Loot)
    """
    id: str
    name: str
    resource_type: ResourceType
    capacity: Optional[float] = None
    current_load: float = 0.0
    condition: float = 100.0  # 0-100 (durability)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_available(self) -> bool:
        """Check if resource is available for use"""
        return self.condition > 0 and self.current_load < (self.capacity or float('inf'))


@dataclass
class Task:
    """
    Professional task (maps to MMO Quest)

    Examples:
    - Deliver Package (MMO: Fetch Quest)
    - Serve Customer (MMO: Talk to NPC)
    - Assemble Product (MMO: Craft Item)
    - Diagnose Patient (MMO: Solve Puzzle)
    """
    id: str
    name: str
    description: str
    task_type: TaskType
    location: Location
    status: TaskStatus = TaskStatus.PENDING

    # Task parameters
    estimated_duration: float = 0.0  # minutes
    priority: int = 0  # 0=low, 1=medium, 2=high, 3=urgent
    deadline: Optional[datetime] = None

    # Requirements
    required_skills: List[str] = field(default_factory=list)
    required_resources: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)

    # Rewards (maps to MMO XP/Gold/Items)
    completion_reward: float = 0.0
    performance_bonus: float = 0.0

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def can_start(self, professional: 'ProfessionalRole') -> bool:
        """Check if professional can start this task"""
        # Check skills
        has_skills = all(skill in professional.skills for skill in self.required_skills)

        # Check resources
        has_resources = all(
            res_id in [r.id for r in professional.resources]
            for res_id in self.required_resources
        )

        return has_skills and has_resources

    def complete(self, performance_score: float = 1.0):
        """Mark task as completed with performance score"""
        self.status = TaskStatus.COMPLETED
        self.metadata['completion_time'] = datetime.now().isoformat()
        self.metadata['performance_score'] = performance_score


@dataclass
class PerformanceMetrics:
    """
    Performance metrics (maps to MMO Stats/Achievements)

    Examples:
    - Deliveries Completed (MMO: Quests Completed)
    - Customer Satisfaction (MMO: Reputation)
    - Efficiency Score (MMO: Speed Run Record)
    - Error Rate (MMO: Deaths/Failures)
    """
    # Core metrics
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_time_worked: float = 0.0  # minutes

    # Performance scores
    efficiency_score: float = 0.0  # 0-1
    quality_score: float = 0.0  # 0-1
    customer_satisfaction: float = 0.0  # 0-1

    # Experience (MMO XP)
    experience_points: float = 0.0
    level: int = 1

    # Achievements
    achievements: List[str] = field(default_factory=list)

    # Domain-specific metrics
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

    def add_task_completion(self, task: Task, performance_score: float):
        """Record task completion"""
        self.tasks_completed += 1
        self.experience_points += task.completion_reward * performance_score

        # Update efficiency
        if task.estimated_duration > 0:
            actual_time = task.metadata.get('actual_duration', task.estimated_duration)
            efficiency = min(1.0, task.estimated_duration / actual_time)
            self.efficiency_score = (self.efficiency_score * (self.tasks_completed - 1) + efficiency) / self.tasks_completed

        # Update quality
        self.quality_score = (self.quality_score * (self.tasks_completed - 1) + performance_score) / self.tasks_completed

        # Level up check
        self._check_level_up()

    def add_task_failure(self, task: Task):
        """Record task failure"""
        self.tasks_failed += 1

    def _check_level_up(self):
        """Check if professional should level up"""
        # Simple XP threshold: level^2 * 100
        xp_needed = (self.level ** 2) * 100

        if self.experience_points >= xp_needed:
            self.level += 1
            self.achievements.append(f"Reached Level {self.level}")


@dataclass
class ProfessionalRole:
    """
    Professional role (maps to MMO Character/Class)

    Examples:
    - Delivery Driver (MMO: Rogue - fast, mobile)
    - Factory Worker (MMO: Warrior - steady, reliable)
    - Doctor (MMO: Healer - precision, care)
    - Dispatcher (MMO: Mage - planning, coordination)
    """
    id: str
    name: str
    role_type: str  # driver, worker, doctor, dispatcher, etc.

    # Skills (maps to MMO Skills/Abilities)
    skills: List[str] = field(default_factory=list)
    skill_levels: Dict[str, int] = field(default_factory=dict)

    # Resources/Equipment
    resources: List[Resource] = field(default_factory=list)

    # Current state
    current_location: Optional[Location] = None
    current_task: Optional[Task] = None
    is_available: bool = True

    # Performance tracking
    metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def assign_task(self, task: Task) -> bool:
        """Assign task to professional"""
        if not self.is_available:
            return False

        if not task.can_start(self):
            return False

        self.current_task = task
        self.is_available = False
        task.status = TaskStatus.IN_PROGRESS

        return True

    def complete_current_task(self, performance_score: float = 1.0):
        """Complete current task"""
        if self.current_task:
            self.current_task.complete(performance_score)
            self.metrics.add_task_completion(self.current_task, performance_score)
            self.current_task = None
            self.is_available = True

    def fail_current_task(self):
        """Fail current task"""
        if self.current_task:
            self.current_task.status = TaskStatus.FAILED
            self.metrics.add_task_failure(self.current_task)
            self.current_task = None
            self.is_available = True

    def add_skill(self, skill: str, level: int = 1):
        """Add or upgrade skill"""
        if skill not in self.skills:
            self.skills.append(skill)
        self.skill_levels[skill] = level

    def has_skill(self, skill: str, min_level: int = 1) -> bool:
        """Check if professional has skill at minimum level"""
        return skill in self.skills and self.skill_levels.get(skill, 0) >= min_level


@dataclass
class SimulationScenario:
    """
    Simulation scenario (maps to MMO Campaign/Story)

    Defines a complete professional scenario with:
    - Roles (MMO: Party Members)
    - Tasks (MMO: Quest Chain)
    - Locations (MMO: Map)
    - Resources (MMO: Loot/Equipment)
    - Objectives (MMO: Victory Conditions)
    """
    id: str
    name: str
    description: str
    scenario_type: str  # daily_operations, emergency, training, etc.

    # Scenario components
    professionals: List[ProfessionalRole] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    locations: List[Location] = field(default_factory=list)
    resources: List[Resource] = field(default_factory=list)

    # Objectives (maps to MMO Victory Conditions)
    objectives: List[Dict[str, Any]] = field(default_factory=list)

    # State
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: bool = False
    is_completed: bool = False

    # Results
    completion_score: float = 0.0
    total_performance: float = 0.0

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def start(self):
        """Start simulation scenario"""
        self.is_active = True
        self.start_time = datetime.now()

    def complete(self):
        """Complete simulation scenario"""
        self.is_active = False
        self.is_completed = True
        self.end_time = datetime.now()

        # Calculate completion score
        self._calculate_completion_score()

    def _calculate_completion_score(self):
        """Calculate overall completion score"""
        if not self.tasks:
            return

        completed_tasks = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        completion_rate = completed_tasks / len(self.tasks)

        # Average performance from all professionals
        if self.professionals:
            avg_quality = sum(p.metrics.quality_score for p in self.professionals) / len(self.professionals)
            avg_efficiency = sum(p.metrics.efficiency_score for p in self.professionals) / len(self.professionals)

            self.total_performance = (avg_quality + avg_efficiency) / 2

        # Combined score
        self.completion_score = completion_rate * self.total_performance


class ProfessionalSimulator:
    """
    Base class for professional simulators

    Provides core simulation mechanics:
    - Scenario management
    - Task assignment
    - Performance tracking
    - Optimization suggestions
    """

    def __init__(self, domain: str):
        """
        Initialize professional simulator

        Args:
            domain: Domain name (logistics, retail, manufacturing, healthcare)
        """
        self.domain = domain
        self.scenarios: Dict[str, SimulationScenario] = {}
        self.active_scenario: Optional[SimulationScenario] = None

    def create_scenario(
        self,
        name: str,
        description: str,
        scenario_type: str
    ) -> SimulationScenario:
        """Create new simulation scenario"""
        scenario = SimulationScenario(
            id=f"{self.domain}_{len(self.scenarios)}",
            name=name,
            description=description,
            scenario_type=scenario_type
        )

        self.scenarios[scenario.id] = scenario

        return scenario

    def start_scenario(self, scenario_id: str) -> bool:
        """Start simulation scenario"""
        if scenario_id not in self.scenarios:
            return False

        scenario = self.scenarios[scenario_id]
        scenario.start()
        self.active_scenario = scenario

        return True

    def assign_tasks(self, scenario: SimulationScenario) -> Dict[str, List[Task]]:
        """
        Assign tasks to professionals

        Override in subclasses for domain-specific assignment logic.
        Base implementation: round-robin assignment
        """
        assignments: Dict[str, List[Task]] = {p.id: [] for p in scenario.professionals}

        # Sort tasks by priority
        sorted_tasks = sorted(scenario.tasks, key=lambda t: t.priority, reverse=True)

        # Round-robin assignment
        prof_index = 0
        for task in sorted_tasks:
            if task.status == TaskStatus.PENDING:
                professionals = scenario.professionals
                if professionals:
                    prof = professionals[prof_index % len(professionals)]

                    if prof.assign_task(task):
                        assignments[prof.id].append(task)

                    prof_index += 1

        return assignments

    def optimize_assignments(
        self,
        scenario: SimulationScenario
    ) -> Dict[str, Any]:
        """
        Optimize task assignments

        Override in subclasses for domain-specific optimization.
        Returns optimization suggestions.
        """
        return {
            "message": "Base optimization - override in subclass",
            "suggestions": []
        }

    def get_performance_report(self, scenario: SimulationScenario) -> Dict[str, Any]:
        """Generate performance report for scenario"""
        return {
            "scenario_id": scenario.id,
            "scenario_name": scenario.name,
            "completion_score": scenario.completion_score,
            "total_performance": scenario.total_performance,
            "tasks": {
                "total": len(scenario.tasks),
                "completed": sum(1 for t in scenario.tasks if t.status == TaskStatus.COMPLETED),
                "failed": sum(1 for t in scenario.tasks if t.status == TaskStatus.FAILED),
                "pending": sum(1 for t in scenario.tasks if t.status == TaskStatus.PENDING)
            },
            "professionals": [
                {
                    "id": p.id,
                    "name": p.name,
                    "role": p.role_type,
                    "level": p.metrics.level,
                    "tasks_completed": p.metrics.tasks_completed,
                    "efficiency": p.metrics.efficiency_score,
                    "quality": p.metrics.quality_score
                }
                for p in scenario.professionals
            ]
        }
