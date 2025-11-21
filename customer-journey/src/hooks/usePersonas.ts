import { useState, useEffect } from 'react'
import type { BuyerPersona } from '@/types/journey'
import { DEFAULT_PERSONA } from '@/constants/journey'
import { generateId } from '@/utils/data'
import { storage } from '@/utils/storage'

export function usePersonas() {
  const [personas, setPersonas] = useState<BuyerPersona[]>(() => {
    const saved = storage.loadPersonas<BuyerPersona[]>([])
    return saved.length > 0 ? saved : [
      {
        ...DEFAULT_PERSONA,
        id: '1',
      },
    ]
  })

  useEffect(() => {
    storage.savePersonas(personas)
  }, [personas])

  const addPersona = (personaData: Omit<BuyerPersona, 'id'>) => {
    const newPersona: BuyerPersona = {
      ...personaData,
      id: generateId('persona'),
    }
    setPersonas((prev) => [...prev, newPersona])
    return newPersona
  }

  const duplicatePersona = (id: string) => {
    const persona = getPersonaById(id)
    if (!persona) return null

    const duplicated: BuyerPersona = {
      ...persona,
      id: generateId('persona'),
      name: `${persona.name} (Copia)`,
    }
    setPersonas((prev) => [...prev, duplicated])
    return duplicated
  }

  const deletePersona = (id: string) => {
    setPersonas((prev) => prev.filter((p) => p.id !== id))
  }

  const getPersonaById = (id: string) => {
    return personas.find((p) => p.id === id) ?? null
  }

  return {
    personas,
    addPersona,
    duplicatePersona,
    deletePersona,
    getPersonaById,
  }
}


