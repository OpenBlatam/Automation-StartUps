export interface ScoringCriteria {
  id: string
  name: string
  type: 'behavior' | 'demographic'
  category: string
  points: number
  description?: string
}

export interface ScoreThreshold {
  id: string
  minScore: number
  maxScore: number
  label: string
  color: string
  automationRules: AutomationRule[]
}

export interface AutomationRule {
  id: string
  action: 'assign_to_team' | 'send_email' | 'create_task' | 'notify_sales' | 'add_to_campaign'
  parameters: Record<string, any>
  enabled: boolean
}

export interface LeadScore {
  leadId: string
  totalScore: number
  behaviorScore: number
  demographicScore: number
  criteriaBreakdown: {
    criteriaId: string
    points: number
  }[]
  threshold: string
  lastUpdated: Date
}




