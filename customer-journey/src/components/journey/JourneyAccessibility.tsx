import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Accessibility, Eye, MousePointerClick, Keyboard } from 'lucide-react'
import { Badge } from '../ui/badge'
import { Tooltip } from '../ui/tooltip'

const accessibilityFeatures = [
  {
    icon: Keyboard,
    title: 'Navegación por teclado',
    description: 'Todas las funciones son accesibles mediante atajos de teclado',
    status: 'Completo',
    color: 'text-primary',
  },
  {
    icon: Eye,
    title: 'Contraste y legibilidad',
    description: 'Colores y contrastes optimizados para mejor legibilidad',
    status: 'Completo',
    color: 'text-primary',
  },
  {
    icon: MousePointerClick,
    title: 'Áreas de toque',
    description: 'Botones y elementos interactivos con tamaño mínimo de 44x44px',
    status: 'Completo',
    color: 'text-primary',
  },
  {
    icon: Accessibility,
    title: 'ARIA labels',
    description: 'Etiquetas ARIA para lectores de pantalla',
    status: 'Completo',
    color: 'text-primary',
  },
]

export function JourneyAccessibility() {
  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Accessibility className="h-5 w-5 text-primary" />
          Accesibilidad
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {accessibilityFeatures.map((feature, index) => {
          const Icon = feature.icon
          return (
            <div
              key={index}
              className="flex items-start gap-3 p-3 rounded-lg border border-border bg-card/50 animate-fade-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className={`p-2 rounded-lg bg-primary/10`}>
                <Icon className={`h-4 w-4 ${feature.color}`} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="text-sm font-semibold">{feature.title}</h4>
                  <Badge variant="outline" className="text-xs">
                    {feature.status}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">{feature.description}</p>
              </div>
            </div>
          )
        })}
        <div className="pt-3 border-t border-border">
          <p className="text-xs text-muted-foreground">
            Esta aplicación sigue las mejores prácticas de accesibilidad web (WCAG 2.1)
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

