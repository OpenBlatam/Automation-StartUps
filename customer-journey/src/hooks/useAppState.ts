import { useState, useCallback, useMemo } from 'react'
import { usePersonas } from './usePersonas'
import { useJourney } from './useJourney'
import { useExport } from './useExport'
import { useToast } from './useToast'
import { storage } from '@/utils/storage'
import type { JourneyStage } from '@/types/journey'

export function useAppState() {
  const [selectedPersonaId, setSelectedPersonaId] = useState<string | null>(() => {
    return storage.loadSelectedPersona()
  })
  const [viewMode, setViewMode] = useState<'builder' | 'visualization'>('builder')

  const { personas, addPersona, duplicatePersona, deletePersona, getPersonaById } = usePersonas()
  const { journey, createJourney, updateStage, getJourneyForPersona, deleteJourney } = useJourney()
  const { exportJourney } = useExport()
  const { toasts, dismiss, success } = useToast()

  const selectedPersona = useMemo(
    () => (selectedPersonaId ? getPersonaById(selectedPersonaId) : null),
    [selectedPersonaId, getPersonaById]
  )

  const handleSelectPersona = useCallback(
    (personaId: string) => {
      setSelectedPersonaId(personaId)
      storage.saveSelectedPersona(personaId)
      const persona = getPersonaById(personaId)
      if (persona) {
        const existingJourney = getJourneyForPersona(personaId)
        if (!existingJourney) {
          createJourney(persona)
        }
      }
    },
    [getPersonaById, getJourneyForPersona, createJourney]
  )

  const handleAddPersona = useCallback(
    (personaData: Parameters<typeof addPersona>[0]) => {
      const newPersona = addPersona(personaData)
      handleSelectPersona(newPersona.id)
      success('Persona creada', `${newPersona.name} ha sido agregado exitosamente`)
    },
    [addPersona, handleSelectPersona, success]
  )

  const handleUpdateStage = useCallback(
    (updatedStage: JourneyStage) => {
      updateStage(updatedStage)
    },
    [updateStage]
  )

  const handleExport = useCallback((format: 'json' | 'csv' = 'json') => {
    if (journey) {
      exportJourney(journey, format)
      success(
        'Journey exportado',
        `El archivo ${format.toUpperCase()} se ha descargado correctamente`
      )
    }
  }, [journey, exportJourney, success])

  const handleDuplicatePersona = useCallback(
    (personaId: string) => {
      const duplicated = duplicatePersona(personaId)
      if (duplicated) {
        handleSelectPersona(duplicated.id)
        success('Persona duplicada', `${duplicated.name} ha sido creada exitosamente`)
      }
    },
    [duplicatePersona, handleSelectPersona, success]
  )

  const handleDeletePersona = useCallback(
    (personaId: string) => {
      deletePersona(personaId)
      deleteJourney(personaId)
      if (selectedPersonaId === personaId) {
        setSelectedPersonaId(null)
      }
      success('Persona eliminada', 'La persona ha sido eliminada exitosamente')
    },
    [deletePersona, deleteJourney, selectedPersonaId]
  )

  return {
    // State
    selectedPersonaId,
    viewMode,
    personas,
    journey,
    selectedPersona,
    toasts,
    // Actions
    setViewMode,
    handleSelectPersona,
    handleAddPersona,
    handleUpdateStage,
    handleExport,
    handleDuplicatePersona,
    handleDeletePersona,
    dismiss,
  }
}


