"""
Domain Value Objects (Level 1 ⭐)
Immutable primitive types for the switchboard system
Based on TECHNICAL_SPEC_PART1_UML.md
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from datetime import datetime


# ============================================================================
# Level 1: Primitive Value Objects (⭐)
# ============================================================================


@dataclass(frozen=True)
class Vector3:
    """
    3D coordinates (immutable)
    Used for spatial positioning in 3D visualization
    """
    x: float
    y: float
    z: float

    def __post_init__(self):
        """Validate coordinates"""
        if not all(isinstance(coord, (int, float)) for coord in [self.x, self.y, self.z]):
            raise ValueError("Coordinates must be numeric")

    def distance_to(self, other: "Vector3") -> float:
        """Calculate Euclidean distance to another point"""
        return ((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)**0.5

    def __str__(self) -> str:
        return f"Vector3({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"


@dataclass(frozen=True)
class Color:
    """
    RGB Color representation (Art Deco palette)
    Values: 0-255 for each channel
    """
    r: int
    g: int
    b: int
    a: float = 1.0  # Alpha channel (0.0-1.0)

    def __post_init__(self):
        """Validate color values"""
        for channel in [self.r, self.g, self.b]:
            if not (0 <= channel <= 255):
                raise ValueError(f"RGB values must be 0-255, got {channel}")
        if not (0.0 <= self.a <= 1.0):
            raise ValueError(f"Alpha must be 0.0-1.0, got {self.a}")

    def to_hex(self) -> str:
        """Convert to hex color string"""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    @classmethod
    def from_hex(cls, hex_color: str) -> "Color":
        """Create Color from hex string (#RRGGBB)"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color: {hex_color}")
        return cls(
            r=int(hex_color[0:2], 16),
            g=int(hex_color[2:4], 16),
            b=int(hex_color[4:6], 16)
        )

    # Art Deco color palette presets
    GOLD = None  # Will be set below
    BRONZE = None
    BLACK = None
    CREAM = None


# Art Deco palette (1920s theme)
Color.GOLD = Color(212, 175, 55)     # #D4AF37
Color.BRONZE = Color(205, 127, 50)   # #CD7F32
Color.BLACK = Color(20, 20, 20)      # #141414
Color.CREAM = Color(255, 253, 208)   # #FFFDD0


class AgentStatus(str, Enum):
    """
    Agent operational status
    Lifecycle states for agent entities
    """
    IDLE = "idle"           # Ready to accept work
    BUSY = "busy"           # Currently processing
    OFFLINE = "offline"     # Disconnected/unavailable
    ERROR = "error"         # In error state
    MAINTENANCE = "maintenance"  # Under maintenance


class ConnectionStatus(str, Enum):
    """
    Connection status between agents
    States for telephonic wire connections
    """
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    TRANSMITTING = "transmitting"
    DISCONNECTING = "disconnecting"
    FAILED = "failed"


class TaskStatus(str, Enum):
    """
    Task execution status
    Lifecycle of tasks flowing through the switchboard
    """
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class AgentCapability:
    """
    Agent capability definition
    Describes what an agent can do
    """
    name: str
    category: str  # e.g., "analysis", "generation", "transformation"
    level: int = 1  # Proficiency level 1-5
    description: Optional[str] = None

    def __post_init__(self):
        """Validate capability"""
        if not self.name or not self.name.strip():
            raise ValueError("Capability name cannot be empty")
        if not (1 <= self.level <= 5):
            raise ValueError(f"Capability level must be 1-5, got {self.level}")


@dataclass(frozen=True)
class PerformanceMetrics:
    """
    Performance metrics for agents
    Tracking operational efficiency
    """
    avg_response_time: float = 0.0  # seconds
    success_rate: float = 1.0       # 0.0-1.0
    total_tasks: int = 0
    current_load: float = 0.0       # 0.0-1.0 (utilization)

    def __post_init__(self):
        """Validate metrics"""
        if self.avg_response_time < 0:
            raise ValueError("Response time cannot be negative")
        if not (0.0 <= self.success_rate <= 1.0):
            raise ValueError("Success rate must be 0.0-1.0")
        if not (0.0 <= self.current_load <= 1.0):
            raise ValueError("Load must be 0.0-1.0")
        if self.total_tasks < 0:
            raise ValueError("Total tasks cannot be negative")


@dataclass(frozen=True)
class TimeRange:
    """
    Time range for queries and filtering
    """
    start: datetime
    end: datetime

    def __post_init__(self):
        """Validate time range"""
        if self.start >= self.end:
            raise ValueError("Start time must be before end time")

    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds"""
        return (self.end - self.start).total_seconds()


# ============================================================================
# Level 1.5: Composite Value Objects (⭐⭐)
# ============================================================================


@dataclass(frozen=True)
class SocketPosition:
    """
    Physical position of a socket on the switchboard
    Combines 3D position with metadata
    """
    position: Vector3
    socket_number: int
    color: Color = Color.BRONZE

    def __post_init__(self):
        """Validate socket position"""
        if self.socket_number < 0:
            raise ValueError("Socket number cannot be negative")


@dataclass(frozen=True)
class WireConnection:
    """
    Visual representation of a wire connection
    Connects two sockets with visual properties
    """
    from_socket: int
    to_socket: int
    color: Color = Color.GOLD
    thickness: float = 0.02  # meters in 3D space
    is_active: bool = False

    def __post_init__(self):
        """Validate wire connection"""
        if self.from_socket == self.to_socket:
            raise ValueError("Cannot connect socket to itself")
        if self.thickness <= 0:
            raise ValueError("Wire thickness must be positive")
