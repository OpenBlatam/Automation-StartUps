import { Badge } from '../ui/badge'
import type { CustomerJourney } from '@/types/journey'

interface VisualizationHeaderProps {
  journey: CustomerJourney
}

export function VisualizationHeader({ journey }: VisualizationHeaderProps) {
  const totalTouchpoints = journey.stages.reduce(
    (acc, s) => acc + s.touchpoints.length,
    0
  )
  const totalTriggers = journey.stages.reduce(
    (acc, s) => acc + s.automationTriggers.length,
    0
  )

  return (
    <div className="pb-6 border-b border-border">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="space-y-3">
          <h2 className="text-3xl font-bold gradient-text">
            Visualización del Journey
          </h2>
          <div className="flex items-center gap-3 flex-wrap">
            <span className="text-sm text-muted-foreground">
              Persona:{' '}
              <span className="font-semibold text-foreground">{journey.persona.name}</span>
            </span>
            <Badge variant="outline" className="text-xs">
              {totalTouchpoints} touchpoints
            </Badge>
            <Badge variant="outline" className="text-xs">
              {totalTriggers} automatizaciones
            </Badge>
          </div>
        </div>
      </div>
    </div>
  )
}

