const STORAGE_KEYS = {
  PERSONAS: 'customer-journey-personas',
  JOURNEYS: 'customer-journey-journeys',
  SELECTED_PERSONA: 'customer-journey-selected-persona',
} as const

export function saveToStorage<T>(key: string, data: T): void {
  try {
    localStorage.setItem(key, JSON.stringify(data))
  } catch (error) {
    console.warn('Failed to save to localStorage:', error)
  }
}

export function loadFromStorage<T>(key: string, defaultValue: T): T {
  try {
    const item = localStorage.getItem(key)
    if (item) {
      return JSON.parse(item) as T
    }
  } catch (error) {
    console.warn('Failed to load from localStorage:', error)
  }
  return defaultValue
}

export function clearStorage(key: string): void {
  try {
    localStorage.removeItem(key)
  } catch (error) {
    console.warn('Failed to clear localStorage:', error)
  }
}

export const storage = {
  savePersonas: (personas: unknown) => saveToStorage(STORAGE_KEYS.PERSONAS, personas),
  loadPersonas: <T>(defaultValue: T): T => loadFromStorage(STORAGE_KEYS.PERSONAS, defaultValue),
  
  saveJourneys: (journeys: unknown) => saveToStorage(STORAGE_KEYS.JOURNEYS, journeys),
  loadJourneys: <T>(defaultValue: T): T => loadFromStorage(STORAGE_KEYS.JOURNEYS, defaultValue),
  
  saveSelectedPersona: (personaId: string | null) => 
    saveToStorage(STORAGE_KEYS.SELECTED_PERSONA, personaId),
  loadSelectedPersona: (): string | null => 
    loadFromStorage(STORAGE_KEYS.SELECTED_PERSONA, null),
}



