import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { User } from 'lucide-react'
import { PersonaInfo } from './PersonaInfo'
import { PersonaActions } from './PersonaActions'
import type { BuyerPersona } from '@/types/journey'

interface PersonaCardProps {
  persona: BuyerPersona
  isSelected: boolean
  onClick: () => void
  onDuplicate?: () => void
  onDelete?: () => void
}

export function PersonaCard({ persona, isSelected, onClick, onDuplicate, onDelete }: PersonaCardProps) {
  return (
    <Card
      className={`cursor-pointer transition-smooth hover-lift animate-scale-in shadow-soft focus-within:ring-2 focus-within:ring-primary/50 group ${
        isSelected
          ? 'border-primary shadow-glow bg-gradient-accent ring-2 ring-primary/20 scale-[1.02]'
          : 'hover:border-primary/50 hover:shadow-hover'
      }`}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onClick()
        }
      }}
      tabIndex={0}
      role="button"
      aria-label={`Seleccionar persona ${persona.name}`}
    >
      <CardHeader>
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <User className="h-5 w-5 text-primary shrink-0" />
            <CardTitle className="text-lg truncate">{persona.name}</CardTitle>
          </div>
          {(onDuplicate || onDelete) && (
            <div onClick={(e) => e.stopPropagation()}>
              <PersonaActions
                personaName={persona.name}
                onDuplicate={onDuplicate || (() => {})}
                onDelete={onDelete || (() => {})}
              />
            </div>
          )}
        </div>
        <CardDescription className="line-clamp-2">
          {persona.description}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <PersonaInfo persona={persona} />
      </CardContent>
    </Card>
  )
}

