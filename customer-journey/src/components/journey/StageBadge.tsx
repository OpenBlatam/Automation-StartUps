import { cn } from '@/lib/utils'

interface StageBadgeProps {
  order: number
  className?: string
}

export function StageBadge({ order, className }: StageBadgeProps) {
  return (
    <div
      className={cn(
        'h-10 w-10 rounded-full bg-gradient-primary flex items-center justify-center text-primary-foreground font-bold shadow-glow transition-smooth',
        className
      )}
    >
      {order}
    </div>
  )
}

