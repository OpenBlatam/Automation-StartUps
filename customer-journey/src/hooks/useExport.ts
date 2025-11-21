import type { CustomerJourney } from '@/types/journey'

export type ExportFormat = 'json' | 'csv'

export function useExport() {
  const exportJourney = (journey: CustomerJourney, format: ExportFormat = 'json') => {
    const baseName = `customer-journey-${journey.persona.name.replace(/\s+/g, '-')}-${Date.now()}`

    if (format === 'json') {
      const dataStr = JSON.stringify(journey, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      downloadFile(dataBlob, `${baseName}.json`)
    } else if (format === 'csv') {
      const csv = generateCSV(journey)
      const dataBlob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      downloadFile(dataBlob, `${baseName}.csv`)
    }
  }

  const downloadFile = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const generateCSV = (journey: CustomerJourney): string => {
    const rows: string[] = []
    
    // Header
    rows.push('Etapa,Orden,Nombre,Descripción,Touchpoints,Triggers,Content Needs')
    
    // Stages data
    journey.stages.forEach((stage) => {
      const touchpoints = stage.touchpoints.map(t => t.name).join('; ')
      const triggers = stage.automationTriggers.map(t => t.name).join('; ')
      const contentNeeds = stage.contentNeeds.join('; ')
      
      rows.push(
        `"${stage.name}",${stage.order},"${stage.name}","${stage.description}","${touchpoints}","${triggers}","${contentNeeds}"`
      )
    })
    
    return rows.join('\n')
  }

  return { exportJourney }
}


