import { Card, CardContent } from '../ui/card'
import { MessageSquare, Zap, FileText } from 'lucide-react'
import { Tooltip } from '../ui/tooltip'
import type { CustomerJourney } from '@/types/journey'

interface StageStatsProps {
  journey: CustomerJourney
}

export function StageStats({ journey }: StageStatsProps) {
  const totalTouchpoints = journey.stages.reduce(
    (acc, s) => acc + s.touchpoints.length,
    0
  )
  const totalTriggers = journey.stages.reduce(
    (acc, s) => acc + s.automationTriggers.length,
    0
  )
  const totalContent = journey.stages.reduce(
    (acc, s) => acc + s.contentNeeds.length,
    0
  )

  const stats = [
    {
      label: 'Total Touchpoints',
      value: totalTouchpoints,
      icon: MessageSquare,
    },
    {
      label: 'Total Automatizaciones',
      value: totalTriggers,
      icon: Zap,
    },
    {
      label: 'Total Contenidos',
      value: totalContent,
      icon: FileText,
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
      {stats.map((stat) => (
        <Tooltip
          key={stat.label}
          content={`Total de ${stat.label.toLowerCase()} en todo el journey`}
        >
          <Card className="bg-gradient-card border-primary/20 hover-lift transition-smooth cursor-help hover:shadow-soft">
            <CardContent className="p-6 text-center">
              <div className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent mb-2">
                {stat.value}
              </div>
              <div className="text-sm text-muted-foreground font-medium flex items-center justify-center gap-2">
                <stat.icon className="h-4 w-4" />
                {stat.label}
              </div>
            </CardContent>
          </Card>
        </Tooltip>
      ))}
    </div>
  )
}

