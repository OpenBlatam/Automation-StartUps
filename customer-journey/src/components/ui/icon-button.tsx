import { Button } from './button'
import { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface IconButtonProps {
  icon: LucideIcon
  onClick: () => void
  variant?: 'default' | 'ghost' | 'outline'
  size?: 'sm' | 'default' | 'lg' | 'icon'
  className?: string
  'aria-label': string
}

export function IconButton({
  icon: Icon,
  onClick,
  variant = 'ghost',
  size = 'icon',
  className,
  'aria-label': ariaLabel,
}: IconButtonProps) {
  return (
    <Button
      variant={variant}
      size={size}
      onClick={onClick}
      className={cn('shrink-0', className)}
      aria-label={ariaLabel}
    >
      <Icon className="h-4 w-4" />
    </Button>
  )
}

