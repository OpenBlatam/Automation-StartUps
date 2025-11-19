import { SearchInput } from '../ui/search-input'
import { Search } from 'lucide-react'
import { useRef, useEffect } from 'react'

interface StageSearchProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  resultsCount?: number
  totalCount?: number
}

export function StageSearch({
  value,
  onChange,
  placeholder = 'Buscar en etapas...',
  resultsCount,
  totalCount,
}: StageSearchProps) {
  const searchInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault()
        searchInputRef.current?.focus()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <div className="relative">
      <div className="relative max-w-md">
        <SearchInput
          ref={searchInputRef}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onClear={() => onChange('')}
          className="w-full"
        />
        {resultsCount !== undefined && totalCount !== undefined && value && (
          <div className="absolute right-12 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
            {resultsCount} / {totalCount}
          </div>
        )}
      </div>
      {value && (
        <div className="mt-2 text-xs text-muted-foreground flex items-center gap-1">
          <Search className="h-3 w-3" />
          <span>Buscando: "{value}"</span>
        </div>
      )}
    </div>
  )
}

