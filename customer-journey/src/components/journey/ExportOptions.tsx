import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Download, FileText, FileSpreadsheet, FileJson, Copy, Check } from 'lucide-react'
import { Tooltip } from '../ui/tooltip'
import { useState } from 'react'
import type { CustomerJourney } from '@/types/journey'

interface ExportOptionsProps {
  journey: CustomerJourney
  onExport: (format: 'json' | 'csv') => void
  onCopy?: () => void
}

export function ExportOptions({ journey, onExport, onCopy }: ExportOptionsProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    if (onCopy) {
      onCopy()
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const exportFormats = [
    {
      id: 'json' as const,
      label: 'JSON',
      description: 'Formato estructurado para desarrolladores',
      icon: FileJson,
      color: 'text-primary',
    },
    {
      id: 'csv' as const,
      label: 'CSV',
      description: 'Formato de hoja de cálculo',
      icon: FileSpreadsheet,
      color: 'text-accent',
    },
  ]

  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Download className="h-5 w-5 text-primary" />
          Opciones de Exportación
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {exportFormats.map((format) => {
            const Icon = format.icon
            return (
              <Tooltip key={format.id} content={format.description}>
                <Button
                  variant="outline"
                  className="w-full justify-start h-auto py-3"
                  onClick={() => onExport(format.id)}
                >
                  <Icon className={`h-5 w-5 mr-3 ${format.color}`} />
                  <div className="flex flex-col items-start">
                    <span className="font-medium">Exportar {format.label}</span>
                    <span className="text-xs text-muted-foreground">
                      {format.description}
                    </span>
                  </div>
                </Button>
              </Tooltip>
            )
          })}
        </div>

        {onCopy && (
          <div className="pt-3 border-t border-border">
            <Tooltip content="Copiar datos del journey al portapapeles">
              <Button
                variant="outline"
                className="w-full"
                onClick={handleCopy}
              >
                {copied ? (
                  <>
                    <Check className="h-4 w-4 mr-2 text-primary" />
                    Copiado
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4 mr-2" />
                    Copiar al Portapapeles
                  </>
                )}
              </Button>
            </Tooltip>
          </div>
        )}

        <div className="pt-3 border-t border-border">
          <div className="text-xs text-muted-foreground space-y-1">
            <p className="font-medium">Información del Journey:</p>
            <ul className="list-disc list-inside space-y-0.5">
              <li>{journey.stages.length} etapas</li>
              <li>
                {journey.stages.reduce(
                  (sum, s) => sum + s.touchpoints.length,
                  0
                )}{' '}
                touchpoints
              </li>
              <li>
                {journey.stages.reduce(
                  (sum, s) => sum + s.automationTriggers.length,
                  0
                )}{' '}
                triggers
              </li>
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

