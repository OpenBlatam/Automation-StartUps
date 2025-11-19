import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Lightbulb, AlertCircle, CheckCircle2, Info } from 'lucide-react'
import { Badge } from '../ui/badge'
import { cn } from '@/lib/utils'
import type { CustomerJourney } from '@/types/journey'

interface JourneyInsightsProps {
  journey: CustomerJourney
}

interface Insight {
  type: 'success' | 'warning' | 'info'
  title: string
  message: string
  icon: typeof CheckCircle2
}

export function JourneyInsights({ journey }: JourneyInsightsProps) {
  const insights: Insight[] = []

  // Calculate insights
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

  const emptyStages = journey.stages.filter(
    (stage) =>
      stage.touchpoints.length === 0 &&
      stage.automationTriggers.length === 0 &&
      stage.contentNeeds.length === 0
  )

  const stagesWithOnlyOneType = journey.stages.filter(
    (stage) =>
      (stage.touchpoints.length > 0 && stage.automationTriggers.length === 0 && stage.contentNeeds.length === 0) ||
      (stage.touchpoints.length === 0 && stage.automationTriggers.length > 0 && stage.contentNeeds.length === 0) ||
      (stage.touchpoints.length === 0 && stage.automationTriggers.length === 0 && stage.contentNeeds.length > 0)
  )

  // Success insights
  if (totalTouchpoints >= journey.stages.length * 2) {
    insights.push({
      type: 'success',
      title: 'Excelente cobertura de touchpoints',
      message: `Tienes ${totalTouchpoints} touchpoints distribuidos en ${journey.stages.length} etapas.`,
      icon: CheckCircle2,
    })
  }

  if (totalTriggers >= journey.stages.length) {
    insights.push({
      type: 'success',
      title: 'Buena automatización',
      message: `Has definido ${totalTriggers} triggers de automatización.`,
      icon: CheckCircle2,
    })
  }

  // Warning insights
  if (emptyStages.length > 0) {
    insights.push({
      type: 'warning',
      title: `${emptyStages.length} etapa${emptyStages.length !== 1 ? 's' : ''} sin contenido`,
      message: `Considera agregar touchpoints, triggers o contenido a: ${emptyStages.map((s) => s.name).join(', ')}`,
      icon: AlertCircle,
    })
  }

  if (stagesWithOnlyOneType.length > 0) {
    insights.push({
      type: 'warning',
      title: 'Etapas con un solo tipo de contenido',
      message: `${stagesWithOnlyOneType.length} etapa${stagesWithOnlyOneType.length !== 1 ? 's' : ''} solo tiene un tipo de elemento. Considera diversificar.`,
      icon: AlertCircle,
    })
  }

  // Info insights
  if (totalContentNeeds === 0) {
    insights.push({
      type: 'info',
      title: 'Sin necesidades de contenido definidas',
      message: 'Considera agregar necesidades de contenido para mejorar la planificación.',
      icon: Info,
    })
  }

  if (insights.length === 0) {
    insights.push({
      type: 'success',
      title: 'Journey bien estructurado',
      message: 'Tu journey tiene una buena distribución de elementos en todas las etapas.',
      icon: CheckCircle2,
    })
  }

  const typeStyles = {
    success: {
      bg: 'bg-primary/10',
      border: 'border-primary/20',
      icon: 'text-primary',
      title: 'text-primary',
    },
    warning: {
      bg: 'bg-accent/10',
      border: 'border-accent/20',
      icon: 'text-accent',
      title: 'text-accent',
    },
    info: {
      bg: 'bg-secondary/10',
      border: 'border-secondary/20',
      icon: 'text-secondary-foreground',
      title: 'text-secondary-foreground',
    },
  }

  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-primary" />
          Insights y Recomendaciones
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {insights.map((insight, index) => {
          const Icon = insight.icon
          const styles = typeStyles[insight.type]

          return (
            <div
              key={index}
              className={cn(
                'p-4 rounded-lg border animate-fade-in',
                styles.bg,
                styles.border
              )}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-start gap-3">
                <Icon className={cn('h-5 w-5 shrink-0 mt-0.5', styles.icon)} />
                <div className="flex-1 min-w-0 space-y-1">
                  <h4 className={cn('font-semibold text-sm', styles.title)}>
                    {insight.title}
                  </h4>
                  <p className="text-sm text-muted-foreground">{insight.message}</p>
                </div>
                <Badge
                  variant={insight.type === 'success' ? 'default' : 'outline'}
                  className="shrink-0 text-xs"
                >
                  {insight.type === 'success' ? 'Éxito' : insight.type === 'warning' ? 'Atención' : 'Info'}
                </Badge>
              </div>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}

