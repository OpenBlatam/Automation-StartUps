import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Keyboard } from 'lucide-react'
import { Badge } from '../ui/badge'
import { Tooltip } from '../ui/tooltip'

const shortcuts = [
  {
    category: 'Navegación',
    items: [
      { keys: ['Ctrl', 'K'], description: 'Buscar personas' },
      { keys: ['Ctrl', 'V'], description: 'Cambiar vista' },
      { keys: ['Ctrl', 'F'], description: 'Buscar en etapas' },
      { keys: ['Esc'], description: 'Cerrar modales' },
    ],
  },
  {
    category: 'Acciones',
    items: [
      { keys: ['Ctrl', 'E'], description: 'Exportar journey' },
      { keys: ['Ctrl', 'N'], description: 'Nueva persona' },
      { keys: ['Ctrl', 'C'], description: 'Copiar elemento' },
      { keys: ['Ctrl', 'V'], description: 'Pegar elemento' },
    ],
  },
  {
    category: 'Edición',
    items: [
      { keys: ['Enter'], description: 'Guardar formulario' },
      { keys: ['Esc'], description: 'Cancelar edición' },
    ],
  },
]

export function JourneyShortcuts() {
  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Keyboard className="h-5 w-5 text-primary" />
          Atajos de Teclado
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {shortcuts.map((category, catIdx) => (
          <div key={catIdx} className="space-y-2">
            <h4 className="text-sm font-semibold text-muted-foreground">
              {category.category}
            </h4>
            <div className="space-y-2">
              {category.items.map((item, itemIdx) => (
                <div
                  key={itemIdx}
                  className="flex items-center justify-between p-2 rounded-md hover:bg-card/50 transition-smooth"
                >
                  <span className="text-sm text-muted-foreground">
                    {item.description}
                  </span>
                  <div className="flex items-center gap-1">
                    {item.keys.map((key, keyIdx) => (
                      <div key={keyIdx} className="flex items-center gap-1">
                        <Badge
                          variant="outline"
                          className="text-xs font-mono px-2 py-0.5"
                        >
                          {key}
                        </Badge>
                        {keyIdx < item.keys.length - 1 && (
                          <span className="text-xs text-muted-foreground">+</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

