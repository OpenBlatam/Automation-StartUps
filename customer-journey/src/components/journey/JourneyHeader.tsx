import { Badge } from '../ui/badge'
import type { BuyerPersona } from '@/types/journey'

interface JourneyHeaderProps {
  persona: BuyerPersona
}

export function JourneyHeader({ persona }: JourneyHeaderProps) {
  return (
    <div className="pb-6 border-b border-border">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-3">
          <div>
            <h2 className="text-3xl font-bold mb-2 gradient-text">
              Journey Builder: {persona.name}
            </h2>
            <p className="text-muted-foreground text-base">
              Define touchpoints, automatizaciones y necesidades de contenido para cada etapa
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline" className="text-xs">
              {persona.purchaseTimeframe}
            </Badge>
            {persona.channels.slice(0, 3).map((channel, idx) => (
              <Badge key={idx} variant="secondary" className="text-xs">
                {channel}
              </Badge>
            ))}
            {persona.channels.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{persona.channels.length - 3} más
              </Badge>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

