import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { TrendingUp, Activity, Target, Zap } from 'lucide-react'
import { Badge } from '../ui/badge'
import { ProgressBar } from '../ui/progress-bar'
import { Tooltip } from '../ui/tooltip'
import type { CustomerJourney } from '@/types/journey'

interface JourneyStatsProps {
  journey: CustomerJourney
}

export function JourneyStats({ journey }: JourneyStatsProps) {
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

  const avgTouchpointsPerStage = totalTouchpoints / journey.stages.length
  const avgTriggersPerStage = totalTriggers / journey.stages.length
  const avgContentPerStage = totalContentNeeds / journey.stages.length

  const completionRate = (completedStages / journey.stages.length) * 100

  const stats = [
    {
      icon: Target,
      label: 'Touchpoints',
      value: totalTouchpoints,
      avg: avgTouchpointsPerStage.toFixed(1),
      color: 'text-primary',
      bgColor: 'bg-primary/10',
      progress: Math.min((avgTouchpointsPerStage / 3) * 100, 100),
    },
    {
      icon: Zap,
      label: 'Automatizaciones',
      value: totalTriggers,
      avg: avgTriggersPerStage.toFixed(1),
      color: 'text-accent',
      bgColor: 'bg-accent/10',
      progress: Math.min((avgTriggersPerStage / 2) * 100, 100),
    },
    {
      icon: Activity,
      label: 'Contenidos',
      value: totalContentNeeds,
      avg: avgContentPerStage.toFixed(1),
      color: 'text-secondary-foreground',
      bgColor: 'bg-secondary/10',
      progress: Math.min((avgContentPerStage / 2) * 100, 100),
    },
    {
      icon: TrendingUp,
      label: 'Completitud',
      value: `${Math.round(completionRate)}%`,
      avg: `${completedStages}/${journey.stages.length}`,
      color: 'text-primary',
      bgColor: 'bg-primary/10',
      progress: completionRate,
    },
  ]

  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Activity className="h-5 w-5 text-primary" />
          Estadísticas Detalladas
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <div
              key={index}
              className="space-y-2 p-4 rounded-lg border border-border bg-card/50 animate-fade-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                    <Icon className={`h-4 w-4 ${stat.color}`} />
                  </div>
                  <div>
                    <div className="text-sm font-medium">{stat.label}</div>
                    <div className="text-xs text-muted-foreground">
                      Promedio: {stat.avg}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold gradient-text">{stat.value}</div>
                </div>
              </div>
              <ProgressBar value={stat.progress} className="h-2" />
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}

