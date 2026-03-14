import React, { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Line } from '@react-three/drei'
import * as THREE from 'three'
import { Connection } from '@/types/connection'
import { Agent } from '@/types/agent'

interface ConnectionCable3DProps {
  connection: Connection
  fromAgent: Agent | undefined
  toAgent: Agent | undefined
}

export const ConnectionCable3D: React.FC<ConnectionCable3DProps> = ({
  connection,
  fromAgent,
  toAgent,
}) => {
  const lineRef = useRef<any>(null)
  const animationRef = useRef({ time: 0, pulseOffset: Math.random() * Math.PI * 2 })

  // Calculate agent positions (same logic as AgentOperator3D positioning)
  const fromPosition = useMemo(() => {
    if (!fromAgent) return [0, 0, 0] as [number, number, number]
    const x = fromAgent.position_x !== undefined ? fromAgent.position_x / 10 : 0
    const y = -3.5 // Agent base height
    const z = fromAgent.position_y !== undefined ? fromAgent.position_y / 10 : 6
    return [x, y + 0.5, z] as [number, number, number] // +0.5 to connect at agent center
  }, [fromAgent])

  const toPosition = useMemo(() => {
    if (!toAgent) return [0, 0, 0] as [number, number, number]
    const x = toAgent.position_x !== undefined ? toAgent.position_x / 10 : 0
    const y = -3.5
    const z = toAgent.position_y !== undefined ? toAgent.position_y / 10 : 6
    return [x, y + 0.5, z] as [number, number, number]
  }, [toAgent])

  // Calculate cable curve with artistic droop
  const points = useMemo(() => {
    const start = new THREE.Vector3(...fromPosition)
    const end = new THREE.Vector3(...toPosition)

    // Calculate midpoint with artistic droop
    const mid = new THREE.Vector3().lerpVectors(start, end, 0.5)
    const distance = start.distanceTo(end)
    const droopAmount = Math.min(distance * 0.3, 1.5) // Artistic cable sag
    mid.y -= droopAmount

    // Create smooth curve
    const curve = new THREE.QuadraticBezierCurve3(start, mid, end)
    return curve.getPoints(50) // 50 segments for smooth curve
  }, [fromPosition, toPosition])

  // Determine cable color based on connection status
  const cableColor = useMemo(() => {
    switch (connection.status) {
      case 'connected':
        return '#28a745' // Green
      case 'transmitting':
        return '#ffd700' // Golden (Art Deco accent)
      case 'pending':
        return '#6c757d' // Gray
      default:
        return '#c0c0c0' // Silver
    }
  }, [connection.status])

  // Animate cable for transmitting status
  useFrame((state, delta) => {
    if (connection.status === 'transmitting' && lineRef.current) {
      animationRef.current.time += delta * 2

      // Pulse effect
      const pulse = Math.sin(animationRef.current.time + animationRef.current.pulseOffset) * 0.5 + 0.5

      if (lineRef.current.material) {
        lineRef.current.material.opacity = 0.6 + pulse * 0.4
      }
    } else if (lineRef.current?.material) {
      lineRef.current.material.opacity = 0.8
    }
  })

  // Don't render if agents not found
  if (!fromAgent || !toAgent) {
    return null
  }

  return (
    <group>
      {/* Main cable line */}
      <Line
        ref={lineRef}
        points={points}
        color={cableColor}
        lineWidth={3}
        transparent
        opacity={0.8}
      />

      {/* Socket connection indicators at endpoints */}
      {connection.socket_from && (
        <mesh position={fromPosition}>
          <sphereGeometry args={[0.12, 12, 12]} />
          <meshStandardMaterial
            color={cableColor}
            emissive={cableColor}
            emissiveIntensity={connection.status === 'transmitting' ? 0.8 : 0.3}
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>
      )}

      {connection.socket_to && (
        <mesh position={toPosition}>
          <sphereGeometry args={[0.12, 12, 12]} />
          <meshStandardMaterial
            color={cableColor}
            emissive={cableColor}
            emissiveIntensity={connection.status === 'transmitting' ? 0.8 : 0.3}
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>
      )}

      {/* Flowing particles for transmitting status */}
      {connection.status === 'transmitting' && <FlowingParticles points={points} color={cableColor} />}
    </group>
  )
}

// Flowing particles component for active transmission visualization
const FlowingParticles: React.FC<{ points: THREE.Vector3[]; color: string }> = ({ points, color }) => {
  const particleRefs = useRef<THREE.Mesh[]>([])
  const progressRefs = useRef(Array.from({ length: 3 }, (_, i) => i / 3))

  useFrame((state, delta) => {
    progressRefs.current.forEach((progress, i) => {
      // Advance particle along curve
      progressRefs.current[i] = (progress + delta * 0.5) % 1.0

      const index = Math.floor(progressRefs.current[i] * (points.length - 1))
      const nextIndex = Math.min(index + 1, points.length - 1)
      const t = (progressRefs.current[i] * (points.length - 1)) - index

      // Interpolate position
      const point = points[index]
      const nextPoint = points[nextIndex]

      if (particleRefs.current[i] && point && nextPoint) {
        particleRefs.current[i].position.lerpVectors(point, nextPoint, t)
      }
    })
  })

  return (
    <>
      {Array.from({ length: 3 }).map((_, i) => (
        <mesh
          key={i}
          ref={(el) => {
            if (el) particleRefs.current[i] = el
          }}
        >
          <sphereGeometry args={[0.08, 8, 8]} />
          <meshBasicMaterial color={color} transparent opacity={0.9} />
        </mesh>
      ))}
    </>
  )
}
