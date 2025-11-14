import { useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { BarChart3, TrendingUp, Clock, Target } from 'lucide-react'
import { Badge } from '../ui/badge'
import type { CustomerJourney } from '@/types/journey'

interface JourneyAnalyticsProps {
  journey: CustomerJourney
}

export function JourneyAnalytics({ journey }: JourneyAnalyticsProps) {
  const analytics = useMemo(() => {
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

    const stagesWithContent = journey.stages.filter(
      (stage) =>
        stage.touchpoints.length > 0 ||
        stage.automationTriggers.length > 0 ||
        stage.contentNeeds.length > 0
    ).length

    const completionRate = (stagesWithContent / journey.stages.length) * 100

    const avgTouchpointsPerStage = totalTouchpoints / journey.stages.length
    const avgTriggersPerStage = totalTriggers / journey.stages.length

    return {
      totalTouchpoints,
      totalTriggers,
      totalContentNeeds,
      completionRate,
      avgTouchpointsPerStage,
      avgTriggersPerStage,
      stagesWithContent,
    }
  }, [journey])

  const stats = [
    {
      label: 'Touchpoints Totales',
      value: analytics.totalTouchpoints,
      icon: Target,
      color: 'text-primary',
      bgColor: 'bg-primary/10',
    },
    {
      label: 'Automatizaciones',
      value: analytics.totalTriggers,
      icon: TrendingUp,
      color: 'text-accent',
      bgColor: 'bg-accent/10',
    },
    {
      label: 'Necesidades de Contenido',
      value: analytics.totalContentNeeds,
      icon: BarChart3,
      color: 'text-secondary-foreground',
      bgColor: 'bg-secondary/10',
    },
    {
      label: 'Completitud',
      value: `${Math.round(analytics.completionRate)}%`,
      icon: Clock,
      color: 'text-primary',
      bgColor: 'bg-primary/10',
    },
  ]

  return (
    <div className="space-y-4 animate-fade-in">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="h-5 w-5 text-primary" />
        <h3 className="text-xl font-semibold">Analíticas del Journey</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <Card
              key={stat.label}
              className="bg-gradient-card hover-lift transition-smooth shadow-soft hover:shadow-hover animate-slide-up"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                    <Icon className={`h-4 w-4 ${stat.color}`} />
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    {stat.label}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold gradient-text">{stat.value}</div>
                {stat.label === 'Completitud' && (
                  <div className="mt-2 w-full bg-muted rounded-full h-2">
                    <div
                      className="bg-gradient-primary h-2 rounded-full transition-all duration-500"
                      style={{ width: `${analytics.completionRate}%` }}
                    />
                  </div>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>

      <Card className="bg-gradient-card shadow-soft animate-slide-up">
        <CardHeader>
          <CardTitle className="text-lg">Promedios por Etapa</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Touchpoints promedio</span>
                <Badge variant="outline">{analytics.avgTouchpointsPerStage.toFixed(1)}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Triggers promedio</span>
                <Badge variant="outline">{analytics.avgTriggersPerStage.toFixed(1)}</Badge>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Etapas completadas</span>
                <Badge variant="outline">
                  {analytics.stagesWithContent} / {journey.stages.length}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Total de etapas</span>
                <Badge variant="outline">{journey.stages.length}</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}



