import { CardDescription, CardHeader, CardTitle } from '../ui/card'
import { StageBadge } from './StageBadge'
import { StageCompletionBadge } from './StageCompletionBadge'
import type { JourneyStage } from '@/types/journey'

interface StageHeaderProps {
  stage: JourneyStage
}

export function StageHeader({ stage }: StageHeaderProps) {
  return (
    <CardHeader className="pb-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <CardTitle className="text-xl flex items-center gap-3 mb-1">
            <StageBadge order={stage.order} />
            <span className="gradient-text">{stage.name}</span>
          </CardTitle>
          <CardDescription className="text-muted-foreground">
            {stage.description}
          </CardDescription>
        </div>
        <StageCompletionBadge stage={stage} />
      </div>
    </CardHeader>
  )
}
