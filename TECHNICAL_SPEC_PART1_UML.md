# Technical Specification Part 1: UML Diagrams & Core Architecture

**Version**: 8.1
**Date**: 2026-02-04
**Status**: Development Stage - Conceptual Design Extension
**Approach**: From Simple to Complex, Beginning to End

---

## 📋 Overview

Этот документ содержит детальные UML диаграммы и архитектурные спецификации для реализации проекта. Движемся **от простого к сложному**:

1. ✅ **Level 1: Basic Data Structures** (Simplest)
2. ⏳ **Level 2: Core Classes**
3. ⏳ **Level 3: Component Interactions**
4. ⏳ **Level 4: System Architecture**
5. ⏳ **Level 5: Integration Patterns** (Most Complex)

---

## 🔷 LEVEL 1: Basic Data Structures (Самое Простое)

### 1.1. Базовые Value Objects

Начинаем с самых простых структур данных - value objects без логики.

```python
"""
Basic Value Objects - Immutable data containers
No business logic, just data + validation
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum


# === ENUMS (Simplest) ===

class AgentStatus(Enum):
    """Статус агента"""
    IDLE = "idle"
    THINKING = "thinking"
    COMMUNICATING = "communicating"
    ERROR = "error"
    OFFLINE = "offline"


class Priority(Enum):
    """Приоритет задачи/соединения"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class MessageType(Enum):
    """Тип сообщения между агентами"""
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    NOTIFICATION = "notification"


class ConnectionProtocol(Enum):
    """Протокол соединения"""
    ONE_WAY = "one_way"
    BIDIRECTIONAL = "bidirectional"
    BROADCAST = "broadcast"


# === SIMPLE VALUE OBJECTS ===

@dataclass(frozen=True)
class Vector3:
    """3D координаты (immutable)"""
    x: float
    y: float
    z: float

    def __post_init__(self):
        # Валидация
        if not all(isinstance(v, (int, float)) for v in [self.x, self.y, self.z]):
            raise ValueError("Coordinates must be numeric")


@dataclass(frozen=True)
class Color:
    """RGB цвет (immutable)"""
    r: int  # 0-255
    g: int  # 0-255
    b: int  # 0-255
    a: int = 255  # alpha, 0-255

    def __post_init__(self):
        # Валидация
        for component in [self.r, self.g, self.b, self.a]:
            if not 0 <= component <= 255:
                raise ValueError(f"Color component must be 0-255, got {component}")

    @classmethod
    def from_hex(cls, hex_string: str) -> 'Color':
        """Create from hex string: '#FF0000' -> Color(255, 0, 0)"""
        hex_string = hex_string.lstrip('#')
        return cls(
            r=int(hex_string[0:2], 16),
            g=int(hex_string[2:4], 16),
            b=int(hex_string[4:6], 16)
        )


@dataclass(frozen=True)
class AgentCapability:
    """Capability агента (что он умеет делать)"""
    name: str
    description: str
    cost: float  # стоимость в токенах/время
    success_rate: float  # 0.0-1.0

    def __post_init__(self):
        if not 0.0 <= self.success_rate <= 1.0:
            raise ValueError("Success rate must be between 0.0 and 1.0")


@dataclass(frozen=True)
class Timestamp:
    """Временная метка"""
    value: datetime

    @classmethod
    def now(cls) -> 'Timestamp':
        return cls(datetime.now())

    def __str__(self) -> str:
        return self.value.isoformat()


# === SLIGHTLY MORE COMPLEX VALUE OBJECTS ===

@dataclass(frozen=True)
class AgentMetadata:
    """Метаданные агента"""
    agent_id: str
    role: str
    capabilities: tuple[AgentCapability, ...]  # immutable
    avg_response_time: float  # seconds
    success_rate: float  # 0.0-1.0
    current_load: float  # 0.0-1.0 (0% to 100%)

    def __post_init__(self):
        if not self.agent_id:
            raise ValueError("Agent ID cannot be empty")
        if not 0.0 <= self.success_rate <= 1.0:
            raise ValueError("Success rate must be 0.0-1.0")
        if not 0.0 <= self.current_load <= 1.0:
            raise ValueError("Current load must be 0.0-1.0")


@dataclass(frozen=True)
class ChannelParameters:
    """Параметры канала связи"""
    bandwidth: str  # "low", "standard", "high"
    priority: Priority
    protocol: ConnectionProtocol
    timeout: int  # seconds
    retry_policy: str  # "none", "simple", "exponential_backoff"

    def __post_init__(self):
        if self.bandwidth not in ["low", "standard", "high"]:
            raise ValueError(f"Invalid bandwidth: {self.bandwidth}")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")


@dataclass(frozen=True)
class Message:
    """Сообщение между агентами"""
    message_id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    content: str
    timestamp: Timestamp
    metadata: dict  # дополнительные данные

    def __post_init__(self):
        if not self.message_id or not self.from_agent or not self.to_agent:
            raise ValueError("Message ID and agent IDs cannot be empty")


# === UML CLASS DIAGRAM (TEXT) ===

"""
┌─────────────────┐
│   Vector3       │
├─────────────────┤
│ + x: float      │
│ + y: float      │
│ + z: float      │
└─────────────────┘

┌─────────────────┐
│   Color         │
├─────────────────┤
│ + r: int        │
│ + g: int        │
│ + b: int        │
│ + a: int        │
├─────────────────┤
│ + from_hex()    │
└─────────────────┘

┌─────────────────────────┐
│   AgentCapability       │
├─────────────────────────┤
│ + name: str             │
│ + description: str      │
│ + cost: float           │
│ + success_rate: float   │
└─────────────────────────┘

┌─────────────────────────┐
│   AgentMetadata         │
├─────────────────────────┤
│ + agent_id: str         │
│ + role: str             │
│ + capabilities: tuple   │
│ + avg_response_time     │
│ + success_rate          │
│ + current_load          │
└─────────────────────────┘

┌─────────────────────────┐
│   ChannelParameters     │
├─────────────────────────┤
│ + bandwidth: str        │
│ + priority: Priority    │
│ + protocol: Protocol    │
│ + timeout: int          │
│ + retry_policy: str     │
└─────────────────────────┘

┌─────────────────────────┐
│   Message               │
├─────────────────────────┤
│ + message_id: str       │
│ + from_agent: str       │
│ + to_agent: str         │
│ + message_type: Type    │
│ + content: str          │
│ + timestamp: Timestamp  │
│ + metadata: dict        │
└─────────────────────────┘
"""
```

**Complexity**: ⭐ (1/5) - Самые простые структуры
**Dependencies**: None - чистые value objects
**Usage**: Используются везде в системе как building blocks

---

## 🔷 LEVEL 2: Core Entity Classes (Простое → Среднее)

### 2.1. Agent Entity (Базовый агент)

```python
"""
Agent Entity - Represents an AI agent in the system
Simple business logic, mainly state management
"""

from typing import List, Optional
from uuid import uuid4


class Agent:
    """
    Базовая сущность агента

    Responsibilities:
    - Хранение состояния агента
    - Управление capabilities
    - Обработка сообщений (делегирует LLM)
    - Метрики производительности
    """

    def __init__(
        self,
        role: str,
        capabilities: List[AgentCapability],
        llm_backend: str = "gpt-4"
    ):
        # Identifiers
        self.id: str = str(uuid4())
        self.role: str = role

        # Capabilities
        self.capabilities: List[AgentCapability] = capabilities

        # State
        self.status: AgentStatus = AgentStatus.IDLE

        # LLM backend
        self.llm_backend: str = llm_backend

        # Metrics
        self._response_times: List[float] = []
        self._success_count: int = 0
        self._failure_count: int = 0
        self._current_load: float = 0.0

        # Message queue
        self._message_queue: List[Message] = []

    # === State Management ===

    def set_status(self, status: AgentStatus) -> None:
        """Change agent status"""
        self.status = status

    def is_available(self) -> bool:
        """Check if agent can accept new tasks"""
        return (
            self.status in [AgentStatus.IDLE, AgentStatus.COMMUNICATING]
            and self._current_load < 0.8  # не перегружен
        )

    # === Capability Queries ===

    def has_capability(self, capability_name: str) -> bool:
        """Check if agent has specific capability"""
        return any(cap.name == capability_name for cap in self.capabilities)

    def get_capability(self, name: str) -> Optional[AgentCapability]:
        """Get capability by name"""
        for cap in self.capabilities:
            if cap.name == name:
                return cap
        return None

    # === Message Handling ===

    def receive_message(self, message: Message) -> None:
        """Receive message and add to queue"""
        if message.to_agent != self.id:
            raise ValueError(f"Message not addressed to this agent (ID: {self.id})")

        self._message_queue.append(message)
        self._update_load()

    def process_messages(self) -> List[Message]:
        """
        Process all queued messages
        Returns list of response messages

        NOTE: Actual LLM processing delegated to LLMBackend
        """
        if not self._message_queue:
            return []

        self.set_status(AgentStatus.THINKING)

        responses = []
        for message in self._message_queue:
            try:
                # Делегирование обработки LLM (simplified)
                response = self._process_single_message(message)
                responses.append(response)
                self._record_success()
            except Exception as e:
                self._record_failure()
                self.set_status(AgentStatus.ERROR)
                # Create error response
                error_response = Message(
                    message_id=str(uuid4()),
                    from_agent=self.id,
                    to_agent=message.from_agent,
                    message_type=MessageType.RESPONSE,
                    content=f"Error processing message: {str(e)}",
                    timestamp=Timestamp.now(),
                    metadata={"error": True}
                )
                responses.append(error_response)

        # Clear queue
        self._message_queue.clear()
        self.set_status(AgentStatus.IDLE)
        self._update_load()

        return responses

    def _process_single_message(self, message: Message) -> Message:
        """
        Process a single message (simplified)
        In real implementation, this calls LLM backend
        """
        # Placeholder - real implementation would call LLM
        import time
        start = time.time()

        # Simulate processing
        response_content = f"Processed: {message.content}"

        # Record response time
        response_time = time.time() - start
        self._response_times.append(response_time)

        # Create response
        return Message(
            message_id=str(uuid4()),
            from_agent=self.id,
            to_agent=message.from_agent,
            message_type=MessageType.RESPONSE,
            content=response_content,
            timestamp=Timestamp.now(),
            metadata={"original_message_id": message.message_id}
        )

    # === Metrics ===

    def get_metadata(self) -> AgentMetadata:
        """Get current agent metadata"""
        return AgentMetadata(
            agent_id=self.id,
            role=self.role,
            capabilities=tuple(self.capabilities),
            avg_response_time=self.get_avg_response_time(),
            success_rate=self.get_success_rate(),
            current_load=self._current_load
        )

    def get_avg_response_time(self) -> float:
        """Get average response time in seconds"""
        if not self._response_times:
            return 0.0
        return sum(self._response_times) / len(self._response_times)

    def get_success_rate(self) -> float:
        """Get success rate (0.0-1.0)"""
        total = self._success_count + self._failure_count
        if total == 0:
            return 1.0
        return self._success_count / total

    def _record_success(self) -> None:
        """Record successful operation"""
        self._success_count += 1

    def _record_failure(self) -> None:
        """Record failed operation"""
        self._failure_count += 1

    def _update_load(self) -> None:
        """Update current load based on queue size"""
        # Simple load calculation: queue size / max queue size
        max_queue_size = 10
        self._current_load = min(1.0, len(self._message_queue) / max_queue_size)

    # === String Representation ===

    def __repr__(self) -> str:
        return f"Agent(id={self.id[:8]}, role={self.role}, status={self.status.value})"


# === UML CLASS DIAGRAM ===

"""
┌─────────────────────────────────────────┐
│              Agent                      │
├─────────────────────────────────────────┤
│ - id: str                               │
│ - role: str                             │
│ - capabilities: List[AgentCapability]   │
│ - status: AgentStatus                   │
│ - llm_backend: str                      │
│ - _response_times: List[float]          │
│ - _success_count: int                   │
│ - _failure_count: int                   │
│ - _current_load: float                  │
│ - _message_queue: List[Message]         │
├─────────────────────────────────────────┤
│ + set_status(status)                    │
│ + is_available(): bool                  │
│ + has_capability(name): bool            │
│ + get_capability(name): Capability?     │
│ + receive_message(message)              │
│ + process_messages(): List[Message]     │
│ + get_metadata(): AgentMetadata         │
│ + get_avg_response_time(): float        │
│ + get_success_rate(): float             │
│ - _process_single_message(msg): Message │
│ - _record_success()                     │
│ - _record_failure()                     │
│ - _update_load()                        │
└─────────────────────────────────────────┘
        │
        │ has
        ↓
┌─────────────────────┐
│  AgentCapability    │
└─────────────────────┘
        │
        │ uses
        ↓
┌─────────────────────┐
│  Message            │
└─────────────────────┘
"""
```

**Complexity**: ⭐⭐ (2/5) - Простая бизнес-логика
**Dependencies**: AgentCapability, Message, AgentStatus, AgentMetadata
**Key Responsibilities**:
- State management
- Message queuing
- Basic metrics tracking

### 2.2. Connection Entity (Соединение между агентами)

```python
"""
Connection Entity - Represents a communication channel between two agents
"""

from typing import Optional


class Connection:
    """
    Соединение между двумя агентами

    Responsibilities:
    - Управление каналом связи
    - Пересылка сообщений
    - Метрики использования
    - Lifecycle management (open/close)
    """

    def __init__(
        self,
        agent_a: Agent,
        agent_b: Agent,
        parameters: ChannelParameters
    ):
        # Identifiers
        self.id: str = f"{agent_a.id}↔{agent_b.id}"

        # Connected agents
        self.agent_a: Agent = agent_a
        self.agent_b: Agent = agent_b

        # Channel parameters
        self.parameters: ChannelParameters = parameters

        # State
        self.is_open: bool = False
        self.start_time: Optional[Timestamp] = None
        self.end_time: Optional[Timestamp] = None

        # Metrics
        self.messages_exchanged: List[Message] = []
        self.total_bytes: int = 0

    # === Lifecycle Management ===

    def open(self) -> None:
        """Open the connection"""
        if self.is_open:
            raise ValueError("Connection already open")

        self.is_open = True
        self.start_time = Timestamp.now()

        # Notify agents (they can prepare resources)
        # In real implementation, agents would be notified

    def close(self) -> None:
        """Close the connection"""
        if not self.is_open:
            raise ValueError("Connection already closed")

        self.is_open = False
        self.end_time = Timestamp.now()

    # === Message Transfer ===

    def send_message(self, message: Message) -> None:
        """
        Send message through connection
        Validates message routing and delivers to recipient
        """
        if not self.is_open:
            raise ValueError("Cannot send on closed connection")

        # Validate routing
        if message.from_agent not in [self.agent_a.id, self.agent_b.id]:
            raise ValueError("Message sender not part of this connection")
        if message.to_agent not in [self.agent_a.id, self.agent_b.id]:
            raise ValueError("Message recipient not part of this connection")

        # Check protocol
        if self.parameters.protocol == ConnectionProtocol.ONE_WAY:
            # One-way: only agent_a can send to agent_b
            if message.from_agent != self.agent_a.id:
                raise ValueError("One-way connection: only agent_a can send")

        # Deliver message
        recipient = self.agent_b if message.to_agent == self.agent_b.id else self.agent_a
        recipient.receive_message(message)

        # Record metrics
        self.messages_exchanged.append(message)
        self.total_bytes += len(message.content.encode('utf-8'))

    # === Metrics ===

    def get_duration(self) -> Optional[float]:
        """Get connection duration in seconds"""
        if not self.start_time:
            return None

        end = self.end_time if self.end_time else Timestamp.now()
        return (end.value - self.start_time.value).total_seconds()

    def get_message_count(self) -> int:
        """Get total messages exchanged"""
        return len(self.messages_exchanged)

    def get_throughput(self) -> float:
        """Get throughput in bytes/second"""
        duration = self.get_duration()
        if not duration or duration == 0:
            return 0.0
        return self.total_bytes / duration

    def get_metrics(self) -> dict:
        """Get all metrics"""
        return {
            "connection_id": self.id,
            "is_open": self.is_open,
            "duration_seconds": self.get_duration(),
            "messages_count": self.get_message_count(),
            "total_bytes": self.total_bytes,
            "throughput_bps": self.get_throughput(),
            "avg_message_size": (
                self.total_bytes / self.get_message_count()
                if self.get_message_count() > 0 else 0
            )
        }

    def __repr__(self) -> str:
        status = "OPEN" if self.is_open else "CLOSED"
        return f"Connection({self.id}, {status}, {self.get_message_count()} msgs)"


# === UML CLASS DIAGRAM ===

"""
┌─────────────────────────────────────────┐
│           Connection                    │
├─────────────────────────────────────────┤
│ - id: str                               │
│ - agent_a: Agent                        │
│ - agent_b: Agent                        │
│ - parameters: ChannelParameters         │
│ - is_open: bool                         │
│ - start_time: Timestamp?                │
│ - end_time: Timestamp?                  │
│ - messages_exchanged: List[Message]     │
│ - total_bytes: int                      │
├─────────────────────────────────────────┤
│ + open()                                │
│ + close()                               │
│ + send_message(message)                 │
│ + get_duration(): float?                │
│ + get_message_count(): int              │
│ + get_throughput(): float               │
│ + get_metrics(): dict                   │
└─────────────────────────────────────────┘
        │                │
        │ connects       │ connects
        ↓                ↓
    ┌───────┐        ┌───────┐
    │ Agent │        │ Agent │
    └───────┘        └───────┘
        │
        │ has
        ↓
┌─────────────────────┐
│ ChannelParameters   │
└─────────────────────┘
        │
        │ transfers
        ↓
┌─────────────────────┐
│    Message          │
└─────────────────────┘
"""
```

**Complexity**: ⭐⭐ (2/5) - Управление соединением
**Dependencies**: Agent, ChannelParameters, Message
**Key Responsibilities**:
- Connection lifecycle
- Message routing
- Metrics collection

---

## 🔷 LEVEL 3: Repository & Registry Classes (Среднее)

### 3.1. AgentRegistry (Реестр агентов)

```python
"""
AgentRegistry - Central registry for all agents
Manages agent lifecycle and provides lookup services
"""

from typing import Dict, List, Optional


class AgentRegistry:
    """
    Централизованный реестр агентов

    Responsibilities:
    - Регистрация/удаление агентов
    - Поиск агентов по различным критериям
    - Мониторинг доступности
    """

    def __init__(self):
        # Storage
        self._agents: Dict[str, Agent] = {}  # agent_id -> Agent
        self._agents_by_role: Dict[str, List[Agent]] = {}  # role -> [Agent]
        self._agents_by_capability: Dict[str, List[Agent]] = {}  # capability -> [Agent]

    # === Registration ===

    def register(self, agent: Agent) -> str:
        """
        Register an agent
        Returns agent ID
        """
        if agent.id in self._agents:
            raise ValueError(f"Agent {agent.id} already registered")

        # Add to main registry
        self._agents[agent.id] = agent

        # Index by role
        if agent.role not in self._agents_by_role:
            self._agents_by_role[agent.role] = []
        self._agents_by_role[agent.role].append(agent)

        # Index by capabilities
        for cap in agent.capabilities:
            if cap.name not in self._agents_by_capability:
                self._agents_by_capability[cap.name] = []
            self._agents_by_capability[cap.name].append(agent)

        return agent.id

    def unregister(self, agent_id: str) -> None:
        """Unregister an agent"""
        if agent_id not in self._agents:
            raise ValueError(f"Agent {agent_id} not found")

        agent = self._agents[agent_id]

        # Remove from main registry
        del self._agents[agent_id]

        # Remove from role index
        if agent.role in self._agents_by_role:
            self._agents_by_role[agent.role].remove(agent)

        # Remove from capability index
        for cap in agent.capabilities:
            if cap.name in self._agents_by_capability:
                self._agents_by_capability[cap.name].remove(agent)

    # === Lookup ===

    def get(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self._agents.get(agent_id)

    def get_by_role(self, role: str) -> List[Agent]:
        """Get all agents with specific role"""
        return self._agents_by_role.get(role, [])

    def get_by_capability(self, capability: str) -> List[Agent]:
        """Get all agents with specific capability"""
        return self._agents_by_capability.get(capability, [])

    def get_all(self) -> List[Agent]:
        """Get all registered agents"""
        return list(self._agents.values())

    # === Availability Queries ===

    def get_available(self) -> List[Agent]:
        """Get all available agents"""
        return [a for a in self._agents.values() if a.is_available()]

    def get_available_count(self) -> int:
        """Get count of available agents"""
        return len(self.get_available())

    def is_available(self, agent_id: str) -> bool:
        """Check if specific agent is available"""
        agent = self.get(agent_id)
        return agent.is_available() if agent else False

    # === Statistics ===

    def get_count(self) -> int:
        """Get total agent count"""
        return len(self._agents)

    def get_stats(self) -> dict:
        """Get registry statistics"""
        agents = list(self._agents.values())
        available = self.get_available()

        return {
            "total_agents": len(agents),
            "available_agents": len(available),
            "roles": len(self._agents_by_role),
            "capabilities": len(self._agents_by_capability),
            "avg_load": (
                sum(a._current_load for a in agents) / len(agents)
                if agents else 0.0
            ),
            "avg_success_rate": (
                sum(a.get_success_rate() for a in agents) / len(agents)
                if agents else 0.0
            )
        }

    def __len__(self) -> int:
        return len(self._agents)

    def __repr__(self) -> str:
        return f"AgentRegistry({len(self)} agents, {self.get_available_count()} available)"


# === UML CLASS DIAGRAM ===

"""
┌────────────────────────────────────────────┐
│          AgentRegistry                     │
├────────────────────────────────────────────┤
│ - _agents: Dict[str, Agent]                │
│ - _agents_by_role: Dict[str, List[Agent]]  │
│ - _agents_by_capability: Dict[...]]        │
├────────────────────────────────────────────┤
│ + register(agent): str                     │
│ + unregister(agent_id)                     │
│ + get(agent_id): Agent?                    │
│ + get_by_role(role): List[Agent]           │
│ + get_by_capability(cap): List[Agent]      │
│ + get_all(): List[Agent]                   │
│ + get_available(): List[Agent]             │
│ + get_available_count(): int               │
│ + is_available(agent_id): bool             │
│ + get_count(): int                         │
│ + get_stats(): dict                        │
└────────────────────────────────────────────┘
                │
                │ manages
                ↓
        ┌───────────────┐
        │    Agent      │
        └───────────────┘
"""
```

**Complexity**: ⭐⭐⭐ (3/5) - Управление коллекцией + индексация
**Dependencies**: Agent
**Key Responsibilities**:
- Agent lifecycle management
- Multi-index lookup
- Statistics aggregation

---

Это первая часть Level 1-3 (от простого к среднему). Продолжить с Level 4-5 (сложные компоненты)?
