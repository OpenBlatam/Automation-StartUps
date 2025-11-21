export interface BuyerPersona {
  id: string
  name: string
  description: string
  demographics: string
  painPoints: string[]
  goals: string[]
  purchaseTimeframe: string
  channels: string[]
}

export interface Touchpoint {
  id: string
  name: string
  channel: string
  content: string
  timing: string
  order: number
}

export interface AutomationTrigger {
  id: string
  name: string
  type: 'event' | 'time' | 'behavior' | 'condition'
  condition: string
  action: string
  delay?: number
}

export interface JourneyStage {
  id: string
  name: string
  description: string
  order: number
  touchpoints: Touchpoint[]
  automationTriggers: AutomationTrigger[]
  contentNeeds: string[]
}

export interface CustomerJourney {
  id: string
  personaId: string
  persona: BuyerPersona
  stages: JourneyStage[]
  createdAt: string
  updatedAt: string
}










