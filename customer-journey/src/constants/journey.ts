import type { JourneyStage } from '@/types/journey'

export const DEFAULT_STAGES: Omit<JourneyStage, 'id'>[] = [
  {
    name: 'Awareness',
    description: 'El cliente descubre tu marca o producto por primera vez',
    order: 1,
    touchpoints: [],
    automationTriggers: [],
    contentNeeds: [],
  },
  {
    name: 'Consideration',
    description: 'El cliente evalúa opciones y compara soluciones',
    order: 2,
    touchpoints: [],
    automationTriggers: [],
    contentNeeds: [],
  },
  {
    name: 'Decision',
    description: 'El cliente está listo para tomar una decisión de compra',
    order: 3,
    touchpoints: [],
    automationTriggers: [],
    contentNeeds: [],
  },
  {
    name: 'Purchase',
    description: 'El cliente completa la compra',
    order: 4,
    touchpoints: [],
    automationTriggers: [],
    contentNeeds: [],
  },
]

export const DEFAULT_PERSONA: Omit<import('@/types/journey').BuyerPersona, 'id'> = {
  name: 'Director de Marketing',
  description: 'Responsable de estrategias de marketing digital y generación de leads',
  demographics: '35-50 años, empresa mediana-grande, sector tecnológico',
  painPoints: ['Falta de tiempo', 'Presupuesto limitado', 'ROI difícil de medir'],
  goals: ['Aumentar leads', 'Mejorar conversión', 'Automatizar procesos'],
  purchaseTimeframe: '1-3 meses',
  channels: ['LinkedIn', 'Email', 'Web', 'Eventos'],
}

export const PURCHASE_TIMEFRAMES = [
  'Inmediato',
  '1-3 meses',
  '3-6 meses',
  '6-12 meses',
  '12+ meses',
] as const

export const TRIGGER_TYPES = ['event', 'time', 'behavior', 'condition'] as const










