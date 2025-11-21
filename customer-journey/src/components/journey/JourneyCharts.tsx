import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { BarChart3, TrendingUp } from 'lucide-react'
import { Badge } from '../ui/badge'
import { Tooltip } from '../ui/tooltip'
import { cn } from '@/lib/utils'
import type { CustomerJourney } from '@/types/journey'

interface JourneyChartsProps {
  journey: CustomerJourney
}

export function JourneyCharts({ journey }: JourneyChartsProps) {
  const stageData = journey.stages.map((stage) => ({
    name: stage.name,
    touchpoints: stage.touchpoints.length,
    triggers: stage.automationTriggers.length,
    contentNeeds: stage.contentNeeds.length,
    total: stage.touchpoints.length + stage.automationTriggers.length + stage.contentNeeds.length,
  }))

  const maxValue = Math.max(...stageData.map((s) => s.total), 1)

  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary" />
          Gráficos de Distribución
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Bar Chart */}
        <div className="space-y-3">
          <h4 className="text-sm font-semibold">Distribución por Etapa</h4>
          <div className="space-y-3">
            {stageData.map((stage, index) => {
              const percentage = (stage.total / maxValue) * 100
              return (
                <div
                  key={index}
                  className="space-y-1.5 animate-fade-in"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium">{stage.name}</span>
                    <Badge variant="outline" className="text-xs">
                      {stage.total} elementos
                    </Badge>
                  </div>
                  <div className="relative h-6 w-full rounded-full bg-muted overflow-hidden">
                    <div
                      className="h-full bg-gradient-primary transition-all duration-500 rounded-full flex items-center justify-end pr-2"
                      style={{ width: `${percentage}%` }}
                    >
                      {percentage > 15 && (
                        <span className="text-xs text-primary-foreground font-medium">
                          {stage.total}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground pl-1">
                    <Tooltip content={`${stage.touchpoints} touchpoints`}>
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-primary"></div>
                        <span>{stage.touchpoints}</span>
                      </div>
                    </Tooltip>
                    <Tooltip content={`${stage.triggers} triggers`}>
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-accent"></div>
                        <span>{stage.triggers}</span>
                      </div>
                    </Tooltip>
                    <Tooltip content={`${stage.contentNeeds} contenidos`}>
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-secondary"></div>
                        <span>{stage.contentNeeds}</span>
                      </div>
                    </Tooltip>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Stacked Chart */}
        <div className="pt-4 border-t border-border space-y-3">
          <h4 className="text-sm font-semibold flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-primary" />
            Composición por Tipo
          </h4>
          <div className="space-y-2">
            {stageData.map((stage, index) => {
              const total = stage.touchpoints + stage.triggers + stage.contentNeeds
              if (total === 0) return null

              const tpPercent = (stage.touchpoints / total) * 100
              const trPercent = (stage.triggers / total) * 100
              const cnPercent = (stage.contentNeeds / total) * 100

              return (
                <div
                  key={index}
                  className="space-y-1 animate-fade-in"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium">{stage.name}</span>
                    <span className="text-muted-foreground">{total} total</span>
                  </div>
                  <div className="relative h-4 w-full rounded-full overflow-hidden bg-muted">
                    {tpPercent > 0 && (
                      <div
                        className="absolute left-0 top-0 h-full bg-primary transition-all duration-500"
                        style={{ width: `${tpPercent}%` }}
                        title={`${stage.touchpoints} touchpoints`}
                      />
                    )}
                    {trPercent > 0 && (
                      <div
                        className="absolute h-full bg-accent transition-all duration-500"
                        style={{
                          left: `${tpPercent}%`,
                          width: `${trPercent}%`,
                        }}
                        title={`${stage.triggers} triggers`}
                      />
                    )}
                    {cnPercent > 0 && (
                      <div
                        className="absolute h-full bg-secondary transition-all duration-500"
                        style={{
                          left: `${tpPercent + trPercent}%`,
                          width: `${cnPercent}%`,
                        }}
                        title={`${stage.contentNeeds} contenidos`}
                      />
                    )}
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

