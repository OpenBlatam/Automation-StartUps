import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Gauge, TrendingUp, Zap, Clock } from 'lucide-react'
import { Badge } from '../ui/badge'
import { ProgressBar } from '../ui/progress-bar'
import { Tooltip } from '../ui/tooltip'
import type { CustomerJourney } from '@/types/journey'

interface JourneyPerformanceProps {
  journey: CustomerJourney
}

export function JourneyPerformance({ journey }: JourneyPerformanceProps) {
  const totalTouchpoints = journey.stages.reduce(
    (sum, stage) => sum + stage.touchpoints.length,
    0
  )
  const totalTriggers = journey.stages.reduce(
    (sum, stage) => sum + stage.automationTriggers.length,
    0
  )
  const totalContentNeeds = journey.stages.reduce(
    (sum, stage) => sum + stage.contentNeeds.length,
    0
  )

  const completedStages = journey.stages.filter(
    (stage) =>
      stage.touchpoints.length > 0 ||
      stage.automationTriggers.length > 0 ||
      stage.contentNeeds.length > 0
  ).length

  const completionRate = (completedStages / journey.stages.length) * 100

  // Calculate performance score (0-100)
  const performanceScore = Math.min(
    (completionRate * 0.4) +
    (Math.min(totalTouchpoints / journey.stages.length, 3) * 10) +
    (Math.min(totalTriggers / journey.stages.length, 2) * 10) +
    (Math.min(totalContentNeeds / journey.stages.length, 2) * 10),
    100
  )

  const getPerformanceLabel = (score: number) => {
    if (score >= 80) return { label: 'Excelente', color: 'text-primary', bg: 'bg-primary/10' }
    if (score >= 60) return { label: 'Bueno', color: 'text-accent', bg: 'bg-accent/10' }
    if (score >= 40) return { label: 'Regular', color: 'text-secondary-foreground', bg: 'bg-secondary/10' }
    return { label: 'Necesita Mejora', color: 'text-muted-foreground', bg: 'bg-muted/10' }
  }

  const performance = getPerformanceLabel(performanceScore)

  const metrics = [
    {
      icon: Gauge,
      label: 'Puntuación General',
      value: Math.round(performanceScore),
      max: 100,
      color: performance.color,
      bgColor: performance.bg,
    },
    {
      icon: TrendingUp,
      label: 'Completitud',
      value: Math.round(completionRate),
      max: 100,
      color: 'text-primary',
      bgColor: 'bg-primary/10',
    },
    {
      icon: Zap,
      label: 'Automatización',
      value: totalTriggers,
      max: journey.stages.length * 2,
      color: 'text-accent',
      bgColor: 'bg-accent/10',
    },
    {
      icon: Clock,
      label: 'Cobertura',
      value: totalTouchpoints,
      max: journey.stages.length * 3,
      color: 'text-secondary-foreground',
      bgColor: 'bg-secondary/10',
    },
  ]

  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Gauge className="h-5 w-5 text-primary" />
          Rendimiento del Journey
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Score */}
        <div className="text-center p-6 rounded-lg border border-border bg-card/50">
          <div className="flex items-center justify-center gap-3 mb-2">
            <div className={`p-3 rounded-full ${performance.bg}`}>
              <Gauge className={`h-6 w-6 ${performance.color}`} />
            </div>
            <div>
              <div className="text-4xl font-bold gradient-text">
                {Math.round(performanceScore)}
              </div>
              <div className={`text-sm font-medium ${performance.color}`}>
                {performance.label}
              </div>
            </div>
          </div>
          <ProgressBar value={performanceScore} className="mt-4" />
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 gap-4">
          {metrics.map((metric, index) => {
            const Icon = metric.icon
            const percentage = (metric.value / metric.max) * 100

            return (
              <Tooltip
                key={metric.label}
                content={`${metric.value} de ${metric.max} (${Math.round(percentage)}%)`}
              >
                <div
                  className="space-y-2 p-3 rounded-lg border border-border bg-card/50 animate-fade-in cursor-help"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="flex items-center gap-2">
                    <div className={`p-1.5 rounded ${metric.bgColor}`}>
                      <Icon className={`h-4 w-4 ${metric.color}`} />
                    </div>
                    <span className="text-xs font-medium text-muted-foreground">
                      {metric.label}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xl font-bold">{metric.value}</span>
                    <Badge variant="outline" className="text-xs">
                      {Math.round(percentage)}%
                    </Badge>
                  </div>
                  <ProgressBar value={percentage} className="h-1.5" />
                </div>
              </Tooltip>
            )
          })}
        </div>

        {/* Recommendations */}
        <div className="pt-4 border-t border-border">
          <h4 className="text-sm font-semibold mb-3">Recomendaciones</h4>
          <div className="space-y-2 text-xs text-muted-foreground">
            {performanceScore < 80 && (
              <p>• Considera agregar más touchpoints y automatizaciones</p>
            )}
            {completionRate < 100 && (
              <p>• Completa todas las etapas para mejorar el rendimiento</p>
            )}
            {totalTriggers < journey.stages.length && (
              <p>• Agrega más triggers de automatización para mejorar la eficiencia</p>
            )}
            {performanceScore >= 80 && (
              <p className="text-primary">✓ Tu journey está bien optimizado</p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

