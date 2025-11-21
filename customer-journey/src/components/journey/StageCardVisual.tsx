import { Card, CardContent } from '../ui/card'
import { ArrowRight } from 'lucide-react'
import { StageBadge } from './StageBadge'
import { StageMetrics } from './StageMetrics'
import { StageCompletionIndicator } from './StageCompletionIndicator'
import { cn } from '@/lib/utils'
import type { JourneyStage } from '@/types/journey'

interface StageCardVisualProps {
  stage: JourneyStage
  index: number
  totalStages: number
}

export function StageCardVisual({ stage, index, totalStages }: StageCardVisualProps) {
  return (
    <div
      className="relative animate-fade-in"
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <Card className="bg-gradient-hero border-primary/30 hover:border-primary/50 transition-smooth hover-lift group animate-scale-in shadow-soft hover:shadow-hover">
        <CardContent className="p-6">
          <div className="flex flex-col items-center text-center space-y-4">
            <StageBadge order={stage.order} className="animate-pulse-glow animate-float" />
            <div>
              <h3 className={cn(
                'font-semibold text-lg mb-1 transition-smooth',
                'group-hover:gradient-text'
              )}>
                {stage.name}
              </h3>
              <p className="text-sm text-muted-foreground line-clamp-2">
                {stage.description}
              </p>
            </div>
            <div className="w-full flex flex-col items-center gap-3">
              <StageMetrics stage={stage} />
              <StageCompletionIndicator stage={stage} />
            </div>
          </div>
        </CardContent>
      </Card>
      {index < totalStages - 1 && (
        <div className="hidden md:block absolute top-1/2 -right-2 z-10">
          <ArrowRight className="h-5 w-5 text-primary animate-pulse" />
        </div>
      )}
    </div>
  )
}

