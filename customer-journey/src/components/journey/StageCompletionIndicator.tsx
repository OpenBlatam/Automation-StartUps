import { CheckCircle2, Circle } from 'lucide-react'
import { Badge } from '../ui/badge'
import { Tooltip } from '../ui/tooltip'
import { cn } from '@/lib/utils'
import type { JourneyStage } from '@/types/journey'

interface StageCompletionIndicatorProps {
  stage: JourneyStage
  showDetails?: boolean
}

export function StageCompletionIndicator({
  stage,
  showDetails = false,
}: StageCompletionIndicatorProps) {
  const hasTouchpoints = stage.touchpoints.length > 0
  const hasTriggers = stage.automationTriggers.length > 0
  const hasContent = stage.contentNeeds.length > 0

  const isComplete = hasTouchpoints || hasTriggers || hasContent
  const completionItems = [
    hasTouchpoints && 'Touchpoints',
    hasTriggers && 'Triggers',
    hasContent && 'Contenido',
  ].filter(Boolean)

  const completionPercentage =
    ((hasTouchpoints ? 1 : 0) + (hasTriggers ? 1 : 0) + (hasContent ? 1 : 0) / 3) * 100

  if (showDetails) {
    return (
      <div className="flex items-center gap-2">
        {isComplete ? (
          <CheckCircle2 className="h-4 w-4 text-primary" />
        ) : (
          <Circle className="h-4 w-4 text-muted-foreground" />
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium">
              {isComplete ? 'Completa' : 'Incompleta'}
            </span>
            <Badge
              variant={isComplete ? 'default' : 'outline'}
              className={cn(
                'text-xs',
                isComplete && 'bg-primary/20 text-primary'
              )}
            >
              {completionItems.length}/3
            </Badge>
          </div>
          {completionItems.length > 0 && (
            <div className="text-xs text-muted-foreground mt-1">
              {completionItems.join(', ')}
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <Tooltip
      content={
        isComplete
          ? `Etapa completa: ${completionItems.join(', ')}`
          : 'Etapa incompleta - Agrega touchpoints, triggers o contenido'
      }
    >
      <div className="flex items-center gap-1.5 cursor-help">
        {isComplete ? (
          <CheckCircle2 className="h-4 w-4 text-primary animate-success-check" />
        ) : (
          <Circle className="h-4 w-4 text-muted-foreground" />
        )}
        <span className="text-xs text-muted-foreground">
          {completionItems.length}/3
        </span>
      </div>
    </Tooltip>
  )
}

