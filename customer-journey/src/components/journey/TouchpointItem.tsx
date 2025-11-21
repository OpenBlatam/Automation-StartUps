import { Card, CardContent } from '../ui/card'
import { IconButton } from '../ui/icon-button'
import { X, Copy } from 'lucide-react'
import { TouchpointFormFields } from './TouchpointFormFields'
import { Tooltip } from '../ui/tooltip'
import type { Touchpoint } from '@/types/journey'

interface TouchpointItemProps {
  touchpoint: Touchpoint
  onUpdate: (updates: Partial<Touchpoint>) => void
  onRemove: () => void
  onCopy?: () => void
}

export function TouchpointItem({ touchpoint, onUpdate, onRemove, onCopy }: TouchpointItemProps) {
  return (
    <Card className="bg-gradient-accent border-border/50 hover:border-primary/30 transition-smooth animate-in hover:shadow-soft">
      <CardContent className="p-4 space-y-3">
        <div className="flex items-start justify-between gap-3">
          <TouchpointFormFields touchpoint={touchpoint} onUpdate={onUpdate} />
          <div className="flex items-center gap-1">
            {onCopy && (
              <Tooltip content="Copiar touchpoint">
                <IconButton
                  icon={Copy}
                  onClick={onCopy}
                  variant="ghost"
                  size="icon"
                  aria-label="Copiar touchpoint"
                />
              </Tooltip>
            )}
            <IconButton
              icon={X}
              onClick={onRemove}
              variant="ghost"
              size="icon"
              aria-label="Eliminar touchpoint"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

