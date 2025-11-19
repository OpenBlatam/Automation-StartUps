import * as React from 'react'
import { X, CheckCircle2, AlertCircle, Info } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface ToastProps {
  id: string
  title?: string
  description?: string
  variant?: 'default' | 'success' | 'error' | 'info'
  onClose: () => void
}

const Toast = React.forwardRef<HTMLDivElement, ToastProps>(
  ({ id, title, description, variant = 'default', onClose }, ref) => {
    const icons = {
      default: Info,
      success: CheckCircle2,
      error: AlertCircle,
      info: Info,
    }

    const Icon = icons[variant]

    return (
      <div
        ref={ref}
        className={cn(
          'group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md border p-6 pr-8 shadow-lg transition-all animate-fade-in',
          variant === 'success' && 'border-primary/20 bg-gradient-card',
          variant === 'error' && 'border-accent/20 bg-gradient-card',
          variant === 'info' && 'border-primary/20 bg-gradient-card',
          variant === 'default' && 'border-border bg-gradient-card'
        )}
      >
        <div className="grid gap-1">
          {title && (
            <div className="text-sm font-semibold flex items-center gap-2">
              <Icon
                className={cn(
                  'h-4 w-4',
                  variant === 'success' && 'text-primary',
                  variant === 'error' && 'text-accent',
                  variant === 'info' && 'text-primary'
                )}
              />
              {title}
            </div>
          )}
          {description && (
            <div className="text-sm text-muted-foreground">{description}</div>
          )}
        </div>
        <button
          className="absolute right-2 top-2 rounded-md p-1 text-muted-foreground opacity-0 transition-opacity hover:text-foreground focus:opacity-100 focus:outline-none focus:ring-2 group-hover:opacity-100"
          onClick={onClose}
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    )
  }
)
Toast.displayName = 'Toast'

export { Toast }










