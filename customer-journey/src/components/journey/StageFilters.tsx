import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { X, Filter } from 'lucide-react'
import { Tooltip } from '../ui/tooltip'
import { cn } from '@/lib/utils'

export type StageFilter = 'all' | 'with-touchpoints' | 'with-triggers' | 'with-content' | 'empty'

interface StageFiltersProps {
  activeFilter: StageFilter
  onFilterChange: (filter: StageFilter) => void
  counts: {
    all: number
    withTouchpoints: number
    withTriggers: number
    withContent: number
    empty: number
  }
}

const filters: Array<{
  id: StageFilter
  label: string
  tooltip: string
}> = [
  { id: 'all', label: 'Todas', tooltip: 'Mostrar todas las etapas' },
  { id: 'with-touchpoints', label: 'Con Touchpoints', tooltip: 'Etapas con touchpoints definidos' },
  { id: 'with-triggers', label: 'Con Triggers', tooltip: 'Etapas con triggers de automatización' },
  { id: 'with-content', label: 'Con Contenido', tooltip: 'Etapas con necesidades de contenido' },
  { id: 'empty', label: 'Vacías', tooltip: 'Etapas sin contenido' },
]

export function StageFilters({ activeFilter, onFilterChange, counts }: StageFiltersProps) {
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <div className="flex items-center gap-2">
        <Filter className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm font-medium text-muted-foreground">Filtros:</span>
      </div>
      {filters.map((filter) => {
        const count = counts[filter.id]
        const isActive = activeFilter === filter.id

        return (
          <Tooltip key={filter.id} content={filter.tooltip}>
            <Button
              variant={isActive ? 'default' : 'outline'}
              size="sm"
              onClick={() => onFilterChange(filter.id)}
              className={cn(
                'relative',
                isActive && 'shadow-soft'
              )}
            >
              {filter.label}
              {count !== undefined && (
                <Badge
                  variant={isActive ? 'secondary' : 'outline'}
                  className={cn(
                    'ml-2 text-xs',
                    isActive && 'bg-primary/20 text-primary-foreground'
                  )}
                >
                  {count}
                </Badge>
              )}
            </Button>
          </Tooltip>
        )
      })}
      {activeFilter !== 'all' && (
        <Button
          variant="ghost"
          size="icon"
          onClick={() => onFilterChange('all')}
          className="h-8 w-8"
          aria-label="Limpiar filtros"
        >
          <X className="h-4 w-4" />
        </Button>
      )}
    </div>
  )
}

