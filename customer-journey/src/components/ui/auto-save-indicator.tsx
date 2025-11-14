import { CheckCircle2, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface AutoSaveIndicatorProps {
  isSaving?: boolean
  lastSaved?: Date
  className?: string
}

export function AutoSaveIndicator({ isSaving, lastSaved, className }: AutoSaveIndicatorProps) {
  if (isSaving) {
    return (
      <div className={cn('flex items-center gap-2 text-xs text-muted-foreground', className)}>
        <Loader2 className="h-3 w-3 animate-spin" />
        <span>Guardando...</span>
      </div>
    )
  }

  if (lastSaved) {
    return (
      <div className={cn('flex items-center gap-2 text-xs text-muted-foreground', className)}>
        <CheckCircle2 className="h-3 w-3 text-primary" />
        <span>Guardado {formatLastSaved(lastSaved)}</span>
      </div>
    )
  }

  return null
}

function formatLastSaved(date: Date): string {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)

  if (seconds < 10) return 'ahora'
  if (seconds < 60) return `hace ${seconds}s`
  if (minutes < 60) return `hace ${minutes}m`
  if (hours < 24) return `hace ${hours}h`
  return date.toLocaleDateString()
}



