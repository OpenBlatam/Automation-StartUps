import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Lightbulb, Sparkles } from 'lucide-react'
import { Badge } from '../ui/badge'

const tips = [
  {
    category: 'Mejores Prácticas',
    items: [
      'Define touchpoints claros y específicos para cada etapa',
      'Agrega triggers de automatización para mejorar la eficiencia',
      'Documenta las necesidades de contenido para facilitar la planificación',
      'Revisa regularmente el journey para mantenerlo actualizado',
    ],
  },
  {
    category: 'Optimización',
    items: [
      'Usa la vista expandida para ver detalles completos',
      'Aprovecha los filtros para encontrar etapas específicas',
      'Exporta el journey para compartirlo con tu equipo',
      'Utiliza los insights para identificar áreas de mejora',
    ],
  },
  {
    category: 'Productividad',
    items: [
      'Usa Ctrl+K para buscar rápidamente',
      'Aprovecha copy/paste para duplicar elementos',
      'Revisa el panel de rendimiento regularmente',
      'Comparte el journey con stakeholders usando el enlace',
    ],
  },
]

export function JourneyTips() {
  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          Consejos y Tips
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {tips.map((category, catIdx) => (
          <div key={catIdx} className="space-y-2">
            <h4 className="text-sm font-semibold flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-primary" />
              {category.category}
            </h4>
            <ul className="space-y-1.5">
              {category.items.map((tip, tipIdx) => (
                <li
                  key={tipIdx}
                  className="text-xs text-muted-foreground flex items-start gap-2 animate-fade-in"
                  style={{ animationDelay: `${(catIdx * 0.1) + (tipIdx * 0.05)}s` }}
                >
                  <span className="text-primary mt-0.5">•</span>
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

