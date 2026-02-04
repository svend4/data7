# Technical Specification Part 4: Data Schemas

**Version**: 8.1 (continued)
**Date**: 2026-02-04
**Schema Format**: JSON Schema (Draft 7) + PostgreSQL DDL
**Approach**: From Simple to Complex

---

## 📋 Overview

Полные схемы данных для всех компонентов системы. Движемся **от простого к сложному**:

1. ✅ **Level 1: Primitive Schemas** (Simplest - basic types)
2. ⏳ **Level 2: Entity Schemas** (Medium - complex objects)
3. ⏳ **Level 3: Database Schemas** (Complex - relational structure)
4. ⏳ **Level 4: Message Formats** (Complex - protocol definitions)
5. ⏳ **Level 5: Event Schemas** (Most Complex - event sourcing)

---

## 🔷 LEVEL 1: Primitive Schemas (Простейшие)

### 1.1. Vector3 Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/vector3.json",
  "title": "Vector3",
  "description": "3D coordinate vector",
  "type": "object",
  "required": ["x", "y", "z"],
  "properties": {
    "x": {
      "type": "number",
      "description": "X coordinate"
    },
    "y": {
      "type": "number",
      "description": "Y coordinate"
    },
    "z": {
      "type": "number",
      "description": "Z coordinate"
    }
  },
  "additionalProperties": false,
  "examples": [
    {
      "x": 0.0,
      "y": 1.5,
      "z": -3.2
    },
    {
      "x": 10,
      "y": 0,
      "z": 5
    }
  ]
}
```

### 1.2. Color Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/color.json",
  "title": "Color",
  "description": "RGBA color representation",
  "type": "object",
  "required": ["r", "g", "b"],
  "properties": {
    "r": {
      "type": "integer",
      "minimum": 0,
      "maximum": 255,
      "description": "Red component (0-255)"
    },
    "g": {
      "type": "integer",
      "minimum": 0,
      "maximum": 255,
      "description": "Green component (0-255)"
    },
    "b": {
      "type": "integer",
      "minimum": 0,
      "maximum": 255,
      "description": "Blue component (0-255)"
    },
    "a": {
      "type": "integer",
      "minimum": 0,
      "maximum": 255,
      "default": 255,
      "description": "Alpha/transparency component (0-255)"
    }
  },
  "additionalProperties": false,
  "examples": [
    {
      "r": 255,
      "g": 0,
      "b": 0,
      "a": 255
    },
    {
      "r": 0,
      "g": 128,
      "b": 255,
      "a": 128
    }
  ]
}
```

### 1.3. Timestamp Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/timestamp.json",
  "title": "Timestamp",
  "description": "ISO 8601 timestamp",
  "type": "string",
  "format": "date-time",
  "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[+-]\\d{2}:\\d{2})$",
  "examples": [
    "2026-02-04T14:30:00Z",
    "2026-02-04T14:30:00.123Z",
    "2026-02-04T14:30:00+00:00"
  ]
}
```

### 1.4. Priority Enum Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/priority.json",
  "title": "Priority",
  "description": "Task/connection priority level",
  "type": "string",
  "enum": ["low", "normal", "high", "critical"],
  "default": "normal",
  "examples": ["high", "critical"]
}
```

### 1.5. AgentStatus Enum Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/agent-status.json",
  "title": "AgentStatus",
  "description": "Current status of an agent",
  "type": "string",
  "enum": ["idle", "thinking", "communicating", "error", "offline"],
  "default": "idle",
  "examples": ["thinking", "communicating"]
}
```

### 1.6. MessageType Enum Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/message-type.json",
  "title": "MessageType",
  "description": "Type of message between agents",
  "type": "string",
  "enum": ["request", "response", "broadcast", "notification"],
  "default": "request",
  "examples": ["request", "response"]
}
```

### 1.7. ConnectionProtocol Enum Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/connection-protocol.json",
  "title": "ConnectionProtocol",
  "description": "Communication protocol type",
  "type": "string",
  "enum": ["one_way", "bidirectional", "broadcast"],
  "default": "bidirectional",
  "examples": ["bidirectional", "one_way"]
}
```

**Complexity**: ⭐ (1/5) - Простейшие схемы

---

## 🔷 LEVEL 2: Entity Schemas (Среднее)

### 2.1. AgentCapability Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/agent-capability.json",
  "title": "AgentCapability",
  "description": "A capability that an agent possesses",
  "type": "object",
  "required": ["name", "description", "cost", "success_rate"],
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100,
      "description": "Capability name",
      "examples": ["data_analysis", "budget_planning"]
    },
    "description": {
      "type": "string",
      "minLength": 1,
      "maxLength": 500,
      "description": "Human-readable description",
      "examples": ["Analyze data and generate insights"]
    },
    "cost": {
      "type": "number",
      "minimum": 0,
      "description": "Cost in tokens or time units",
      "examples": [0.5, 1.2, 5.0]
    },
    "success_rate": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Success rate (0.0-1.0)",
      "examples": [0.95, 0.88, 0.99]
    }
  },
  "additionalProperties": false,
  "examples": [
    {
      "name": "statistical_analysis",
      "description": "Perform statistical analysis on datasets",
      "cost": 1.2,
      "success_rate": 0.96
    }
  ]
}
```

### 2.2. ChannelParameters Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/channel-parameters.json",
  "title": "ChannelParameters",
  "description": "Parameters for communication channel",
  "type": "object",
  "required": ["bandwidth", "priority", "protocol", "timeout"],
  "properties": {
    "bandwidth": {
      "type": "string",
      "enum": ["low", "standard", "high"],
      "description": "Communication bandwidth"
    },
    "priority": {
      "$ref": "https://mmo-ai-bridge.com/schemas/priority.json"
    },
    "protocol": {
      "$ref": "https://mmo-ai-bridge.com/schemas/connection-protocol.json"
    },
    "timeout": {
      "type": "integer",
      "minimum": 1,
      "maximum": 3600,
      "description": "Timeout in seconds"
    },
    "retry_policy": {
      "type": "string",
      "enum": ["none", "simple", "exponential_backoff"],
      "default": "simple",
      "description": "Retry policy on failure"
    }
  },
  "additionalProperties": false,
  "examples": [
    {
      "bandwidth": "high",
      "priority": "high",
      "protocol": "bidirectional",
      "timeout": 60,
      "retry_policy": "exponential_backoff"
    }
  ]
}
```

### 2.3. Message Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/message.json",
  "title": "Message",
  "description": "Message between agents",
  "type": "object",
  "required": ["message_id", "from_agent", "to_agent", "message_type", "content", "timestamp"],
  "properties": {
    "message_id": {
      "type": "string",
      "pattern": "^msg_[a-zA-Z0-9]{8,}$",
      "description": "Unique message identifier",
      "examples": ["msg_abc123def456"]
    },
    "from_agent": {
      "type": "string",
      "pattern": "^agent_[a-zA-Z0-9]{8,}$",
      "description": "Sender agent ID",
      "examples": ["agent_123abc"]
    },
    "to_agent": {
      "type": "string",
      "pattern": "^agent_[a-zA-Z0-9]{8,}$",
      "description": "Recipient agent ID",
      "examples": ["agent_456def"]
    },
    "message_type": {
      "$ref": "https://mmo-ai-bridge.com/schemas/message-type.json"
    },
    "content": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100000,
      "description": "Message content"
    },
    "timestamp": {
      "$ref": "https://mmo-ai-bridge.com/schemas/timestamp.json"
    },
    "metadata": {
      "type": "object",
      "description": "Additional metadata",
      "additionalProperties": true
    }
  },
  "additionalProperties": false,
  "examples": [
    {
      "message_id": "msg_abc123",
      "from_agent": "agent_pm",
      "to_agent": "agent_budget",
      "message_type": "request",
      "content": "Please analyze Q4 budget",
      "timestamp": "2026-02-04T14:30:00Z",
      "metadata": {
        "priority": "high",
        "deadline": "2026-02-05T00:00:00Z"
      }
    }
  ]
}
```

### 2.4. AgentMetadata Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/agent-metadata.json",
  "title": "AgentMetadata",
  "description": "Metadata about an agent",
  "type": "object",
  "required": ["agent_id", "role", "capabilities", "avg_response_time", "success_rate", "current_load"],
  "properties": {
    "agent_id": {
      "type": "string",
      "pattern": "^agent_[a-zA-Z0-9]{8,}$",
      "description": "Agent identifier"
    },
    "role": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100,
      "description": "Agent role",
      "examples": ["budget_analyst", "project_manager"]
    },
    "capabilities": {
      "type": "array",
      "items": {
        "$ref": "https://mmo-ai-bridge.com/schemas/agent-capability.json"
      },
      "minItems": 1,
      "description": "List of agent capabilities"
    },
    "avg_response_time": {
      "type": "number",
      "minimum": 0,
      "description": "Average response time in seconds"
    },
    "success_rate": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Success rate (0.0-1.0)"
    },
    "current_load": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Current load (0.0-1.0)"
    }
  },
  "additionalProperties": false,
  "examples": [
    {
      "agent_id": "agent_123abc",
      "role": "budget_analyst",
      "capabilities": [
        {
          "name": "cost_analysis",
          "description": "Analyze costs",
          "cost": 0.5,
          "success_rate": 0.95
        }
      ],
      "avg_response_time": 2.3,
      "success_rate": 0.94,
      "current_load": 0.15
    }
  ]
}
```

**Complexity**: ⭐⭐ (2/5) - Вложенные объекты

---

## 🔷 LEVEL 3: Complex Entity Schemas (Сложное)

### 3.1. Agent Schema (Full)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/agent.json",
  "title": "Agent",
  "description": "Complete agent entity",
  "type": "object",
  "required": ["id", "role", "status", "capabilities"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^agent_[a-zA-Z0-9]{8,}$",
      "description": "Unique agent identifier"
    },
    "role": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100,
      "description": "Agent role"
    },
    "status": {
      "$ref": "https://mmo-ai-bridge.com/schemas/agent-status.json"
    },
    "capabilities": {
      "type": "array",
      "items": {
        "$ref": "https://mmo-ai-bridge.com/schemas/agent-capability.json"
      },
      "minItems": 1
    },
    "llm_backend": {
      "type": "string",
      "enum": ["gpt-4", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet", "custom"],
      "default": "gpt-4"
    },
    "avg_response_time": {
      "type": "number",
      "minimum": 0,
      "description": "Average response time in seconds"
    },
    "success_rate": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Historical success rate"
    },
    "current_load": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Current load (0.0-1.0)"
    },
    "created_at": {
      "$ref": "https://mmo-ai-bridge.com/schemas/timestamp.json"
    },
    "updated_at": {
      "$ref": "https://mmo-ai-bridge.com/schemas/timestamp.json"
    },
    "metadata": {
      "type": "object",
      "description": "Additional metadata",
      "additionalProperties": true
    }
  },
  "additionalProperties": false
}
```

### 3.2. Connection Schema (Full)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/connection.json",
  "title": "Connection",
  "description": "Connection between two agents",
  "type": "object",
  "required": ["id", "agent_a_id", "agent_b_id", "is_open", "parameters"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^conn_",
      "description": "Connection identifier"
    },
    "agent_a_id": {
      "type": "string",
      "pattern": "^agent_"
    },
    "agent_b_id": {
      "type": "string",
      "pattern": "^agent_"
    },
    "is_open": {
      "type": "boolean",
      "description": "Whether connection is currently open"
    },
    "start_time": {
      "$ref": "https://mmo-ai-bridge.com/schemas/timestamp.json"
    },
    "end_time": {
      "oneOf": [
        { "$ref": "https://mmo-ai-bridge.com/schemas/timestamp.json" },
        { "type": "null" }
      ]
    },
    "parameters": {
      "$ref": "https://mmo-ai-bridge.com/schemas/channel-parameters.json"
    },
    "metrics": {
      "type": "object",
      "properties": {
        "messages_count": {
          "type": "integer",
          "minimum": 0
        },
        "total_bytes": {
          "type": "integer",
          "minimum": 0
        },
        "duration_seconds": {
          "type": "number",
          "minimum": 0
        },
        "throughput_bps": {
          "type": "number",
          "minimum": 0
        }
      }
    }
  },
  "additionalProperties": false
}
```

### 3.3. CommunicationGraph Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/communication-graph.json",
  "title": "CommunicationGraph",
  "description": "Graph of agent communications",
  "type": "object",
  "required": ["id", "name", "directed", "nodes", "edges"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^graph_[a-zA-Z0-9]{8,}$"
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "Graph name"
    },
    "directed": {
      "type": "boolean",
      "description": "Whether graph is directed",
      "default": true
    },
    "nodes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["agent_id"],
        "properties": {
          "agent_id": {
            "type": "string",
            "pattern": "^agent_"
          },
          "metadata": {
            "$ref": "https://mmo-ai-bridge.com/schemas/agent-metadata.json"
          },
          "position": {
            "$ref": "https://mmo-ai-bridge.com/schemas/vector3.json",
            "description": "Visual position in 3D space"
          }
        }
      },
      "minItems": 1
    },
    "edges": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["source", "target", "parameters"],
        "properties": {
          "source": {
            "type": "string",
            "pattern": "^agent_",
            "description": "Source agent ID"
          },
          "target": {
            "type": "string",
            "pattern": "^agent_",
            "description": "Target agent ID"
          },
          "parameters": {
            "$ref": "https://mmo-ai-bridge.com/schemas/channel-parameters.json"
          },
          "weight": {
            "type": "number",
            "minimum": 0,
            "default": 1.0,
            "description": "Edge weight for algorithms"
          }
        }
      }
    },
    "created_at": {
      "$ref": "https://mmo-ai-bridge.com/schemas/timestamp.json"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "is_acyclic": {
          "type": "boolean"
        },
        "node_count": {
          "type": "integer",
          "minimum": 0
        },
        "edge_count": {
          "type": "integer",
          "minimum": 0
        },
        "density": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        }
      }
    }
  },
  "additionalProperties": false
}
```

### 3.4. ExecutionPlan Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/execution-plan.json",
  "title": "ExecutionPlan",
  "description": "Plan for executing communication graph",
  "type": "object",
  "required": ["graph_id", "order", "parallel_groups", "estimated_time"],
  "properties": {
    "graph_id": {
      "type": "string",
      "pattern": "^graph_"
    },
    "order": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^agent_"
      },
      "description": "Topological execution order"
    },
    "parallel_groups": {
      "type": "array",
      "items": {
        "type": "array",
        "items": {
          "type": "string",
          "pattern": "^agent_"
        }
      },
      "description": "Groups that can execute in parallel"
    },
    "estimated_time": {
      "type": "number",
      "minimum": 0,
      "description": "Estimated execution time in seconds"
    },
    "critical_path": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^agent_"
      },
      "description": "Critical path through graph"
    },
    "created_at": {
      "$ref": "https://mmo-ai-bridge.com/schemas/timestamp.json"
    }
  },
  "additionalProperties": false
}
```

### 3.5. ExecutionResult Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/execution-result.json",
  "title": "ExecutionResult",
  "description": "Result of graph execution",
  "type": "object",
  "required": ["execution_id", "graph_id", "status", "total_time", "success_rate"],
  "properties": {
    "execution_id": {
      "type": "string",
      "pattern": "^exec_[a-zA-Z0-9]{8,}$"
    },
    "graph_id": {
      "type": "string",
      "pattern": "^graph_"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "running", "completed", "failed", "partial"],
      "description": "Execution status"
    },
    "total_time": {
      "type": "number",
      "minimum": 0,
      "description": "Total execution time in seconds"
    },
    "success_rate": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Success rate (0.0-1.0)"
    },
    "message_count": {
      "type": "integer",
      "minimum": 0,
      "description": "Total messages exchanged"
    },
    "error_count": {
      "type": "integer",
      "minimum": 0,
      "description": "Number of errors encountered"
    },
    "results": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "agent_id": {
            "type": "string"
          },
          "status": {
            "type": "string",
            "enum": ["success", "failure", "timeout"]
          },
          "output": {
            "type": "string"
          },
          "error": {
            "type": "string"
          },
          "processing_time": {
            "type": "number"
          }
        }
      }
    },
    "started_at": {
      "$ref": "https://mmo-ai-bridge.com/schemas/timestamp.json"
    },
    "completed_at": {
      "$ref": "https://mmo-ai-bridge.com/schemas/timestamp.json"
    }
  },
  "additionalProperties": false
}
```

**Complexity**: ⭐⭐⭐ (3/5) - Сложные вложенные структуры

---

## 🔷 LEVEL 4: Database Schemas (PostgreSQL)

### 4.1. Database Schema DDL

```sql
-- ============================================
-- MMO AI Bridge - PostgreSQL Database Schema
-- Version: 1.0
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- TABLE: agents
-- ============================================
CREATE TABLE agents (
    id VARCHAR(255) PRIMARY KEY,
    role VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'idle',
    llm_backend VARCHAR(50) NOT NULL DEFAULT 'gpt-4',
    avg_response_time DECIMAL(10, 3) DEFAULT 0.0,
    success_rate DECIMAL(5, 4) DEFAULT 1.0,
    current_load DECIMAL(5, 4) DEFAULT 0.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT agents_status_check CHECK (status IN ('idle', 'thinking', 'communicating', 'error', 'offline')),
    CONSTRAINT agents_success_rate_check CHECK (success_rate >= 0.0 AND success_rate <= 1.0),
    CONSTRAINT agents_load_check CHECK (current_load >= 0.0 AND current_load <= 1.0)
);

-- Indexes for agents
CREATE INDEX idx_agents_role ON agents(role);
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_load ON agents(current_load);
CREATE INDEX idx_agents_created ON agents(created_at);

-- ============================================
-- TABLE: agent_capabilities
-- ============================================
CREATE TABLE agent_capabilities (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    success_rate DECIMAL(5, 4) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT capabilities_cost_check CHECK (cost >= 0),
    CONSTRAINT capabilities_rate_check CHECK (success_rate >= 0.0 AND success_rate <= 1.0),
    UNIQUE(agent_id, name)
);

-- Indexes for capabilities
CREATE INDEX idx_capabilities_agent ON agent_capabilities(agent_id);
CREATE INDEX idx_capabilities_name ON agent_capabilities(name);

-- ============================================
-- TABLE: connections
-- ============================================
CREATE TABLE connections (
    id VARCHAR(255) PRIMARY KEY,
    agent_a_id VARCHAR(255) NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    agent_b_id VARCHAR(255) NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    is_open BOOLEAN NOT NULL DEFAULT true,
    bandwidth VARCHAR(20) NOT NULL DEFAULT 'standard',
    priority VARCHAR(20) NOT NULL DEFAULT 'normal',
    protocol VARCHAR(20) NOT NULL DEFAULT 'bidirectional',
    timeout INTEGER NOT NULL DEFAULT 60,
    retry_policy VARCHAR(30) NOT NULL DEFAULT 'simple',
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    messages_count INTEGER DEFAULT 0,
    total_bytes BIGINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT connections_bandwidth_check CHECK (bandwidth IN ('low', 'standard', 'high')),
    CONSTRAINT connections_priority_check CHECK (priority IN ('low', 'normal', 'high', 'critical')),
    CONSTRAINT connections_protocol_check CHECK (protocol IN ('one_way', 'bidirectional', 'broadcast')),
    CONSTRAINT connections_timeout_check CHECK (timeout > 0),
    CONSTRAINT connections_agents_different CHECK (agent_a_id != agent_b_id)
);

-- Indexes for connections
CREATE INDEX idx_connections_agent_a ON connections(agent_a_id);
CREATE INDEX idx_connections_agent_b ON connections(agent_b_id);
CREATE INDEX idx_connections_is_open ON connections(is_open);
CREATE INDEX idx_connections_priority ON connections(priority);

-- ============================================
-- TABLE: messages
-- ============================================
CREATE TABLE messages (
    id VARCHAR(255) PRIMARY KEY,
    from_agent VARCHAR(255) NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    to_agent VARCHAR(255) NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    connection_id VARCHAR(255) REFERENCES connections(id) ON DELETE SET NULL,
    message_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT messages_type_check CHECK (message_type IN ('request', 'response', 'broadcast', 'notification'))
);

-- Indexes for messages
CREATE INDEX idx_messages_from ON messages(from_agent);
CREATE INDEX idx_messages_to ON messages(to_agent);
CREATE INDEX idx_messages_connection ON messages(connection_id);
CREATE INDEX idx_messages_type ON messages(message_type);
CREATE INDEX idx_messages_created ON messages(created_at);

-- ============================================
-- TABLE: communication_graphs
-- ============================================
CREATE TABLE communication_graphs (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    directed BOOLEAN NOT NULL DEFAULT true,
    node_count INTEGER DEFAULT 0,
    edge_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for graphs
CREATE INDEX idx_graphs_name ON communication_graphs(name);
CREATE INDEX idx_graphs_created ON communication_graphs(created_at);

-- ============================================
-- TABLE: graph_nodes
-- ============================================
CREATE TABLE graph_nodes (
    id SERIAL PRIMARY KEY,
    graph_id VARCHAR(255) NOT NULL REFERENCES communication_graphs(id) ON DELETE CASCADE,
    agent_id VARCHAR(255) NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    position_x DECIMAL(10, 3),
    position_y DECIMAL(10, 3),
    position_z DECIMAL(10, 3),
    metadata JSONB DEFAULT '{}',

    UNIQUE(graph_id, agent_id)
);

-- Indexes for graph nodes
CREATE INDEX idx_graph_nodes_graph ON graph_nodes(graph_id);
CREATE INDEX idx_graph_nodes_agent ON graph_nodes(agent_id);

-- ============================================
-- TABLE: graph_edges
-- ============================================
CREATE TABLE graph_edges (
    id SERIAL PRIMARY KEY,
    graph_id VARCHAR(255) NOT NULL REFERENCES communication_graphs(id) ON DELETE CASCADE,
    source_agent VARCHAR(255) NOT NULL,
    target_agent VARCHAR(255) NOT NULL,
    bandwidth VARCHAR(20) NOT NULL DEFAULT 'standard',
    priority VARCHAR(20) NOT NULL DEFAULT 'normal',
    protocol VARCHAR(20) NOT NULL DEFAULT 'bidirectional',
    timeout INTEGER NOT NULL DEFAULT 60,
    weight DECIMAL(10, 3) DEFAULT 1.0,

    CONSTRAINT graph_edges_bandwidth_check CHECK (bandwidth IN ('low', 'standard', 'high')),
    CONSTRAINT graph_edges_priority_check CHECK (priority IN ('low', 'normal', 'high', 'critical')),
    CONSTRAINT graph_edges_protocol_check CHECK (protocol IN ('one_way', 'bidirectional', 'broadcast')),
    CONSTRAINT graph_edges_weight_check CHECK (weight >= 0)
);

-- Indexes for graph edges
CREATE INDEX idx_graph_edges_graph ON graph_edges(graph_id);
CREATE INDEX idx_graph_edges_source ON graph_edges(source_agent);
CREATE INDEX idx_graph_edges_target ON graph_edges(target_agent);

-- ============================================
-- TABLE: executions
-- ============================================
CREATE TABLE executions (
    id VARCHAR(255) PRIMARY KEY,
    graph_id VARCHAR(255) NOT NULL REFERENCES communication_graphs(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    total_time DECIMAL(10, 3),
    success_rate DECIMAL(5, 4),
    message_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    results JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT executions_status_check CHECK (status IN ('pending', 'running', 'completed', 'failed', 'partial')),
    CONSTRAINT executions_success_rate_check CHECK (success_rate IS NULL OR (success_rate >= 0.0 AND success_rate <= 1.0))
);

-- Indexes for executions
CREATE INDEX idx_executions_graph ON executions(graph_id);
CREATE INDEX idx_executions_status ON executions(status);
CREATE INDEX idx_executions_created ON executions(created_at);

-- ============================================
-- TRIGGERS
-- ============================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_graphs_updated_at BEFORE UPDATE ON communication_graphs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS
-- ============================================

-- View: agent_statistics
CREATE VIEW agent_statistics AS
SELECT
    a.id,
    a.role,
    a.status,
    a.current_load,
    a.success_rate,
    a.avg_response_time,
    COUNT(DISTINCT c.id) as active_connections,
    COUNT(DISTINCT m.id) as messages_sent,
    a.created_at
FROM agents a
LEFT JOIN connections c ON (c.agent_a_id = a.id OR c.agent_b_id = a.id) AND c.is_open = true
LEFT JOIN messages m ON m.from_agent = a.id
GROUP BY a.id;

-- View: graph_statistics
CREATE VIEW graph_statistics AS
SELECT
    g.id,
    g.name,
    g.directed,
    COUNT(DISTINCT n.agent_id) as node_count,
    COUNT(DISTINCT e.id) as edge_count,
    COUNT(DISTINCT ex.id) as execution_count,
    AVG(ex.success_rate) as avg_success_rate,
    AVG(ex.total_time) as avg_execution_time,
    g.created_at
FROM communication_graphs g
LEFT JOIN graph_nodes n ON n.graph_id = g.id
LEFT JOIN graph_edges e ON e.graph_id = g.id
LEFT JOIN executions ex ON ex.graph_id = g.id
GROUP BY g.id;

-- ============================================
-- SAMPLE QUERIES
-- ============================================

-- Get available agents
-- SELECT * FROM agents WHERE status = 'idle' AND current_load < 0.8;

-- Get active connections for agent
-- SELECT * FROM connections WHERE (agent_a_id = 'agent_123' OR agent_b_id = 'agent_123') AND is_open = true;

-- Get agent with capabilities
-- SELECT a.*, json_agg(c.*) as capabilities
-- FROM agents a
-- LEFT JOIN agent_capabilities c ON c.agent_id = a.id
-- WHERE a.id = 'agent_123'
-- GROUP BY a.id;

-- Get graph with nodes and edges
-- SELECT g.*,
--        json_agg(DISTINCT n.*) as nodes,
--        json_agg(DISTINCT e.*) as edges
-- FROM communication_graphs g
-- LEFT JOIN graph_nodes n ON n.graph_id = g.id
-- LEFT JOIN graph_edges e ON e.graph_id = g.id
-- WHERE g.id = 'graph_123'
-- GROUP BY g.id;
```

**Complexity**: ⭐⭐⭐⭐ (4/5) - Relational structure + constraints

---

Создана первая часть Data Schemas (Levels 1-4). Продолжить с Level 5 (Event Schemas & Message Formats)?