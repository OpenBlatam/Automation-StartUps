import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { FileText, TrendingUp, Target, Zap } from 'lucide-react'
import { Badge } from '../ui/badge'
import { ProgressBar } from '../ui/progress-bar'
import type { CustomerJourney } from '@/types/journey'

interface JourneySummaryProps {
  journey: CustomerJourney
}

export function JourneySummary({ journey }: JourneySummaryProps) {
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

  const stats = [
    {
      icon: Target,
      label: 'Touchpoints',
      value: totalTouchpoints,
      color: 'text-primary',
      bgColor: 'bg-primary/10',
    },
    {
      icon: Zap,
      label: 'Automatizaciones',
      value: totalTriggers,
      color: 'text-accent',
      bgColor: 'bg-accent/10',
    },
    {
      icon: FileText,
      label: 'Contenidos',
      value: totalContentNeeds,
      color: 'text-secondary-foreground',
      bgColor: 'bg-secondary/10',
    },
    {
      icon: TrendingUp,
      label: 'Completitud',
      value: `${Math.round(completionRate)}%`,
      color: 'text-primary',
      bgColor: 'bg-primary/10',
    },
  ]

  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <FileText className="h-5 w-5 text-primary" />
          Resumen del Journey
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((stat, index) => {
            const Icon = stat.icon
            return (
              <div
                key={stat.label}
                className="flex flex-col items-center gap-2 p-4 rounded-lg bg-card/50 border border-border animate-fade-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`h-5 w-5 ${stat.color}`} />
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold gradient-text">{stat.value}</div>
                  <div className="text-xs text-muted-foreground mt-1">{stat.label}</div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Progress */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">Progreso General</span>
            <Badge variant="secondary">
              {completedStages} / {journey.stages.length} etapas
            </Badge>
          </div>
          <ProgressBar value={completionRate} />
          <p className="text-xs text-muted-foreground">
            {completedStages === journey.stages.length
              ? '¡Journey completo!'
              : `${journey.stages.length - completedStages} etapa${journey.stages.length - completedStages !== 1 ? 's' : ''} pendiente${journey.stages.length - completedStages !== 1 ? 's' : ''}`}
          </p>
        </div>

        {/* Stage Breakdown */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Desglose por Etapa</h4>
          <div className="space-y-2">
            {journey.stages.map((stage, index) => {
              const stageItems =
                stage.touchpoints.length +
                stage.automationTriggers.length +
                stage.contentNeeds.length
              const maxItems = Math.max(
                ...journey.stages.map(
                  (s) =>
                    s.touchpoints.length +
                    s.automationTriggers.length +
                    s.contentNeeds.length
                ),
                1
              )
              const stageProgress = (stageItems / maxItems) * 100

              return (
                <div
                  key={stage.id}
                  className="space-y-1 animate-fade-in"
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">{stage.name}</span>
                    <Badge variant="outline" className="text-xs">
                      {stageItems} elementos
                    </Badge>
                  </div>
                  <ProgressBar value={stageProgress} className="h-1.5" />
                </div>
              )
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

