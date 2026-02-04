# Technical Specification Part 3: API Specifications

**Version**: 8.1 (continued)
**Date**: 2026-02-04
**API Style**: RESTful + WebSocket
**Format**: OpenAPI 3.0

---

## 📋 Overview

API спецификации для всех компонентов системы. Движемся **от простого к сложному**:

1. ✅ **Level 1: Agent Management API** (Simplest - CRUD operations)
2. ⏳ **Level 2: Connection Management API** (Medium)
3. ⏳ **Level 3: Graph Management API** (Complex)
4. ⏳ **Level 4: Execution API** (Very Complex)
5. ⏳ **Level 5: Real-time Streaming API** (WebSocket)

---

## 🔷 LEVEL 1: Agent Management API (Простейший)

### 1.1. Overview

```yaml
openapi: 3.0.0
info:
  title: Agent Management API
  version: 1.0.0
  description: |
    API для управления AI агентами в системе.
    Базовые CRUD операции.

servers:
  - url: https://api.mmo-ai-bridge.com/v1
    description: Production
  - url: http://localhost:8000/v1
    description: Development

tags:
  - name: agents
    description: Agent management operations
```

### 1.2. Endpoints

#### **GET /agents** - List all agents

```yaml
/agents:
  get:
    summary: List all registered agents
    tags: [agents]
    parameters:
      - name: role
        in: query
        description: Filter by agent role
        required: false
        schema:
          type: string
          example: "budget_analyst"

      - name: status
        in: query
        description: Filter by status
        required: false
        schema:
          type: string
          enum: [idle, thinking, communicating, error, offline]

      - name: capability
        in: query
        description: Filter by capability
        required: false
        schema:
          type: string
          example: "data_analysis"

      - name: limit
        in: query
        description: Max number of results
        required: false
        schema:
          type: integer
          default: 100
          minimum: 1
          maximum: 1000

      - name: offset
        in: query
        description: Pagination offset
        required: false
        schema:
          type: integer
          default: 0
          minimum: 0

    responses:
      '200':
        description: List of agents
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
                    $ref: '#/components/schemas/Agent'
                pagination:
                  $ref: '#/components/schemas/Pagination'
                metadata:
                  type: object
                  properties:
                    total_count:
                      type: integer
                    available_count:
                      type: integer
                    avg_load:
                      type: number
                      format: float

            example:
              data:
                - id: "agent_123abc"
                  role: "budget_analyst"
                  status: "idle"
                  capabilities:
                    - name: "cost_analysis"
                      description: "Analyze costs and budgets"
                      cost: 0.5
                      success_rate: 0.95
                  avg_response_time: 2.3
                  success_rate: 0.94
                  current_load: 0.15
                - id: "agent_456def"
                  role: "project_manager"
                  status: "thinking"
                  capabilities:
                    - name: "task_planning"
                      description: "Plan and organize tasks"
                      cost: 0.8
                      success_rate: 0.92
                  avg_response_time: 3.1
                  success_rate: 0.89
                  current_load: 0.67
              pagination:
                limit: 100
                offset: 0
                total: 2
              metadata:
                total_count: 2
                available_count: 1
                avg_load: 0.41

      '400':
        $ref: '#/components/responses/BadRequest'
      '500':
        $ref: '#/components/responses/InternalError'
```

#### **POST /agents** - Register new agent

```yaml
  post:
    summary: Register a new agent
    tags: [agents]
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - role
              - capabilities
            properties:
              role:
                type: string
                description: Agent role/type
                example: "data_scientist"

              capabilities:
                type: array
                description: List of agent capabilities
                items:
                  type: object
                  required: [name, description, cost, success_rate]
                  properties:
                    name:
                      type: string
                    description:
                      type: string
                    cost:
                      type: number
                      format: float
                    success_rate:
                      type: number
                      format: float
                      minimum: 0.0
                      maximum: 1.0

              llm_backend:
                type: string
                description: LLM backend to use
                enum: [gpt-4, gpt-3.5-turbo, claude-3, custom]
                default: gpt-4

              metadata:
                type: object
                description: Additional metadata
                additionalProperties: true

          example:
            role: "data_scientist"
            capabilities:
              - name: "statistical_analysis"
                description: "Perform statistical analysis"
                cost: 1.2
                success_rate: 0.96
              - name: "ml_modeling"
                description: "Build ML models"
                cost: 2.5
                success_rate: 0.88
            llm_backend: "gpt-4"
            metadata:
              team: "analytics"
              region: "us-west"

    responses:
      '201':
        description: Agent created successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: string
                  description: Generated agent ID
                message:
                  type: string
                agent:
                  $ref: '#/components/schemas/Agent'

            example:
              id: "agent_789ghi"
              message: "Agent registered successfully"
              agent:
                id: "agent_789ghi"
                role: "data_scientist"
                status: "idle"
                capabilities:
                  - name: "statistical_analysis"
                    description: "Perform statistical analysis"
                    cost: 1.2
                    success_rate: 0.96
                avg_response_time: 0.0
                success_rate: 1.0
                current_load: 0.0

      '400':
        $ref: '#/components/responses/BadRequest'
      '409':
        description: Agent already exists
      '500':
        $ref: '#/components/responses/InternalError'
```

#### **GET /agents/{agentId}** - Get specific agent

```yaml
  /agents/{agentId}:
    get:
      summary: Get agent details
      tags: [agents]
      parameters:
        - name: agentId
          in: path
          required: true
          schema:
            type: string
          description: Agent ID
          example: "agent_123abc"

      responses:
        '200':
          description: Agent details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Agent'

              example:
                id: "agent_123abc"
                role: "budget_analyst"
                status: "idle"
                capabilities:
                  - name: "cost_analysis"
                    description: "Analyze costs"
                    cost: 0.5
                    success_rate: 0.95
                avg_response_time: 2.3
                success_rate: 0.94
                current_load: 0.15
                created_at: "2026-02-04T10:00:00Z"
                updated_at: "2026-02-04T12:30:00Z"

        '404':
          $ref: '#/components/responses/NotFound'
        '500':
          $ref: '#/components/responses/InternalError'
```

#### **PATCH /agents/{agentId}** - Update agent

```yaml
    patch:
      summary: Update agent properties
      tags: [agents]
      parameters:
        - name: agentId
          in: path
          required: true
          schema:
            type: string

      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: [idle, thinking, communicating, error, offline]
                capabilities:
                  type: array
                  items:
                    type: object
                metadata:
                  type: object

            example:
              status: "offline"
              metadata:
                maintenance: true

      responses:
        '200':
          description: Agent updated
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                  agent:
                    $ref: '#/components/schemas/Agent'

        '400':
          $ref: '#/components/responses/BadRequest'
        '404':
          $ref: '#/components/responses/NotFound'
        '500':
          $ref: '#/components/responses/InternalError'
```

#### **DELETE /agents/{agentId}** - Unregister agent

```yaml
    delete:
      summary: Unregister agent
      tags: [agents]
      parameters:
        - name: agentId
          in: path
          required: true
          schema:
            type: string

      responses:
        '204':
          description: Agent deleted successfully

        '404':
          $ref: '#/components/responses/NotFound'

        '409':
          description: Cannot delete - agent has active connections
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                error: "conflict"
                message: "Cannot delete agent with active connections"
                details:
                  active_connections: 3

        '500':
          $ref: '#/components/responses/InternalError'
```

#### **POST /agents/{agentId}/messages** - Send message to agent

```yaml
  /agents/{agentId}/messages:
    post:
      summary: Send message to agent
      tags: [agents]
      parameters:
        - name: agentId
          in: path
          required: true
          schema:
            type: string

      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [content, message_type]
              properties:
                content:
                  type: string
                  description: Message content
                message_type:
                  type: string
                  enum: [request, response, broadcast, notification]
                from_agent:
                  type: string
                  description: Sender agent ID (optional)
                metadata:
                  type: object
                  description: Additional metadata

            example:
              content: "Please analyze Q4 budget"
              message_type: "request"
              from_agent: "agent_456def"
              metadata:
                priority: "high"
                deadline: "2026-02-05T00:00:00Z"

      responses:
        '202':
          description: Message accepted for processing
          content:
            application/json:
              schema:
                type: object
                properties:
                  message_id:
                    type: string
                  status:
                    type: string
                  queued_at:
                    type: string
                    format: date-time

              example:
                message_id: "msg_abc123"
                status: "queued"
                queued_at: "2026-02-04T14:30:00Z"

        '400':
          $ref: '#/components/responses/BadRequest'
        '404':
          $ref: '#/components/responses/NotFound'
        '503':
          description: Agent overloaded
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                error: "overloaded"
                message: "Agent queue is full"
                details:
                  current_load: 0.98
                  queue_size: 50
```

---

## 🔷 LEVEL 2: Connection Management API (Среднее)

### 2.1. Endpoints

#### **POST /connections** - Create connection

```yaml
/connections:
  post:
    summary: Create connection between two agents
    tags: [connections]
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [agent_a_id, agent_b_id, parameters]
            properties:
              agent_a_id:
                type: string
              agent_b_id:
                type: string
              parameters:
                type: object
                required: [bandwidth, priority, protocol, timeout]
                properties:
                  bandwidth:
                    type: string
                    enum: [low, standard, high]
                  priority:
                    type: string
                    enum: [low, normal, high, critical]
                  protocol:
                    type: string
                    enum: [one_way, bidirectional, broadcast]
                  timeout:
                    type: integer
                    minimum: 1
                  retry_policy:
                    type: string
                    enum: [none, simple, exponential_backoff]

          example:
            agent_a_id: "agent_123abc"
            agent_b_id: "agent_456def"
            parameters:
              bandwidth: "high"
              priority: "high"
              protocol: "bidirectional"
              timeout: 60
              retry_policy: "exponential_backoff"

    responses:
      '201':
        description: Connection created
        content:
          application/json:
            schema:
              type: object
              properties:
                connection_id:
                  type: string
                message:
                  type: string
                connection:
                  $ref: '#/components/schemas/Connection'

            example:
              connection_id: "conn_agent_123abc<->agent_456def"
              message: "Connection established"
              connection:
                id: "conn_agent_123abc<->agent_456def"
                agent_a_id: "agent_123abc"
                agent_b_id: "agent_456def"
                is_open: true
                start_time: "2026-02-04T14:35:00Z"
                parameters:
                  bandwidth: "high"
                  priority: "high"
                  protocol: "bidirectional"
                  timeout: 60
                metrics:
                  messages_count: 0
                  total_bytes: 0
                  duration_seconds: 0

      '400':
        $ref: '#/components/responses/BadRequest'
      '409':
        description: Connection already exists
      '507':
        description: Insufficient capacity
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Error'
            example:
              error: "insufficient_capacity"
              message: "Switchboard at capacity"
              details:
                capacity: 100
                active_connections: 100
                utilization: 1.0
```

#### **GET /connections** - List connections

```yaml
  get:
    summary: List all connections
    tags: [connections]
    parameters:
      - name: agent_id
        in: query
        description: Filter by agent ID (either end)
        schema:
          type: string
      - name: status
        in: query
        description: Filter by status
        schema:
          type: string
          enum: [open, closed]
      - name: priority
        in: query
        description: Filter by priority
        schema:
          type: string
          enum: [low, normal, high, critical]

    responses:
      '200':
        description: List of connections
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
                    $ref: '#/components/schemas/Connection'
                pagination:
                  $ref: '#/components/schemas/Pagination'
```

#### **DELETE /connections/{connectionId}** - Close connection

```yaml
  /connections/{connectionId}:
    delete:
      summary: Close and remove connection
      tags: [connections]
      parameters:
        - name: connectionId
          in: path
          required: true
          schema:
            type: string

      responses:
        '200':
          description: Connection closed
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                  metrics:
                    type: object
                    properties:
                      duration_seconds:
                        type: number
                      messages_count:
                        type: integer
                      total_bytes:
                        type: integer
                      throughput_bps:
                        type: number

              example:
                message: "Connection closed"
                metrics:
                  duration_seconds: 125.3
                  messages_count: 42
                  total_bytes: 15847
                  throughput_bps: 126.5

        '404':
          $ref: '#/components/responses/NotFound'
```

---

## 🔷 LEVEL 3: Graph Management API (Сложное)

### 3.1. Endpoints

#### **POST /graphs** - Create communication graph

```yaml
/graphs:
  post:
    summary: Create communication graph
    tags: [graphs]
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [nodes, edges]
            properties:
              name:
                type: string
                description: Graph name
              directed:
                type: boolean
                default: true
              nodes:
                type: array
                items:
                  type: object
                  required: [agent_id]
                  properties:
                    agent_id:
                      type: string
              edges:
                type: array
                items:
                  type: object
                  required: [source, target, parameters]
                  properties:
                    source:
                      type: string
                    target:
                      type: string
                    parameters:
                      $ref: '#/components/schemas/ChannelParameters'
                    weight:
                      type: number
                      default: 1.0

          example:
            name: "budget_planning_graph"
            directed: true
            nodes:
              - agent_id: "agent_pm"
              - agent_id: "agent_budget"
              - agent_id: "agent_venue"
            edges:
              - source: "agent_pm"
                target: "agent_budget"
                parameters:
                  bandwidth: "high"
                  priority: "high"
                  protocol: "bidirectional"
                  timeout: 60
                weight: 2.0
              - source: "agent_pm"
                target: "agent_venue"
                parameters:
                  bandwidth: "standard"
                  priority: "normal"
                  protocol: "bidirectional"
                  timeout: 60
                weight: 1.0

    responses:
      '201':
        description: Graph created
        content:
          application/json:
            schema:
              type: object
              properties:
                graph_id:
                  type: string
                message:
                  type: string
                graph:
                  $ref: '#/components/schemas/Graph'
                analysis:
                  type: object
                  properties:
                    is_acyclic:
                      type: boolean
                    critical_path:
                      type: array
                      items:
                        type: string
                    parallel_groups:
                      type: array
                      items:
                        type: array
                        items:
                          type: string
```

#### **POST /graphs/{graphId}/analyze** - Analyze graph

```yaml
  /graphs/{graphId}/analyze:
    post:
      summary: Perform graph analysis
      tags: [graphs]
      parameters:
        - name: graphId
          in: path
          required: true
          schema:
            type: string

      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                analysis_type:
                  type: array
                  items:
                    type: string
                    enum:
                      - topological_sort
                      - critical_path
                      - parallel_groups
                      - cycles
                      - shortest_paths
                      - bottlenecks

      responses:
        '200':
          description: Analysis results
          content:
            application/json:
              schema:
                type: object
                properties:
                  graph_id:
                    type: string
                  analysis:
                    type: object
                  recommendations:
                    type: array
                    items:
                      type: object
                      properties:
                        type:
                          type: string
                        description:
                          type: string
                        impact:
                          type: string
                          enum: [low, medium, high]
```

---

## 📦 Components & Schemas

### Schemas

```yaml
components:
  schemas:
    Agent:
      type: object
      properties:
        id:
          type: string
        role:
          type: string
        status:
          type: string
          enum: [idle, thinking, communicating, error, offline]
        capabilities:
          type: array
          items:
            $ref: '#/components/schemas/Capability'
        avg_response_time:
          type: number
          format: float
        success_rate:
          type: number
          format: float
        current_load:
          type: number
          format: float
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    Capability:
      type: object
      required: [name, description, cost, success_rate]
      properties:
        name:
          type: string
        description:
          type: string
        cost:
          type: number
          format: float
        success_rate:
          type: number
          format: float
          minimum: 0.0
          maximum: 1.0

    Connection:
      type: object
      properties:
        id:
          type: string
        agent_a_id:
          type: string
        agent_b_id:
          type: string
        is_open:
          type: boolean
        start_time:
          type: string
          format: date-time
        end_time:
          type: string
          format: date-time
          nullable: true
        parameters:
          $ref: '#/components/schemas/ChannelParameters'
        metrics:
          type: object
          properties:
            messages_count:
              type: integer
            total_bytes:
              type: integer
            duration_seconds:
              type: number
            throughput_bps:
              type: number

    ChannelParameters:
      type: object
      required: [bandwidth, priority, protocol, timeout]
      properties:
        bandwidth:
          type: string
          enum: [low, standard, high]
        priority:
          type: string
          enum: [low, normal, high, critical]
        protocol:
          type: string
          enum: [one_way, bidirectional, broadcast]
        timeout:
          type: integer
          minimum: 1
        retry_policy:
          type: string
          enum: [none, simple, exponential_backoff]
          default: "simple"

    Graph:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        directed:
          type: boolean
        node_count:
          type: integer
        edge_count:
          type: integer
        created_at:
          type: string
          format: date-time

    Pagination:
      type: object
      properties:
        limit:
          type: integer
        offset:
          type: integer
        total:
          type: integer

    Error:
      type: object
      properties:
        error:
          type: string
        message:
          type: string
        details:
          type: object
          additionalProperties: true

  responses:
    BadRequest:
      description: Bad request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "validation_error"
            message: "Invalid request parameters"
            details:
              field: "capabilities"
              issue: "must be non-empty array"

    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "not_found"
            message: "Agent not found"

    InternalError:
      description: Internal server error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "internal_error"
            message: "An unexpected error occurred"
```

---

**Complexity Level**:
- Level 1 (Agent API): ⭐⭐ - CRUD operations
- Level 2 (Connection API): ⭐⭐⭐ - Resource management
- Level 3 (Graph API): ⭐⭐⭐⭐ - Complex analysis

Продолжить с Level 4-5 (Execution API & WebSocket)?
