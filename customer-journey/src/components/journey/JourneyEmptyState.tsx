import { Card, CardContent } from '../ui/card'
import { Map, Plus, Sparkles } from 'lucide-react'
import { Button } from '../ui/button'
import { JourneyTemplates } from './JourneyTemplates'
import { useState } from 'react'

interface JourneyEmptyStateProps {
  onAddPersona?: () => void
  onSelectTemplate?: (templateId: string) => void
}

export function JourneyEmptyState({
  onAddPersona,
  onSelectTemplate,
}: JourneyEmptyStateProps) {
  const [showTemplates, setShowTemplates] = useState(false)

  return (
    <div className="space-y-8 animate-fade-in">
      <Card className="border-dashed bg-gradient-card">
        <CardContent className="p-12 text-center">
          <div className="h-16 w-16 mx-auto mb-6 rounded-full bg-gradient-primary/20 flex items-center justify-center animate-float">
            <Map className="h-8 w-8 text-primary" />
          </div>
          <h3 className="text-xl font-semibold mb-2">No hay journey seleccionado</h3>
          <p className="text-muted-foreground mb-6 max-w-md mx-auto">
            Selecciona un buyer persona para visualizar el journey o crea uno nuevo para comenzar
          </p>
          <div className="flex items-center justify-center gap-3 flex-wrap">
            {onAddPersona && (
              <Button onClick={onAddPersona} variant="default">
                <Plus className="h-4 w-4 mr-2" />
                Crear Nueva Persona
              </Button>
            )}
            <Button
              onClick={() => setShowTemplates(!showTemplates)}
              variant="outline"
            >
              <Sparkles className="h-4 w-4 mr-2" />
              {showTemplates ? 'Ocultar' : 'Ver'} Plantillas
            </Button>
          </div>
        </CardContent>
      </Card>

      {showTemplates && (
        <div className="animate-slide-up">
          <JourneyTemplates onSelectTemplate={onSelectTemplate} />
        </div>
      )}
    </div>
  )
}

