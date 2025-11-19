import { Card, CardContent } from '../ui/card'
import { Clock, CheckCircle2, Circle } from 'lucide-react'
import { Badge } from '../ui/badge'
import { Tooltip } from '../ui/tooltip'
import { cn } from '@/lib/utils'
import type { CustomerJourney } from '@/types/journey'

interface JourneyTimelineProps {
  journey: CustomerJourney
}

export function JourneyTimeline({ journey }: JourneyTimelineProps) {
  const totalStages = journey.stages.length

  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardContent className="p-6">
        <div className="flex items-center gap-2 mb-6">
          <Clock className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-semibold">Timeline del Journey</h3>
        </div>
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gradient-primary opacity-20" />

          <div className="space-y-6">
            {journey.stages.map((stage, index) => {
              const isComplete =
                stage.touchpoints.length > 0 ||
                stage.automationTriggers.length > 0 ||
                stage.contentNeeds.length > 0

              const isLast = index === totalStages - 1

              return (
                <div
                  key={stage.id}
                  className="relative flex items-start gap-4 animate-fade-in"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  {/* Timeline dot */}
                  <div className="relative z-10 flex items-center justify-center shrink-0">
                    <div
                      className={cn(
                        'w-8 h-8 rounded-full flex items-center justify-center border-2 transition-smooth',
                        isComplete
                          ? 'bg-primary border-primary shadow-glow'
                          : 'bg-card border-muted-foreground'
                      )}
                    >
                      {isComplete ? (
                        <CheckCircle2 className="h-4 w-4 text-primary-foreground animate-success-check" />
                      ) : (
                        <Circle className="h-4 w-4 text-muted-foreground" />
                      )}
                    </div>
                    {!isLast && (
                      <div className="absolute top-8 left-1/2 -translate-x-1/2 w-0.5 h-6 bg-gradient-primary opacity-20" />
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0 pt-1">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-semibold text-base">{stage.name}</h4>
                          <Badge
                            variant="outline"
                            className="text-xs shrink-0"
                          >
                            Etapa {stage.order}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {stage.description}
                        </p>
                      </div>
                    </div>

                    {/* Metrics */}
                    <div className="flex items-center gap-4 mt-3 text-xs">
                      <Tooltip content={`${stage.touchpoints.length} touchpoint${stage.touchpoints.length !== 1 ? 's' : ''}`}>
                        <div className="flex items-center gap-1.5 text-muted-foreground">
                          <div className="w-2 h-2 rounded-full bg-primary"></div>
                          <span>{stage.touchpoints.length} TP</span>
                        </div>
                      </Tooltip>
                      <Tooltip content={`${stage.automationTriggers.length} trigger${stage.automationTriggers.length !== 1 ? 's' : ''}`}>
                        <div className="flex items-center gap-1.5 text-muted-foreground">
                          <div className="w-2 h-2 rounded-full bg-accent"></div>
                          <span>{stage.automationTriggers.length} TR</span>
                        </div>
                      </Tooltip>
                      <Tooltip content={`${stage.contentNeeds.length} necesidad${stage.contentNeeds.length !== 1 ? 'es' : ''} de contenido`}>
                        <div className="flex items-center gap-1.5 text-muted-foreground">
                          <div className="w-2 h-2 rounded-full bg-secondary"></div>
                          <span>{stage.contentNeeds.length} CN</span>
                        </div>
                      </Tooltip>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

