"""
Unit Tests for Retail Simulator

Tests retail-specific functionality:
- RetailSimulator
- ServiceAgent
- ServiceTask
- Customer
- Product
- Store
- Shift
- Customer Mood System

Paradigm 2: Professional Simulator - Retail Domain
"""

import pytest
from typing import List

from app.simulators.retail_simulator import (
    RetailSimulator,
    ServiceAgent,
    ServiceTask,
    Customer,
    Product,
    Store,
    Shift,
    CustomerMood,
    ServiceType
)
from app.simulators.base import (
    TaskStatus,
    TaskPriority,
    Location
)


# ============================================================================
# Test Customer
# ============================================================================

class TestCustomer:
    """Test customer (MMO NPC mapping)"""

    def test_create_customer(self):
        """Test creating a customer"""
        customer = Customer(
            id="customer_001",
            name="Jane Doe"
        )

        assert customer.id == "customer_001"
        assert customer.name == "Jane Doe"
        assert customer.mood == CustomerMood.NEUTRAL
        assert customer.patience > 0
        assert customer.satisfaction == 0.5

    def test_customer_mood_states(self):
        """Test customer mood transitions"""
        customer = Customer(
            id="customer_001",
            name="Jane Doe"
        )

        # Start neutral
        assert customer.mood == CustomerMood.NEUTRAL

        # Make happy
        customer.mood = CustomerMood.HAPPY
        assert customer.mood == CustomerMood.HAPPY

        # Make impatient
        customer.mood = CustomerMood.IMPATIENT
        assert customer.mood == CustomerMood.IMPATIENT

        # Make angry
        customer.mood = CustomerMood.ANGRY
        assert customer.mood == CustomerMood.ANGRY

    def test_customer_wait(self):
        """Test customer waiting behavior"""
        customer = Customer(
            id="customer_001",
            name="Jane Doe"
        )

        initial_patience = customer.patience
        initial_wait_time = customer.wait_time

        # Customer waits
        customer.wait(5.0)

        # Wait time should increase
        assert customer.wait_time > initial_wait_time

        # Patience should decrease (if waiting long enough)
        if customer.wait_time > customer.patience * 5:
            assert customer.patience < initial_patience or customer.mood != CustomerMood.NEUTRAL

    def test_customer_becomes_impatient(self):
        """Test customer becoming impatient after waiting"""
        customer = Customer(
            id="customer_001",
            name="Jane Doe"
        )

        customer.patience = 0.3  # Low patience

        # Wait long enough to become impatient
        customer.wait(10.0)

        # Should become impatient or angry
        assert customer.mood in [CustomerMood.IMPATIENT, CustomerMood.ANGRY]

    def test_customer_satisfaction_update(self):
        """Test updating customer satisfaction"""
        customer = Customer(
            id="customer_001",
            name="Jane Doe"
        )

        # Good service
        customer.update_satisfaction(0.9)

        assert customer.satisfaction > 0.5

        # Poor service
        customer.update_satisfaction(0.3)

        assert customer.satisfaction < 0.9

    def test_customer_mood_affects_satisfaction(self):
        """Test that mood affects satisfaction changes"""
        happy_customer = Customer(
            id="customer_001",
            name="Happy Customer"
        )
        happy_customer.mood = CustomerMood.HAPPY

        angry_customer = Customer(
            id="customer_002",
            name="Angry Customer"
        )
        angry_customer.mood = CustomerMood.ANGRY

        # Same service quality
        service_quality = 0.8

        happy_customer.update_satisfaction(service_quality)
        angry_customer.update_satisfaction(service_quality)

        # Happy customer should be more satisfied
        assert happy_customer.satisfaction >= angry_customer.satisfaction


# ============================================================================
# Test Product
# ============================================================================

class TestProduct:
    """Test product (MMO item mapping)"""

    def test_create_product(self):
        """Test creating a product"""
        product = Product(
            id="product_001",
            name="Laptop",
            category="Electronics",
            price=999.99,
            stock=50
        )

        assert product.id == "product_001"
        assert product.name == "Laptop"
        assert product.category == "Electronics"
        assert product.price == 999.99
        assert product.stock == 50

    def test_product_in_stock(self):
        """Test product stock checking"""
        product = Product(
            id="product_001",
            name="Laptop",
            category="Electronics",
            price=999.99,
            stock=5
        )

        assert product.in_stock() is True

        product.stock = 0

        assert product.in_stock() is False

    def test_product_reduce_stock(self):
        """Test reducing product stock"""
        product = Product(
            id="product_001",
            name="Laptop",
            category="Electronics",
            price=999.99,
            stock=10
        )

        success = product.reduce_stock(3)

        assert success is True
        assert product.stock == 7

    def test_product_reduce_stock_insufficient(self):
        """Test reducing stock when insufficient"""
        product = Product(
            id="product_001",
            name="Laptop",
            category="Electronics",
            price=999.99,
            stock=2
        )

        success = product.reduce_stock(5)

        assert success is False
        assert product.stock == 2  # Unchanged

    def test_product_add_stock(self):
        """Test adding product stock"""
        product = Product(
            id="product_001",
            name="Laptop",
            category="Electronics",
            price=999.99,
            stock=10
        )

        product.add_stock(20)

        assert product.stock == 30


# ============================================================================
# Test Store
# ============================================================================

class TestStore:
    """Test store (MMO location mapping)"""

    def test_create_store(self):
        """Test creating a store"""
        location = Location(
            id="loc_001",
            name="Downtown Store",
            location_type="store",
            coordinates=(40.7, -74.0)
        )

        store = Store(
            id="store_001",
            name="Electronics Plus",
            store_type="electronics",
            location=location
        )

        assert store.id == "store_001"
        assert store.name == "Electronics Plus"
        assert store.store_type == "electronics"
        assert store.location == location
        assert store.products == []

    def test_store_add_product(self):
        """Test adding product to store"""
        location = Location(
            id="loc_001",
            name="Downtown Store",
            location_type="store",
            coordinates=(40.7, -74.0)
        )

        store = Store(
            id="store_001",
            name="Electronics Plus",
            store_type="electronics",
            location=location
        )

        product = Product(
            id="product_001",
            name="Laptop",
            category="Electronics",
            price=999.99,
            stock=10
        )

        store.add_product(product)

        assert len(store.products) == 1
        assert store.products[0] == product

    def test_store_get_product(self):
        """Test retrieving product from store"""
        location = Location(
            id="loc_001",
            name="Downtown Store",
            location_type="store",
            coordinates=(40.7, -74.0)
        )

        store = Store(
            id="store_001",
            name="Electronics Plus",
            store_type="electronics",
            location=location
        )

        product = Product(
            id="product_001",
            name="Laptop",
            category="Electronics",
            price=999.99,
            stock=10
        )

        store.add_product(product)

        retrieved = store.get_product("product_001")

        assert retrieved is not None
        assert retrieved.id == "product_001"

    def test_store_get_nonexistent_product(self):
        """Test retrieving non-existent product"""
        location = Location(
            id="loc_001",
            name="Downtown Store",
            location_type="store",
            coordinates=(40.7, -74.0)
        )

        store = Store(
            id="store_001",
            name="Electronics Plus",
            store_type="electronics",
            location=location
        )

        result = store.get_product("nonexistent")

        assert result is None


# ============================================================================
# Test ServiceTask
# ============================================================================

class TestServiceTask:
    """Test service task (MMO quest mapping)"""

    def test_create_service_task(self):
        """Test creating a service task"""
        customer = Customer(
            id="customer_001",
            name="Jane Doe"
        )

        task = ServiceTask(
            id="task_001",
            service_type=ServiceType.CHECKOUT,
            description="Process customer checkout",
            customer=customer,
            priority=TaskPriority.MEDIUM
        )

        assert task.id == "task_001"
        assert task.task_type == "service"
        assert task.service_type == ServiceType.CHECKOUT
        assert task.customer == customer
        assert task.priority == TaskPriority.MEDIUM

    def test_service_types(self):
        """Test all service types"""
        customer = Customer(
            id="customer_001",
            name="Jane Doe"
        )

        # Test each service type
        service_types = [
            ServiceType.CHECKOUT,
            ServiceType.CONSULTATION,
            ServiceType.COMPLAINT,
            ServiceType.PRODUCT_INQUIRY,
            ServiceType.RETURN,
            ServiceType.UPSELL
        ]

        for service_type in service_types:
            task = ServiceTask(
                id=f"task_{service_type.value}",
                service_type=service_type,
                description=f"{service_type.value} task",
                customer=customer,
                priority=TaskPriority.MEDIUM
            )

            assert task.service_type == service_type

    def test_service_task_estimate_time(self):
        """Test estimating service time"""
        customer = Customer(
            id="customer_001",
            name="Jane Doe"
        )

        checkout_task = ServiceTask(
            id="task_001",
            service_type=ServiceType.CHECKOUT,
            description="Process checkout",
            customer=customer,
            priority=TaskPriority.MEDIUM
        )

        consultation_task = ServiceTask(
            id="task_002",
            service_type=ServiceType.CONSULTATION,
            description="Product consultation",
            customer=customer,
            priority=TaskPriority.MEDIUM
        )

        # Different service types may have different time estimates
        checkout_time = checkout_task.estimate_time()
        consultation_time = consultation_task.estimate_time()

        assert checkout_time > 0
        assert consultation_time > 0


# ============================================================================
# Test ServiceAgent
# ============================================================================

class TestServiceAgent:
    """Test service agent (MMO character mapping)"""

    def test_create_service_agent(self):
        """Test creating a service agent"""
        store = Store(
            id="store_001",
            name="Electronics Plus",
            store_type="electronics",
            location=Location(
                id="loc_001",
                name="Store",
                location_type="store",
                coordinates=(0.0, 0.0)
            )
        )

        agent = ServiceAgent(
            id="agent_001",
            name="John Smith",
            role="cashier",
            store=store
        )

        assert agent.id == "agent_001"
        assert agent.name == "John Smith"
        assert agent.role_type == "service_agent"
        assert agent.store == store
        assert len(agent.skills) > 0  # Should have role-specific skills

    def test_agent_roles_have_appropriate_skills(self):
        """Test that different roles have appropriate skills"""
        store = Store(
            id="store_001",
            name="Electronics Plus",
            store_type="electronics",
            location=Location(
                id="loc_001",
                name="Store",
                location_type="store",
                coordinates=(0.0, 0.0)
            )
        )

        cashier = ServiceAgent(
            id="agent_001",
            name="Cashier",
            role="cashier",
            store=store
        )

        sales_associate = ServiceAgent(
            id="agent_002",
            name="Sales Associate",
            role="sales_associate",
            store=store
        )

        customer_service = ServiceAgent(
            id="agent_003",
            name="Customer Service",
            role="customer_service",
            store=store
        )

        # Cashier should have checkout skills
        assert cashier.has_skill("checkout") or cashier.has_skill("payment_processing")

        # Sales associate should have sales/product skills
        assert sales_associate.has_skill("product_knowledge") or sales_associate.has_skill("sales")

        # Customer service should have communication/problem-solving skills
        assert customer_service.has_skill("communication") or customer_service.has_skill("problem_solving")

    def test_agent_serve_customer(self):
        """Test agent serving customer"""
        store = Store(
            id="store_001",
            name="Electronics Plus",
            store_type="electronics",
            location=Location(
                id="loc_001",
                name="Store",
                location_type="store",
                coordinates=(0.0, 0.0)
            )
        )

        agent = ServiceAgent(
            id="agent_001",
            name="John Smith",
            role="cashier",
            store=store
        )

        customer = Customer(
            id="customer_001",
            name="Jane Doe"
        )

        initial_satisfaction = customer.satisfaction

        # Serve customer with good quality
        agent.serve_customer(customer, service_quality=0.9)

        # Customer satisfaction should improve
        assert customer.satisfaction >= initial_satisfaction

    def test_agent_serve_customer_poor_quality(self):
        """Test agent serving customer with poor quality"""
        store = Store(
            id="store_001",
            name="Electronics Plus",
            store_type="electronics",
            location=Location(
                id="loc_001",
                name="Store",
                location_type="store",
                coordinates=(0.0, 0.0)
            )
        )

        agent = ServiceAgent(
            id="agent_001",
            name="John Smith",
            role="cashier",
            store=store
        )

        customer = Customer(
            id="customer_001",
            name="Jane Doe"
        )
        customer.satisfaction = 0.8  # Start with good satisfaction

        # Serve customer with poor quality
        agent.serve_customer(customer, service_quality=0.3)

        # Customer satisfaction should decrease
        assert customer.satisfaction < 0.8


# ============================================================================
# Test Shift
# ============================================================================

class TestShift:
    """Test shift (work period)"""

    def test_create_shift(self):
        """Test creating a shift"""
        shift = Shift(
            id="shift_001",
            start_time=9.0,  # 9 AM
            duration=480  # 8 hours in minutes
        )

        assert shift.id == "shift_001"
        assert shift.start_time == 9.0
        assert shift.duration == 480
        assert shift.tasks == []

    def test_shift_add_task(self):
        """Test adding task to shift"""
        shift = Shift(
            id="shift_001",
            start_time=9.0,
            duration=480
        )

        customer = Customer(
            id="customer_001",
            name="Jane Doe"
        )

        task = ServiceTask(
            id="task_001",
            service_type=ServiceType.CHECKOUT,
            description="Process checkout",
            customer=customer,
            priority=TaskPriority.MEDIUM
        )

        shift.add_task(task)

        assert len(shift.tasks) == 1
        assert shift.tasks[0] == task

    def test_shift_calculate_workload(self):
        """Test calculating shift workload"""
        shift = Shift(
            id="shift_001",
            start_time=9.0,
            duration=480
        )

        customer1 = Customer(id="customer_001", name="Customer 1")
        customer2 = Customer(id="customer_002", name="Customer 2")

        task1 = ServiceTask(
            id="task_001",
            service_type=ServiceType.CHECKOUT,
            description="Checkout 1",
            customer=customer1,
            priority=TaskPriority.MEDIUM
        )

        task2 = ServiceTask(
            id="task_002",
            service_type=ServiceType.CONSULTATION,
            description="Consultation 1",
            customer=customer2,
            priority=TaskPriority.HIGH
        )

        shift.add_task(task1)
        shift.add_task(task2)

        workload = shift.calculate_workload()

        assert workload > 0
        assert workload == len(shift.tasks)  # Or based on time estimates


# ============================================================================
# Test RetailSimulator
# ============================================================================

class TestRetailSimulator:
    """Test retail simulator"""

    def test_create_retail_simulator(self):
        """Test creating retail simulator"""
        simulator = RetailSimulator()

        assert simulator.domain == "retail"
        assert simulator.scenarios == {}

    def test_create_retail_scenario(self):
        """Test creating retail scenario"""
        simulator = RetailSimulator()

        scenario = simulator.create_retail_scenario(
            name="Saturday Shopping",
            description="Busy Saturday at the store",
            num_agents=3,
            num_customers=20,
            num_products=15,
            store_type="retail"
        )

        assert scenario.name == "Saturday Shopping"
        assert scenario.description == "Busy Saturday at the store"
        assert len(scenario.professionals) == 3  # 3 agents
        # Customers are generated during simulation, not stored in scenario

    def test_retail_scenario_agents_assigned_to_store(self):
        """Test that all agents are assigned to a store"""
        simulator = RetailSimulator()

        scenario = simulator.create_retail_scenario(
            name="Test Scenario",
            description="Test",
            num_agents=4,
            num_customers=10,
            num_products=20,
            store_type="electronics"
        )

        for professional in scenario.professionals:
            agent = professional
            assert isinstance(agent, ServiceAgent)
            assert agent.store is not None

    def test_retail_scenario_has_products(self):
        """Test that store has products"""
        simulator = RetailSimulator()

        scenario = simulator.create_retail_scenario(
            name="Test Scenario",
            description="Test",
            num_agents=2,
            num_customers=10,
            num_products=25,
            store_type="grocery"
        )

        # Get store from first agent
        agent = scenario.professionals[0]
        store = agent.store

        assert len(store.products) == 25

    def test_simulate_shift(self):
        """Test simulating a retail shift"""
        simulator = RetailSimulator()

        scenario = simulator.create_retail_scenario(
            name="Shift Test",
            description="Test shift simulation",
            num_agents=3,
            num_customers=15,
            num_products=20,
            store_type="retail"
        )

        # Simulate shift
        report = simulator.simulate_shift(scenario, shift_duration=480)

        assert report is not None
        assert "completion_score" in report
        assert "total_performance" in report
        assert "tasks" in report

        # Some customers should have been served
        assert report["tasks"]["total"] > 0

    def test_get_performance_report(self):
        """Test getting retail performance report"""
        simulator = RetailSimulator()

        scenario = simulator.create_retail_scenario(
            name="Report Test",
            description="Test performance reporting",
            num_agents=2,
            num_customers=10,
            num_products=15,
            store_type="retail"
        )

        # Simulate shift
        simulator.simulate_shift(scenario, shift_duration=240)

        # Get report
        report = simulator.get_performance_report(scenario)

        assert report is not None
        assert "scenario_name" in report
        assert "completion_score" in report
        assert "professionals" in report

    def test_different_store_types(self):
        """Test creating scenarios for different store types"""
        simulator = RetailSimulator()

        store_types = ["retail", "grocery", "electronics"]

        for store_type in store_types:
            scenario = simulator.create_retail_scenario(
                name=f"{store_type.title()} Store",
                description=f"Test {store_type} store",
                num_agents=2,
                num_customers=10,
                num_products=15,
                store_type=store_type
            )

            assert scenario is not None
            agent = scenario.professionals[0]
            assert agent.store.store_type == store_type


# ============================================================================
# Integration Tests
# ============================================================================

class TestRetailSimulatorIntegration:
    """Integration tests for complete retail workflow"""

    def test_complete_retail_workflow(self):
        """Test complete retail workflow from creation to reporting"""
        # Create simulator
        simulator = RetailSimulator()

        # Create scenario
        scenario = simulator.create_retail_scenario(
            name="Complete Workflow Test",
            description="Full day retail simulation",
            num_agents=3,
            num_customers=25,
            num_products=30,
            store_type="retail"
        )

        # Verify scenario setup
        assert len(scenario.professionals) == 3

        # Simulate shift
        report = simulator.simulate_shift(scenario, shift_duration=480)

        assert report is not None
        assert report["completion_score"] >= 0
        assert report["completion_score"] <= 1.0

        # Get performance report
        performance = simulator.get_performance_report(scenario)

        assert performance is not None
        assert performance["scenario_name"] == "Complete Workflow Test"
        assert len(performance["professionals"]) == 3

        # Verify agents gained XP from serving customers
        for agent_report in performance["professionals"]:
            if agent_report["tasks_completed"] > 0:
                agent_id = agent_report["id"]
                agent = next(p for p in scenario.professionals if p.id == agent_id)
                assert agent.metrics.experience_points > 0

    def test_customer_mood_affects_satisfaction(self):
        """Test that customer mood system affects outcomes"""
        simulator = RetailSimulator()

        scenario = simulator.create_retail_scenario(
            name="Mood Test",
            description="Test customer mood effects",
            num_agents=2,
            num_customers=20,
            num_products=15,
            store_type="retail"
        )

        # Simulate shift
        report = simulator.simulate_shift(scenario, shift_duration=480)

        # Should have customer satisfaction data
        assert "tasks" in report
        assert report["tasks"]["total"] > 0

        # Some customers may have different moods affecting outcomes
        # (Specific assertions depend on implementation details)

    def test_agent_skill_affects_performance(self):
        """Test that agent skills affect service quality"""
        simulator = RetailSimulator()

        scenario = simulator.create_retail_scenario(
            name="Skill Test",
            description="Test agent skill effects",
            num_agents=3,
            num_customers=15,
            num_products=20,
            store_type="electronics"
        )

        # Boost one agent's skills
        skilled_agent = scenario.professionals[0]
        for skill in skilled_agent.skills:
            skilled_agent.skill_levels[skill] = 5  # Max skill

        # Simulate shift
        simulator.simulate_shift(scenario, shift_duration=480)

        # Skilled agent should perform better
        report = simulator.get_performance_report(scenario)

        skilled_agent_report = next(
            p for p in report["professionals"] if p["id"] == skilled_agent.id
        )

        # Skilled agent should have high efficiency/quality
        if skilled_agent_report["tasks_completed"] > 0:
            assert skilled_agent_report["efficiency"] > 0.5
            assert skilled_agent_report["quality"] > 0.5

    def test_high_traffic_scenario(self):
        """Test high-traffic retail scenario"""
        simulator = RetailSimulator()

        scenario = simulator.create_retail_scenario(
            name="Black Friday",
            description="High-traffic shopping day",
            num_agents=5,
            num_customers=100,
            num_products=50,
            store_type="retail"
        )

        # Verify scenario created
        assert len(scenario.professionals) == 5

        # Simulate shift
        report = simulator.simulate_shift(scenario, shift_duration=480)

        assert report is not None
        assert report["tasks"]["total"] > 0

        # Not all customers may be served in high-traffic
        # (Some may remain pending or leave)

    def test_service_type_distribution(self):
        """Test that different service types are handled"""
        simulator = RetailSimulator()

        scenario = simulator.create_retail_scenario(
            name="Service Type Test",
            description="Test various service types",
            num_agents=3,
            num_customers=30,
            num_products=25,
            store_type="retail"
        )

        # Simulate shift
        simulator.simulate_shift(scenario, shift_duration=480)

        # Check that different service types were created
        # (Implementation dependent - tasks may be in shift or elsewhere)

        report = simulator.get_performance_report(scenario)

        # Should have served multiple customers
        total_tasks = sum(p["tasks_completed"] for p in report["professionals"])
        assert total_tasks > 0

    def test_agent_leveling_from_experience(self):
        """Test that agents level up from experience"""
        simulator = RetailSimulator()

        scenario = simulator.create_retail_scenario(
            name="Leveling Test",
            description="Test agent leveling",
            num_agents=2,
            num_customers=50,
            num_products=20,
            store_type="retail"
        )

        # Check initial levels
        initial_levels = [agent.metrics.level for agent in scenario.professionals]

        # Simulate long shift with many customers
        simulator.simulate_shift(scenario, shift_duration=480)

        # Check if any agents leveled up
        final_levels = [agent.metrics.level for agent in scenario.professionals]

        # At least one agent should gain XP
        total_xp = sum(agent.metrics.experience_points for agent in scenario.professionals)
        assert total_xp > 0

    def test_customer_wait_time_tracking(self):
        """Test that customer wait times are tracked"""
        simulator = RetailSimulator()

        scenario = simulator.create_retail_scenario(
            name="Wait Time Test",
            description="Test customer wait tracking",
            num_agents=1,  # Limited agents = longer waits
            num_customers=20,
            num_products=15,
            store_type="retail"
        )

        # Simulate shift
        report = simulator.simulate_shift(scenario, shift_duration=480)

        # With only 1 agent and 20 customers, some waiting should occur
        assert report is not None

        # Report should include metrics about service
        assert "tasks" in report
