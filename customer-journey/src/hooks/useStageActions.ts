import { useCallback } from 'react'
import type { JourneyStage, Touchpoint, AutomationTrigger } from '@/types/journey'
import { generateId } from '@/utils/data'

interface UseStageActionsProps {
  stage: JourneyStage
  onUpdateStage: (stage: JourneyStage) => void
}

export function useStageActions({ stage, onUpdateStage }: UseStageActionsProps) {
  const addTouchpoint = useCallback(() => {
    const newTouchpoint: Touchpoint = {
      id: generateId('touchpoint'),
      name: '',
      channel: '',
      content: '',
      timing: '',
      order: stage.touchpoints.length,
    }
    onUpdateStage({
      ...stage,
      touchpoints: [...stage.touchpoints, newTouchpoint],
    })
  }, [stage, onUpdateStage])

  const updateTouchpoint = useCallback(
    (id: string, updates: Partial<Touchpoint>) => {
      onUpdateStage({
        ...stage,
        touchpoints: stage.touchpoints.map((tp) =>
          tp.id === id ? { ...tp, ...updates } : tp
        ),
      })
    },
    [stage, onUpdateStage]
  )

  const removeTouchpoint = useCallback(
    (id: string) => {
      onUpdateStage({
        ...stage,
        touchpoints: stage.touchpoints.filter((tp) => tp.id !== id),
      })
    },
    [stage, onUpdateStage]
  )

  const addTrigger = useCallback(() => {
    const newTrigger: AutomationTrigger = {
      id: generateId('trigger'),
      name: '',
      type: 'event',
      condition: '',
      action: '',
    }
    onUpdateStage({
      ...stage,
      automationTriggers: [...stage.automationTriggers, newTrigger],
    })
  }, [stage, onUpdateStage])

  const updateTrigger = useCallback(
    (id: string, updates: Partial<AutomationTrigger>) => {
      onUpdateStage({
        ...stage,
        automationTriggers: stage.automationTriggers.map((trigger) =>
          trigger.id === id ? { ...trigger, ...updates } : trigger
        ),
      })
    },
    [stage, onUpdateStage]
  )

  const removeTrigger = useCallback(
    (id: string) => {
      onUpdateStage({
        ...stage,
        automationTriggers: stage.automationTriggers.filter((t) => t.id !== id),
      })
    },
    [stage, onUpdateStage]
  )

  const updateContentNeeds = useCallback(
    (contentNeeds: string[]) => {
      onUpdateStage({
        ...stage,
        contentNeeds,
      })
    },
    [stage, onUpdateStage]
  )

  const copyTouchpoint = useCallback(
    (id: string) => {
      const touchpoint = stage.touchpoints.find((tp) => tp.id === id)
      if (touchpoint) {
        try {
          sessionStorage.setItem('copied-touchpoint', JSON.stringify(touchpoint))
        } catch (error) {
          console.warn('Failed to copy touchpoint:', error)
        }
      }
    },
    [stage.touchpoints]
  )

  const pasteTouchpoint = useCallback(() => {
    try {
      const copied = sessionStorage.getItem('copied-touchpoint')
      if (copied) {
        const touchpoint: Touchpoint = JSON.parse(copied)
        const newTouchpoint: Touchpoint = {
          ...touchpoint,
          id: generateId('touchpoint'),
          name: `${touchpoint.name} (Copia)`,
          order: stage.touchpoints.length,
        }
        onUpdateStage({
          ...stage,
          touchpoints: [...stage.touchpoints, newTouchpoint],
        })
      }
    } catch (error) {
      console.warn('Failed to paste touchpoint:', error)
    }
  }, [stage, onUpdateStage])

  const copyTrigger = useCallback(
    (id: string) => {
      const trigger = stage.automationTriggers.find((t) => t.id === id)
      if (trigger) {
        try {
          sessionStorage.setItem('copied-trigger', JSON.stringify(trigger))
        } catch (error) {
          console.warn('Failed to copy trigger:', error)
        }
      }
    },
    [stage.automationTriggers]
  )

  const pasteTrigger = useCallback(() => {
    try {
      const copied = sessionStorage.getItem('copied-trigger')
      if (copied) {
        const trigger: AutomationTrigger = JSON.parse(copied)
        const newTrigger: AutomationTrigger = {
          ...trigger,
          id: generateId('trigger'),
          name: `${trigger.name} (Copia)`,
        }
        onUpdateStage({
          ...stage,
          automationTriggers: [...stage.automationTriggers, newTrigger],
        })
      }
    } catch (error) {
      console.warn('Failed to paste trigger:', error)
    }
  }, [stage, onUpdateStage])

  return {
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
  }
}




