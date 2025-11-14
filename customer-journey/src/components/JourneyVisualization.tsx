import { Card, CardContent } from './ui/card'
import { Map } from 'lucide-react'
import { StageStats } from './journey/StageStats'
import { StageCardVisual } from './journey/StageCardVisual'
import { VisualizationHeader } from './journey/VisualizationHeader'
import { StageConnectionLine } from './journey/StageConnectionLine'
import { JourneyAnalytics } from './journey/JourneyAnalytics'
import type { CustomerJourney } from '@/types/journey'

interface JourneyVisualizationProps {
  journey: CustomerJourney | null
}

export function JourneyVisualization({ journey }: JourneyVisualizationProps) {
  if (!journey) {
    return (
      <Card className="border-dashed bg-gradient-card animate-fade-in">
        <CardContent className="p-12 text-center">
          <div className="h-16 w-16 mx-auto mb-6 rounded-full bg-gradient-primary/20 flex items-center justify-center animate-float">
            <Map className="h-8 w-8 text-primary" />
          </div>
          <h3 className="text-xl font-semibold mb-2">No hay journey seleccionado</h3>
          <p className="text-muted-foreground">
            Selecciona un buyer persona para visualizar el journey
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <VisualizationHeader journey={journey} />

      <div className="relative">
        <StageConnectionLine totalStages={journey.stages.length} />

        <div className="relative grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {journey.stages.map((stage, index) => (
            <StageCardVisual
              key={stage.id}
              stage={stage}
              index={index}
              totalStages={journey.stages.length}
            />
          ))}
        </div>
      </div>

      <StageStats journey={journey} />
      <JourneyAnalytics journey={journey} />
    </div>
  )
}

