import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Sparkles, TrendingUp, AlertCircle, CheckCircle2 } from 'lucide-react'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Tooltip } from '../ui/tooltip'
import { cn } from '@/lib/utils'
import type { CustomerJourney } from '@/types/journey'

interface JourneyOptimizerProps {
  journey: CustomerJourney
  onOptimize?: () => void
}

interface Optimization {
  id: string
  title: string
  description: string
  impact: 'high' | 'medium' | 'low'
  category: 'touchpoints' | 'automation' | 'content' | 'structure'
  icon: typeof CheckCircle2
}

export function JourneyOptimizer({ journey, onOptimize }: JourneyOptimizerProps) {
  const optimizations: Optimization[] = []

  // Analyze journey for optimization opportunities
  const emptyStages = journey.stages.filter(
    (stage) =>
      stage.touchpoints.length === 0 &&
      stage.automationTriggers.length === 0 &&
      stage.contentNeeds.length === 0
  )

  const stagesWithLowTouchpoints = journey.stages.filter(
    (stage) => stage.touchpoints.length < 2
  )

  const stagesWithNoAutomation = journey.stages.filter(
    (stage) => stage.automationTriggers.length === 0
  )

  const stagesWithNoContent = journey.stages.filter(
    (stage) => stage.contentNeeds.length === 0
  )

  if (emptyStages.length > 0) {
    optimizations.push({
      id: 'empty-stages',
      title: `${emptyStages.length} etapa${emptyStages.length !== 1 ? 's' : ''} vacía${emptyStages.length !== 1 ? 's' : ''}`,
      description: `Agrega contenido a: ${emptyStages.map((s) => s.name).join(', ')}`,
      impact: 'high',
      category: 'structure',
      icon: AlertCircle,
    })
  }

  if (stagesWithLowTouchpoints.length > 0) {
    optimizations.push({
      id: 'low-touchpoints',
      title: 'Etapas con pocos touchpoints',
      description: `${stagesWithLowTouchpoints.length} etapa${stagesWithLowTouchpoints.length !== 1 ? 's' : ''} tiene menos de 2 touchpoints`,
      impact: 'medium',
      category: 'touchpoints',
      icon: TrendingUp,
    })
  }

  if (stagesWithNoAutomation.length > 0) {
    optimizations.push({
      id: 'no-automation',
      title: 'Falta automatización',
      description: `${stagesWithNoAutomation.length} etapa${stagesWithNoAutomation.length !== 1 ? 's' : ''} sin triggers de automatización`,
      impact: 'medium',
      category: 'automation',
      icon: Sparkles,
    })
  }

  if (stagesWithNoContent.length > 0) {
    optimizations.push({
      id: 'no-content',
      title: 'Necesidades de contenido',
      description: `${stagesWithNoContent.length} etapa${stagesWithNoContent.length !== 1 ? 's' : ''} sin necesidades de contenido definidas`,
      impact: 'low',
      category: 'content',
      icon: CheckCircle2,
    })
  }

  if (optimizations.length === 0) {
    optimizations.push({
      id: 'optimized',
      title: 'Journey optimizado',
      description: 'Tu journey está bien estructurado y completo',
      impact: 'high',
      category: 'structure',
      icon: CheckCircle2,
    })
  }

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'text-destructive'
      case 'medium':
        return 'text-accent'
      case 'low':
        return 'text-primary'
      default:
        return 'text-muted-foreground'
    }
  }

  const getImpactBadge = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'destructive'
      case 'medium':
        return 'outline'
      case 'low':
        return 'secondary'
      default:
        return 'default'
    }
  }

  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          Optimizaciones Sugeridas
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {optimizations.map((opt, index) => {
          const Icon = opt.icon
          return (
            <div
              key={opt.id}
              className={cn(
                'p-4 rounded-lg border animate-fade-in',
                opt.impact === 'high'
                  ? 'bg-destructive/10 border-destructive/20'
                  : opt.impact === 'medium'
                  ? 'bg-accent/10 border-accent/20'
                  : 'bg-primary/10 border-primary/20'
              )}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-start gap-3">
                <Icon className={cn('h-5 w-5 shrink-0 mt-0.5', getImpactColor(opt.impact))} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="text-sm font-semibold">{opt.title}</h4>
                    <Badge variant={getImpactBadge(opt.impact) as any} className="text-xs">
                      {opt.impact === 'high' ? 'Alto' : opt.impact === 'medium' ? 'Medio' : 'Bajo'}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">{opt.description}</p>
                </div>
              </div>
            </div>
          )
        })}

        {optimizations.length > 0 && optimizations[0].id !== 'optimized' && onOptimize && (
          <div className="pt-3 border-t border-border">
            <Tooltip content="Ir al builder para implementar las optimizaciones">
              <Button
                variant="default"
                className="w-full"
                onClick={onOptimize}
              >
                <Sparkles className="h-4 w-4 mr-2" />
                Ir a Optimizar
              </Button>
            </Tooltip>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

