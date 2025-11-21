import { cn } from '@/lib/utils'

interface ProgressBarProps {
  value: number
  max?: number
  className?: string
  showLabel?: boolean
}

export function ProgressBar({
  value,
  max = 100,
  className,
  showLabel = false,
}: ProgressBarProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)

  return (
    <div className={cn('w-full space-y-1', className)}>
      {showLabel && (
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>Progreso</span>
          <span>{Math.round(percentage)}%</span>
        </div>
      )}
      <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
        <div
          className="h-full bg-gradient-primary transition-smooth"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}










