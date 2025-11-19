import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { History, Clock } from 'lucide-react'
import { Badge } from '../ui/badge'
import { Tooltip } from '../ui/tooltip'
import type { CustomerJourney } from '@/types/journey'

interface JourneyHistoryProps {
  journey: CustomerJourney
}

export function JourneyHistory({ journey }: JourneyHistoryProps) {
  const history = [
    {
      event: 'Journey creado',
      date: journey.createdAt,
      type: 'creation',
    },
    {
      event: 'Última actualización',
      date: journey.updatedAt,
      type: 'update',
    },
  ]

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return {
      date: date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      }),
      time: date.toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit',
      }),
    }
  }

  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <History className="h-5 w-5 text-primary" />
          Historial
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {history.map((item, index) => {
          const { date, time } = formatDate(item.date)
          return (
            <div
              key={index}
              className="flex items-start gap-3 p-3 rounded-lg border border-border bg-card/50 animate-fade-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="p-2 rounded-lg bg-primary/10">
                <Clock className="h-4 w-4 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium">{item.event}</span>
                  <Badge variant="outline" className="text-xs">
                    {item.type === 'creation' ? 'Creación' : 'Actualización'}
                  </Badge>
                </div>
                <div className="text-xs text-muted-foreground">
                  {date} a las {time}
                </div>
              </div>
            </div>
          )
        })}

        <div className="pt-3 border-t border-border">
          <div className="text-xs text-muted-foreground space-y-1">
            <p className="font-medium mb-2">Información del Journey:</p>
            <div className="space-y-1">
              <p>• ID: {journey.id}</p>
              <p>• Persona: {journey.persona.name}</p>
              <p>• Etapas: {journey.stages.length}</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

