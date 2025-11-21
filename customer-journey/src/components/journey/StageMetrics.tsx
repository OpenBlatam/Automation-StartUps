import { MessageSquare, Zap, FileText } from 'lucide-react'
import { Tooltip } from '../ui/tooltip'
import type { JourneyStage } from '@/types/journey'

interface StageMetricsProps {
  stage: JourneyStage
}

export function StageMetrics({ stage }: StageMetricsProps) {
  const metrics = [
    {
      icon: MessageSquare,
      label: 'Touchpoints',
      value: stage.touchpoints.length,
      tooltip: `${stage.touchpoints.length} punto${stage.touchpoints.length !== 1 ? 's' : ''} de contacto definido${stage.touchpoints.length !== 1 ? 's' : ''}`,
    },
    {
      icon: Zap,
      label: 'Triggers',
      value: stage.automationTriggers.length,
      tooltip: `${stage.automationTriggers.length} trigger${stage.automationTriggers.length !== 1 ? 's' : ''} de automatización`,
    },
    {
      icon: FileText,
      label: 'Contenidos',
      value: stage.contentNeeds.length,
      tooltip: `${stage.contentNeeds.length} necesidad${stage.contentNeeds.length !== 1 ? 'es' : ''} de contenido`,
    },
  ]

  return (
    <div className="flex items-center gap-4 text-xs">
      {metrics.map((metric) => (
        <Tooltip key={metric.label} content={metric.tooltip}>
          <div className="flex items-center gap-1.5 text-muted-foreground cursor-help">
            <metric.icon className="h-3 w-3" />
            <span>
              {metric.value} {metric.label}
            </span>
          </div>
        </Tooltip>
      ))}
    </div>
  )
}

