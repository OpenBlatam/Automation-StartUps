import { Badge } from '../ui/badge'
import { Clock, Globe } from 'lucide-react'
import type { BuyerPersona } from '@/types/journey'

interface PersonaInfoProps {
  persona: BuyerPersona
}

export function PersonaInfo({ persona }: PersonaInfoProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-sm">
        <Clock className="h-4 w-4 text-muted-foreground" />
        <span className="text-muted-foreground">Tiempo de compra:</span>
        <Badge variant="outline" className="text-xs">
          {persona.purchaseTimeframe}
        </Badge>
      </div>
      <div className="flex items-center gap-2 flex-wrap">
        <Globe className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm text-muted-foreground">Canales:</span>
        {persona.channels.map((channel, idx) => (
          <Badge key={idx} variant="secondary" className="text-xs">
            {channel}
          </Badge>
        ))}
      </div>
    </div>
  )
}




