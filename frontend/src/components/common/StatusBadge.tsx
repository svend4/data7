import React from 'react'

interface StatusBadgeProps {
  status: string
  style?: React.CSSProperties
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, style }) => {
  const getColor = (status: string): string => {
    const lowerStatus = status.toLowerCase()
    
    // Task statuses
    if (lowerStatus === 'pending' || lowerStatus === 'queued') return '#ffc107'
    if (lowerStatus === 'running') return '#007bff'
    if (lowerStatus === 'completed') return '#28a745'
    if (lowerStatus === 'failed') return '#dc3545'
    
    // Agent statuses
    if (lowerStatus === 'idle') return '#6c757d'
    if (lowerStatus === 'busy') return '#007bff'
    if (lowerStatus === 'error') return '#dc3545'
    if (lowerStatus === 'offline') return '#495057'
    
    // Connection statuses
    if (lowerStatus === 'disconnected') return '#6c757d'
    if (lowerStatus === 'connected') return '#28a745'
    if (lowerStatus === 'transmitting') return '#17a2b8'
    
    return '#6c757d'
  }

  const badgeStyle: React.CSSProperties = {
    display: 'inline-block',
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: 600,
    textTransform: 'uppercase',
    backgroundColor: getColor(status),
    color: 'white',
    ...style,
  }

  return <span style={badgeStyle}>{status}</span>
}
