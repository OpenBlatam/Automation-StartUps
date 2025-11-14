import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Keyboard, X } from 'lucide-react'

export function KeyboardShortcutsHelp() {
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault()
        setIsOpen((prev) => !prev)
      }
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen])

  if (!isOpen) {
    return (
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 z-40 shadow-soft hover:shadow-hover"
        aria-label="Mostrar atajos de teclado"
      >
        <Keyboard className="h-4 w-4" />
      </Button>
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm animate-fade-in">
      <Card className="w-full max-w-2xl mx-4 shadow-hover animate-scale-in">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-2xl gradient-text">Atajos de Teclado</CardTitle>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsOpen(false)}
            aria-label="Cerrar"
          >
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ShortcutItem
              keys={['Ctrl', 'K']}
              description="Buscar personas y etapas"
            />
            <ShortcutItem
              keys={['Ctrl', 'E']}
              description="Exportar journey"
            />
            <ShortcutItem
              keys={['Ctrl', 'N']}
              description="Nueva persona"
            />
            <ShortcutItem
              keys={['Ctrl', 'V']}
              description="Alternar vista"
            />
            <ShortcutItem
              keys={['Ctrl', '/']}
              description="Mostrar/ocultar ayuda"
            />
            <ShortcutItem
              keys={['Esc']}
              description="Cerrar modales"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function ShortcutItem({ keys, description }: { keys: string[]; description: string }) {
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0
  const displayKeys = keys.map((key) => (key === 'Ctrl' && isMac ? '⌘' : key))

  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-smooth">
      <span className="text-sm text-muted-foreground">{description}</span>
      <div className="flex items-center gap-1">
        {displayKeys.map((key, index) => (
          <React.Fragment key={index}>
            <kbd className="px-2 py-1 text-xs font-semibold text-foreground bg-card border border-border rounded shadow-soft">
              {key}
            </kbd>
            {index < displayKeys.length - 1 && (
              <span className="text-muted-foreground mx-1">+</span>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  )
}

