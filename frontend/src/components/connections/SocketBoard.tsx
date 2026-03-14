import React, { useMemo } from 'react'
import { Card } from '../common/Card'

interface SocketBoardProps {
  allocatedSockets: number[]
}

export const SocketBoard: React.FC<SocketBoardProps> = ({ allocatedSockets }) => {
  const sockets = useMemo(() => {
    return Array.from({ length: 100 }, (_, i) => i + 1)
  }, [])

  const isAllocated = (socketNum: number) => allocatedSockets.includes(socketNum)

  return (
    <Card title="🎭 Switchboard Sockets (1-100)">
      <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>
        Art Deco 1920s Telephonic Exchange - {allocatedSockets.length} sockets allocated
      </p>
      
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(50px, 1fr))',
          gap: '8px',
        }}
      >
        {sockets.map((socketNum) => {
          const allocated = isAllocated(socketNum)
          
          return (
            <div
              key={socketNum}
              style={{
                width: '50px',
                height: '50px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: allocated ? '#28a745' : '#e9ecef',
                color: allocated ? 'white' : '#495057',
                border: allocated ? '2px solid #1e7e34' : '2px solid #ced4da',
                borderRadius: '8px',
                fontSize: '12px',
                fontWeight: 600,
                transition: 'all 0.2s',
                cursor: 'default',
              }}
              title={allocated ? `Socket ${socketNum} - ALLOCATED` : `Socket ${socketNum} - AVAILABLE`}
            >
              {socketNum}
            </div>
          )
        })}
      </div>

      <div style={{ marginTop: '16px', display: 'flex', gap: '16px', fontSize: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style={{
              width: '20px',
              height: '20px',
              backgroundColor: '#28a745',
              border: '2px solid #1e7e34',
              borderRadius: '4px',
            }}
          />
          <span>Allocated ({allocatedSockets.length})</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style={{
              width: '20px',
              height: '20px',
              backgroundColor: '#e9ecef',
              border: '2px solid #ced4da',
              borderRadius: '4px',
            }}
          />
          <span>Available ({100 - allocatedSockets.length})</span>
        </div>
      </div>
    </Card>
  )
}
