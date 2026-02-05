import React, { useRef, useState } from 'react'
import { useFrame, ThreeEvent } from '@react-three/fiber'
import { Text, Html } from '@react-three/drei'
import { Agent } from '@/types/agent'
import { Mesh } from 'three'

interface AgentOperator3DProps {
  agent: Agent
  position: [number, number, number]
  onClick?: (agent: Agent) => void
}

export const AgentOperator3D: React.FC<AgentOperator3DProps> = ({ agent, position, onClick }) => {
  const meshRef = useRef<Mesh>(null)
  const bobRef = useRef({ time: 0 })
  const [hovered, setHovered] = useState(false)

  // Idle animation (subtle bob)
  useFrame((state, delta) => {
    if (meshRef.current && agent.status === 'idle') {
      bobRef.current.time += delta
      meshRef.current.position.y = position[1] + Math.sin(bobRef.current.time * 2) * 0.08
    } else if (meshRef.current) {
      meshRef.current.position.y = position[1]
    }
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'idle':
        return '#6c757d'
      case 'busy':
        return '#007bff'
      case 'error':
        return '#dc3545'
      case 'offline':
        return '#343a40'
      default:
        return '#495057'
    }
  }

  const getEmissiveIntensity = (status: string) => {
    return status === 'busy' ? 0.4 : status === 'error' ? 0.6 : 0.1
  }

  const handleClick = (e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation()
    onClick?.(agent)
  }

  const handlePointerOver = (e: ThreeEvent<PointerEvent>) => {
    e.stopPropagation()
    setHovered(true)
    document.body.style.cursor = 'pointer'
  }

  const handlePointerOut = (e: ThreeEvent<PointerEvent>) => {
    e.stopPropagation()
    setHovered(false)
    document.body.style.cursor = 'auto'
  }

  return (
    <group position={position}>
      {/* Agent body - simplified humanoid (capsule) */}
      <mesh
        ref={meshRef}
        castShadow
        receiveShadow
        onClick={handleClick}
        onPointerOver={handlePointerOver}
        onPointerOut={handlePointerOut}
      >
        <capsuleGeometry args={[0.35, 0.9, 8, 16]} />
        <meshStandardMaterial
          color={getStatusColor(agent.status)}
          metalness={0.3}
          roughness={0.7}
          emissive={getStatusColor(agent.status)}
          emissiveIntensity={hovered ? getEmissiveIntensity(agent.status) + 0.3 : getEmissiveIntensity(agent.status)}
        />
      </mesh>

      {/* Head (sphere) */}
      <mesh position={[0, 0.9, 0]} castShadow>
        <sphereGeometry args={[0.25, 16, 16]} />
        <meshStandardMaterial
          color={getStatusColor(agent.status)}
          metalness={0.2}
          roughness={0.8}
        />
      </mesh>

      {/* Status indicator (glowing sphere above head) */}
      <mesh position={[0, 1.5, 0]}>
        <sphereGeometry args={[0.1, 16, 16]} />
        <meshStandardMaterial
          color={getStatusColor(agent.status)}
          emissive={getStatusColor(agent.status)}
          emissiveIntensity={1}
        />
      </mesh>

      {/* Role name tag */}
      <Text
        position={[0, 1.9, 0]}
        fontSize={0.18}
        color="#d4af37"
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.02}
        outlineColor="#000000"
      >
        {agent.role}
      </Text>

      {/* Load indicator */}
      {agent.current_load > 0 && (
        <Text
          position={[0, 1.65, 0]}
          fontSize={0.12}
          color="#ffffff"
          anchorX="center"
          anchorY="middle"
        >
          {(agent.current_load * 100).toFixed(0)}% load
        </Text>
      )}

      {/* Hover info panel */}
      {hovered && (
        <Html position={[0, 2.2, 0]} center style={{ pointerEvents: 'none' }}>
          <div
            style={{
              background: 'rgba(0, 0, 0, 0.9)',
              padding: '10px 12px',
              borderRadius: '6px',
              color: 'white',
              fontSize: '11px',
              minWidth: '140px',
              border: '2px solid #d4af37',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
            }}
          >
          <div><strong>{agent.role}</strong></div>
          <div>Status: {agent.status}</div>
          <div>Tasks: {agent.total_tasks_completed}</div>
          {agent.capabilities.length > 0 && (
            <div style={{ marginTop: '4px' }}>
              <div style={{ fontSize: '10px', opacity: 0.8 }}>Capabilities:</div>
              {agent.capabilities.slice(0, 3).map((cap, i) => (
                <div key={i} style={{ fontSize: '10px' }}>
                  • {cap.name} (L{cap.level})
                </div>
              ))}
            </div>
          )}
        </div>
        </Html>
      )}
    </group>
  )
}
