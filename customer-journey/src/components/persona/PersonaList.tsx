import { useMemo } from 'react'
import { PersonaCard } from './PersonaCard'
import { EmptyPersonaList } from './EmptyPersonaList'
import { PersonaSortOptions, type SortOption } from './PersonaSortOptions'
import type { BuyerPersona } from '@/types/journey'

interface PersonaListProps {
  personas: BuyerPersona[]
  selectedPersonaId: string | null
  onSelectPersona: (personaId: string) => void
  onAddPersona: () => void
  onDuplicatePersona?: (personaId: string) => void
  onDeletePersona?: (personaId: string) => void
  searchQuery?: string
  sortBy?: SortOption
  onSortChange?: (sort: SortOption) => void
}

export function PersonaList({
  personas,
  selectedPersonaId,
  onSelectPersona,
  onAddPersona,
  onDuplicatePersona,
  onDeletePersona,
  searchQuery = '',
  sortBy = 'name-asc',
  onSortChange,
}: PersonaListProps) {
  const filteredAndSortedPersonas = useMemo(() => {
    let filtered = personas
    
    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (persona) =>
          persona.name.toLowerCase().includes(query) ||
          persona.description.toLowerCase().includes(query) ||
          persona.demographics.toLowerCase().includes(query) ||
          persona.painPoints.some((p) => p.toLowerCase().includes(query)) ||
          persona.goals.some((g) => g.toLowerCase().includes(query))
      )
    }
    
    // Sort
    const sorted = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'name-asc':
          return a.name.localeCompare(b.name)
        case 'name-desc':
          return b.name.localeCompare(a.name)
        case 'recent':
          // Assuming personas have an id that can be used for recency
          return b.id.localeCompare(a.id)
        case 'oldest':
          return a.id.localeCompare(b.id)
        default:
          return 0
      }
    })
    
    return sorted
  }, [personas, searchQuery, sortBy])

  if (personas.length === 0) {
    return <EmptyPersonaList onAddPersona={onAddPersona} />
  }

  if (filteredAndSortedPersonas.length === 0 && searchQuery) {
    return (
      <div className="text-center py-12 animate-fade-in">
        <p className="text-muted-foreground">
          No se encontraron personas que coincidan con "{searchQuery}"
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {onSortChange && personas.length > 1 && (
        <div className="flex justify-end">
          <PersonaSortOptions sortBy={sortBy} onSortChange={onSortChange} />
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredAndSortedPersonas.map((persona) => (
          <PersonaCard
            key={persona.id}
            persona={persona}
            isSelected={selectedPersonaId === persona.id}
            onClick={() => onSelectPersona(persona.id)}
            onDuplicate={onDuplicatePersona ? () => onDuplicatePersona(persona.id) : undefined}
            onDelete={onDeletePersona ? () => onDeletePersona(persona.id) : undefined}
          />
        ))}
      </div>
    </div>
  )
}

