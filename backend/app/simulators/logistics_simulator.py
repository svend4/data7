"""
Logistics and Transport Professional Simulator

Domain: Delivery, Routing, Fleet Management
Status: 15% → 60% (integrating with TSP)

Maps logistics operations to MMO mechanics:
- Delivery Driver → MMO Rogue (fast, mobile, route optimization)
- Warehouse → MMO City (quest hub)
- Delivery Task → MMO Fetch Quest
- Vehicle → MMO Mount
- Route → MMO Quest Chain

Uses existing TSP algorithms for route optimization.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta

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

# Import existing TSP for route optimization
from app.services.tsp_algorithms import (
    TSPNode,
    TSPDepot,
    MultiDepotTSP,
    DynamicTSP,
    StochasticTSP,
    TSPSolution
)


@dataclass
class Vehicle(Resource):
    """
    Delivery vehicle (maps to MMO Mount)

    Attributes:
    - speed: Average speed in km/h
    - fuel_capacity: Fuel tank capacity
    - current_fuel: Current fuel level
    - cargo_capacity: Max cargo weight in kg
    """

    def __init__(
        self,
        id: str,
        name: str,
        speed: float = 60.0,  # km/h
        fuel_capacity: float = 50.0,  # liters
        cargo_capacity: float = 1000.0  # kg
    ):
        super().__init__(
            id=id,
            name=name,
            resource_type=ResourceType.VEHICLE,
            capacity=cargo_capacity
        )
        self.speed = speed
        self.fuel_capacity = fuel_capacity
        self.current_fuel = fuel_capacity
        self.metadata.update({
            "speed": speed,
            "fuel_capacity": fuel_capacity,
            "current_fuel": fuel_capacity,
            "total_distance_traveled": 0.0
        })

    def consume_fuel(self, distance_km: float):
        """Consume fuel based on distance traveled"""
        fuel_consumption_rate = 0.1  # liters per km
        fuel_used = distance_km * fuel_consumption_rate
        self.current_fuel = max(0.0, self.current_fuel - fuel_used)
        self.metadata["total_distance_traveled"] += distance_km

    def refuel(self):
        """Refuel vehicle"""
        self.current_fuel = self.fuel_capacity

    def needs_refuel(self) -> bool:
        """Check if vehicle needs refueling"""
        return self.current_fuel < self.fuel_capacity * 0.2  # 20% threshold


@dataclass
class Warehouse(Location):
    """
    Warehouse location (maps to MMO City/Quest Hub)
    """

    def __init__(
        self,
        id: str,
        name: str,
        coordinates: tuple,
        capacity: int = 1000,
        address: Optional[str] = None
    ):
        super().__init__(
            id=id,
            name=name,
            location_type="warehouse",
            coordinates=coordinates,
            capacity=capacity,
            address=address
        )
        self.metadata.update({
            "packages_in_stock": 0,
            "packages_shipped": 0,
            "is_operational": True
        })


@dataclass
class DeliveryTask(Task):
    """
    Delivery task (maps to MMO Fetch Quest)

    Attributes:
    - pickup_location: Where to pick up package
    - delivery_location: Where to deliver package
    - package_weight: Weight of package in kg
    - delivery_window: Time window for delivery
    """

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        pickup_location: Location,
        delivery_location: Location,
        package_weight: float = 10.0,
        priority: int = 0,
        delivery_window: Optional[Tuple[datetime, datetime]] = None
    ):
        super().__init__(
            id=id,
            name=name,
            description=description,
            task_type=TaskType.DELIVERY,
            location=delivery_location,
            priority=priority
        )
        self.pickup_location = pickup_location
        self.delivery_location = delivery_location
        self.package_weight = package_weight
        self.delivery_window = delivery_window

        # Calculate estimated duration based on distance
        self.estimated_duration = self._estimate_duration()

        self.required_skills = ["driving", "navigation"]
        self.required_resources = ["vehicle"]

    def _estimate_duration(self) -> float:
        """Estimate delivery duration based on distance"""
        # Simple Euclidean distance
        pickup_coords = self.pickup_location.coordinates
        delivery_coords = self.delivery_location.coordinates

        distance = ((pickup_coords[0] - delivery_coords[0])**2 +
                   (pickup_coords[1] - delivery_coords[1])**2)**0.5

        # Assume 60 km/h average speed
        travel_time = (distance / 60.0) * 60  # Convert to minutes
        handling_time = 10.0  # 10 minutes for pickup/delivery

        return travel_time + handling_time


@dataclass
class DeliveryDriver(ProfessionalRole):
    """
    Delivery driver (maps to MMO Rogue - fast, mobile)

    Skills:
    - Driving: Ability to operate vehicle safely
    - Navigation: Route finding and optimization
    - Time Management: Meeting delivery windows
    - Customer Service: Professional interaction
    """

    def __init__(
        self,
        id: str,
        name: str,
        vehicle: Vehicle,
        home_warehouse: Warehouse
    ):
        super().__init__(
            id=id,
            name=name,
            role_type="delivery_driver"
        )

        # Driver-specific skills
        self.add_skill("driving", level=1)
        self.add_skill("navigation", level=1)
        self.add_skill("time_management", level=1)
        self.add_skill("customer_service", level=1)

        # Assign vehicle
        self.resources = [vehicle]
        self.vehicle = vehicle

        # Home warehouse
        self.current_location = home_warehouse
        self.home_warehouse = home_warehouse

        # Route tracking
        self.current_route: List[Location] = []
        self.route_distance: float = 0.0

    def start_route(self, route: List[Location], distance: float):
        """Start delivery route"""
        self.current_route = route
        self.route_distance = distance

    def complete_route(self, performance_score: float = 1.0):
        """Complete delivery route"""
        # Consume fuel
        self.vehicle.consume_fuel(self.route_distance)

        # Update metrics
        self.metadata["total_deliveries"] = self.metadata.get("total_deliveries", 0) + len(self.current_route)
        self.metadata["total_distance"] = self.metadata.get("total_distance", 0.0) + self.route_distance

        # Clear route
        self.current_route = []
        self.route_distance = 0.0

        # Return to warehouse
        self.current_location = self.home_warehouse


@dataclass
class Route:
    """
    Delivery route (maps to MMO Quest Chain)

    A sequence of delivery tasks optimized using TSP
    """
    id: str
    driver: DeliveryDriver
    tasks: List[DeliveryTask]
    locations: List[Location]
    total_distance: float
    estimated_time: float
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "planned"  # planned, active, completed, failed

    def start(self):
        """Start route execution"""
        self.status = "active"
        self.start_time = datetime.now()
        self.driver.start_route(self.locations, self.total_distance)

    def complete(self, performance_score: float = 1.0):
        """Complete route"""
        self.status = "completed"
        self.end_time = datetime.now()
        self.driver.complete_route(performance_score)


class LogisticsSimulator(ProfessionalSimulator):
    """
    Logistics and Transport Simulator

    Domain: Delivery, Routing, Fleet Management
    Uses TSP algorithms for route optimization

    Features:
    - Multi-depot TSP for multiple warehouses
    - Dynamic TSP for real-time deliveries
    - Stochastic TSP for uncertain availability
    - Vehicle routing with constraints
    - Performance tracking and optimization
    """

    def __init__(self):
        super().__init__(domain="logistics")
        self.warehouses: List[Warehouse] = []
        self.drivers: List[DeliveryDriver] = []
        self.vehicles: List[Vehicle] = []
        self.routes: List[Route] = []

    def create_logistics_scenario(
        self,
        name: str,
        description: str,
        num_drivers: int = 3,
        num_deliveries: int = 20
    ) -> SimulationScenario:
        """
        Create logistics scenario

        Args:
            name: Scenario name
            description: Scenario description
            num_drivers: Number of delivery drivers
            num_deliveries: Number of delivery tasks

        Returns:
            SimulationScenario configured for logistics
        """
        scenario = self.create_scenario(name, description, "daily_operations")

        # Create main warehouse
        warehouse = Warehouse(
            id="warehouse_central",
            name="Central Warehouse",
            coordinates=(0.0, 0.0),
            capacity=1000,
            address="123 Main St"
        )
        self.warehouses.append(warehouse)
        scenario.locations.append(warehouse)

        # Create drivers with vehicles
        for i in range(num_drivers):
            # Create vehicle
            vehicle = Vehicle(
                id=f"vehicle_{i+1}",
                name=f"Delivery Van {i+1}",
                speed=60.0,
                fuel_capacity=50.0,
                cargo_capacity=1000.0
            )
            self.vehicles.append(vehicle)
            scenario.resources.append(vehicle)

            # Create driver
            driver = DeliveryDriver(
                id=f"driver_{i+1}",
                name=f"Driver {i+1}",
                vehicle=vehicle,
                home_warehouse=warehouse
            )
            self.drivers.append(driver)
            scenario.professionals.append(driver)

        # Create delivery tasks
        import random
        random.seed(42)

        for i in range(num_deliveries):
            # Random delivery location
            delivery_loc = Location(
                id=f"delivery_{i+1}",
                name=f"Customer {i+1}",
                location_type="customer",
                coordinates=(
                    random.uniform(-10.0, 10.0),
                    random.uniform(-10.0, 10.0)
                ),
                address=f"{random.randint(1, 999)} Street {i+1}"
            )
            scenario.locations.append(delivery_loc)

            # Create delivery task
            delivery = DeliveryTask(
                id=f"delivery_task_{i+1}",
                name=f"Deliver to Customer {i+1}",
                description=f"Deliver package to {delivery_loc.address}",
                pickup_location=warehouse,
                delivery_location=delivery_loc,
                package_weight=random.uniform(5.0, 50.0),
                priority=random.choice([0, 1, 2])
            )
            scenario.tasks.append(delivery)

        # Set objectives
        scenario.objectives = [
            {
                "type": "complete_all_deliveries",
                "description": "Complete all delivery tasks",
                "target": num_deliveries
            },
            {
                "type": "minimize_total_distance",
                "description": "Minimize total distance traveled"
            },
            {
                "type": "maximize_efficiency",
                "description": "Maximize delivery efficiency",
                "target": 0.8
            }
        ]

        return scenario

    def optimize_routes_with_tsp(
        self,
        scenario: SimulationScenario
    ) -> List[Route]:
        """
        Optimize delivery routes using Multi-depot TSP

        Uses existing TSP implementation from services/tsp_algorithms.py

        Args:
            scenario: Logistics scenario

        Returns:
            List of optimized routes
        """
        # Extract delivery tasks
        delivery_tasks = [t for t in scenario.tasks if isinstance(t, DeliveryTask)]

        if not delivery_tasks:
            return []

        # Convert locations to TSP nodes
        tsp_nodes = []
        for task in delivery_tasks:
            loc = task.delivery_location
            node = TSPNode(
                id=loc.id,
                x=loc.coordinates[0],
                y=loc.coordinates[1],
                demand=task.package_weight,
                service_time=10.0,  # 10 minutes per delivery
                priority=task.priority
            )
            tsp_nodes.append(node)

        # Convert warehouses to TSP depots
        tsp_depots = []
        for warehouse in self.warehouses:
            depot = TSPDepot(
                id=warehouse.id,
                node=TSPNode(
                    id=warehouse.id,
                    x=warehouse.coordinates[0],
                    y=warehouse.coordinates[1]
                ),
                capacity=warehouse.capacity or 1000.0,
                available_agents=len([d for d in self.drivers if d.home_warehouse.id == warehouse.id])
            )
            tsp_depots.append(depot)

        # Build distance matrix
        distance_matrix = {}
        all_nodes = tsp_nodes + [d.node for d in tsp_depots]

        for i, node1 in enumerate(all_nodes):
            for node2 in all_nodes[i+1:]:
                dist = ((node1.x - node2.x)**2 + (node1.y - node2.y)**2)**0.5
                distance_matrix[(node1.id, node2.id)] = dist
                distance_matrix[(node2.id, node1.id)] = dist

        # Solve Multi-depot TSP
        mdtsp = MultiDepotTSP(tsp_nodes, tsp_depots, distance_matrix)
        solution = mdtsp.solve(algorithm="cluster_first_route_second")

        # Convert TSP solution to routes
        routes = self._convert_tsp_solution_to_routes(
            solution,
            delivery_tasks,
            scenario.professionals
        )

        self.routes.extend(routes)

        return routes

    def _convert_tsp_solution_to_routes(
        self,
        tsp_solution: TSPSolution,
        tasks: List[DeliveryTask],
        drivers: List[ProfessionalRole]
    ) -> List[Route]:
        """Convert TSP solution to delivery routes"""
        routes = []

        task_dict = {t.delivery_location.id: t for t in tasks}

        for route_idx, tsp_route in enumerate(tsp_solution.routes):
            if route_idx >= len(drivers):
                break

            driver = drivers[route_idx]
            if not isinstance(driver, DeliveryDriver):
                continue

            # Extract tasks and locations from TSP route
            route_tasks = []
            route_locations = []

            for location_id in tsp_route:
                if location_id in task_dict:
                    task = task_dict[location_id]
                    route_tasks.append(task)
                    route_locations.append(task.delivery_location)

            if not route_tasks:
                continue

            # Calculate route distance
            route_distance = 0.0
            prev_loc = driver.home_warehouse.coordinates

            for loc in route_locations:
                curr_coords = loc.coordinates
                dist = ((prev_loc[0] - curr_coords[0])**2 +
                       (prev_loc[1] - curr_coords[1])**2)**0.5
                route_distance += dist
                prev_loc = curr_coords

            # Return distance to warehouse
            route_distance += ((prev_loc[0] - driver.home_warehouse.coordinates[0])**2 +
                              (prev_loc[1] - driver.home_warehouse.coordinates[1])**2)**0.5

            # Estimate time
            estimated_time = (route_distance / driver.vehicle.speed) * 60  # Convert to minutes
            estimated_time += len(route_tasks) * 10  # 10 min per delivery

            # Create route
            route = Route(
                id=f"route_{route_idx+1}",
                driver=driver,
                tasks=route_tasks,
                locations=route_locations,
                total_distance=route_distance,
                estimated_time=estimated_time
            )

            routes.append(route)

        return routes

    def assign_tasks(self, scenario: SimulationScenario) -> Dict[str, List[Task]]:
        """
        Assign tasks using TSP optimization

        Override base implementation to use TSP
        """
        # Optimize routes with TSP
        routes = self.optimize_routes_with_tsp(scenario)

        # Build assignments
        assignments: Dict[str, List[Task]] = {p.id: [] for p in scenario.professionals}

        for route in routes:
            assignments[route.driver.id] = route.tasks

            # Assign tasks to driver
            for task in route.tasks:
                route.driver.assign_task(task)

        return assignments

    def optimize_assignments(
        self,
        scenario: SimulationScenario
    ) -> Dict[str, Any]:
        """
        Optimize task assignments using TSP

        Returns optimization report with suggestions
        """
        # Optimize routes
        routes = self.optimize_routes_with_tsp(scenario)

        # Calculate metrics
        total_distance = sum(r.total_distance for r in routes)
        total_time = sum(r.estimated_time for r in routes)
        max_time = max((r.estimated_time for r in routes), default=0)

        # Load balance
        route_loads = [len(r.tasks) for r in routes]
        avg_load = sum(route_loads) / len(route_loads) if route_loads else 0
        load_variance = sum((load - avg_load)**2 for load in route_loads) / len(route_loads) if route_loads else 0

        # Generate suggestions
        suggestions = []

        # Check for unbalanced routes
        if load_variance > avg_load * 0.5:
            suggestions.append({
                "type": "load_imbalance",
                "message": "Routes are imbalanced - consider redistributing deliveries",
                "details": {
                    "avg_load": avg_load,
                    "variance": load_variance
                }
            })

        # Check for long routes
        for route in routes:
            if route.estimated_time > 480:  # 8 hours
                suggestions.append({
                    "type": "route_too_long",
                    "message": f"Route {route.id} exceeds 8 hours",
                    "details": {
                        "route_id": route.id,
                        "driver": route.driver.name,
                        "estimated_time": route.estimated_time
                    }
                })

        # Check fuel levels
        for route in routes:
            fuel_needed = route.total_distance * 0.1  # liters
            if fuel_needed > route.driver.vehicle.current_fuel:
                suggestions.append({
                    "type": "insufficient_fuel",
                    "message": f"Vehicle {route.driver.vehicle.name} needs refueling",
                    "details": {
                        "vehicle_id": route.driver.vehicle.id,
                        "current_fuel": route.driver.vehicle.current_fuel,
                        "fuel_needed": fuel_needed
                    }
                })

        return {
            "total_routes": len(routes),
            "total_distance": total_distance,
            "total_time": total_time,
            "max_time": max_time,
            "avg_route_load": avg_load,
            "load_variance": load_variance,
            "suggestions": suggestions,
            "routes": [
                {
                    "id": r.id,
                    "driver": r.driver.name,
                    "num_deliveries": len(r.tasks),
                    "distance": r.total_distance,
                    "estimated_time": r.estimated_time
                }
                for r in routes
            ]
        }

    def simulate_day(self, scenario: SimulationScenario) -> Dict[str, Any]:
        """
        Simulate a full day of deliveries

        Returns simulation results
        """
        # Start scenario
        scenario.start()

        # Optimize and assign routes
        assignments = self.assign_tasks(scenario)

        # Simulate route execution
        for route in self.routes:
            route.start()

            # Simulate deliveries
            for task in route.tasks:
                # Random performance score (0.8 - 1.0)
                import random
                performance = random.uniform(0.8, 1.0)

                task.complete(performance)
                route.driver.complete_current_task(performance)

            route.complete(performance)

        # Complete scenario
        scenario.complete()

        # Generate report
        report = self.get_performance_report(scenario)

        # Add logistics-specific metrics
        report["logistics_metrics"] = {
            "total_distance_traveled": sum(r.total_distance for r in self.routes),
            "avg_distance_per_route": sum(r.total_distance for r in self.routes) / len(self.routes) if self.routes else 0,
            "total_deliveries": sum(len(r.tasks) for r in self.routes),
            "avg_deliveries_per_driver": sum(len(r.tasks) for r in self.routes) / len(self.drivers) if self.drivers else 0
        }

        return report
