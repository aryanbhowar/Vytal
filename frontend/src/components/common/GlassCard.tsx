import type { ElementType, ReactNode } from 'react'

interface GlassCardProps {
  children: ReactNode
  as?: ElementType
  blur?: boolean
  subtle?: boolean
  large?: boolean
  className?: string
  labelledBy?: string
}

export function GlassCard({ children, as: Tag = 'div', blur, subtle, large, className, labelledBy }: GlassCardProps) {
  const classes = ['glass-card', blur && 'glass-card--blur', subtle && 'glass-card--subtle', large && 'glass-card--padded-lg', className]
    .filter(Boolean)
    .join(' ')
  return (
    <Tag className={classes} aria-labelledby={labelledBy}>
      {children}
    </Tag>
  )
}
