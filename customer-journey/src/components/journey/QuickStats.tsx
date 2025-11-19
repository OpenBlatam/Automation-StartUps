import { Card, CardContent } from '../ui/card'
import { TrendingUp, Zap, MessageSquare, FileText } from 'lucide-react'
import { Badge } from '../ui/badge'
import { Tooltip } from '../ui/tooltip'
import type { CustomerJourney } from '@/types/journey'

interface QuickStatsProps {
  journey: CustomerJourney
}

export function QuickStats({ journey }: QuickStatsProps) {
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

  const stats = [
    {
      icon: MessageSquare,
      label: 'Touchpoints',
      value: totalTouchpoints,
      color: 'text-primary',
      bgColor: 'bg-primary/10',
    },
    {
      icon: Zap,
      label: 'Triggers',
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
      label: 'Completadas',
      value: `${completedStages}/${journey.stages.length}`,
      color: 'text-primary',
      bgColor: 'bg-primary/10',
    },
  ]

  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardContent className="p-4">
        <div className="flex items-center justify-between gap-4">
          {stats.map((stat, index) => {
            const Icon = stat.icon
            return (
              <Tooltip
                key={stat.label}
                content={`${stat.label}: ${stat.value}`}
              >
                <div
                  className="flex items-center gap-2 cursor-help animate-fade-in"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                    <Icon className={`h-4 w-4 ${stat.color}`} />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs text-muted-foreground">{stat.label}</span>
                    <span className="text-sm font-semibold">{stat.value}</span>
                  </div>
                </div>
              </Tooltip>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}

