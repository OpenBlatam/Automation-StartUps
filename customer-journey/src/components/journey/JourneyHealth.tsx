import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Heart, AlertTriangle, CheckCircle2, Info } from 'lucide-react'
import { Badge } from '../ui/badge'
import { cn } from '@/lib/utils'
import type { CustomerJourney } from '@/types/journey'

interface JourneyHealthProps {
  journey: CustomerJourney
}

interface HealthCheck {
  id: string
  label: string
  status: 'healthy' | 'warning' | 'critical'
  message: string
  icon: typeof CheckCircle2
}

export function JourneyHealth({ journey }: JourneyHealthProps) {
  const totalTouchpoints = journey.stages.reduce(
    (sum, stage) => sum + stage.touchpoints.length,
    0
  )
  const totalTriggers = journey.stages.reduce(
    (sum, stage) => sum + stage.automationTriggers.length,
    0
  )
  const emptyStages = journey.stages.filter(
    (stage) =>
      stage.touchpoints.length === 0 &&
      stage.automationTriggers.length === 0 &&
      stage.contentNeeds.length === 0
  )

  const healthChecks: HealthCheck[] = [
    {
      id: 'stages',
      label: 'Etapas completadas',
      status: emptyStages.length === 0 ? 'healthy' : emptyStages.length <= 1 ? 'warning' : 'critical',
      message:
        emptyStages.length === 0
          ? 'Todas las etapas tienen contenido'
          : `${emptyStages.length} etapa${emptyStages.length !== 1 ? 's' : ''} sin contenido`,
      icon: emptyStages.length === 0 ? CheckCircle2 : AlertTriangle,
    },
    {
      id: 'touchpoints',
      label: 'Cobertura de touchpoints',
      status:
        totalTouchpoints >= journey.stages.length * 2
          ? 'healthy'
          : totalTouchpoints >= journey.stages.length
          ? 'warning'
          : 'critical',
      message:
        totalTouchpoints >= journey.stages.length * 2
          ? 'Excelente cobertura de touchpoints'
          : `Considera agregar más touchpoints (${totalTouchpoints} actuales)`,
      icon: totalTouchpoints >= journey.stages.length * 2 ? CheckCircle2 : Info,
    },
    {
      id: 'automation',
      label: 'Nivel de automatización',
      status:
        totalTriggers >= journey.stages.length
          ? 'healthy'
          : totalTriggers >= journey.stages.length * 0.5
          ? 'warning'
          : 'critical',
      message:
        totalTriggers >= journey.stages.length
          ? 'Buen nivel de automatización'
          : `Agrega más triggers para mejorar la automatización (${totalTriggers} actuales)`,
      icon: totalTriggers >= journey.stages.length ? CheckCircle2 : Info,
    },
    {
      id: 'balance',
      label: 'Balance del journey',
      status: 'healthy',
      message: 'El journey está bien balanceado entre etapas',
      icon: CheckCircle2,
    },
  ]

  const getStatusStyles = (status: string) => {
    switch (status) {
      case 'healthy':
        return {
          bg: 'bg-primary/10',
          border: 'border-primary/20',
          icon: 'text-primary',
          badge: 'default',
        }
      case 'warning':
        return {
          bg: 'bg-accent/10',
          border: 'border-accent/20',
          icon: 'text-accent',
          badge: 'outline',
        }
      case 'critical':
        return {
          bg: 'bg-destructive/10',
          border: 'border-destructive/20',
          icon: 'text-destructive',
          badge: 'destructive',
        }
      default:
        return {
          bg: 'bg-secondary/10',
          border: 'border-secondary/20',
          icon: 'text-secondary-foreground',
          badge: 'outline',
        }
    }
  }

  const overallHealth =
    healthChecks.filter((check) => check.status === 'healthy').length /
    healthChecks.length

  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Heart className="h-5 w-5 text-primary" />
          Salud del Journey
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Overall Health Score */}
        <div className="text-center p-4 rounded-lg border border-border bg-card/50">
          <div className="flex items-center justify-center gap-3 mb-2">
            <Heart
              className={cn(
                'h-8 w-8',
                overallHealth >= 0.75
                  ? 'text-primary'
                  : overallHealth >= 0.5
                  ? 'text-accent'
                  : 'text-destructive'
              )}
            />
            <div>
              <div
                className={cn(
                  'text-3xl font-bold',
                  overallHealth >= 0.75
                    ? 'text-primary'
                    : overallHealth >= 0.5
                    ? 'text-accent'
                    : 'text-destructive'
                )}
              >
                {Math.round(overallHealth * 100)}%
              </div>
              <div className="text-xs text-muted-foreground">Salud General</div>
            </div>
          </div>
        </div>

        {/* Health Checks */}
        <div className="space-y-2">
          {healthChecks.map((check, index) => {
            const Icon = check.icon
            const styles = getStatusStyles(check.status)

            return (
              <div
                key={check.id}
                className={cn(
                  'p-3 rounded-lg border animate-fade-in',
                  styles.bg,
                  styles.border
                )}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="flex items-start gap-3">
                  <Icon className={cn('h-5 w-5 shrink-0 mt-0.5', styles.icon)} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium">{check.label}</span>
                      <Badge variant={styles.badge as any} className="text-xs">
                        {check.status === 'healthy'
                          ? 'Saludable'
                          : check.status === 'warning'
                          ? 'Atención'
                          : 'Crítico'}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">{check.message}</p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}

