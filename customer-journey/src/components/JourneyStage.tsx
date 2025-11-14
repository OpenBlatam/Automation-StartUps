import { ContentNeedsEditor } from './journey/ContentNeedsEditor'
import { TouchpointList } from './journey/TouchpointList'
import { AutomationTriggerList } from './journey/AutomationTriggerList'
import { StageCard } from './journey/StageCard'
import { useStageActions } from '@/hooks/useStageActions'
import type { JourneyStage as JourneyStageType } from '@/types/journey'

interface JourneyStageProps {
  stage: JourneyStageType
  onUpdateStage: (stage: JourneyStageType) => void
}

export function JourneyStage({ stage, onUpdateStage }: JourneyStageProps) {
  const {
    addTouchpoint,
    updateTouchpoint,
    removeTouchpoint,
    copyTouchpoint,
    pasteTouchpoint,
    addTrigger,
    updateTrigger,
    removeTrigger,
    copyTrigger,
    pasteTrigger,
    updateContentNeeds,
  } = useStageActions({ stage, onUpdateStage })

  return (
    <StageCard stage={stage}>
      <ContentNeedsEditor
        contentNeeds={stage.contentNeeds}
        onSave={updateContentNeeds}
      />
      <TouchpointList
        touchpoints={stage.touchpoints}
        onAdd={addTouchpoint}
        onUpdate={updateTouchpoint}
        onRemove={removeTouchpoint}
        onCopy={copyTouchpoint}
        onPaste={pasteTouchpoint}
      />
      <AutomationTriggerList
        triggers={stage.automationTriggers}
        onAdd={addTrigger}
        onUpdate={updateTrigger}
        onRemove={removeTrigger}
        onCopy={copyTrigger}
        onPaste={pasteTrigger}
      />
    </StageCard>
  )
}

