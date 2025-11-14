import { Card, CardContent } from '../ui/card'
import { StageHeader } from './StageHeader'
import type { JourneyStage as JourneyStageType } from '@/types/journey'

interface StageCardProps {
  stage: JourneyStageType
  children: React.ReactNode
}

export function StageCard({ stage, children }: StageCardProps) {
  return (
    <Card className="border-primary/30 bg-gradient-card hover-lift transition-smooth animate-slide-up shadow-soft">
      <StageHeader stage={stage} />
      <CardContent className="space-y-6 pt-0">{children}</CardContent>
    </Card>
  )
}

