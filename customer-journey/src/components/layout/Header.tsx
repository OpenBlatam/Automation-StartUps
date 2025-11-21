import { AppLogo } from './AppLogo'
import { ViewModeToggle } from './ViewModeToggle'
import { ExportMenu } from './ExportMenu'
import { AutoSaveIndicator } from '../ui/auto-save-indicator'
import type { CustomerJourney } from '@/types/journey'
import type { ExportFormat } from '@/hooks/useExport'

interface HeaderProps {
  viewMode: 'builder' | 'visualization'
  onViewModeChange: (mode: 'builder' | 'visualization') => void
  journey: CustomerJourney | null
  onExport: (format: ExportFormat) => void
}

export function Header({ viewMode, onViewModeChange, journey, onExport }: HeaderProps) {
  return (
    <header className="border-b border-border glass-effect sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between gap-4">
          <AppLogo />
          <div className="flex items-center gap-4 flex-shrink-0">
            {journey && (
              <AutoSaveIndicator
                lastSaved={journey.updatedAt ? new Date(journey.updatedAt) : undefined}
                className="hidden sm:flex"
              />
            )}
            <ViewModeToggle viewMode={viewMode} onViewModeChange={onViewModeChange} />
            <ExportMenu journey={journey} onExport={onExport} />
          </div>
        </div>
      </div>
    </header>
  )
}

