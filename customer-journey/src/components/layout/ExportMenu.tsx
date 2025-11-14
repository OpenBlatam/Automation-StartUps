import { useState, useRef, useEffect } from 'react'
import { Button } from '../ui/button'
import { Download, FileJson, FileSpreadsheet, ChevronDown } from 'lucide-react'
import { Card, CardContent } from '../ui/card'
import { cn } from '@/lib/utils'
import type { CustomerJourney } from '@/types/journey'
import type { ExportFormat } from '@/hooks/useExport'

interface ExportMenuProps {
  journey: CustomerJourney | null
  onExport: (format: ExportFormat) => void
}

export function ExportMenu({ journey, onExport }: ExportMenuProps) {
  const [isOpen, setIsOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false)
      }
    }

    window.addEventListener('keydown', handleEscape)
    return () => window.removeEventListener('keydown', handleEscape)
  }, [isOpen])

  if (!journey) return null

  return (
    <div className="relative" ref={menuRef}>
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="animate-slide-in-right"
      >
        <Download className="h-4 w-4 mr-2" />
        Exportar
        <ChevronDown className={cn('h-4 w-4 ml-2 transition-smooth', isOpen && 'rotate-180')} />
      </Button>

      {isOpen && (
        <Card className="absolute right-0 top-full mt-2 w-48 shadow-hover z-50 animate-scale-in">
          <CardContent className="p-2">
            <div className="space-y-1">
              <button
                onClick={() => {
                  onExport('json')
                  setIsOpen(false)
                }}
                className="w-full flex items-center gap-2 px-3 py-2 rounded-md hover:bg-accent transition-smooth text-left"
              >
                <FileJson className="h-4 w-4 text-primary" />
                <span className="text-sm">Exportar JSON</span>
              </button>
              <button
                onClick={() => {
                  onExport('csv')
                  setIsOpen(false)
                }}
                className="w-full flex items-center gap-2 px-3 py-2 rounded-md hover:bg-accent transition-smooth text-left"
              >
                <FileSpreadsheet className="h-4 w-4 text-primary" />
                <span className="text-sm">Exportar CSV</span>
              </button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}



