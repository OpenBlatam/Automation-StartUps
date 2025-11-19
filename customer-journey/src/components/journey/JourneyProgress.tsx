import { ProgressBar } from '../ui/progress-bar'
import { Card, CardContent } from '../ui/card'
import type { CustomerJourney } from '@/types/journey'

interface JourneyProgressProps {
  journey: CustomerJourney
}

export function JourneyProgress({ journey }: JourneyProgressProps) {
  const totalItems =
    journey.stages.reduce((acc, stage) => {
      return (
        acc +
        stage.touchpoints.length +
        stage.automationTriggers.length +
        stage.contentNeeds.length
      )
    }, 0) || 1

  const completedItems = journey.stages.reduce((acc, stage) => {
    const touchpointsComplete = stage.touchpoints.filter(
      (tp) => tp.name && tp.channel && tp.content
    ).length
    const triggersComplete = stage.automationTriggers.filter(
      (t) => t.name && t.condition && t.action
    ).length
    const contentComplete = stage.contentNeeds.length > 0 ? 1 : 0

    return acc + touchpointsComplete + triggersComplete + contentComplete
  }, 0)

  const progress = (completedItems / totalItems) * 100

  return (
    <Card className="bg-gradient-card border-primary/20">
      <CardContent className="p-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">Progreso del Journey</span>
            <span className="text-muted-foreground">{Math.round(progress)}%</span>
          </div>
          <ProgressBar value={progress} />
          <p className="text-xs text-muted-foreground">
            {completedItems} de {totalItems} elementos completados
          </p>
        </div>
      </CardContent>
    </Card>
  )
}










