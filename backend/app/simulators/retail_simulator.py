"""
Retail and Service Professional Simulator

Domain: Customer Service, Sales, Inventory Management
Status: 0% → 40%

Maps retail operations to MMO mechanics:
- Service Agent → MMO Bard (persuasion, communication)
- Sales Person → MMO Merchant (trading, negotiation)
- Cashier → MMO Crafter (fast processing)
- Customer → MMO NPC (quest giver)
- Product → MMO Item/Loot
- Store → MMO Shop/Market
- Shift → MMO Quest Chain
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


class CustomerMood(Enum):
    """Customer mood states"""
    HAPPY = "happy"
    NEUTRAL = "neutral"
    IMPATIENT = "impatient"
    ANGRY = "angry"


class ServiceType(Enum):
    """Types of retail services"""
    CHECKOUT = "checkout"
    CONSULTATION = "consultation"
    COMPLAINT = "complaint"
    PRODUCT_INQUIRY = "product_inquiry"
    RETURN = "return"
    UPSELL = "upsell"


@dataclass
class Product(Resource):
    """
    Product in store (maps to MMO Item)

    Attributes:
    - price: Product price
    - stock_quantity: Available stock
    - category: Product category
    - popularity: How popular (affects sales)
    """

    def __init__(
        self,
        id: str,
        name: str,
        price: float,
        stock_quantity: int = 100,
        category: str = "general"
    ):
        super().__init__(
            id=id,
            name=name,
            resource_type=ResourceType.INVENTORY
        )
        self.price = price
        self.stock_quantity = stock_quantity
        self.category = category
        self.metadata.update({
            "price": price,
            "stock_quantity": stock_quantity,
            "category": category,
            "sales_count": 0,
            "revenue": 0.0
        })

    def sell(self, quantity: int = 1) -> bool:
        """Sell product"""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.metadata["sales_count"] += quantity
            self.metadata["revenue"] += self.price * quantity
            return True
        return False

    def restock(self, quantity: int):
        """Restock product"""
        self.stock_quantity += quantity


@dataclass
class Store(Location):
    """
    Retail store (maps to MMO Shop/Market)
    """

    def __init__(
        self,
        id: str,
        name: str,
        store_type: str = "retail",  # retail, grocery, electronics, etc.
        coordinates: tuple = (0.0, 0.0),
        opening_hours: Tuple[int, int] = (9, 21)  # 9 AM - 9 PM
    ):
        super().__init__(
            id=id,
            name=name,
            location_type=store_type,
            coordinates=coordinates
        )
        self.opening_hours = opening_hours
        self.metadata.update({
            "opening_hours": opening_hours,
            "total_sales": 0.0,
            "total_customers": 0,
            "avg_satisfaction": 0.0
        })


@dataclass
class Customer:
    """
    Customer (maps to MMO NPC/Quest Giver)

    Attributes:
    - patience: How patient (affects waiting tolerance)
    - budget: Available money
    - needs: What they want to buy
    - mood: Current emotional state
    """
    id: str
    name: str
    patience: float = 1.0  # 0-1 (1 = very patient)
    budget: float = 100.0
    needs: List[str] = field(default_factory=list)  # Product IDs they want
    mood: CustomerMood = CustomerMood.NEUTRAL

    # Shopping state
    cart: List[Tuple[str, int]] = field(default_factory=list)  # (product_id, quantity)
    satisfaction: float = 0.5  # 0-1
    wait_time: float = 0.0  # minutes waited

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_to_cart(self, product_id: str, quantity: int = 1):
        """Add product to shopping cart"""
        self.cart.append((product_id, quantity))

    def wait(self, minutes: float):
        """Customer waits"""
        self.wait_time += minutes

        # Patience decreases with waiting
        patience_loss = minutes / (self.patience * 10)

        if self.wait_time > self.patience * 5:  # Waited too long
            if self.mood == CustomerMood.NEUTRAL:
                self.mood = CustomerMood.IMPATIENT
            elif self.mood == CustomerMood.IMPATIENT:
                self.mood = CustomerMood.ANGRY

    def get_satisfied(self, service_quality: float):
        """Update satisfaction based on service"""
        # Service quality affects satisfaction
        self.satisfaction = (self.satisfaction + service_quality) / 2

        # Mood improves with good service
        if service_quality > 0.8 and self.mood == CustomerMood.IMPATIENT:
            self.mood = CustomerMood.NEUTRAL
        elif service_quality > 0.9:
            self.mood = CustomerMood.HAPPY


@dataclass
class ServiceTask(Task):
    """
    Service task (maps to MMO Quest)

    Types:
    - Checkout: Ring up customer purchases
    - Consultation: Help customer find products
    - Complaint: Handle customer complaint
    - Return: Process product return
    """

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        customer: Customer,
        service_type: ServiceType,
        location: Store,
        priority: int = 0,
        estimated_duration: float = 5.0  # minutes
    ):
        super().__init__(
            id=id,
            name=name,
            description=description,
            task_type=TaskType.SERVICE,
            location=location,
            priority=priority
        )
        self.customer = customer
        self.service_type = service_type
        self.estimated_duration = estimated_duration

        # Required skills based on service type
        if service_type == ServiceType.CHECKOUT:
            self.required_skills = ["cashier_operations"]
        elif service_type == ServiceType.CONSULTATION:
            self.required_skills = ["product_knowledge", "communication"]
        elif service_type == ServiceType.COMPLAINT:
            self.required_skills = ["conflict_resolution", "communication"]
        elif service_type == ServiceType.RETURN:
            self.required_skills = ["cashier_operations", "policy_knowledge"]
        elif service_type == ServiceType.UPSELL:
            self.required_skills = ["sales", "persuasion"]


@dataclass
class ServiceAgent(ProfessionalRole):
    """
    Retail service agent (maps to MMO Bard/Merchant)

    Roles:
    - Cashier: Fast transaction processing (MMO Crafter)
    - Sales Associate: Product consultation (MMO Bard)
    - Customer Service: Problem resolution (MMO Diplomat)

    Skills:
    - Cashier Operations: Speed and accuracy
    - Product Knowledge: Know the inventory
    - Communication: Interact with customers
    - Sales: Upselling and persuasion
    - Conflict Resolution: Handle complaints
    """

    def __init__(
        self,
        id: str,
        name: str,
        agent_role: str,  # cashier, sales_associate, customer_service
        store: Store
    ):
        super().__init__(
            id=id,
            name=name,
            role_type=agent_role
        )

        # Role-specific skills
        if agent_role == "cashier":
            self.add_skill("cashier_operations", level=2)
            self.add_skill("communication", level=1)
        elif agent_role == "sales_associate":
            self.add_skill("product_knowledge", level=2)
            self.add_skill("communication", level=2)
            self.add_skill("sales", level=1)
        elif agent_role == "customer_service":
            self.add_skill("communication", level=3)
            self.add_skill("conflict_resolution", level=2)
            self.add_skill("policy_knowledge", level=2)

        # Work location
        self.current_location = store
        self.store = store

        # Performance tracking
        self.metadata.update({
            "customers_served": 0,
            "total_sales": 0.0,
            "avg_customer_satisfaction": 0.0,
            "avg_transaction_time": 0.0,
            "complaints_resolved": 0
        })

    def serve_customer(
        self,
        customer: Customer,
        service_quality: float = 0.8
    ) -> Dict[str, Any]:
        """
        Serve customer

        Returns service results
        """
        # Customer satisfaction based on service quality and wait time
        wait_penalty = min(0.2, customer.wait_time / 30.0)  # Max 20% penalty
        final_satisfaction = service_quality - wait_penalty

        customer.get_satisfied(final_satisfaction)

        # Update metrics
        self.metadata["customers_served"] += 1

        # Update average satisfaction
        current_avg = self.metadata["avg_customer_satisfaction"]
        total_served = self.metadata["customers_served"]
        self.metadata["avg_customer_satisfaction"] = (
            (current_avg * (total_served - 1) + customer.satisfaction) / total_served
        )

        return {
            "customer_id": customer.id,
            "satisfaction": customer.satisfaction,
            "mood": customer.mood.value,
            "service_quality": service_quality
        }


@dataclass
class Shift:
    """
    Work shift (maps to MMO Quest Chain)

    A shift is a sequence of service tasks during work hours
    """
    id: str
    agent: ServiceAgent
    store: Store
    start_time: datetime
    end_time: datetime
    tasks: List[ServiceTask] = field(default_factory=list)
    customers_served: int = 0
    total_revenue: float = 0.0
    avg_satisfaction: float = 0.0
    status: str = "planned"  # planned, active, completed

    def start(self):
        """Start shift"""
        self.status = "active"

    def complete(self):
        """Complete shift"""
        self.status = "completed"

        # Calculate metrics
        if self.customers_served > 0:
            self.avg_satisfaction = sum(
                t.customer.satisfaction for t in self.tasks
            ) / self.customers_served


class RetailSimulator(ProfessionalSimulator):
    """
    Retail and Service Simulator

    Domain: Customer Service, Sales, Inventory Management

    Features:
    - Customer service simulation
    - Sales and upselling
    - Inventory management
    - Queue management
    - Performance tracking
    """

    def __init__(self):
        super().__init__(domain="retail")
        self.stores: List[Store] = []
        self.agents: List[ServiceAgent] = []
        self.products: List[Product] = []
        self.customers: List[Customer] = []
        self.shifts: List[Shift] = []

    def create_retail_scenario(
        self,
        name: str,
        description: str,
        num_agents: int = 3,
        num_customers: int = 30,
        num_products: int = 20,
        store_type: str = "retail"
    ) -> SimulationScenario:
        """
        Create retail scenario

        Args:
            name: Scenario name
            description: Scenario description
            num_agents: Number of service agents
            num_customers: Number of customers
            num_products: Number of products in store
            store_type: Type of store

        Returns:
            SimulationScenario configured for retail
        """
        scenario = self.create_scenario(name, description, "daily_operations")

        # Create store
        store = Store(
            id="store_main",
            name="Main Store",
            store_type=store_type,
            coordinates=(0.0, 0.0)
        )
        self.stores.append(store)
        scenario.locations.append(store)

        # Create products
        product_categories = ["electronics", "clothing", "food", "home", "books"]
        for i in range(num_products):
            category = random.choice(product_categories)
            product = Product(
                id=f"product_{i+1}",
                name=f"{category.title()} Item {i+1}",
                price=random.uniform(10.0, 500.0),
                stock_quantity=random.randint(10, 100),
                category=category
            )
            self.products.append(product)
            scenario.resources.append(product)

        # Create service agents
        agent_roles = ["cashier", "sales_associate", "customer_service"]
        for i in range(num_agents):
            role = agent_roles[i % len(agent_roles)]
            agent = ServiceAgent(
                id=f"agent_{i+1}",
                name=f"{role.replace('_', ' ').title()} {i+1}",
                agent_role=role,
                store=store
            )
            self.agents.append(agent)
            scenario.professionals.append(agent)

        # Create customers
        for i in range(num_customers):
            # Random customer needs (want 1-3 products)
            num_needs = random.randint(1, 3)
            needs = random.sample([p.id for p in self.products], num_needs)

            customer = Customer(
                id=f"customer_{i+1}",
                name=f"Customer {i+1}",
                patience=random.uniform(0.5, 1.0),
                budget=random.uniform(50.0, 1000.0),
                needs=needs
            )
            self.customers.append(customer)

        # Create service tasks
        service_types = [
            ServiceType.CHECKOUT,
            ServiceType.CONSULTATION,
            ServiceType.PRODUCT_INQUIRY
        ]

        for customer in self.customers:
            # Each customer needs at least checkout
            service_type = random.choice(service_types)

            task = ServiceTask(
                id=f"service_{customer.id}",
                name=f"Serve {customer.name}",
                description=f"{service_type.value} for {customer.name}",
                customer=customer,
                service_type=service_type,
                location=store,
                priority=1 if customer.mood == CustomerMood.ANGRY else 0
            )
            scenario.tasks.append(task)

        # Set objectives
        scenario.objectives = [
            {
                "type": "serve_all_customers",
                "description": "Serve all customers",
                "target": num_customers
            },
            {
                "type": "maintain_satisfaction",
                "description": "Maintain customer satisfaction above 70%",
                "target": 0.7
            },
            {
                "type": "maximize_sales",
                "description": "Maximize total sales revenue"
            }
        ]

        return scenario

    def assign_tasks(self, scenario: SimulationScenario) -> Dict[str, List[Task]]:
        """
        Assign service tasks to agents

        Prioritizes:
        1. Angry customers (high priority)
        2. Agent skill match
        3. Load balancing
        """
        assignments: Dict[str, List[Task]] = {p.id: [] for p in scenario.professionals}

        # Sort tasks by priority and customer mood
        service_tasks = [t for t in scenario.tasks if isinstance(t, ServiceTask)]
        service_tasks.sort(
            key=lambda t: (
                -t.priority,
                1 if t.customer.mood == CustomerMood.ANGRY else 0,
                t.customer.wait_time
            ),
            reverse=True
        )

        # Assign tasks
        for task in service_tasks:
            if task.status != TaskStatus.PENDING:
                continue

            # Find best agent for this service type
            best_agent = None
            best_score = -1

            for agent in scenario.professionals:
                if not isinstance(agent, ServiceAgent):
                    continue

                if not agent.is_available:
                    continue

                # Skill match score
                skill_score = sum(
                    agent.skill_levels.get(skill, 0)
                    for skill in task.required_skills
                )

                # Load balance score (prefer less loaded agents)
                load_score = 1.0 / (1.0 + len(assignments[agent.id]))

                # Combined score
                total_score = skill_score + load_score

                if total_score > best_score:
                    best_score = total_score
                    best_agent = agent

            if best_agent and best_agent.assign_task(task):
                assignments[best_agent.id].append(task)

        return assignments

    def simulate_shift(
        self,
        scenario: SimulationScenario,
        shift_duration: int = 480  # 8 hours in minutes
    ) -> Dict[str, Any]:
        """
        Simulate retail shift

        Returns simulation results
        """
        scenario.start()

        # Assign tasks
        assignments = self.assign_tasks(scenario)

        # Create shifts for each agent
        current_time = datetime.now()

        for agent_id, tasks in assignments.items():
            agent = next(a for a in scenario.professionals if a.id == agent_id)

            if not isinstance(agent, ServiceAgent):
                continue

            shift = Shift(
                id=f"shift_{agent.id}",
                agent=agent,
                store=agent.store,
                start_time=current_time,
                end_time=current_time + timedelta(minutes=shift_duration),
                tasks=[t for t in tasks if isinstance(t, ServiceTask)]
            )
            shift.start()
            self.shifts.append(shift)

            # Simulate serving customers
            for task in shift.tasks:
                if not isinstance(task, ServiceTask):
                    continue

                customer = task.customer

                # Simulate wait time
                wait_minutes = random.uniform(0, 5)
                customer.wait(wait_minutes)

                # Service quality based on agent skills
                base_quality = 0.7
                skill_bonus = sum(
                    agent.skill_levels.get(skill, 0) * 0.05
                    for skill in task.required_skills
                )
                service_quality = min(1.0, base_quality + skill_bonus)

                # Add randomness
                service_quality += random.uniform(-0.1, 0.1)
                service_quality = max(0.0, min(1.0, service_quality))

                # Serve customer
                result = agent.serve_customer(customer, service_quality)

                # Process sale if checkout
                if task.service_type == ServiceType.CHECKOUT:
                    total_sale = 0.0
                    for product_id, quantity in customer.cart:
                        product = next((p for p in self.products if p.id == product_id), None)
                        if product and product.sell(quantity):
                            total_sale += product.price * quantity

                    shift.total_revenue += total_sale
                    agent.metadata["total_sales"] += total_sale

                # Complete task
                task.complete(service_quality)
                agent.complete_current_task(service_quality)
                shift.customers_served += 1

            shift.complete()

        # Complete scenario
        scenario.complete()

        # Generate report
        report = self.get_performance_report(scenario)

        # Add retail-specific metrics
        total_revenue = sum(s.total_revenue for s in self.shifts)
        total_customers = sum(s.customers_served for s in self.shifts)

        report["retail_metrics"] = {
            "total_revenue": total_revenue,
            "total_customers_served": total_customers,
            "avg_revenue_per_customer": total_revenue / total_customers if total_customers > 0 else 0,
            "avg_customer_satisfaction": sum(c.satisfaction for c in self.customers) / len(self.customers) if self.customers else 0,
            "products_sold": sum(p.metadata["sales_count"] for p in self.products)
        }

        return report
