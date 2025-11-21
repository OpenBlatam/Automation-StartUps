import { JourneyStage } from '../JourneyStage'
import { EmptyState } from './EmptyState'
import { JourneyHeader } from './JourneyHeader'
import { JourneyProgress } from './JourneyProgress'
import type { BuyerPersona, CustomerJourney, JourneyStage as JourneyStageType } from '@/types/journey'

interface JourneyBuilderProps {
  persona: BuyerPersona | null
  journey: CustomerJourney | null
  onUpdateStage: (stage: JourneyStageType) => void
  onToast?: (title: string, description?: string) => void
}

export function JourneyBuilder({ persona, journey, onUpdateStage, onToast }: JourneyBuilderProps) {
  if (!persona || !journey) {
    return <EmptyState />
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <JourneyHeader persona={persona} />
      <JourneyProgress journey={journey} />

      <div className="space-y-6">
        {journey.stages.map((stage, index) => (
          <div
            key={stage.id}
            className="animate-slide-up"
            style={{ animationDelay: `${index * 0.1}s`, animationFillMode: 'both' }}
          >
            <JourneyStage stage={stage} onUpdateStage={onUpdateStage} onToast={onToast} />
          </div>
        ))}
      </div>
    </div>
  )
}

