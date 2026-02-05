import React from 'react'
import { useConnectionsStore } from '@/store/connections'

interface SocketProps {
  position: [number, number, number]
  socketNum: number
  isAllocated: boolean
}

const Socket: React.FC<SocketProps> = ({ position, socketNum, isAllocated }) => {
  return (
    <group position={position}>
      {/* Socket cylinder */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.15, 0.15, 0.3, 16]} />
        <meshStandardMaterial
          color={isAllocated ? '#28a745' : '#c0c0c0'}
          metalness={0.9}
          roughness={0.1}
          emissive={isAllocated ? '#28a745' : '#000000'}
          emissiveIntensity={isAllocated ? 0.5 : 0}
        />
      </mesh>

      {/* Socket number label */}
      <mesh position={[0, 0, 0.2]}>
        <planeGeometry args={[0.2, 0.2]} />
        <meshBasicMaterial color="#000000" />
      </mesh>
    </group>
  )
}

export const Switchboard3D: React.FC = () => {
  const getAllocatedSockets = useConnectionsStore((state) => state.getAllocatedSockets)
  const allocatedSockets = getAllocatedSockets()

  const sockets = []

  for (let row = 0; row < 10; row++) {
    for (let col = 0; col < 10; col++) {
      const x = (col - 4.5) * 1.1
      const y = (4.5 - row) * 0.7
      const socketNum = row * 10 + col + 1
      const isAllocated = allocatedSockets.includes(socketNum)

      sockets.push(
        <Socket
          key={socketNum}
          position={[x, y, 0]}
          socketNum={socketNum}
          isAllocated={isAllocated}
        />
      )
    }
  }

  return (
    <group>
      {/* Main panel background */}
      <mesh position={[0, 0, -0.2]}>
        <boxGeometry args={[12, 8, 0.4]} />
        <meshStandardMaterial
          color="#8B4513"
          metalness={0.3}
          roughness={0.7}
        />
      </mesh>

      {/* Brass frame */}
      <mesh position={[0, 0, -0.1]}>
        <boxGeometry args={[12.5, 8.5, 0.1]} />
        <meshStandardMaterial
          color="#d4af37"
          metalness={0.95}
          roughness={0.1}
        />
      </mesh>

      {/* Sockets */}
      {sockets}

      {/* Art Deco corner decorations */}
      <group>
        {/* Top-left corner */}
        <mesh position={[-5.8, 3.8, 0.1]}>
          <torusGeometry args={[0.3, 0.05, 8, 6]} />
          <meshStandardMaterial color="#d4af37" metalness={1} roughness={0.1} />
        </mesh>

        {/* Top-right corner */}
        <mesh position={[5.8, 3.8, 0.1]}>
          <torusGeometry args={[0.3, 0.05, 8, 6]} />
          <meshStandardMaterial color="#d4af37" metalness={1} roughness={0.1} />
        </mesh>

        {/* Bottom-left corner */}
        <mesh position={[-5.8, -3.8, 0.1]}>
          <torusGeometry args={[0.3, 0.05, 8, 6]} />
          <meshStandardMaterial color="#d4af37" metalness={1} roughness={0.1} />
        </mesh>

        {/* Bottom-right corner */}
        <mesh position={[5.8, -3.8, 0.1]}>
          <torusGeometry args={[0.3, 0.05, 8, 6]} />
          <meshStandardMaterial color="#d4af37" metalness={1} roughness={0.1} />
        </mesh>
      </group>

      {/* Title nameplate */}
      <mesh position={[0, 4.5, 0.1]}>
        <boxGeometry args={[6, 0.6, 0.1]} />
        <meshStandardMaterial color="#d4af37" metalness={0.95} roughness={0.1} />
      </mesh>
    </group>
  )
}
