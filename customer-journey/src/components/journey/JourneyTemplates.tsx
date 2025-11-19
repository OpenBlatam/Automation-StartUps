import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { FileText, Sparkles } from 'lucide-react'
import { Badge } from '../ui/badge'
import { Tooltip } from '../ui/tooltip'

interface JourneyTemplatesProps {
  onSelectTemplate?: (templateId: string) => void
}

const templates = [
  {
    id: 'saas-b2b',
    name: 'SaaS B2B',
    description: 'Journey para productos SaaS orientados a empresas',
    stages: ['Awareness', 'Consideration', 'Decision', 'Purchase', 'Retention'],
    icon: '💼',
  },
  {
    id: 'ecommerce',
    name: 'E-commerce',
    description: 'Journey para tiendas online y ventas digitales',
    stages: ['Discovery', 'Research', 'Comparison', 'Purchase', 'Post-Purchase'],
    icon: '🛒',
  },
  {
    id: 'saas-b2c',
    name: 'SaaS B2C',
    description: 'Journey para productos SaaS orientados a consumidores',
    stages: ['Awareness', 'Trial', 'Conversion', 'Onboarding', 'Engagement'],
    icon: '📱',
  },
  {
    id: 'consulting',
    name: 'Consultoría',
    description: 'Journey para servicios de consultoría profesional',
    stages: ['Initial Contact', 'Needs Assessment', 'Proposal', 'Engagement', 'Delivery'],
    icon: '🎯',
  },
]

export function JourneyTemplates({ onSelectTemplate }: JourneyTemplatesProps) {
  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          Plantillas de Journey
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-muted-foreground mb-4">
          Selecciona una plantilla para comenzar rápidamente con un journey predefinido
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {templates.map((template) => (
            <Tooltip key={template.id} content={template.description}>
              <Button
                variant="outline"
                className="w-full h-auto py-3 justify-start flex-col items-start"
                onClick={() => onSelectTemplate?.(template.id)}
              >
                <div className="flex items-center gap-2 w-full mb-2">
                  <span className="text-2xl">{template.icon}</span>
                  <span className="font-medium flex-1 text-left">{template.name}</span>
                </div>
                <p className="text-xs text-muted-foreground text-left w-full mb-2">
                  {template.description}
                </p>
                <div className="flex items-center gap-1 flex-wrap">
                  {template.stages.map((stage, idx) => (
                    <Badge key={idx} variant="secondary" className="text-xs">
                      {stage}
                    </Badge>
                  ))}
                </div>
              </Button>
            </Tooltip>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

