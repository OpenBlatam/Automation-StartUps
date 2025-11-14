import { Button } from '../ui/button'
import { UserPlus } from 'lucide-react'

interface EmptyPersonaListProps {
  onAddPersona: () => void
}

export function EmptyPersonaList({ onAddPersona }: EmptyPersonaListProps) {
  return (
    <div className="text-center py-12 px-4 border border-dashed border-border rounded-lg bg-gradient-card animate-fade-in">
      <div className="flex flex-col items-center gap-4 max-w-md mx-auto">
        <div className="h-16 w-16 rounded-full bg-gradient-primary/20 flex items-center justify-center animate-float">
          <UserPlus className="h-8 w-8 text-primary" />
        </div>
        <div>
          <h3 className="text-lg font-semibold mb-2">No hay buyer personas</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Crea tu primer buyer persona para comenzar a mapear su customer journey
          </p>
          <Button onClick={onAddPersona} variant="default" className="animate-scale-in">
            <UserPlus className="h-4 w-4 mr-2" />
            Crear Primera Persona
          </Button>
        </div>
      </div>
    </div>
  )
}

