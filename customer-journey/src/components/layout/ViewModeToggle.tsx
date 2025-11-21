import { Button } from '../ui/button'

interface ViewModeToggleProps {
  viewMode: 'builder' | 'visualization'
  onViewModeChange: (mode: 'builder' | 'visualization') => void
}

export function ViewModeToggle({ viewMode, onViewModeChange }: ViewModeToggleProps) {
  return (
    <div className="flex items-center gap-2">
      <Button
        variant={viewMode === 'builder' ? 'default' : 'outline'}
        size="sm"
        onClick={() => onViewModeChange('builder')}
      >
        Constructor
      </Button>
      <Button
        variant={viewMode === 'visualization' ? 'default' : 'outline'}
        size="sm"
        onClick={() => onViewModeChange('visualization')}
      >
        Visualización
      </Button>
    </div>
  )
}










