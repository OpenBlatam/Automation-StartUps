import { useState, useEffect } from 'react'
import type { CustomerJourney, JourneyStage, BuyerPersona } from '@/types/journey'
import { DEFAULT_STAGES } from '@/constants/journey'
import { generateId } from '@/utils/data'
import { storage } from '@/utils/storage'

export function useJourney() {
  const [journey, setJourney] = useState<CustomerJourney | null>(() => {
    const saved = storage.loadJourneys<CustomerJourney | null>(null)
    return saved
  })

  useEffect(() => {
    if (journey) {
      storage.saveJourneys(journey)
    }
  }, [journey])

  const createJourney = (persona: BuyerPersona) => {
    const newJourney: CustomerJourney = {
      id: generateId('journey'),
      personaId: persona.id,
      persona,
      stages: DEFAULT_STAGES.map((stage, idx) => ({
        ...stage,
        id: generateId('stage'),
        order: idx + 1,
      })),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    setJourney(newJourney)
    return newJourney
  }

  const updateStage = (updatedStage: JourneyStage) => {
    if (!journey) return
    setJourney({
      ...journey,
      stages: journey.stages.map((s) =>
        s.id === updatedStage.id ? updatedStage : s
      ),
      updatedAt: new Date().toISOString(),
    })
  }

  const getJourneyForPersona = (personaId: string): CustomerJourney | null => {
    if (journey && journey.personaId === personaId) {
      return journey
    }
    return null
  }

  const deleteJourney = (personaId: string) => {
    if (journey && journey.personaId === personaId) {
      setJourney(null)
    }
  }

  return {
    journey,
    createJourney,
    updateStage,
    getJourneyForPersona,
    deleteJourney,
    setJourney,
  }
}

