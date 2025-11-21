import { useState, useRef, useEffect } from 'react'
import { Button } from './ui/button'
import { Plus } from 'lucide-react'
import { PersonaForm } from './persona/PersonaForm'
import { PersonaList } from './persona/PersonaList'
import { SearchInput } from './ui/search-input'
import type { BuyerPersona } from '@/types/journey'
import type { SortOption } from './persona/PersonaSortOptions'

interface BuyerPersonaSelectorProps {
  personas: BuyerPersona[]
  selectedPersonaId: string | null
  onSelectPersona: (personaId: string) => void
  onAddPersona: (persona: Omit<BuyerPersona, 'id'>) => void
  onDuplicatePersona?: (personaId: string) => void
  onDeletePersona?: (personaId: string) => void
}

export function BuyerPersonaSelector({
  personas,
  selectedPersonaId,
  onSelectPersona,
  onAddPersona,
  onDuplicatePersona,
  onDeletePersona,
}: BuyerPersonaSelectorProps) {
  const [isAdding, setIsAdding] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<SortOption>('name-asc')
  const searchInputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = (persona: Omit<BuyerPersona, 'id'>) => {
    onAddPersona(persona)
    setIsAdding(false)
  }

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        searchInputRef.current?.focus()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between pb-4 border-b border-border">
        <h2 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
          Buyer Persona
        </h2>
        {!isAdding && (
          <Button onClick={() => setIsAdding(true)} variant="outline" size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Nueva Persona
          </Button>
        )}
      </div>

      {!isAdding && personas.length > 0 && (
        <div className="max-w-md animate-slide-up">
          <SearchInput
            ref={searchInputRef}
            placeholder="Buscar personas... (Ctrl+K)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onClear={() => setSearchQuery('')}
          />
        </div>
      )}

      {isAdding && (
        <PersonaForm onSubmit={handleSubmit} onCancel={() => setIsAdding(false)} />
      )}

      <PersonaList
        personas={personas}
        selectedPersonaId={selectedPersonaId}
        onSelectPersona={onSelectPersona}
        onAddPersona={() => setIsAdding(true)}
        onDuplicatePersona={onDuplicatePersona}
        onDeletePersona={onDeletePersona}
        searchQuery={searchQuery}
        sortBy={sortBy}
        onSortChange={setSortBy}
      />
    </div>
  )
}

