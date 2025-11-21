import { Button } from '../ui/button'
import { Download } from 'lucide-react'
import type { CustomerJourney } from '@/types/journey'

interface ExportButtonProps {
  journey: CustomerJourney | null
  onExport: () => void
}

export function ExportButton({ journey, onExport }: ExportButtonProps) {
  if (!journey) return null

  return (
    <Button variant="outline" size="sm" onClick={onExport}>
      <Download className="h-4 w-4 mr-2" />
      Exportar
    </Button>
  )
}










