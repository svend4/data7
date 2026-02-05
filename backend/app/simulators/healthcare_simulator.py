"""
Healthcare and Medical Professional Simulator

Domain: Patient Care, Diagnosis, Treatment
Status: 0% → 40%

Maps healthcare operations to MMO mechanics:
- Doctor/Nurse → MMO Healer (treats/heals)
- Patient → MMO NPC/Quest Giver
- Diagnosis → MMO Quest Investigation
- Treatment → MMO Healing Spell
- Medical Equipment → MMO Consumable/Tool
- Hospital Ward → MMO Healing Temple
- Patient Case → MMO Quest Chain

Simulates realistic healthcare scenarios with patient outcomes.
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


class HealthcareRole(Enum):
    """Healthcare worker roles"""
    DOCTOR = "doctor"
    NURSE = "nurse"
    TECHNICIAN = "technician"
    PHARMACIST = "pharmacist"
    ADMINISTRATOR = "administrator"


class MedicalTaskType(Enum):
    """Types of medical tasks"""
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    SURGERY = "surgery"
    MEDICATION = "medication"
    EXAMINATION = "examination"
    LAB_TEST = "lab_test"
    IMAGING = "imaging"


class PatientCondition(Enum):
    """Patient health condition severity"""
    STABLE = "stable"
    MODERATE = "moderate"
    SERIOUS = "serious"
    CRITICAL = "critical"


class TreatmentOutcome(Enum):
    """Treatment outcome status"""
    SUCCESSFUL = "successful"
    IMPROVING = "improving"
    NO_CHANGE = "no_change"
    DETERIORATING = "deteriorating"
    COMPLICATIONS = "complications"


@dataclass
class MedicalEquipment(Resource):
    """
    Medical equipment (maps to MMO Tool/Consumable)

    Attributes:
    - equipment_type: Type of equipment (diagnostic, treatment, etc.)
    - uses_remaining: For consumables
    - calibration_date: When last calibrated
    """

    def __init__(
        self,
        id: str,
        name: str,
        equipment_type: str = "diagnostic",
        uses_remaining: Optional[int] = None
    ):
        super().__init__(
            id=id,
            name=name,
            resource_type=ResourceType.EQUIPMENT,
            capacity=uses_remaining or 100.0
        )
        self.equipment_type = equipment_type
        self.uses_remaining = uses_remaining
        self.calibration_date = datetime.now()
        self.metadata.update({
            "equipment_type": equipment_type,
            "uses_remaining": uses_remaining,
            "total_uses": 0
        })

    def use_equipment(self) -> bool:
        """Use equipment (decreases remaining uses for consumables)"""
        if self.uses_remaining is not None:
            if self.uses_remaining <= 0:
                return False
            self.uses_remaining -= 1

        self.metadata["total_uses"] += 1
        return True

    def needs_calibration(self) -> bool:
        """Check if equipment needs calibration"""
        days_since_calibration = (datetime.now() - self.calibration_date).days
        return days_since_calibration > 30  # Monthly calibration


@dataclass
class Hospital(Location):
    """
    Hospital location (maps to MMO Healing Temple/Guild Hall)
    """

    def __init__(
        self,
        id: str,
        name: str,
        coordinates: tuple,
        num_beds: int = 50,
        specialties: List[str] = None
    ):
        super().__init__(
            id=id,
            name=name,
            location_type="hospital",
            coordinates=coordinates,
            capacity=num_beds
        )
        self.num_beds = num_beds
        self.specialties = specialties or ["general", "emergency", "surgery"]
        self.occupied_beds = 0
        self.metadata.update({
            "num_beds": num_beds,
            "occupied_beds": 0,
            "specialties": self.specialties,
            "total_patients_treated": 0
        })

    def admit_patient(self) -> bool:
        """Admit patient to hospital"""
        if self.occupied_beds >= self.num_beds:
            return False
        self.occupied_beds += 1
        self.metadata["occupied_beds"] = self.occupied_beds
        return True

    def discharge_patient(self):
        """Discharge patient from hospital"""
        if self.occupied_beds > 0:
            self.occupied_beds -= 1
            self.metadata["occupied_beds"] = self.occupied_beds
            self.metadata["total_patients_treated"] += 1


@dataclass
class Patient:
    """
    Patient (maps to MMO NPC/Quest Giver)

    Attributes:
    - condition: Health severity level
    - symptoms: List of symptoms
    - diagnosis: Current diagnosis
    - vital_signs: Health metrics
    """
    id: str
    name: str
    age: int
    condition: PatientCondition = PatientCondition.STABLE

    # Medical information
    symptoms: List[str] = field(default_factory=list)
    diagnosis: Optional[str] = None
    medications: List[str] = field(default_factory=list)

    # Vital signs
    heart_rate: int = 70  # bpm
    blood_pressure: Tuple[int, int] = (120, 80)  # systolic, diastolic
    temperature: float = 98.6  # Fahrenheit
    oxygen_saturation: int = 98  # %

    # Treatment tracking
    treatments_received: List[str] = field(default_factory=list)
    recovery_progress: float = 0.0  # 0-1
    admission_time: Optional[datetime] = None
    discharge_time: Optional[datetime] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_symptom(self, symptom: str):
        """Add symptom to patient"""
        if symptom not in self.symptoms:
            self.symptoms.append(symptom)

    def set_diagnosis(self, diagnosis: str):
        """Set patient diagnosis"""
        self.diagnosis = diagnosis

    def add_treatment(self, treatment: str):
        """Record treatment received"""
        self.treatments_received.append(treatment)

    def update_vitals(
        self,
        heart_rate: Optional[int] = None,
        blood_pressure: Optional[Tuple[int, int]] = None,
        temperature: Optional[float] = None,
        oxygen_saturation: Optional[int] = None
    ):
        """Update patient vital signs"""
        if heart_rate is not None:
            self.heart_rate = heart_rate
        if blood_pressure is not None:
            self.blood_pressure = blood_pressure
        if temperature is not None:
            self.temperature = temperature
        if oxygen_saturation is not None:
            self.oxygen_saturation = oxygen_saturation

    def assess_condition(self) -> PatientCondition:
        """Assess patient condition based on vitals"""
        critical_factors = 0

        if self.heart_rate < 50 or self.heart_rate > 120:
            critical_factors += 1
        if self.temperature < 95.0 or self.temperature > 103.0:
            critical_factors += 1
        if self.oxygen_saturation < 90:
            critical_factors += 1
        if self.blood_pressure[0] > 180 or self.blood_pressure[0] < 90:
            critical_factors += 1

        if critical_factors >= 3:
            self.condition = PatientCondition.CRITICAL
        elif critical_factors == 2:
            self.condition = PatientCondition.SERIOUS
        elif critical_factors == 1:
            self.condition = PatientCondition.MODERATE
        else:
            self.condition = PatientCondition.STABLE

        return self.condition


@dataclass
class MedicalTask(Task):
    """
    Medical task (maps to MMO Quest/Healing Action)

    Attributes:
    - medical_type: Type of medical procedure
    - patient: Patient being treated
    - urgency: How urgent the task is
    - equipment_needed: Required medical equipment
    """

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        medical_type: MedicalTaskType,
        patient: Patient,
        hospital: Hospital,
        urgency: int = 1,  # 1-4 (1=routine, 4=emergency)
        equipment_ids: List[str] = None
    ):
        super().__init__(
            id=id,
            name=name,
            description=description,
            task_type=TaskType.DIAGNOSIS,
            location=hospital,
            priority=urgency
        )
        self.medical_type = medical_type
        self.patient = patient
        self.urgency = urgency
        self.equipment_ids = equipment_ids or []

        # Outcome tracking
        self.outcome: Optional[TreatmentOutcome] = None
        self.completion_quality: float = 0.0  # 0-1
        self.complications: List[str] = []

        self.metadata.update({
            "medical_type": medical_type.value,
            "patient_id": patient.id,
            "urgency": urgency
        })

    def perform_procedure(self, healthcare_worker: 'HealthcareWorker') -> TreatmentOutcome:
        """Perform medical procedure"""
        # Calculate success based on worker skill
        skill_level = healthcare_worker.get_skill_level("medical_knowledge") / 5.0
        base_success = 0.7 + skill_level * 0.2

        # Adjust for urgency and patient condition
        if self.patient.condition == PatientCondition.CRITICAL:
            base_success *= 0.8
        elif self.patient.condition == PatientCondition.SERIOUS:
            base_success *= 0.9

        # Random factor
        success_roll = random.random()

        if success_roll < base_success:
            self.outcome = TreatmentOutcome.SUCCESSFUL
            self.completion_quality = min(1.0, base_success + random.uniform(0, 0.2))
            self.patient.recovery_progress = min(1.0, self.patient.recovery_progress + 0.3)
        elif success_roll < base_success + 0.15:
            self.outcome = TreatmentOutcome.IMPROVING
            self.completion_quality = base_success
            self.patient.recovery_progress += 0.1
        elif success_roll < base_success + 0.25:
            self.outcome = TreatmentOutcome.NO_CHANGE
            self.completion_quality = base_success * 0.8
        else:
            if random.random() < 0.3:
                self.outcome = TreatmentOutcome.COMPLICATIONS
                self.complications.append("Unexpected complication during procedure")
                self.completion_quality = base_success * 0.5
            else:
                self.outcome = TreatmentOutcome.DETERIORATING
                self.completion_quality = base_success * 0.6

        self.status = TaskStatus.COMPLETED
        self.patient.add_treatment(self.medical_type.value)

        return self.outcome


@dataclass
class HealthcareWorker(ProfessionalRole):
    """
    Healthcare worker (maps to MMO Healer/Cleric)

    Specializations:
    - Doctor: Diagnoses and treats patients
    - Nurse: Provides care and administers treatments
    - Technician: Operates medical equipment
    - Pharmacist: Manages medications
    - Administrator: Manages hospital operations
    """

    def __init__(
        self,
        id: str,
        name: str,
        role: HealthcareRole,
        hospital: Hospital,
        specialty: Optional[str] = None,
        shift_number: int = 1
    ):
        super().__init__(
            id=id,
            name=name,
            role_type="healthcare_worker"
        )
        self.healthcare_role = role
        self.hospital = hospital
        self.specialty = specialty
        self.shift_number = shift_number

        # Add role-specific skills
        self._initialize_skills_for_role(role)

        # Patient tracking
        self.patients_treated_today = 0
        self.successful_treatments = 0
        self.complications_encountered = 0

        self.metadata.update({
            "healthcare_role": role.value,
            "hospital_id": hospital.id,
            "specialty": specialty,
            "shift_number": shift_number
        })

    def _initialize_skills_for_role(self, role: HealthcareRole):
        """Initialize skills based on healthcare role"""
        if role == HealthcareRole.DOCTOR:
            self.add_skill("medical_knowledge", level=4)
            self.add_skill("diagnosis", level=4)
            self.add_skill("surgery", level=3)
            self.add_skill("patient_care", level=3)
        elif role == HealthcareRole.NURSE:
            self.add_skill("patient_care", level=4)
            self.add_skill("medication_administration", level=3)
            self.add_skill("vital_monitoring", level=4)
            self.add_skill("wound_care", level=3)
        elif role == HealthcareRole.TECHNICIAN:
            self.add_skill("equipment_operation", level=4)
            self.add_skill("technical_analysis", level=3)
            self.add_skill("maintenance", level=3)
        elif role == HealthcareRole.PHARMACIST:
            self.add_skill("pharmacology", level=4)
            self.add_skill("medication_management", level=4)
            self.add_skill("drug_interaction", level=3)
        elif role == HealthcareRole.ADMINISTRATOR:
            self.add_skill("resource_management", level=3)
            self.add_skill("scheduling", level=3)
            self.add_skill("coordination", level=3)

    def diagnose_patient(self, patient: Patient) -> Optional[str]:
        """Diagnose patient based on symptoms"""
        if self.healthcare_role != HealthcareRole.DOCTOR:
            return None

        diagnosis_skill = self.get_skill_level("diagnosis") / 5.0

        # Simple diagnosis based on symptoms
        if "chest pain" in patient.symptoms and "shortness of breath" in patient.symptoms:
            diagnosis = "Cardiac concerns - requires further evaluation"
        elif "fever" in patient.symptoms and "cough" in patient.symptoms:
            diagnosis = "Respiratory infection"
        elif "headache" in patient.symptoms and "fatigue" in patient.symptoms:
            diagnosis = "Viral syndrome"
        else:
            diagnosis = "General assessment needed"

        # Accuracy based on skill
        if random.random() > diagnosis_skill:
            diagnosis = "Diagnosis uncertain - additional tests recommended"

        patient.set_diagnosis(diagnosis)

        # Gain XP for diagnosis
        self.metrics.experience_points += 15.0

        return diagnosis

    def treat_patient(
        self,
        patient: Patient,
        task: MedicalTask,
        equipment: Optional[MedicalEquipment] = None
    ) -> TreatmentOutcome:
        """Treat patient"""
        # Perform procedure
        outcome = task.perform_procedure(self)

        # Track statistics
        self.patients_treated_today += 1

        if outcome == TreatmentOutcome.SUCCESSFUL:
            self.successful_treatments += 1
            xp_gain = 25.0
        elif outcome == TreatmentOutcome.IMPROVING:
            xp_gain = 15.0
        elif outcome == TreatmentOutcome.COMPLICATIONS:
            self.complications_encountered += 1
            xp_gain = 10.0
        else:
            xp_gain = 5.0

        # Award XP
        self.metrics.experience_points += xp_gain
        self.metrics.tasks_completed += 1

        # Update patient recovery
        if outcome in [TreatmentOutcome.SUCCESSFUL, TreatmentOutcome.IMPROVING]:
            patient.recovery_progress = min(1.0, patient.recovery_progress + 0.2)

        return outcome

    def administer_medication(self, patient: Patient, medication: str):
        """Administer medication to patient"""
        if self.healthcare_role not in [HealthcareRole.DOCTOR, HealthcareRole.NURSE]:
            return

        patient.medications.append(medication)

        # Medication improves patient condition slightly
        patient.recovery_progress = min(1.0, patient.recovery_progress + 0.1)

        # Small XP gain
        self.metrics.experience_points += 5.0

    def monitor_vitals(self, patient: Patient) -> Dict[str, Any]:
        """Monitor patient vital signs"""
        if self.healthcare_role != HealthcareRole.NURSE:
            return {}

        # Check vitals and assess condition
        condition = patient.assess_condition()

        vitals = {
            "heart_rate": patient.heart_rate,
            "blood_pressure": patient.blood_pressure,
            "temperature": patient.temperature,
            "oxygen_saturation": patient.oxygen_saturation,
            "condition": condition.value
        }

        # Small XP gain
        self.metrics.experience_points += 3.0

        return vitals


@dataclass
class MedicalShift:
    """
    Medical shift (work period for healthcare workers)
    """
    id: str
    shift_number: int  # 1, 2, or 3
    start_hour: int  # 0-23
    duration: int  # hours
    workers: List[HealthcareWorker] = field(default_factory=list)
    patients: List[Patient] = field(default_factory=list)
    tasks: List[MedicalTask] = field(default_factory=list)

    # Shift metrics
    patients_treated: int = 0
    successful_treatments: int = 0
    complications: int = 0
    average_quality: float = 0.0

    def add_worker(self, worker: HealthcareWorker):
        """Add worker to shift"""
        self.workers.append(worker)

    def add_patient(self, patient: Patient):
        """Add patient to shift"""
        self.patients.append(patient)

    def add_task(self, task: MedicalTask):
        """Add medical task to shift"""
        self.tasks.append(task)

    def calculate_metrics(self):
        """Calculate shift performance metrics"""
        self.patients_treated = len([t for t in self.tasks if t.status == TaskStatus.COMPLETED])

        completed_tasks = [t for t in self.tasks if isinstance(t, MedicalTask) and t.outcome]

        if completed_tasks:
            self.successful_treatments = len([
                t for t in completed_tasks
                if t.outcome in [TreatmentOutcome.SUCCESSFUL, TreatmentOutcome.IMPROVING]
            ])

            self.complications = len([
                t for t in completed_tasks
                if t.outcome == TreatmentOutcome.COMPLICATIONS
            ])

            self.average_quality = sum(t.completion_quality for t in completed_tasks) / len(completed_tasks)


class HealthcareSimulator(ProfessionalSimulator):
    """
    Healthcare operations simulator

    Simulates:
    - Patient admission and diagnosis
    - Medical treatments and procedures
    - Shift management
    - Equipment usage
    - Patient outcomes
    """

    def __init__(self):
        super().__init__(domain="healthcare")
        self.hospitals: Dict[str, Hospital] = {}
        self.equipment: Dict[str, MedicalEquipment] = {}
        self.patients: Dict[str, Patient] = {}
        self.shifts: Dict[str, MedicalShift] = {}

    def create_healthcare_scenario(
        self,
        name: str,
        description: str,
        num_doctors: int = 3,
        num_nurses: int = 6,
        num_patients: int = 20,
        hospital_type: str = "general"
    ) -> SimulationScenario:
        """
        Create healthcare scenario

        Args:
            name: Scenario name
            description: Scenario description
            num_doctors: Number of doctors
            num_nurses: Number of nurses
            num_patients: Number of patients
            hospital_type: Type of hospital

        Returns:
            SimulationScenario with healthcare workers, patients, and tasks
        """
        scenario = self.create_scenario(
            name=name,
            description=description,
            scenario_type="healthcare"
        )

        # Create hospital
        specialties = []
        if hospital_type == "general":
            specialties = ["emergency", "surgery", "internal_medicine", "pediatrics"]
        elif hospital_type == "emergency":
            specialties = ["emergency", "trauma", "critical_care"]
        elif hospital_type == "surgical":
            specialties = ["surgery", "orthopedics", "cardiology"]

        hospital = Hospital(
            id="hospital_001",
            name=f"{hospital_type.title()} Hospital",
            coordinates=(random.uniform(-90, 90), random.uniform(-180, 180)),
            num_beds=max(50, num_patients + 10),
            specialties=specialties
        )
        scenario.add_location(hospital)
        self.hospitals[hospital.id] = hospital

        # Create medical equipment
        equipment_types = [
            ("X-Ray Machine", "imaging"),
            ("Ultrasound", "imaging"),
            ("ECG Monitor", "diagnostic"),
            ("Defibrillator", "treatment"),
            ("IV Pump", "treatment")
        ]

        for i, (eq_name, eq_type) in enumerate(equipment_types):
            equipment = MedicalEquipment(
                id=f"equipment_{i:03d}",
                name=eq_name,
                equipment_type=eq_type
            )
            self.equipment[equipment.id] = equipment

        # Create healthcare workers
        total_workers = num_doctors + num_nurses + 2  # +2 for technician and pharmacist

        # Doctors
        for i in range(num_doctors):
            specialty = specialties[i % len(specialties)] if specialties else "general"
            shift_number = (i % 3) + 1

            doctor = HealthcareWorker(
                id=f"doctor_{i:03d}",
                name=f"Dr. {chr(65 + i)}",  # Dr. A, Dr. B, etc.
                role=HealthcareRole.DOCTOR,
                hospital=hospital,
                specialty=specialty,
                shift_number=shift_number
            )
            scenario.add_professional(doctor)

        # Nurses
        for i in range(num_nurses):
            shift_number = (i % 3) + 1

            nurse = HealthcareWorker(
                id=f"nurse_{i:03d}",
                name=f"Nurse {i+1}",
                role=HealthcareRole.NURSE,
                hospital=hospital,
                shift_number=shift_number
            )
            scenario.add_professional(nurse)

        # Technician
        technician = HealthcareWorker(
            id="tech_001",
            name="Tech Specialist",
            role=HealthcareRole.TECHNICIAN,
            hospital=hospital,
            shift_number=1
        )
        scenario.add_professional(technician)

        # Pharmacist
        pharmacist = HealthcareWorker(
            id="pharm_001",
            name="Pharmacist",
            role=HealthcareRole.PHARMACIST,
            hospital=hospital,
            shift_number=1
        )
        scenario.add_professional(pharmacist)

        # Create patients with various conditions
        common_symptoms = [
            ["fever", "cough", "fatigue"],
            ["chest pain", "shortness of breath"],
            ["headache", "nausea"],
            ["abdominal pain", "fever"],
            ["joint pain", "swelling"],
            ["dizziness", "weakness"]
        ]

        for i in range(num_patients):
            patient = Patient(
                id=f"patient_{i:03d}",
                name=f"Patient {i+1}",
                age=random.randint(20, 80)
            )

            # Assign symptoms
            symptoms = random.choice(common_symptoms)
            for symptom in symptoms:
                patient.add_symptom(symptom)

            # Set condition severity
            severity_roll = random.random()
            if severity_roll < 0.6:
                patient.condition = PatientCondition.STABLE
            elif severity_roll < 0.85:
                patient.condition = PatientCondition.MODERATE
            elif severity_roll < 0.95:
                patient.condition = PatientCondition.SERIOUS
            else:
                patient.condition = PatientCondition.CRITICAL

            # Randomize vitals based on condition
            if patient.condition == PatientCondition.CRITICAL:
                patient.heart_rate = random.randint(50, 140)
                patient.temperature = random.uniform(95.0, 104.0)
                patient.oxygen_saturation = random.randint(85, 95)
            elif patient.condition in [PatientCondition.SERIOUS, PatientCondition.MODERATE]:
                patient.heart_rate = random.randint(60, 110)
                patient.temperature = random.uniform(97.0, 102.0)
                patient.oxygen_saturation = random.randint(92, 98)

            self.patients[patient.id] = patient

            # Admit patient to hospital
            hospital.admit_patient()

        # Create medical tasks for patients
        task_types = [
            MedicalTaskType.DIAGNOSIS,
            MedicalTaskType.EXAMINATION,
            MedicalTaskType.TREATMENT,
            MedicalTaskType.LAB_TEST
        ]

        for patient in self.patients.values():
            # Create initial task (diagnosis or examination)
            task_type = random.choice([MedicalTaskType.DIAGNOSIS, MedicalTaskType.EXAMINATION])

            urgency = 4 if patient.condition == PatientCondition.CRITICAL else \
                      3 if patient.condition == PatientCondition.SERIOUS else \
                      2 if patient.condition == PatientCondition.MODERATE else 1

            task = MedicalTask(
                id=f"task_{patient.id}",
                name=f"{task_type.value.title()} for {patient.name}",
                description=f"Perform {task_type.value} on patient with {', '.join(patient.symptoms)}",
                medical_type=task_type,
                patient=patient,
                hospital=hospital,
                urgency=urgency,
                equipment_ids=[f"equipment_{random.randint(0, 4):03d}"]
            )

            scenario.add_task(task)

        # Store scenario
        self.scenarios[scenario.id] = scenario

        return scenario

    def assign_tasks_to_shift(
        self,
        scenario: SimulationScenario,
        shift_number: int
    ) -> MedicalShift:
        """
        Assign tasks to healthcare workers in a shift

        Args:
            scenario: Simulation scenario
            shift_number: Shift number (1, 2, or 3)

        Returns:
            MedicalShift with assigned workers and tasks
        """
        shift_hours = [8, 8, 8]  # 8-hour shifts
        start_hours = [7, 15, 23]  # 7 AM, 3 PM, 11 PM

        shift = MedicalShift(
            id=f"shift_{shift_number}",
            shift_number=shift_number,
            start_hour=start_hours[shift_number - 1],
            duration=shift_hours[shift_number - 1]
        )

        # Add workers from this shift
        shift_workers = [
            p for p in scenario.professionals
            if isinstance(p, HealthcareWorker) and p.shift_number == shift_number
        ]

        for worker in shift_workers:
            shift.add_worker(worker)

        # Add patients
        for patient in self.patients.values():
            shift.add_patient(patient)

        # Add tasks (prioritize by urgency)
        sorted_tasks = sorted(
            scenario.tasks,
            key=lambda t: t.priority if isinstance(t, MedicalTask) else 0,
            reverse=True
        )

        for task in sorted_tasks:
            if isinstance(task, MedicalTask):
                shift.add_task(task)

        self.shifts[shift.id] = shift

        return shift

    def simulate_medical_shift(
        self,
        scenario: SimulationScenario,
        shift_number: int = 1,
        shift_duration: int = 8
    ) -> Dict[str, Any]:
        """
        Simulate a medical shift

        Args:
            scenario: Simulation scenario
            shift_number: Which shift (1, 2, or 3)
            shift_duration: Shift duration in hours

        Returns:
            Dictionary with shift results
        """
        # Create shift
        shift = self.assign_tasks_to_shift(scenario, shift_number)

        # Get doctors and nurses
        doctors = [w for w in shift.workers if w.healthcare_role == HealthcareRole.DOCTOR]
        nurses = [w for w in shift.workers if w.healthcare_role == HealthcareRole.NURSE]

        # Process patients
        for task in shift.tasks:
            if not isinstance(task, MedicalTask):
                continue

            patient = task.patient

            # Assign to appropriate worker
            if task.medical_type in [MedicalTaskType.DIAGNOSIS, MedicalTaskType.SURGERY, MedicalTaskType.TREATMENT]:
                if doctors:
                    doctor = min(doctors, key=lambda d: len(d.assigned_tasks))

                    # Diagnose if needed
                    if not patient.diagnosis:
                        doctor.diagnose_patient(patient)

                    # Treat patient
                    outcome = doctor.treat_patient(patient, task)

                    # Update task
                    doctor.assign_task(task)
                    task.status = TaskStatus.COMPLETED

            elif task.medical_type in [MedicalTaskType.MEDICATION, MedicalTaskType.EXAMINATION]:
                if nurses:
                    nurse = min(nurses, key=lambda n: len(n.assigned_tasks))

                    # Monitor vitals
                    vitals = nurse.monitor_vitals(patient)

                    # Administer medication if needed
                    if task.medical_type == MedicalTaskType.MEDICATION:
                        nurse.administer_medication(patient, "Standard medication")

                    # Treat patient
                    outcome = nurse.treat_patient(patient, task)

                    # Update task
                    nurse.assign_task(task)
                    task.status = TaskStatus.COMPLETED

        # Calculate shift metrics
        shift.calculate_metrics()

        # Update worker performance metrics
        for worker in shift.workers:
            if isinstance(worker, HealthcareWorker):
                success_rate = worker.successful_treatments / max(1, worker.patients_treated_today)
                worker.metrics.update_efficiency(success_rate)
                worker.metrics.update_quality(success_rate)

        return {
            "shift_number": shift_number,
            "duration": shift_duration,
            "workers": len(shift.workers),
            "patients": {
                "total": len(shift.patients),
                "treated": shift.patients_treated,
                "critical": len([p for p in shift.patients if p.condition == PatientCondition.CRITICAL]),
                "stable": len([p for p in shift.patients if p.condition == PatientCondition.STABLE])
            },
            "treatments": {
                "successful": shift.successful_treatments,
                "complications": shift.complications,
                "success_rate": shift.successful_treatments / max(1, shift.patients_treated)
            },
            "average_quality": shift.average_quality,
            "tasks_completed": len([t for t in shift.tasks if t.status == TaskStatus.COMPLETED])
        }

    def get_performance_report(self, scenario: SimulationScenario) -> Dict[str, Any]:
        """
        Generate performance report for healthcare scenario

        Args:
            scenario: Simulation scenario

        Returns:
            Dictionary with performance metrics
        """
        total_patients = len(self.patients)
        total_tasks = len(scenario.tasks)
        completed_tasks = len([t for t in scenario.tasks if t.status == TaskStatus.COMPLETED])

        medical_tasks = [t for t in scenario.tasks if isinstance(t, MedicalTask) and t.outcome]

        successful_outcomes = len([
            t for t in medical_tasks
            if t.outcome in [TreatmentOutcome.SUCCESSFUL, TreatmentOutcome.IMPROVING]
        ])

        success_rate = successful_outcomes / max(1, len(medical_tasks))

        # Worker statistics
        worker_stats = []
        for professional in scenario.professionals:
            if isinstance(professional, HealthcareWorker):
                worker_stats.append({
                    "id": professional.id,
                    "name": professional.name,
                    "role": professional.healthcare_role.value,
                    "specialty": professional.specialty,
                    "shift": professional.shift_number,
                    "patients_treated": professional.patients_treated_today,
                    "successful_treatments": professional.successful_treatments,
                    "complications": professional.complications_encountered,
                    "level": professional.metrics.level,
                    "experience": professional.metrics.experience_points,
                    "efficiency": professional.metrics.efficiency_score,
                    "quality": professional.metrics.quality_score
                })

        # Patient statistics
        patient_stats = {
            "total": total_patients,
            "stable": len([p for p in self.patients.values() if p.condition == PatientCondition.STABLE]),
            "moderate": len([p for p in self.patients.values() if p.condition == PatientCondition.MODERATE]),
            "serious": len([p for p in self.patients.values() if p.condition == PatientCondition.SERIOUS]),
            "critical": len([p for p in self.patients.values() if p.condition == PatientCondition.CRITICAL]),
            "diagnosed": len([p for p in self.patients.values() if p.diagnosis]),
            "average_recovery": sum(p.recovery_progress for p in self.patients.values()) / total_patients
        }

        return {
            "scenario_id": scenario.id,
            "scenario_name": scenario.name,
            "completion_score": completed_tasks / max(1, total_tasks),
            "success_rate": success_rate,
            "patients": patient_stats,
            "workers": worker_stats,
            "equipment": {
                "total": len(self.equipment),
                "needs_calibration": len([e for e in self.equipment.values() if e.needs_calibration()])
            },
            "shifts_completed": len(self.shifts)
        }
