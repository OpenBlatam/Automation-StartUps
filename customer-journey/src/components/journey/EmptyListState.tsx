import { LucideIcon } from 'lucide-react'

interface EmptyListStateProps {
  icon: LucideIcon
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
}

export function EmptyListState({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
}: EmptyListStateProps) {
  return (
    <div className="text-center py-8 px-4 border border-dashed border-border rounded-lg bg-muted/20 animate-fade-in">
      <div className="flex flex-col items-center gap-3">
        <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center animate-pulse">
          <Icon className="h-6 w-6 text-primary" />
        </div>
        <div>
          <h4 className="font-semibold text-sm mb-1">{title}</h4>
          <p className="text-xs text-muted-foreground">{description}</p>
        </div>
        {actionLabel && onAction && (
          <button
            onClick={onAction}
            className="text-xs text-primary hover:underline font-medium transition-smooth"
          >
            {actionLabel}
          </button>
        )}
      </div>
    </div>
  )
}

