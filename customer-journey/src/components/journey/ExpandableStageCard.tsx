import { useState } from 'react'
import { Card, CardContent, CardHeader } from '../ui/card'
import { ChevronDown, ChevronUp, ArrowRight } from 'lucide-react'
import { StageBadge } from './StageBadge'
import { StageMetrics } from './StageMetrics'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { cn } from '@/lib/utils'
import type { JourneyStage } from '@/types/journey'

interface ExpandableStageCardProps {
  stage: JourneyStage
  index: number
  totalStages: number
  onExpand?: () => void
}

export function ExpandableStageCard({
  stage,
  index,
  totalStages,
  onExpand,
}: ExpandableStageCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const toggleExpand = () => {
    setIsExpanded(!isExpanded)
    if (!isExpanded && onExpand) {
      onExpand()
    }
  }

  const hasContent =
    stage.touchpoints.length > 0 ||
    stage.automationTriggers.length > 0 ||
    stage.contentNeeds.length > 0

  return (
    <div
      className="relative animate-fade-in"
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <Card
        className={cn(
          'bg-gradient-hero border-primary/30 hover:border-primary/50 transition-smooth hover-lift group animate-scale-in shadow-soft hover:shadow-hover',
          isExpanded && 'ring-2 ring-primary/20'
        )}
      >
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3 flex-1">
              <StageBadge order={stage.order} className="animate-pulse-glow shrink-0" />
              <div className="flex-1 min-w-0">
                <h3
                  className={cn(
                    'font-semibold text-lg mb-1 transition-smooth',
                    'group-hover:gradient-text'
                  )}
                >
                  {stage.name}
                </h3>
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {stage.description}
                </p>
              </div>
            </div>
            {hasContent && (
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleExpand}
                className="shrink-0"
                aria-label={isExpanded ? 'Colapsar' : 'Expandir'}
              >
                {isExpanded ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </Button>
            )}
          </div>
        </CardHeader>

        <CardContent className="pt-0">
          <div className="flex flex-col items-center space-y-4">
            <div className="w-full flex justify-center">
              <StageMetrics stage={stage} />
            </div>

            {isExpanded && (
              <div className="w-full space-y-4 pt-4 border-t border-border animate-slide-down">
                {stage.touchpoints.length > 0 && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm font-medium">
                      <span>Touchpoints</span>
                      <Badge variant="secondary" className="text-xs">
                        {stage.touchpoints.length}
                      </Badge>
                    </div>
                    <div className="space-y-1 pl-4">
                      {stage.touchpoints.slice(0, 3).map((tp) => (
                        <div
                          key={tp.id}
                          className="text-xs text-muted-foreground flex items-center gap-2"
                        >
                          <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
                          <span className="truncate">{tp.name || 'Sin nombre'}</span>
                          {tp.channel && (
                            <Badge variant="outline" className="text-xs ml-auto">
                              {tp.channel}
                            </Badge>
                          )}
                        </div>
                      ))}
                      {stage.touchpoints.length > 3 && (
                        <div className="text-xs text-muted-foreground pl-4">
                          +{stage.touchpoints.length - 3} más
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {stage.automationTriggers.length > 0 && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm font-medium">
                      <span>Automatizaciones</span>
                      <Badge variant="secondary" className="text-xs">
                        {stage.automationTriggers.length}
                      </Badge>
                    </div>
                    <div className="space-y-1 pl-4">
                      {stage.automationTriggers.slice(0, 3).map((trigger) => (
                        <div
                          key={trigger.id}
                          className="text-xs text-muted-foreground flex items-center gap-2"
                        >
                          <span className="w-1.5 h-1.5 rounded-full bg-accent"></span>
                          <span className="truncate">{trigger.name || 'Sin nombre'}</span>
                          {trigger.type && (
                            <Badge variant="outline" className="text-xs ml-auto">
                              {trigger.type}
                            </Badge>
                          )}
                        </div>
                      ))}
                      {stage.automationTriggers.length > 3 && (
                        <div className="text-xs text-muted-foreground pl-4">
                          +{stage.automationTriggers.length - 3} más
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {stage.contentNeeds.length > 0 && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm font-medium">
                      <span>Necesidades de Contenido</span>
                      <Badge variant="secondary" className="text-xs">
                        {stage.contentNeeds.length}
                      </Badge>
                    </div>
                    <div className="space-y-1 pl-4">
                      {stage.contentNeeds.slice(0, 3).map((content, idx) => (
                        <div
                          key={idx}
                          className="text-xs text-muted-foreground flex items-center gap-2"
                        >
                          <span className="w-1.5 h-1.5 rounded-full bg-secondary"></span>
                          <span className="truncate">{content}</span>
                        </div>
                      ))}
                      {stage.contentNeeds.length > 3 && (
                        <div className="text-xs text-muted-foreground pl-4">
                          +{stage.contentNeeds.length - 3} más
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
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

