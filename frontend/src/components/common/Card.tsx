import React from 'react'

interface CardProps {
  children: React.ReactNode
  title?: string
  style?: React.CSSProperties
  className?: string
}

export const Card: React.FC<CardProps> = ({ children, title, style, className }) => {
  const cardStyle: React.CSSProperties = {
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    padding: '20px',
    ...style,
  }

  return (
    <div style={cardStyle} className={className}>
      {title && (
        <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: 600 }}>
          {title}
        </h3>
      )}
      {children}
    </div>
  )
}
