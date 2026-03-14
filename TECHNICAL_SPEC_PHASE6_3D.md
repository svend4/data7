# Technical Specification: Phase 6 - 3D Visualization

**Status**: 🔄 In Progress
**Timeline**: Week 8-12 of 32-week roadmap
**Dependencies**: Phase 5 (Frontend Integration) ✅ Complete

---

## 🎯 Phase 6 Mission

**Goal**: Create immersive 3D visualization of the Art Deco 1920s telephonic switchboard

**Problem**: Current 2D dashboard doesn't capture the physical nature of the switchboard
- No spatial representation of agents
- Connections shown as abstract cards
- Socket board is flat grid
- Missing the "operator at switchboard" metaphor

**Solution**: Three.js-based 3D scene with Art Deco aesthetic

---

## 📋 Requirements

### Functional Requirements

1. **3D Switchboard Model**
   - Art Deco 1920s style switchboard panel
   - 100 physical socket jacks (10x10 grid)
   - Brass/copper metallic materials
   - Geometric Art Deco patterns
   - Vintage rotary phone aesthetic

2. **3D Agent Representations**
   - Agents as operator avatars
   - Positioned in 3D space
   - Status indicators (color-coded)
   - Capability tags floating above
   - Smooth animations for state changes

3. **Connection Cables**
   - Physical cable models connecting sockets
   - Catenary curve (realistic sag)
   - Color-coded by protocol
   - Glow effect for active transmissions
   - Dynamic creation/removal

4. **Interactive Camera**
   - Orbit controls (mouse drag)
   - Zoom in/out (mouse wheel)
   - Pan (right-click drag)
   - Auto-rotate option
   - Reset to default view

5. **Real-time Updates**
   - WebSocket events update 3D scene
   - New agents appear in 3D space
   - Connections show as cables
   - Task progress indicators
   - Smooth animations (< 60ms)

### Non-Functional Requirements

1. **Performance**
   - 60 FPS on modern hardware
   - < 100 draw calls per frame
   - Optimized geometry (< 10K polygons per model)
   - Texture atlasing
   - Level of detail (LOD) for distant objects

2. **Aesthetics**
   - Art Deco 1920s style
   - Golden/brass color palette
   - Geometric patterns
   - Vintage lighting (warm tones)
   - Film grain effect (subtle)

3. **User Experience**
   - Intuitive camera controls
   - Smooth animations
   - Hover effects on clickable objects
   - Tooltip on hover
   - Loading indicator during scene init

---

## 🏗️ Architecture

### Technology Stack

**Core 3D:**
- Three.js 0.160+ (WebGL rendering)
- @react-three/fiber 8.15+ (React integration)
- @react-three/drei 9.92+ (helpers and utilities)

**Additional:**
- @react-three/postprocessing (visual effects)
- leva (debug GUI)
- cannon-es (physics, optional)

---

### 3D Scene Structure

```
Scene
├── Lighting
│   ├── AmbientLight (warm, low intensity)
│   ├── DirectionalLight (key light, golden)
│   ├── PointLights (accent lights on sockets)
│   └── SpotLight (dramatic top-down)
│
├── Switchboard
│   ├── Panel (Art Deco frame)
│   ├── SocketGrid (100 jacks in 10x10)
│   ├── NameplateDecoration
│   └── BasePlate
│
├── Agents
│   ├── AgentOperator1 (3D model)
│   ├── AgentOperator2
│   ├── ...
│   └── CapabilityTags (billboards)
│
├── Connections
│   ├── Cable1 (catenary curve)
│   ├── Cable2
│   └── ...
│
├── Effects
│   ├── BloomEffect (glow)
│   ├── VignetteEffect
│   └── FilmGrainEffect
│
└── Camera
    └── OrbitControls
```

---

## 📦 Implementation Plan

### Week 8: Three.js Setup & Basic Scene

#### Day 1: Dependencies & Setup

**Install Three.js packages:**

```bash
cd frontend
npm install three @react-three/fiber @react-three/drei
npm install @react-three/postprocessing leva
npm install -D @types/three
```

**File: `frontend/src/components/3d/Scene.tsx`**

```typescript
import React, { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera } from '@react-three/drei'

export const Scene3D: React.FC = () => {
  return (
    <div style={{ width: '100%', height: '600px' }}>
      <Canvas>
        <PerspectiveCamera makeDefault position={[0, 5, 10]} />
        <OrbitControls enableDamping dampingFactor={0.05} />

        {/* Lighting */}
        <ambientLight intensity={0.3} color="#fff5e6" />
        <directionalLight position={[5, 5, 5]} intensity={0.8} color="#ffd700" />
        <pointLight position={[0, 10, 0]} intensity={0.5} color="#ff9900" />

        {/* Placeholder */}
        <Suspense fallback={null}>
          <mesh>
            <boxGeometry args={[1, 1, 1]} />
            <meshStandardMaterial color="#d4af37" metalness={0.8} roughness={0.2} />
          </mesh>
        </Suspense>
      </Canvas>
    </div>
  )
}
```

---

#### Day 2-3: Switchboard Model

**File: `frontend/src/components/3d/Switchboard.tsx`**

```typescript
import React, { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Mesh, BoxGeometry, MeshStandardMaterial } from 'three'

export const Switchboard: React.FC = () => {
  return (
    <group position={[0, 0, 0]}>
      {/* Main panel */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[12, 8, 0.5]} />
        <meshStandardMaterial
          color="#8B4513"
          metalness={0.3}
          roughness={0.7}
        />
      </mesh>

      {/* Socket grid */}
      <SocketGrid />

      {/* Art Deco decorations */}
      <Decorations />
    </group>
  )
}

const SocketGrid: React.FC = () => {
  const sockets = []

  for (let row = 0; row < 10; row++) {
    for (let col = 0; col < 10; col++) {
      const x = (col - 4.5) * 1.1
      const y = (4.5 - row) * 0.7
      const socketNum = row * 10 + col + 1

      sockets.push(
        <Socket
          key={socketNum}
          position={[x, y, 0.3]}
          number={socketNum}
        />
      )
    }
  }

  return <>{sockets}</>
}

interface SocketProps {
  position: [number, number, number]
  number: number
  isAllocated?: boolean
}

const Socket: React.FC<SocketProps> = ({ position, number, isAllocated = false }) => {
  return (
    <mesh position={position}>
      <cylinderGeometry args={[0.15, 0.15, 0.3, 16]} />
      <meshStandardMaterial
        color={isAllocated ? "#28a745" : "#c0c0c0"}
        metalness={0.9}
        roughness={0.1}
        emissive={isAllocated ? "#28a745" : "#000000"}
        emissiveIntensity={isAllocated ? 0.3 : 0}
      />
    </mesh>
  )
}

const Decorations: React.FC = () => {
  return (
    <group>
      {/* Art Deco corner ornaments */}
      <mesh position={[-5.5, 3.5, 0.3]}>
        <torusGeometry args={[0.3, 0.05, 8, 6]} />
        <meshStandardMaterial color="#d4af37" metalness={1} roughness={0.1} />
      </mesh>

      {/* Similar for other corners */}
    </group>
  )
}
```

---

### Week 9: Agents & Connections

#### Agent Operators

**File: `frontend/src/components/3d/AgentOperator.tsx`**

```typescript
import React, { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Agent } from '@/types/agent'
import { Text } from '@react-three/drei'

interface AgentOperatorProps {
  agent: Agent
  position: [number, number, number]
}

export const AgentOperator: React.FC<AgentOperatorProps> = ({ agent, position }) => {
  const meshRef = useRef<Mesh>(null)

  // Idle animation (subtle bob)
  useFrame((state) => {
    if (meshRef.current && agent.status === 'idle') {
      meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime) * 0.1
    }
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'idle': return '#6c757d'
      case 'busy': return '#007bff'
      case 'error': return '#dc3545'
      default: return '#495057'
    }
  }

  return (
    <group position={position}>
      {/* Agent body (simplified humanoid) */}
      <mesh ref={meshRef}>
        <capsuleGeometry args={[0.3, 0.8, 8, 16]} />
        <meshStandardMaterial
          color={getStatusColor(agent.status)}
          metalness={0.2}
          roughness={0.8}
        />
      </mesh>

      {/* Name tag */}
      <Text
        position={[0, 1.5, 0]}
        fontSize={0.2}
        color="#d4af37"
        anchorX="center"
        anchorY="middle"
      >
        {agent.role}
      </Text>

      {/* Capabilities (floating tags) */}
      {agent.capabilities.map((cap, i) => (
        <Text
          key={i}
          position={[0, 1.8 + i * 0.2, 0]}
          fontSize={0.12}
          color="#ffffff"
          anchorX="center"
        >
          {cap.name} (L{cap.level})
        </Text>
      ))}
    </group>
  )
}
```

---

#### Connection Cables

**File: `frontend/src/components/3d/ConnectionCable.tsx`**

```typescript
import React, { useMemo } from 'react'
import { Connection } from '@/types/connection'
import { CatmullRomCurve3, Vector3 } from 'three'
import { Line } from '@react-three/drei'

interface ConnectionCableProps {
  connection: Connection
  fromPos: Vector3
  toPos: Vector3
}

export const ConnectionCable: React.FC<ConnectionCableProps> = ({
  connection,
  fromPos,
  toPos
}) => {
  // Create catenary curve (realistic cable sag)
  const curvePoints = useMemo(() => {
    const mid = new Vector3(
      (fromPos.x + toPos.x) / 2,
      Math.min(fromPos.y, toPos.y) - 0.5, // Sag
      (fromPos.z + toPos.z) / 2
    )

    const curve = new CatmullRomCurve3([
      fromPos,
      mid,
      toPos
    ])

    return curve.getPoints(50)
  }, [fromPos, toPos])

  const getProtocolColor = (protocol: string) => {
    switch (protocol) {
      case 'TCP': return '#007bff'
      case 'UDP': return '#28a745'
      case 'HTTP': return '#ffc107'
      case 'WebSocket': return '#17a2b8'
      case 'gRPC': return '#6f42c1'
      default: return '#6c757d'
    }
  }

  return (
    <Line
      points={curvePoints}
      color={getProtocolColor(connection.protocol)}
      lineWidth={2}
      transparent
      opacity={connection.status === 'transmitting' ? 1 : 0.6}
    >
      {connection.status === 'transmitting' && (
        <lineBasicMaterial
          attach="material"
          color={getProtocolColor(connection.protocol)}
          opacity={0.8}
          transparent
        />
      )}
    </Line>
  )
}
```

---

### Week 10: Real-time Integration

**File: `frontend/src/components/3d/SwitchboardScene.tsx`**

```typescript
import React, { useEffect } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Environment } from '@react-three/drei'
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'
import { useTasksStore } from '@/store/tasks'
import { useAgentsStore } from '@/store/agents'
import { useConnectionsStore } from '@/store/connections'
import { Switchboard } from './Switchboard'
import { AgentOperator } from './AgentOperator'
import { ConnectionCable } from './ConnectionCable'

export const SwitchboardScene: React.FC = () => {
  const agents = useAgentsStore((state) => state.agents)
  const connections = useConnectionsStore((state) => state.connections)

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <Canvas shadows>
        <PerspectiveCamera makeDefault position={[0, 8, 15]} />
        <OrbitControls
          enableDamping
          dampingFactor={0.05}
          maxPolarAngle={Math.PI / 2}
          minDistance={5}
          maxDistance={30}
        />

        {/* Environment */}
        <color attach="background" args={['#1a1a1a']} />
        <fog attach="fog" args={['#1a1a1a', 10, 50]} />

        {/* Lighting */}
        <ambientLight intensity={0.2} color="#fff5e6" />
        <directionalLight
          position={[10, 10, 5]}
          intensity={0.8}
          color="#ffd700"
          castShadow
        />
        <pointLight position={[0, 10, 0]} intensity={0.5} color="#ff9900" />

        {/* Main switchboard */}
        <Switchboard />

        {/* Agents */}
        {agents.map((agent, i) => (
          <AgentOperator
            key={agent.id}
            agent={agent}
            position={[
              (agent.position_x || i * 2 - 5),
              -3,
              (agent.position_y || 5)
            ]}
          />
        ))}

        {/* Connections */}
        {connections.map((connection) => {
          const fromAgent = agents.find((a) => a.id === connection.from_agent_id)
          const toAgent = agents.find((a) => a.id === connection.to_agent_id)

          if (!fromAgent || !toAgent || !connection.socket_from || !connection.socket_to) {
            return null
          }

          // Calculate socket positions
          const fromSocketPos = getSocketPosition(connection.socket_from)
          const toSocketPos = getSocketPosition(connection.socket_to)

          return (
            <ConnectionCable
              key={connection.id}
              connection={connection}
              fromPos={fromSocketPos}
              toPos={toSocketPos}
            />
          )
        })}

        {/* Post-processing effects */}
        <EffectComposer>
          <Bloom luminanceThreshold={0.9} luminanceSmoothing={0.9} height={300} />
          <Vignette eskil={false} offset={0.1} darkness={0.5} />
        </EffectComposer>

        {/* Environment map for reflections */}
        <Environment preset="night" />
      </Canvas>
    </div>
  )
}

function getSocketPosition(socketNum: number): Vector3 {
  const row = Math.floor((socketNum - 1) / 10)
  const col = (socketNum - 1) % 10
  const x = (col - 4.5) * 1.1
  const y = (4.5 - row) * 0.7
  return new Vector3(x, y, 0.5)
}
```

---

### Week 11-12: Polish & Integration

**Features to Add:**

1. **Click interactions**
   - Click socket to show connection details
   - Click agent to show info panel
   - Click connection cable to highlight

2. **Animations**
   - Agent spawn animation (fade in + scale up)
   - Cable creation animation (grow from socket)
   - Socket glow when connection established

3. **Art Deco Details**
   - Geometric patterns on panel
   - Brass corner decorations
   - Vintage phone handset model
   - Nameplate with engraved text

4. **Performance Optimization**
   - Instance rendering for sockets
   - LOD for agents
   - Frustum culling
   - Texture compression

---

## 🎨 Art Deco Visual Style

### Color Palette

```typescript
const ArtDecoColors = {
  // Metals
  brass: '#d4af37',
  copper: '#b87333',
  bronze: '#cd7f32',
  silver: '#c0c0c0',

  // Accent colors
  emerald: '#50c878',
  ruby: '#e0115f',
  sapphire: '#0f52ba',

  // Backgrounds
  charcoal: '#36454f',
  cream: '#fffdd0',
  burgundy: '#800020',
}
```

### Materials

```typescript
const brassMaterial = {
  color: '#d4af37',
  metalness: 0.9,
  roughness: 0.1,
  envMapIntensity: 1.5,
}

const woodMaterial = {
  color: '#8B4513',
  metalness: 0,
  roughness: 0.8,
}

const glassMaterial = {
  color: '#ffffff',
  metalness: 0,
  roughness: 0,
  transparent: true,
  opacity: 0.3,
  transmission: 0.9,
}
```

---

## 🎯 Success Criteria

Phase 6 is complete when:

- ✅ 3D switchboard scene renders at 60 FPS
- ✅ 100 sockets visible in 10x10 grid
- ✅ Agents appear as 3D operators
- ✅ Connections show as physical cables
- ✅ Camera controls work (orbit, zoom, pan)
- ✅ Real-time WebSocket updates 3D scene
- ✅ Art Deco aesthetic achieved
- ✅ Click interactions work
- ✅ Animations smooth (< 60ms)
- ✅ Integrated with existing dashboard

---

## 📝 Integration with Existing App

**Add 3D view tab to dashboard:**

```typescript
// In App.tsx
const [view, setView] = useState<'2d' | '3d'>('2d')

return (
  <div>
    <Header>
      <Button onClick={() => setView('2d')}>2D View</Button>
      <Button onClick={() => setView('3d')}>3D View</Button>
    </Header>

    {view === '2d' ? (
      <Dashboard2D />
    ) : (
      <SwitchboardScene />
    )}
  </div>
)
```

---

**Meta-Orchestrator Switchboard**
*Phase 6: 3D Visualization*
**Status**: 🔄 In Progress
**Target Completion**: Week 12

