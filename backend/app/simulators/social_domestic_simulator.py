"""
Social and Domestic Services Professional Simulator

Domain: Legal, Social Work, Domestic, and Home Care Services
Status: New Domain (0% → 40%)

Maps social/domestic service operations to MMO mechanics:
- Lawyer/Attorney → MMO Quest Giver (provides legal guidance)
- Social Worker → MMO Support Character (helps NPCs)
- Housekeeper/Estate Manager → MMO Maintenance NPC (maintains facilities)
- Caregiver → MMO Healer Assistant (assists with care)
- Client → MMO NPC (needs assistance)

Simulates realistic social and domestic service scenarios.
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


class ServiceRole(Enum):
    """Social and domestic service roles"""
    # Legal Services
    LAWYER = "lawyer"
    SOCIAL_LAW_SPECIALIST = "social_law_specialist"
    FAMILY_LAW_SPECIALIST = "family_law_specialist"

    # Social Work
    SOCIAL_WORKER = "social_worker"
    CASE_MANAGER = "case_manager"

    # Domestic Services
    HOUSEKEEPER = "housekeeper"
    ESTATE_MANAGER = "estate_manager"
    GROUNDSKEEPER = "groundskeeper"

    # Home Care
    CAREGIVER = "caregiver"
    HOME_HEALTH_AIDE = "home_health_aide"


class ServiceTaskType(Enum):
    """Types of service tasks"""
    # Legal
    LEGAL_CONSULTATION = "legal_consultation"
    CASE_PREPARATION = "case_preparation"
    DOCUMENT_REVIEW = "document_review"

    # Social Work
    CLIENT_ASSESSMENT = "client_assessment"
    RESOURCE_COORDINATION = "resource_coordination"
    CRISIS_INTERVENTION = "crisis_intervention"

    # Domestic
    HOUSE_CLEANING = "house_cleaning"
    PROPERTY_MAINTENANCE = "property_maintenance"
    GARDEN_CARE = "garden_care"
    ESTATE_MANAGEMENT = "estate_management"

    # Home Care
    PERSONAL_CARE = "personal_care"
    MEDICATION_ASSISTANCE = "medication_assistance"
    COMPANIONSHIP = "companionship"


class ClientNeedLevel(Enum):
    """Client need severity level"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    URGENT = "urgent"


class ServiceOutcome(Enum):
    """Service outcome status"""
    SUCCESSFUL = "successful"
    IN_PROGRESS = "in_progress"
    PARTIALLY_RESOLVED = "partially_resolved"
    NEEDS_FOLLOWUP = "needs_followup"
    ESCALATED = "escalated"


@dataclass
class Client:
    """
    Service client (maps to MMO NPC needing help)

    Attributes:
    - need_level: How urgent their needs are
    - service_needs: What services they require
    - satisfaction: Client satisfaction (0-1)
    """
    id: str
    name: str
    age: int
    need_level: ClientNeedLevel = ClientNeedLevel.MODERATE

    # Service needs
    service_needs: List[str] = field(default_factory=list)
    legal_issues: List[str] = field(default_factory=list)
    care_requirements: List[str] = field(default_factory=list)

    # Tracking
    satisfaction: float = 0.5  # 0-1
    services_received: List[str] = field(default_factory=list)
    progress: float = 0.0  # 0-1 (problem resolution)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_service_need(self, need: str):
        """Add service need"""
        if need not in self.service_needs:
            self.service_needs.append(need)

    def receive_service(self, service_type: str, quality: float):
        """Record service received and update satisfaction"""
        self.services_received.append(service_type)

        # Update satisfaction based on quality
        satisfaction_change = (quality - 0.5) * 0.2
        self.satisfaction = max(0.0, min(1.0, self.satisfaction + satisfaction_change))

        # Update progress
        self.progress = min(1.0, self.progress + quality * 0.15)


@dataclass
class ServiceLocation(Location):
    """
    Service location (office, home, estate, etc.)
    """

    def __init__(
        self,
        id: str,
        name: str,
        location_type: str,  # office, home, estate, care_facility
        coordinates: tuple,
        capacity: int = 10
    ):
        super().__init__(
            id=id,
            name=name,
            location_type=location_type,
            coordinates=coordinates,
            capacity=capacity
        )
        self.clients_served = 0
        self.metadata.update({
            "clients_served": 0,
            "service_quality_avg": 0.0
        })


@dataclass
class ServiceTask(Task):
    """
    Service task (maps to MMO Quest/Service Request)

    Attributes:
    - service_type: Type of service
    - client: Client receiving service
    - urgency: Task urgency
    - complexity: Task complexity (affects time/skill needed)
    """

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        service_type: ServiceTaskType,
        client: Client,
        location: ServiceLocation,
        urgency: int = 1,  # 1-4
        complexity: float = 0.5  # 0-1
    ):
        super().__init__(
            id=id,
            name=name,
            description=description,
            task_type=TaskType.SERVICE,
            location=location,
            priority=urgency
        )
        self.service_type = service_type
        self.client = client
        self.urgency = urgency
        self.complexity = complexity

        # Outcome tracking
        self.outcome: Optional[ServiceOutcome] = None
        self.quality: float = 0.0
        self.notes: List[str] = []

        self.metadata.update({
            "service_type": service_type.value,
            "client_id": client.id,
            "urgency": urgency,
            "complexity": complexity
        })

    def perform_service(self, worker: 'ServiceWorker') -> ServiceOutcome:
        """Perform service task"""
        # Calculate success based on worker skill and task complexity
        relevant_skills = []

        if self.service_type in [ServiceTaskType.LEGAL_CONSULTATION,
                                ServiceTaskType.CASE_PREPARATION,
                                ServiceTaskType.DOCUMENT_REVIEW]:
            relevant_skills = ["legal_knowledge", "analytical_thinking"]
        elif self.service_type in [ServiceTaskType.CLIENT_ASSESSMENT,
                                   ServiceTaskType.RESOURCE_COORDINATION,
                                   ServiceTaskType.CRISIS_INTERVENTION]:
            relevant_skills = ["empathy", "communication", "problem_solving"]
        elif self.service_type in [ServiceTaskType.HOUSE_CLEANING,
                                   ServiceTaskType.PROPERTY_MAINTENANCE,
                                   ServiceTaskType.GARDEN_CARE]:
            relevant_skills = ["attention_to_detail", "physical_stamina"]
        elif self.service_type in [ServiceTaskType.PERSONAL_CARE,
                                   ServiceTaskType.MEDICATION_ASSISTANCE,
                                   ServiceTaskType.COMPANIONSHIP]:
            relevant_skills = ["patience", "caregiving", "empathy"]

        # Calculate skill level
        avg_skill = sum(worker.get_skill_level(skill) for skill in relevant_skills) / max(1, len(relevant_skills))
        skill_factor = avg_skill / 5.0

        # Base success rate
        base_success = 0.6 + skill_factor * 0.3

        # Adjust for complexity and urgency
        base_success *= (1.2 - self.complexity * 0.4)

        if self.urgency == 4:  # Urgent
            base_success *= 0.85

        # Random factor
        success_roll = random.random()

        if success_roll < base_success:
            self.outcome = ServiceOutcome.SUCCESSFUL
            self.quality = min(1.0, base_success + random.uniform(0, 0.2))
        elif success_roll < base_success + 0.2:
            self.outcome = ServiceOutcome.IN_PROGRESS
            self.quality = base_success * 0.8
        elif success_roll < base_success + 0.3:
            self.outcome = ServiceOutcome.PARTIALLY_RESOLVED
            self.quality = base_success * 0.6
        else:
            if self.urgency >= 3:
                self.outcome = ServiceOutcome.ESCALATED
                self.quality = base_success * 0.4
            else:
                self.outcome = ServiceOutcome.NEEDS_FOLLOWUP
                self.quality = base_success * 0.5

        self.status = TaskStatus.COMPLETED

        # Client receives service
        self.client.receive_service(self.service_type.value, self.quality)

        return self.outcome


@dataclass
class ServiceWorker(ProfessionalRole):
    """
    Service worker (maps to MMO Support Character)

    Specializations:
    - Lawyer: Provides legal services
    - Social Worker: Coordinates social services
    - Housekeeper/Estate Manager: Maintains properties
    - Caregiver: Provides home care
    """

    def __init__(
        self,
        id: str,
        name: str,
        role: ServiceRole,
        location: ServiceLocation,
        specialty: Optional[str] = None
    ):
        super().__init__(
            id=id,
            name=name,
            role_type="service_worker"
        )
        self.service_role = role
        self.location = location
        self.specialty = specialty

        # Add role-specific skills
        self._initialize_skills_for_role(role)

        # Service tracking
        self.clients_served_today = 0
        self.successful_services = 0
        self.escalations = 0

        self.metadata.update({
            "service_role": role.value,
            "location_id": location.id,
            "specialty": specialty
        })

    def _initialize_skills_for_role(self, role: ServiceRole):
        """Initialize skills based on service role"""
        if role in [ServiceRole.LAWYER, ServiceRole.SOCIAL_LAW_SPECIALIST,
                   ServiceRole.FAMILY_LAW_SPECIALIST]:
            # Юрист
            self.add_skill("legal_knowledge", level=4)
            self.add_skill("analytical_thinking", level=4)
            self.add_skill("communication", level=3)
            self.add_skill("document_preparation", level=3)

        elif role in [ServiceRole.SOCIAL_WORKER, ServiceRole.CASE_MANAGER]:
            # Социальный работник
            self.add_skill("empathy", level=4)
            self.add_skill("communication", level=4)
            self.add_skill("problem_solving", level=3)
            self.add_skill("resource_coordination", level=3)

        elif role in [ServiceRole.HOUSEKEEPER, ServiceRole.ESTATE_MANAGER,
                     ServiceRole.GROUNDSKEEPER]:
            # Домработник / Управляющий имением
            self.add_skill("attention_to_detail", level=4)
            self.add_skill("physical_stamina", level=3)
            self.add_skill("organization", level=3)
            self.add_skill("maintenance", level=3)

        elif role in [ServiceRole.CAREGIVER, ServiceRole.HOME_HEALTH_AIDE]:
            # Сиделка / Помощник по уходу
            self.add_skill("patience", level=4)
            self.add_skill("caregiving", level=4)
            self.add_skill("empathy", level=4)
            self.add_skill("physical_care", level=3)

    def provide_service(
        self,
        client: Client,
        task: ServiceTask
    ) -> ServiceOutcome:
        """Provide service to client"""
        # Perform service
        outcome = task.perform_service(self)

        # Track statistics
        self.clients_served_today += 1

        if outcome == ServiceOutcome.SUCCESSFUL:
            self.successful_services += 1
            xp_gain = 20.0
        elif outcome == ServiceOutcome.IN_PROGRESS:
            xp_gain = 10.0
        elif outcome == ServiceOutcome.ESCALATED:
            self.escalations += 1
            xp_gain = 5.0
        else:
            xp_gain = 8.0

        # Bonus XP for complex tasks
        xp_gain *= (1.0 + task.complexity * 0.5)

        # Award XP
        self.metrics.experience_points += xp_gain
        self.metrics.tasks_completed += 1

        return outcome

    def assess_client_needs(self, client: Client) -> List[str]:
        """Assess client needs (for social workers)"""
        if self.service_role not in [ServiceRole.SOCIAL_WORKER, ServiceRole.CASE_MANAGER]:
            return []

        # Analyze client situation
        recommendations = []

        if client.need_level in [ClientNeedLevel.HIGH, ClientNeedLevel.URGENT]:
            recommendations.append("Immediate intervention required")

        if len(client.service_needs) > 3:
            recommendations.append("Multiple service coordination needed")

        if client.satisfaction < 0.3:
            recommendations.append("Crisis support recommended")

        # Small XP gain
        self.metrics.experience_points += 5.0

        return recommendations


@dataclass
class ServiceShift:
    """Service shift (work period)"""
    id: str
    shift_type: str  # office_hours, home_visit, on_call
    start_hour: int
    duration: int
    workers: List[ServiceWorker] = field(default_factory=list)
    clients: List[Client] = field(default_factory=list)
    tasks: List[ServiceTask] = field(default_factory=list)

    # Metrics
    clients_served: int = 0
    successful_outcomes: int = 0
    escalations: int = 0
    average_satisfaction: float = 0.0

    def add_worker(self, worker: ServiceWorker):
        """Add worker to shift"""
        self.workers.append(worker)

    def add_client(self, client: Client):
        """Add client to shift"""
        self.clients.append(client)

    def add_task(self, task: ServiceTask):
        """Add task to shift"""
        self.tasks.append(task)

    def calculate_metrics(self):
        """Calculate shift performance metrics"""
        completed_tasks = [t for t in self.tasks if isinstance(t, ServiceTask) and t.outcome]

        self.clients_served = len(set(t.client.id for t in completed_tasks))

        self.successful_outcomes = len([
            t for t in completed_tasks
            if t.outcome in [ServiceOutcome.SUCCESSFUL, ServiceOutcome.IN_PROGRESS]
        ])

        self.escalations = len([
            t for t in completed_tasks
            if t.outcome == ServiceOutcome.ESCALATED
        ])

        if self.clients:
            self.average_satisfaction = sum(c.satisfaction for c in self.clients) / len(self.clients)


class SocialDomesticSimulator(ProfessionalSimulator):
    """
    Social and domestic services simulator

    Simulates:
    - Legal consultations and case management
    - Social work and client support
    - Domestic services and estate management
    - Home care and caregiving
    """

    def __init__(self):
        super().__init__(domain="social_domestic_services")
        self.locations: Dict[str, ServiceLocation] = {}
        self.clients: Dict[str, Client] = {}
        self.shifts: Dict[str, ServiceShift] = {}

    def create_service_scenario(
        self,
        name: str,
        description: str,
        service_type: str = "mixed",  # legal, social_work, domestic, home_care, mixed
        num_workers: int = 5,
        num_clients: int = 15
    ) -> SimulationScenario:
        """
        Create social/domestic services scenario

        Args:
            name: Scenario name
            description: Scenario description
            service_type: Type of services to simulate
            num_workers: Number of service workers
            num_clients: Number of clients

        Returns:
            SimulationScenario with workers, clients, and tasks
        """
        scenario = self.create_scenario(
            name=name,
            description=description,
            scenario_type="social_domestic_services"
        )

        # Create service location
        location_types = {
            "legal": "law_office",
            "social_work": "social_services_office",
            "domestic": "estate",
            "home_care": "care_facility",
            "mixed": "service_center"
        }

        location = ServiceLocation(
            id="location_001",
            name=f"{service_type.replace('_', ' ').title()} Service Center",
            location_type=location_types.get(service_type, "service_center"),
            coordinates=(random.uniform(-90, 90), random.uniform(-180, 180)),
            capacity=num_clients + 5
        )
        scenario.add_location(location)
        self.locations[location.id] = location

        # Create service workers based on type
        if service_type == "legal":
            roles = [
                ServiceRole.LAWYER,
                ServiceRole.SOCIAL_LAW_SPECIALIST,
                ServiceRole.FAMILY_LAW_SPECIALIST
            ]
        elif service_type == "social_work":
            roles = [
                ServiceRole.SOCIAL_WORKER,
                ServiceRole.CASE_MANAGER
            ]
        elif service_type == "domestic":
            roles = [
                ServiceRole.HOUSEKEEPER,
                ServiceRole.ESTATE_MANAGER,
                ServiceRole.GROUNDSKEEPER
            ]
        elif service_type == "home_care":
            roles = [
                ServiceRole.CAREGIVER,
                ServiceRole.HOME_HEALTH_AIDE
            ]
        else:  # mixed
            roles = [
                ServiceRole.LAWYER,
                ServiceRole.SOCIAL_WORKER,
                ServiceRole.HOUSEKEEPER,
                ServiceRole.CAREGIVER
            ]

        for i in range(num_workers):
            role = roles[i % len(roles)]

            # Set specialty based on role
            specialty = None
            if role == ServiceRole.SOCIAL_LAW_SPECIALIST:
                specialty = "social_law"
            elif role == ServiceRole.FAMILY_LAW_SPECIALIST:
                specialty = "family_law"
            elif role == ServiceRole.ESTATE_MANAGER:
                specialty = "full_estate"

            worker = ServiceWorker(
                id=f"worker_{i:03d}",
                name=f"{role.value.replace('_', ' ').title()} {i+1}",
                role=role,
                location=location,
                specialty=specialty
            )
            scenario.add_professional(worker)

        # Create clients with various needs
        for i in range(num_clients):
            client = Client(
                id=f"client_{i:03d}",
                name=f"Client {i+1}",
                age=random.randint(18, 85)
            )

            # Assign need level
            need_roll = random.random()
            if need_roll < 0.5:
                client.need_level = ClientNeedLevel.LOW
            elif need_roll < 0.8:
                client.need_level = ClientNeedLevel.MODERATE
            elif need_roll < 0.95:
                client.need_level = ClientNeedLevel.HIGH
            else:
                client.need_level = ClientNeedLevel.URGENT

            # Add service needs based on scenario type
            if service_type in ["legal", "mixed"]:
                client.add_service_need("legal_advice")
                if random.random() < 0.5:
                    client.legal_issues.append("social_benefits")

            if service_type in ["social_work", "mixed"]:
                client.add_service_need("social_support")
                if random.random() < 0.4:
                    client.add_service_need("crisis_intervention")

            if service_type in ["domestic", "mixed"]:
                client.add_service_need("house_maintenance")
                if random.random() < 0.3:
                    client.add_service_need("property_care")

            if service_type in ["home_care", "mixed"]:
                client.add_service_need("personal_care")
                client.care_requirements.append("daily_assistance")

            self.clients[client.id] = client

        # Create service tasks
        for client in self.clients.values():
            # Determine task type based on client needs
            if "legal_advice" in client.service_needs:
                task_type = ServiceTaskType.LEGAL_CONSULTATION
            elif "social_support" in client.service_needs:
                task_type = ServiceTaskType.CLIENT_ASSESSMENT
            elif "house_maintenance" in client.service_needs:
                task_type = ServiceTaskType.HOUSE_CLEANING
            elif "personal_care" in client.service_needs:
                task_type = ServiceTaskType.PERSONAL_CARE
            else:
                task_type = random.choice(list(ServiceTaskType))

            urgency = 4 if client.need_level == ClientNeedLevel.URGENT else \
                     3 if client.need_level == ClientNeedLevel.HIGH else \
                     2 if client.need_level == ClientNeedLevel.MODERATE else 1

            task = ServiceTask(
                id=f"task_{client.id}",
                name=f"{task_type.value.replace('_', ' ').title()} for {client.name}",
                description=f"Provide {task_type.value} service to client",
                service_type=task_type,
                client=client,
                location=location,
                urgency=urgency,
                complexity=random.uniform(0.3, 0.9)
            )

            scenario.add_task(task)

        # Store scenario
        self.scenarios[scenario.id] = scenario

        return scenario

    def simulate_service_shift(
        self,
        scenario: SimulationScenario,
        shift_type: str = "office_hours",
        shift_duration: int = 8
    ) -> Dict[str, Any]:
        """
        Simulate a service shift

        Args:
            scenario: Simulation scenario
            shift_type: Type of shift (office_hours, home_visit, on_call)
            shift_duration: Shift duration in hours

        Returns:
            Dictionary with shift results
        """
        shift = ServiceShift(
            id=f"shift_{len(self.shifts)+1}",
            shift_type=shift_type,
            start_hour=8 if shift_type == "office_hours" else 9,
            duration=shift_duration
        )

        # Add workers
        for worker in scenario.professionals:
            if isinstance(worker, ServiceWorker):
                shift.add_worker(worker)

        # Add clients
        for client in self.clients.values():
            shift.add_client(client)

        # Process tasks
        for task in scenario.tasks:
            if isinstance(task, ServiceTask):
                shift.add_task(task)

                # Assign to appropriate worker
                suitable_worker = None

                if task.service_type in [ServiceTaskType.LEGAL_CONSULTATION,
                                        ServiceTaskType.CASE_PREPARATION,
                                        ServiceTaskType.DOCUMENT_REVIEW]:
                    suitable_worker = next((w for w in shift.workers
                                          if w.service_role in [ServiceRole.LAWYER,
                                                               ServiceRole.SOCIAL_LAW_SPECIALIST,
                                                               ServiceRole.FAMILY_LAW_SPECIALIST]),
                                         None)

                elif task.service_type in [ServiceTaskType.CLIENT_ASSESSMENT,
                                          ServiceTaskType.RESOURCE_COORDINATION,
                                          ServiceTaskType.CRISIS_INTERVENTION]:
                    suitable_worker = next((w for w in shift.workers
                                          if w.service_role in [ServiceRole.SOCIAL_WORKER,
                                                               ServiceRole.CASE_MANAGER]),
                                         None)

                elif task.service_type in [ServiceTaskType.HOUSE_CLEANING,
                                          ServiceTaskType.PROPERTY_MAINTENANCE,
                                          ServiceTaskType.GARDEN_CARE]:
                    suitable_worker = next((w for w in shift.workers
                                          if w.service_role in [ServiceRole.HOUSEKEEPER,
                                                               ServiceRole.ESTATE_MANAGER,
                                                               ServiceRole.GROUNDSKEEPER]),
                                         None)

                elif task.service_type in [ServiceTaskType.PERSONAL_CARE,
                                          ServiceTaskType.MEDICATION_ASSISTANCE,
                                          ServiceTaskType.COMPANIONSHIP]:
                    suitable_worker = next((w for w in shift.workers
                                          if w.service_role in [ServiceRole.CAREGIVER,
                                                               ServiceRole.HOME_HEALTH_AIDE]),
                                         None)

                if suitable_worker:
                    # Provide service
                    outcome = suitable_worker.provide_service(task.client, task)

                    # Update worker tasks
                    suitable_worker.assign_task(task)

        # Calculate metrics
        shift.calculate_metrics()

        # Update worker performance
        for worker in shift.workers:
            if isinstance(worker, ServiceWorker):
                success_rate = worker.successful_services / max(1, worker.clients_served_today)
                worker.metrics.update_efficiency(success_rate)
                worker.metrics.update_quality(shift.average_satisfaction)

        self.shifts[shift.id] = shift

        return {
            "shift_type": shift_type,
            "duration": shift_duration,
            "workers": len(shift.workers),
            "clients": {
                "total": len(shift.clients),
                "served": shift.clients_served,
                "high_need": len([c for c in shift.clients if c.need_level == ClientNeedLevel.HIGH]),
                "urgent": len([c for c in shift.clients if c.need_level == ClientNeedLevel.URGENT])
            },
            "outcomes": {
                "successful": shift.successful_outcomes,
                "escalations": shift.escalations,
                "success_rate": shift.successful_outcomes / max(1, shift.clients_served)
            },
            "average_satisfaction": shift.average_satisfaction,
            "tasks_completed": len([t for t in shift.tasks if t.status == TaskStatus.COMPLETED])
        }

    def get_performance_report(self, scenario: SimulationScenario) -> Dict[str, Any]:
        """
        Generate performance report for service scenario

        Args:
            scenario: Simulation scenario

        Returns:
            Dictionary with performance metrics
        """
        total_clients = len(self.clients)
        total_tasks = len(scenario.tasks)
        completed_tasks = len([t for t in scenario.tasks if t.status == TaskStatus.COMPLETED])

        service_tasks = [t for t in scenario.tasks if isinstance(t, ServiceTask) and t.outcome]

        successful_outcomes = len([
            t for t in service_tasks
            if t.outcome in [ServiceOutcome.SUCCESSFUL, ServiceOutcome.IN_PROGRESS]
        ])

        success_rate = successful_outcomes / max(1, len(service_tasks))

        # Worker statistics
        worker_stats = []
        for professional in scenario.professionals:
            if isinstance(professional, ServiceWorker):
                worker_stats.append({
                    "id": professional.id,
                    "name": professional.name,
                    "role": professional.service_role.value,
                    "specialty": professional.specialty,
                    "clients_served": professional.clients_served_today,
                    "successful_services": professional.successful_services,
                    "escalations": professional.escalations,
                    "level": professional.metrics.level,
                    "experience": professional.metrics.experience_points,
                    "efficiency": professional.metrics.efficiency_score,
                    "quality": professional.metrics.quality_score
                })

        # Client statistics
        client_stats = {
            "total": total_clients,
            "low_need": len([c for c in self.clients.values() if c.need_level == ClientNeedLevel.LOW]),
            "moderate_need": len([c for c in self.clients.values() if c.need_level == ClientNeedLevel.MODERATE]),
            "high_need": len([c for c in self.clients.values() if c.need_level == ClientNeedLevel.HIGH]),
            "urgent_need": len([c for c in self.clients.values() if c.need_level == ClientNeedLevel.URGENT]),
            "average_satisfaction": sum(c.satisfaction for c in self.clients.values()) / total_clients,
            "average_progress": sum(c.progress for c in self.clients.values()) / total_clients
        }

        return {
            "scenario_id": scenario.id,
            "scenario_name": scenario.name,
            "completion_score": completed_tasks / max(1, total_tasks),
            "success_rate": success_rate,
            "clients": client_stats,
            "workers": worker_stats,
            "shifts_completed": len(self.shifts)
        }
