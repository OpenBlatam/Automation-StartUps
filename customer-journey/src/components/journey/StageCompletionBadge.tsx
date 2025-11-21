import { Badge } from '../ui/badge'
import { CheckCircle2 } from 'lucide-react'
import type { JourneyStage } from '@/types/journey'

interface StageCompletionBadgeProps {
  stage: JourneyStage
}

export function StageCompletionBadge({ stage }: StageCompletionBadgeProps) {
  const hasTouchpoints = stage.touchpoints.length > 0
  const hasTriggers = stage.automationTriggers.length > 0
  const hasContent = stage.contentNeeds.length > 0

  const isComplete = hasTouchpoints && hasTriggers && hasContent

  if (!isComplete) return null

  return (
    <Badge variant="default" className="text-xs gap-1.5">
      <CheckCircle2 className="h-3 w-3" />
      Completo
    </Badge>
  )
}










