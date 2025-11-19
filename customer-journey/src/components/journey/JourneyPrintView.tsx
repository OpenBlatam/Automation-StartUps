import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Printer } from 'lucide-react'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import type { CustomerJourney } from '@/types/journey'

interface JourneyPrintViewProps {
  journey: CustomerJourney
}

export function JourneyPrintView({ journey }: JourneyPrintViewProps) {
  const handlePrint = () => {
    window.print()
  }

  return (
    <div className="print-view space-y-6">
      <div className="flex items-center justify-between mb-6 print:hidden">
        <h2 className="text-2xl font-bold">Vista de Impresión</h2>
        <Button onClick={handlePrint} variant="default">
          <Printer className="h-4 w-4 mr-2" />
          Imprimir
        </Button>
      </div>

      {/* Header */}
      <div className="border-b border-border pb-4 mb-6">
        <h1 className="text-3xl font-bold mb-2">
          Customer Journey: {journey.persona.name}
        </h1>
        <p className="text-muted-foreground">{journey.persona.description}</p>
        <div className="flex items-center gap-4 mt-4 text-sm text-muted-foreground">
          <span>Fecha: {new Date(journey.updatedAt).toLocaleDateString()}</span>
          <span>•</span>
          <span>
            {journey.stages.length} etapa{journey.stages.length !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Stages */}
      <div className="space-y-8">
        {journey.stages.map((stage, index) => (
          <Card key={stage.id} className="break-inside-avoid">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl">
                    Etapa {stage.order}: {stage.name}
                  </CardTitle>
                  <p className="text-sm text-muted-foreground mt-1">
                    {stage.description}
                  </p>
                </div>
                <Badge variant="outline">Etapa {stage.order}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Touchpoints */}
              {stage.touchpoints.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <span>Touchpoints ({stage.touchpoints.length})</span>
                  </h4>
                  <div className="space-y-3">
                    {stage.touchpoints.map((tp) => (
                      <div
                        key={tp.id}
                        className="p-3 border border-border rounded-lg"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h5 className="font-medium">{tp.name || 'Sin nombre'}</h5>
                          {tp.channel && (
                            <Badge variant="outline" className="text-xs">
                              {tp.channel}
                            </Badge>
                          )}
                        </div>
                        {tp.content && (
                          <p className="text-sm text-muted-foreground">
                            {tp.content}
                          </p>
                        )}
                        {tp.timing && (
                          <p className="text-xs text-muted-foreground mt-1">
                            Timing: {tp.timing}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Triggers */}
              {stage.automationTriggers.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-3">
                    Triggers de Automatización ({stage.automationTriggers.length})
                  </h4>
                  <div className="space-y-3">
                    {stage.automationTriggers.map((trigger) => (
                      <div
                        key={trigger.id}
                        className="p-3 border border-border rounded-lg"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h5 className="font-medium">
                            {trigger.name || 'Sin nombre'}
                          </h5>
                          {trigger.type && (
                            <Badge variant="outline" className="text-xs">
                              {trigger.type}
                            </Badge>
                          )}
                        </div>
                        {trigger.condition && (
                          <p className="text-sm text-muted-foreground">
                            <strong>Condición:</strong> {trigger.condition}
                          </p>
                        )}
                        {trigger.action && (
                          <p className="text-sm text-muted-foreground mt-1">
                            <strong>Acción:</strong> {trigger.action}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Content Needs */}
              {stage.contentNeeds.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-3">
                    Necesidades de Contenido ({stage.contentNeeds.length})
                  </h4>
                  <ul className="list-disc list-inside space-y-1">
                    {stage.contentNeeds.map((content, idx) => (
                      <li key={idx} className="text-sm text-muted-foreground">
                        {content}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Empty state */}
              {stage.touchpoints.length === 0 &&
                stage.automationTriggers.length === 0 &&
                stage.contentNeeds.length === 0 && (
                  <p className="text-sm text-muted-foreground italic">
                    Esta etapa aún no tiene contenido definido.
                  </p>
                )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Footer */}
      <div className="mt-8 pt-6 border-t border-border text-center text-sm text-muted-foreground print:mt-12">
        <p>Generado el {new Date().toLocaleString()}</p>
      </div>
    </div>
  )
}

