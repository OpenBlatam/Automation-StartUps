import { Card, CardContent } from '../ui/card'
import { IconButton } from '../ui/icon-button'
import { X, Copy } from 'lucide-react'
import { TriggerFormFields } from './TriggerFormFields'
import { Tooltip } from '../ui/tooltip'
import type { AutomationTrigger } from '@/types/journey'

interface AutomationTriggerItemProps {
  trigger: AutomationTrigger
  onUpdate: (updates: Partial<AutomationTrigger>) => void
  onRemove: () => void
  onCopy?: () => void
}

export function AutomationTriggerItem({
  trigger,
  onUpdate,
  onRemove,
  onCopy,
}: AutomationTriggerItemProps) {
  return (
    <Card className="bg-gradient-accent border-border/50 hover:border-accent/50 transition-smooth animate-in hover:shadow-soft">
      <CardContent className="p-4 space-y-3">
        <div className="flex items-start justify-between gap-3">
          <TriggerFormFields trigger={trigger} onUpdate={onUpdate} />
          <div className="flex items-center gap-1">
            {onCopy && (
              <Tooltip content="Copiar trigger">
                <IconButton
                  icon={Copy}
                  onClick={onCopy}
                  variant="ghost"
                  size="icon"
                  aria-label="Copiar trigger"
                />
              </Tooltip>
            )}
            <IconButton
              icon={X}
              onClick={onRemove}
              variant="ghost"
              size="icon"
              aria-label="Eliminar trigger"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

