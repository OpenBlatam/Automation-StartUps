import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { BarChart3, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { Badge } from '../ui/badge'
import { Tooltip } from '../ui/tooltip'
import { cn } from '@/lib/utils'
import type { CustomerJourney } from '@/types/journey'

interface StageComparisonProps {
  journey: CustomerJourney
}

export function StageComparison({ journey }: StageComparisonProps) {
  const stageData = journey.stages.map((stage) => ({
    name: stage.name,
    touchpoints: stage.touchpoints.length,
    triggers: stage.automationTriggers.length,
    contentNeeds: stage.contentNeeds.length,
    total: stage.touchpoints.length + stage.automationTriggers.length + stage.contentNeeds.length,
  }))

  const maxTotal = Math.max(...stageData.map((s) => s.total), 1)
  const avgTotal = stageData.reduce((sum, s) => sum + s.total, 0) / stageData.length

  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary" />
          Comparación de Etapas
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {stageData.map((stage, index) => {
          const percentage = (stage.total / maxTotal) * 100
          const vsAvg = stage.total - avgTotal
          const isAboveAvg = vsAvg > 0
          const isBelowAvg = vsAvg < 0

          return (
            <div
              key={stage.name}
              className="space-y-2 animate-fade-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <span className="font-medium text-sm truncate">{stage.name}</span>
                  <Badge variant="outline" className="text-xs shrink-0">
                    {stage.total} total
                  </Badge>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  {isAboveAvg && (
                    <Tooltip content={`${Math.abs(vsAvg).toFixed(1)} por encima del promedio`}>
                      <TrendingUp className="h-4 w-4 text-primary" />
                    </Tooltip>
                  )}
                  {isBelowAvg && (
                    <Tooltip content={`${Math.abs(vsAvg).toFixed(1)} por debajo del promedio`}>
                      <TrendingDown className="h-4 w-4 text-muted-foreground" />
                    </Tooltip>
                  )}
                  {!isAboveAvg && !isBelowAvg && (
                    <Tooltip content="En el promedio">
                      <Minus className="h-4 w-4 text-muted-foreground" />
                    </Tooltip>
                  )}
                </div>
              </div>

              {/* Progress bar */}
              <div className="relative">
                <div className="h-3 w-full rounded-full bg-muted overflow-hidden">
                  <div
                    className={cn(
                      'h-full transition-all duration-500 rounded-full',
                      isAboveAvg
                        ? 'bg-gradient-primary'
                        : isBelowAvg
                        ? 'bg-gradient-accent opacity-60'
                        : 'bg-secondary'
                    )}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>

              {/* Breakdown */}
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <Tooltip content={`${stage.touchpoints} touchpoint${stage.touchpoints !== 1 ? 's' : ''}`}>
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full bg-primary"></div>
                    <span>{stage.touchpoints} TP</span>
                  </div>
                </Tooltip>
                <Tooltip content={`${stage.triggers} trigger${stage.triggers !== 1 ? 's' : ''}`}>
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full bg-accent"></div>
                    <span>{stage.triggers} TR</span>
                  </div>
                </Tooltip>
                <Tooltip content={`${stage.contentNeeds} contenido${stage.contentNeeds !== 1 ? 's' : ''}`}>
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full bg-secondary"></div>
                    <span>{stage.contentNeeds} CN</span>
                  </div>
                </Tooltip>
              </div>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}

