# API Usage Examples

This directory contains comprehensive examples demonstrating how to use the Switchboard API endpoints.

## 📋 Prerequisites

1. **Start the API server:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
   The server will be available at `http://localhost:8000`

2. **Install dependencies:**
   ```bash
   pip install httpx asyncio
   ```

## 📁 Available Examples

### 1. TSP API Examples (`tsp_api_examples.py`)

Demonstrates all TSP (Traveling Salesman Problem) algorithms and their applications.

**Run:**
```bash
python backend/examples/tsp_api_examples.py
```

**Includes:**
- ✅ **Multi-depot TSP** - Allocate tasks to multiple agents
- ✅ **Hierarchical TSP** - Optimize dissertation chapter order
- ✅ **Stochastic TSP** - Handle uncertain task availability
- ✅ **2-opt Optimization** - Fast route improvement (15-30% better)
- ✅ **Genetic Algorithm** - Global optimization for complex routes
- ✅ **List Algorithms** - View all available algorithms

**Use Cases:**
- Multi-agent task allocation
- Document structure optimization
- Planning under uncertainty
- Route optimization

---

### 2. Multi-Agent Coordination Examples (`multi_agent_api_examples.py`)

Shows how to coordinate multiple AI agents using different strategies.

**Run:**
```bash
python backend/examples/multi_agent_api_examples.py
```

**Includes:**
- ✅ **Minimize Time** - Fastest completion (urgent deadlines)
- ✅ **Minimize Cost** - Lowest API costs (budget constraints)
- ✅ **Balance Load** - Even distribution (fair allocation)
- ✅ **Maximize Throughput** - Maximum parallelism (high volume)
- ✅ **Predict Completion** - Estimate before executing
- ✅ **Compare Strategies** - Side-by-side comparison
- ✅ **List Strategies** - View all available strategies

**Use Cases:**
- Software development teams
- Customer support automation
- Data processing pipelines
- Resource planning

---

### 3. Knowledge Transformation Examples (`knowledge_api_examples.py`)

Demonstrates transforming AI knowledge into educational game content.

**Run:**
```bash
python backend/examples/knowledge_api_examples.py
```

**Includes:**
- ✅ **Paper → Quests** - Transform research papers into quest chains
- ✅ **Concept → Class** - Convert ML concepts to character classes
- ✅ **Graph → MMO World** - Generate complete game worlds
- ✅ **Learning Path** - Create optimized quest orders
- ✅ **Complete Workflow** - Full pipeline from curriculum to game
- ✅ **List Transformations** - View all transformation patterns

**Use Cases:**
- Educational game development
- AI/ML curriculum gamification
- Research paper onboarding
- Interactive learning experiences

---

## 🎯 Quick Start

### Run All Examples

```bash
# Run TSP examples
python backend/examples/tsp_api_examples.py

# Run Multi-Agent examples
python backend/examples/multi_agent_api_examples.py

# Run Knowledge Transformation examples
python backend/examples/knowledge_api_examples.py
```

### Run Individual Examples

Each example file contains a `main()` function that runs all examples sequentially. To run specific examples, modify the `main()` function:

```python
async def main():
    # Run only specific examples
    await example_minimize_time()
    await example_predict_completion()
```

---

## 📊 Example Output

### TSP API Example Output:
```
================================================================================
Example 1: Multi-depot TSP for Agent Task Allocation
================================================================================

✅ Successfully solved Multi-depot TSP!
Total Distance: 12.45
Total Cost: 45.30
Total Time: 38.50

Agent Assignments:
  Agent 1: depot1 → ticket1 → ticket2 → depot1
  Agent 2: depot2 → ticket3 → ticket4 → ticket5 → depot2
  Agent 3: depot3 → ticket6 → ticket7 → ticket8 → depot3
```

### Multi-Agent Example Output:
```
================================================================================
Example 1: Minimize Time Strategy
================================================================================

✅ Successfully coordinated agents (MINIMIZE_TIME)!
Total Time: 30.00 minutes
Total Cost: $0.26
Load Balance Score: 0.85
Parallelism Factor: 2.5x

Task Assignments:

  Senior Developer (agent1):
    Tasks: task1, task2
    Time: 30.00 min
    Cost: $0.18

  DevOps Engineer (agent3):
    Tasks: task4
    Time: 10.00 min
    Cost: $0.03
```

### Knowledge API Example Output:
```
================================================================================
Example 1: Research Paper → Quest Chain
================================================================================

✅ Successfully transformed paper into 4 quests!

📜 Quest Chain:

Quest 1: The Sequential Problem
  Difficulty: advanced
  Description: Discover the limitations of recurrent models
  Objectives:
    - Understand sequential computation bottleneck
    - Identify parallelization challenges
  Rewards:
    - Understanding of RNN limitations
    - 100 XP

Quest 2: The Attention Mechanism
  Difficulty: advanced
  Description: Learn how self-attention enables parallel computation
  ...
```

---

## 🔍 API Endpoints Reference

### TSP API (`/api/tsp`)
- `POST /multi-depot/solve` - Solve multi-depot TSP
- `POST /hierarchical/solve` - Solve hierarchical TSP
- `POST /stochastic/solve` - Solve stochastic TSP
- `POST /optimize` - Optimize route with various algorithms
- `GET /algorithms` - List available algorithms

### Multi-Agent API (`/api/multi-agent`)
- `POST /coordinate` - Coordinate agents with strategy
- `POST /predict` - Predict completion time
- `GET /strategies` - List coordination strategies
- `GET /metrics` - Get metrics information

### Knowledge API (`/api/knowledge`)
- `POST /paper-to-quests` - Transform paper to quest chain
- `POST /concept-to-class` - Transform concept to character class
- `POST /graph-to-mmo` - Transform knowledge graph to MMO world
- `POST /learning-path` - Create optimal learning path
- `GET /transformations` - List available transformations

---

## 🛠️ Customizing Examples

### Modify TSP Parameters:

```python
# Change number of nodes
nodes = [
    TSPNode(id=f"node{i}", x=i*1.0, y=i*0.5, demand=1.0)
    for i in range(10)  # 10 nodes instead of 4
]

# Try different algorithms
payload = {
    "nodes": nodes,
    "depots": depots,
    "distance_matrix": distance_matrix,
    "algorithm": "savings"  # Try "savings" or "nearest_neighbor"
}
```

### Modify Multi-Agent Strategies:

```python
# Compare different strategies
strategies = ["minimize_time", "minimize_cost", "balance_load"]

for strategy in strategies:
    result = await coordinate_agents(agents, tasks, strategy)
    print(f"{strategy}: Time={result.total_time}, Cost={result.total_cost}")
```

### Modify Knowledge Transformations:

```python
# Transform your own paper
payload = {
    "title": "Your Paper Title",
    "content": "Your paper content...",
    "type": "paper",
    "difficulty": "intermediate",  # beginner, intermediate, advanced, expert
    "keywords": ["keyword1", "keyword2"],
    "sections": {
        "introduction": "...",
        "method": "...",
        "experiments": "...",
        "conclusion": "..."
    }
}
```

---

## 📚 Additional Resources

- **API Documentation:** http://localhost:8000/api/docs (Swagger UI)
- **API Reference:** http://localhost:8000/api/redoc (ReDoc)
- **OpenAPI Spec:** http://localhost:8000/api/openapi.json

---

## 🐛 Troubleshooting

### Error: "Could not connect to API server"
**Solution:** Make sure the server is running:
```bash
uvicorn app.main:app --reload
```

### Error: "Module not found: httpx"
**Solution:** Install dependencies:
```bash
pip install httpx
```

### Error: 400 Bad Request
**Solution:** Check your payload format. Compare with examples and ensure all required fields are present.

### Error: 500 Internal Server Error
**Solution:** Check server logs for detailed error messages:
```bash
# Server terminal will show detailed traceback
```

---

## 💡 Tips

1. **Start Simple:** Begin with the simplest examples (list endpoints) before moving to complex ones
2. **Check Responses:** Always verify HTTP status codes and response structure
3. **Experiment:** Modify parameters to see how results change
4. **Read Metadata:** Response metadata often contains useful debugging information
5. **Use Async:** All examples use `async/await` for better performance with multiple requests

---

## 🤝 Contributing

To add new examples:

1. Create a new example function in the appropriate file
2. Follow the existing pattern:
   - Clear docstring explaining the scenario
   - Print section headers
   - Make API request
   - Display results in readable format
3. Add the example to the `main()` function
4. Update this README with the new example

---

## 📝 License

Part of the Switchboard API project. See main project LICENSE for details.
