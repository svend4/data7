import React, { Suspense, useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Environment, Grid } from '@react-three/drei'
import { Switchboard3D } from './Switchboard3D'
import { AgentOperator3D } from './AgentOperator3D'
import { useAgentsStore } from '@/store/agents'

export const Scene3D: React.FC = () => {
  const agents = useAgentsStore((state) => state.agents)
  const [autoRotate, setAutoRotate] = useState(false)

  return (
    <div style={{ width: '100%', height: '700px', position: 'relative' }}>
      {/* Controls overlay */}
      <div
        style={{
          position: 'absolute',
          top: '20px',
          right: '20px',
          zIndex: 10,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          padding: '12px',
          borderRadius: '8px',
          color: 'white',
        }}
      >
        <div style={{ fontSize: '14px', marginBottom: '8px' }}>
          <strong>🎮 Controls</strong>
        </div>
        <div style={{ fontSize: '12px', lineHeight: '1.6' }}>
          <div>🖱️ Left-click drag: Rotate</div>
          <div>🖱️ Right-click drag: Pan</div>
          <div>🎡 Scroll: Zoom</div>
        </div>
        <div style={{ marginTop: '12px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px' }}>
            <input
              type="checkbox"
              checked={autoRotate}
              onChange={(e) => setAutoRotate(e.target.checked)}
            />
            Auto-rotate
          </label>
        </div>
      </div>

      <Canvas shadows>
        {/* Camera */}
        <PerspectiveCamera makeDefault position={[0, 8, 15]} fov={50} />

        {/* Controls */}
        <OrbitControls
          enableDamping
          dampingFactor={0.05}
          maxPolarAngle={Math.PI / 2.1}
          minPolarAngle={Math.PI / 6}
          minDistance={8}
          maxDistance={30}
          autoRotate={autoRotate}
          autoRotateSpeed={1}
        />

        {/* Environment */}
        <color attach="background" args={['#1a1a1a']} />
        <fog attach="fog" args={['#1a1a1a', 15, 40]} />

        {/* Lighting - Art Deco warm golden tones */}
        <ambientLight intensity={0.25} color="#fff5e6" />
        
        {/* Key light (golden, from top-right) */}
        <directionalLight
          position={[10, 10, 5]}
          intensity={0.9}
          color="#ffd700"
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
        />

        {/* Fill light (warm, from left) */}
        <directionalLight
          position={[-5, 5, 5]}
          intensity={0.4}
          color="#ffcc99"
        />

        {/* Top accent light (warm orange) */}
        <pointLight position={[0, 12, 0]} intensity={0.6} color="#ff9900" />

        {/* Switchboard spotlights */}
        <spotLight
          position={[0, 5, 8]}
          intensity={0.5}
          angle={Math.PI / 4}
          penumbra={0.5}
          color="#ffffff"
          castShadow
        />

        {/* Main scene content */}
        <Suspense fallback={null}>
          {/* Switchboard */}
          <Switchboard3D />

          {/* Agents */}
          {agents.map((agent, i) => (
            <AgentOperator3D
              key={agent.id}
              agent={agent}
              position={[
                (agent.position_x !== undefined ? agent.position_x / 10 : i * 2.5 - 5),
                -3.5,
                (agent.position_y !== undefined ? agent.position_y / 10 : 6)
              ]}
            />
          ))}

          {/* Ground grid */}
          <Grid
            args={[30, 30]}
            position={[0, -4, 0]}
            cellSize={0.5}
            cellThickness={0.5}
            cellColor="#444444"
            sectionSize={3}
            sectionThickness={1}
            sectionColor="#666666"
            fadeDistance={25}
            fadeStrength={1}
          />

          {/* Environment map for reflections */}
          <Environment preset="night" />
        </Suspense>
      </Canvas>
    </div>
  )
}
