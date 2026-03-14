# Technical Specification Part 5: Event Schemas & Protocols

**Version**: 8.1 (continued)
**Date**: 2026-02-04
**Format**: Event Sourcing + WebSocket + Serialization
**Continuation from**: TECHNICAL_SPEC_PART4_SCHEMAS.md

---

## 🔷 LEVEL 5: Event Schemas (Наиболее Сложное)

### 5.1. Event Sourcing Pattern

Система использует Event Sourcing для аудита и replay capability.

#### Base Event Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/event-base.json",
  "title": "BaseEvent",
  "description": "Base schema for all events in the system",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "version"],
  "properties": {
    "event_id": {
      "type": "string",
      "pattern": "^evt_[a-zA-Z0-9]{16,}$",
      "description": "Unique event identifier"
    },
    "event_type": {
      "type": "string",
      "description": "Type of event"
    },
    "timestamp": {
      "$ref": "https://mmo-ai-bridge.com/schemas/timestamp.json"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Event schema version (semver)",
      "examples": ["1.0.0", "2.1.3"]
    },
    "correlation_id": {
      "type": "string",
      "description": "ID to correlate related events"
    },
    "causation_id": {
      "type": "string",
      "description": "ID of event that caused this event"
    },
    "aggregate_id": {
      "type": "string",
      "description": "ID of aggregate (agent, connection, graph) this event relates to"
    },
    "aggregate_type": {
      "type": "string",
      "enum": ["agent", "connection", "graph", "execution", "system"],
      "description": "Type of aggregate"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "user_id": {
          "type": "string"
        },
        "source": {
          "type": "string"
        },
        "ip_address": {
          "type": "string"
        }
      }
    }
  }
}
```

### 5.2. Agent Events

#### AgentRegistered Event

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/events/agent-registered.json",
  "title": "AgentRegistered",
  "allOf": [
    { "$ref": "https://mmo-ai-bridge.com/schemas/event-base.json" },
    {
      "type": "object",
      "required": ["data"],
      "properties": {
        "event_type": {
          "const": "agent.registered"
        },
        "data": {
          "type": "object",
          "required": ["agent_id", "role", "capabilities"],
          "properties": {
            "agent_id": {
              "type": "string",
              "pattern": "^agent_"
            },
            "role": {
              "type": "string"
            },
            "capabilities": {
              "type": "array",
              "items": {
                "$ref": "https://mmo-ai-bridge.com/schemas/agent-capability.json"
              }
            },
            "llm_backend": {
              "type": "string"
            }
          }
        }
      }
    }
  ],
  "examples": [
    {
      "event_id": "evt_abc123def456ghi7",
      "event_type": "agent.registered",
      "timestamp": "2026-02-04T14:30:00Z",
      "version": "1.0.0",
      "aggregate_id": "agent_123abc",
      "aggregate_type": "agent",
      "data": {
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
        "llm_backend": "gpt-4"
      }
    }
  ]
}
```

#### AgentStatusChanged Event

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/events/agent-status-changed.json",
  "title": "AgentStatusChanged",
  "allOf": [
    { "$ref": "https://mmo-ai-bridge.com/schemas/event-base.json" },
    {
      "type": "object",
      "required": ["data"],
      "properties": {
        "event_type": {
          "const": "agent.status_changed"
        },
        "data": {
          "type": "object",
          "required": ["agent_id", "old_status", "new_status"],
          "properties": {
            "agent_id": {
              "type": "string",
              "pattern": "^agent_"
            },
            "old_status": {
              "$ref": "https://mmo-ai-bridge.com/schemas/agent-status.json"
            },
            "new_status": {
              "$ref": "https://mmo-ai-bridge.com/schemas/agent-status.json"
            },
            "reason": {
              "type": "string",
              "description": "Reason for status change"
            }
          }
        }
      }
    }
  ]
}
```

#### AgentMessageReceived Event

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/events/agent-message-received.json",
  "title": "AgentMessageReceived",
  "allOf": [
    { "$ref": "https://mmo-ai-bridge.com/schemas/event-base.json" },
    {
      "type": "object",
      "required": ["data"],
      "properties": {
        "event_type": {
          "const": "agent.message_received"
        },
        "data": {
          "type": "object",
          "required": ["agent_id", "message"],
          "properties": {
            "agent_id": {
              "type": "string",
              "pattern": "^agent_"
            },
            "message": {
              "$ref": "https://mmo-ai-bridge.com/schemas/message.json"
            },
            "queue_position": {
              "type": "integer",
              "minimum": 0
            }
          }
        }
      }
    }
  ]
}
```

### 5.3. Connection Events

#### ConnectionEstablished Event

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/events/connection-established.json",
  "title": "ConnectionEstablished",
  "allOf": [
    { "$ref": "https://mmo-ai-bridge.com/schemas/event-base.json" },
    {
      "type": "object",
      "required": ["data"],
      "properties": {
        "event_type": {
          "const": "connection.established"
        },
        "data": {
          "type": "object",
          "required": ["connection_id", "agent_a_id", "agent_b_id", "parameters"],
          "properties": {
            "connection_id": {
              "type": "string"
            },
            "agent_a_id": {
              "type": "string",
              "pattern": "^agent_"
            },
            "agent_b_id": {
              "type": "string",
              "pattern": "^agent_"
            },
            "parameters": {
              "$ref": "https://mmo-ai-bridge.com/schemas/channel-parameters.json"
            }
          }
        }
      }
    }
  ]
}
```

#### ConnectionClosed Event

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/events/connection-closed.json",
  "title": "ConnectionClosed",
  "allOf": [
    { "$ref": "https://mmo-ai-bridge.com/schemas/event-base.json" },
    {
      "type": "object",
      "required": ["data"],
      "properties": {
        "event_type": {
          "const": "connection.closed"
        },
        "data": {
          "type": "object",
          "required": ["connection_id", "duration_seconds", "metrics"],
          "properties": {
            "connection_id": {
              "type": "string"
            },
            "duration_seconds": {
              "type": "number",
              "minimum": 0
            },
            "metrics": {
              "type": "object",
              "properties": {
                "messages_count": {
                  "type": "integer"
                },
                "total_bytes": {
                  "type": "integer"
                },
                "throughput_bps": {
                  "type": "number"
                }
              }
            },
            "reason": {
              "type": "string",
              "enum": ["normal", "timeout", "error", "forced"]
            }
          }
        }
      }
    }
  ]
}
```

### 5.4. Execution Events

#### ExecutionStarted Event

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/events/execution-started.json",
  "title": "ExecutionStarted",
  "allOf": [
    { "$ref": "https://mmo-ai-bridge.com/schemas/event-base.json" },
    {
      "type": "object",
      "required": ["data"],
      "properties": {
        "event_type": {
          "const": "execution.started"
        },
        "data": {
          "type": "object",
          "required": ["execution_id", "graph_id", "plan"],
          "properties": {
            "execution_id": {
              "type": "string",
              "pattern": "^exec_"
            },
            "graph_id": {
              "type": "string",
              "pattern": "^graph_"
            },
            "plan": {
              "$ref": "https://mmo-ai-bridge.com/schemas/execution-plan.json"
            }
          }
        }
      }
    }
  ]
}
```

#### ExecutionCompleted Event

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/events/execution-completed.json",
  "title": "ExecutionCompleted",
  "allOf": [
    { "$ref": "https://mmo-ai-bridge.com/schemas/event-base.json" },
    {
      "type": "object",
      "required": ["data"],
      "properties": {
        "event_type": {
          "const": "execution.completed"
        },
        "data": {
          "type": "object",
          "required": ["execution_id", "result"],
          "properties": {
            "execution_id": {
              "type": "string",
              "pattern": "^exec_"
            },
            "result": {
              "$ref": "https://mmo-ai-bridge.com/schemas/execution-result.json"
            }
          }
        }
      }
    }
  ]
}
```

### 5.5. System Events

#### SystemHealthCheck Event

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/events/system-health-check.json",
  "title": "SystemHealthCheck",
  "allOf": [
    { "$ref": "https://mmo-ai-bridge.com/schemas/event-base.json" },
    {
      "type": "object",
      "required": ["data"],
      "properties": {
        "event_type": {
          "const": "system.health_check"
        },
        "data": {
          "type": "object",
          "required": ["status", "metrics"],
          "properties": {
            "status": {
              "type": "string",
              "enum": ["healthy", "degraded", "unhealthy"]
            },
            "metrics": {
              "type": "object",
              "properties": {
                "total_agents": {
                  "type": "integer"
                },
                "available_agents": {
                  "type": "integer"
                },
                "active_connections": {
                  "type": "integer"
                },
                "switchboard_utilization": {
                  "type": "number",
                  "minimum": 0.0,
                  "maximum": 1.0
                },
                "avg_response_time": {
                  "type": "number"
                },
                "error_rate": {
                  "type": "number"
                }
              }
            }
          }
        }
      }
    }
  ]
}
```

---

## 🔷 LEVEL 6: WebSocket Protocol

### 6.1. WebSocket Message Format

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://mmo-ai-bridge.com/schemas/websocket-message.json",
  "title": "WebSocketMessage",
  "description": "Message format for WebSocket communication",
  "type": "object",
  "required": ["type", "payload"],
  "properties": {
    "type": {
      "type": "string",
      "enum": [
        "subscribe",
        "unsubscribe",
        "event",
        "command",
        "query",
        "response",
        "error",
        "ping",
        "pong"
      ],
      "description": "Message type"
    },
    "id": {
      "type": "string",
      "description": "Message ID for request/response correlation"
    },
    "payload": {
      "type": "object",
      "description": "Message payload (structure depends on type)"
    },
    "timestamp": {
      "$ref": "https://mmo-ai-bridge.com/schemas/timestamp.json"
    }
  },
  "additionalProperties": false
}
```

### 6.2. WebSocket Subscription

```json
{
  "title": "WebSocket Subscribe Message",
  "type": "object",
  "required": ["type", "payload"],
  "properties": {
    "type": {
      "const": "subscribe"
    },
    "id": {
      "type": "string"
    },
    "payload": {
      "type": "object",
      "required": ["channel"],
      "properties": {
        "channel": {
          "type": "string",
          "enum": [
            "agents",
            "agents:{agent_id}",
            "connections",
            "connections:{connection_id}",
            "graphs",
            "graphs:{graph_id}",
            "executions",
            "executions:{execution_id}",
            "system"
          ]
        },
        "filters": {
          "type": "object",
          "additionalProperties": true
        }
      }
    }
  },
  "examples": [
    {
      "type": "subscribe",
      "id": "sub_123",
      "payload": {
        "channel": "agents",
        "filters": {
          "status": "thinking"
        }
      }
    },
    {
      "type": "subscribe",
      "id": "sub_456",
      "payload": {
        "channel": "agents:agent_123abc"
      }
    }
  ]
}
```

### 6.3. WebSocket Event Notification

```json
{
  "title": "WebSocket Event Message",
  "type": "object",
  "required": ["type", "payload"],
  "properties": {
    "type": {
      "const": "event"
    },
    "payload": {
      "type": "object",
      "required": ["channel", "event"],
      "properties": {
        "channel": {
          "type": "string"
        },
        "event": {
          "$ref": "https://mmo-ai-bridge.com/schemas/event-base.json"
        }
      }
    }
  },
  "examples": [
    {
      "type": "event",
      "payload": {
        "channel": "agents:agent_123abc",
        "event": {
          "event_id": "evt_abc123",
          "event_type": "agent.status_changed",
          "timestamp": "2026-02-04T14:30:00Z",
          "version": "1.0.0",
          "aggregate_id": "agent_123abc",
          "aggregate_type": "agent",
          "data": {
            "agent_id": "agent_123abc",
            "old_status": "idle",
            "new_status": "thinking"
          }
        }
      }
    }
  ]
}
```

### 6.4. WebSocket Command

```json
{
  "title": "WebSocket Command Message",
  "type": "object",
  "required": ["type", "id", "payload"],
  "properties": {
    "type": {
      "const": "command"
    },
    "id": {
      "type": "string",
      "description": "Command ID for response correlation"
    },
    "payload": {
      "type": "object",
      "required": ["action", "params"],
      "properties": {
        "action": {
          "type": "string",
          "enum": [
            "register_agent",
            "unregister_agent",
            "send_message",
            "create_connection",
            "close_connection",
            "execute_graph"
          ]
        },
        "params": {
          "type": "object",
          "description": "Action-specific parameters"
        }
      }
    }
  },
  "examples": [
    {
      "type": "command",
      "id": "cmd_123",
      "payload": {
        "action": "send_message",
        "params": {
          "to_agent": "agent_123abc",
          "content": "Process this request",
          "message_type": "request"
        }
      }
    }
  ]
}
```

---

## 🔷 LEVEL 7: Serialization Formats

### 7.1. Binary Protocol (Protocol Buffers)

```protobuf
// agent.proto
syntax = "proto3";

package mmo_ai_bridge;

message Vector3 {
  float x = 1;
  float y = 2;
  float z = 3;
}

message Color {
  int32 r = 1;  // 0-255
  int32 g = 2;  // 0-255
  int32 b = 3;  // 0-255
  int32 a = 4;  // 0-255, default 255
}

message AgentCapability {
  string name = 1;
  string description = 2;
  float cost = 3;
  float success_rate = 4;
}

enum AgentStatus {
  IDLE = 0;
  THINKING = 1;
  COMMUNICATING = 2;
  ERROR = 3;
  OFFLINE = 4;
}

message Agent {
  string id = 1;
  string role = 2;
  AgentStatus status = 3;
  repeated AgentCapability capabilities = 4;
  string llm_backend = 5;
  float avg_response_time = 6;
  float success_rate = 7;
  float current_load = 8;
  int64 created_at = 9;  // Unix timestamp
  int64 updated_at = 10;
  map<string, string> metadata = 11;
}

enum MessageType {
  REQUEST = 0;
  RESPONSE = 1;
  BROADCAST = 2;
  NOTIFICATION = 3;
}

message Message {
  string message_id = 1;
  string from_agent = 2;
  string to_agent = 3;
  MessageType message_type = 4;
  string content = 5;
  int64 timestamp = 6;
  map<string, string> metadata = 7;
}

enum Priority {
  LOW = 0;
  NORMAL = 1;
  HIGH = 2;
  CRITICAL = 3;
}

enum ConnectionProtocol {
  ONE_WAY = 0;
  BIDIRECTIONAL = 1;
  BROADCAST = 2;
}

message ChannelParameters {
  string bandwidth = 1;  // "low", "standard", "high"
  Priority priority = 2;
  ConnectionProtocol protocol = 3;
  int32 timeout = 4;
  string retry_policy = 5;
}

message Connection {
  string id = 1;
  string agent_a_id = 2;
  string agent_b_id = 3;
  bool is_open = 4;
  ChannelParameters parameters = 5;
  int64 start_time = 6;
  int64 end_time = 7;
  int32 messages_count = 8;
  int64 total_bytes = 9;
}

message GraphNode {
  string agent_id = 1;
  Vector3 position = 2;
}

message GraphEdge {
  string source = 1;
  string target = 2;
  ChannelParameters parameters = 3;
  float weight = 4;
}

message CommunicationGraph {
  string id = 1;
  string name = 2;
  bool directed = 3;
  repeated GraphNode nodes = 4;
  repeated GraphEdge edges = 5;
  int64 created_at = 6;
}

// Event base
message BaseEvent {
  string event_id = 1;
  string event_type = 2;
  int64 timestamp = 3;
  string version = 4;
  string correlation_id = 5;
  string causation_id = 6;
  string aggregate_id = 7;
  string aggregate_type = 8;
  bytes data = 9;  // Serialized event-specific data
}
```

### 7.2. MessagePack Format

```python
"""
MessagePack serialization example
Faster and more compact than JSON
"""

import msgpack
from typing import Dict, Any

def serialize_agent(agent: Dict[str, Any]) -> bytes:
    """Serialize agent to MessagePack format"""
    return msgpack.packb(agent, use_bin_type=True)

def deserialize_agent(data: bytes) -> Dict[str, Any]:
    """Deserialize agent from MessagePack format"""
    return msgpack.unpackb(data, raw=False)

# Example
agent = {
    "id": "agent_123abc",
    "role": "budget_analyst",
    "status": "idle",
    "capabilities": [
        {
            "name": "cost_analysis",
            "description": "Analyze costs",
            "cost": 0.5,
            "success_rate": 0.95
        }
    ],
    "current_load": 0.15
}

# Serialize
packed = serialize_agent(agent)
print(f"MessagePack size: {len(packed)} bytes")

# Deserialize
unpacked = deserialize_agent(packed)
assert unpacked == agent

# Compare with JSON
import json
json_str = json.dumps(agent)
print(f"JSON size: {len(json_str.encode())} bytes")
print(f"Space saving: {(1 - len(packed) / len(json_str.encode())) * 100:.1f}%")
```

### 7.3. Compression

```python
"""
Compression for large payloads
"""

import gzip
import zlib
import brotli
from typing import bytes

def compress_gzip(data: bytes, level: int = 6) -> bytes:
    """Compress using gzip (widely supported)"""
    return gzip.compress(data, compresslevel=level)

def compress_brotli(data: bytes, level: int = 11) -> bytes:
    """Compress using Brotli (better compression, slower)"""
    return brotli.compress(data, quality=level)

def compress_zlib(data: bytes, level: int = 6) -> bytes:
    """Compress using zlib (fast)"""
    return zlib.compress(data, level=level)

# Example: Large graph serialization
large_graph = {
    "id": "graph_large",
    "nodes": [{"agent_id": f"agent_{i}"} for i in range(1000)],
    "edges": [
        {"source": f"agent_{i}", "target": f"agent_{i+1}"}
        for i in range(999)
    ]
}

# Serialize to JSON
import json
json_data = json.dumps(large_graph).encode()
print(f"Original size: {len(json_data)} bytes")

# Compress
gzip_data = compress_gzip(json_data)
brotli_data = compress_brotli(json_data)
zlib_data = compress_zlib(json_data)

print(f"Gzip size: {len(gzip_data)} bytes ({len(gzip_data)/len(json_data)*100:.1f}%)")
print(f"Brotli size: {len(brotli_data)} bytes ({len(brotli_data)/len(json_data)*100:.1f}%)")
print(f"Zlib size: {len(zlib_data)} bytes ({len(zlib_data)/len(json_data)*100:.1f}%)")
```

---

## 📋 Summary

### Schemas Created

**Level 1 (Primitives)**: 7 schemas
- Vector3, Color, Timestamp, Priority, AgentStatus, MessageType, ConnectionProtocol

**Level 2 (Entities)**: 4 schemas
- AgentCapability, ChannelParameters, Message, AgentMetadata

**Level 3 (Complex)**: 5 schemas
- Agent, Connection, CommunicationGraph, ExecutionPlan, ExecutionResult

**Level 4 (Database)**: 1 complete DDL
- PostgreSQL schema with 9 tables, indexes, triggers, views

**Level 5 (Events)**: 8 event schemas
- AgentRegistered, AgentStatusChanged, AgentMessageReceived
- ConnectionEstablished, ConnectionClosed
- ExecutionStarted, ExecutionCompleted
- SystemHealthCheck

**Level 6 (WebSocket)**: 4 message types
- Subscribe, Event, Command, Response

**Level 7 (Serialization)**: 3 formats
- Protocol Buffers (binary)
- MessagePack (compact)
- Compression (gzip, brotli, zlib)

**Total**: 32 schemas + 1 database + 3 serialization formats

**Complexity progression**: ⭐ → ⭐⭐⭐⭐⭐

---

**Status**: Data Schemas Complete ✅
**Next**: Visualization Mockups
