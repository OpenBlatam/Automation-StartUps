import { Button } from '../ui/button'
import { Select } from '../ui/select'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { Tooltip } from '../ui/tooltip'

export type SortOption = 'name-asc' | 'name-desc' | 'recent' | 'oldest'

interface PersonaSortOptionsProps {
  sortBy: SortOption
  onSortChange: (sort: SortOption) => void
}

export function PersonaSortOptions({ sortBy, onSortChange }: PersonaSortOptionsProps) {
  return (
    <div className="flex items-center gap-2">
      <Tooltip content="Ordenar personas">
        <ArrowUpDown className="h-4 w-4 text-muted-foreground" />
      </Tooltip>
      <Select
        value={sortBy}
        onChange={(e) => onSortChange(e.target.value as SortOption)}
        className="w-auto min-w-[140px]"
      >
        <option value="name-asc">Nombre A-Z</option>
        <option value="name-desc">Nombre Z-A</option>
        <option value="recent">Más recientes</option>
        <option value="oldest">Más antiguas</option>
      </Select>
    </div>
  )
}

