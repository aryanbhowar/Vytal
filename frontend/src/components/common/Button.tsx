import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { Link } from 'react-router-dom'

type Variant = 'primary' | 'secondary' | 'ghost'

function classes(variant: Variant, large?: boolean, extra?: string): string {
  return ['button', `button--${variant}`, large && 'button--large', extra].filter(Boolean).join(' ')
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  large?: boolean
}

export function Button({ variant = 'primary', large, className, type = 'button', ...props }: ButtonProps) {
  return <button type={type} className={classes(variant, large, className)} {...props} />
}

interface ButtonLinkProps {
  to: string
  children: ReactNode
  variant?: Variant
  large?: boolean
  className?: string
}

export function ButtonLink({ to, children, variant = 'primary', large, className }: ButtonLinkProps) {
  return (
    <Link to={to} className={classes(variant, large, className)}>
      {children}
    </Link>
  )
}
