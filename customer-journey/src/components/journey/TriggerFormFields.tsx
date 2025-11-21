import { FormField } from '../ui/form-field'
import { Zap, Settings, Play, AlertCircle } from 'lucide-react'
import { TRIGGER_TYPES } from '@/constants/journey'
import type { AutomationTrigger } from '@/types/journey'

interface TriggerFormFieldsProps {
  trigger: AutomationTrigger
  onUpdate: (updates: Partial<AutomationTrigger>) => void
}

const triggerTypeOptions = TRIGGER_TYPES.map((type) => ({
  value: type,
  label:
    type === 'event'
      ? 'Evento'
      : type === 'time'
      ? 'Tiempo'
      : type === 'behavior'
      ? 'Comportamiento'
      : 'Condición',
}))

export function TriggerFormFields({ trigger, onUpdate }: TriggerFormFieldsProps) {
  return (
    <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-3">
      <FormField
        id={`trigger-name-${trigger.id}`}
        label="Nombre"
        value={trigger.name}
        onChange={(value) => onUpdate({ name: value })}
        placeholder="Nombre del trigger"
        icon={Zap}
      />
      <FormField
        id={`trigger-type-${trigger.id}`}
        label="Tipo"
        value={trigger.type}
        onChange={(value) =>
          onUpdate({
            type: value as AutomationTrigger['type'],
          })
        }
        type="select"
        options={triggerTypeOptions}
        icon={Settings}
      />
      <FormField
        id={`trigger-condition-${trigger.id}`}
        label="Condición"
        value={trigger.condition}
        onChange={(value) => onUpdate({ condition: value })}
        placeholder="Condición"
        icon={AlertCircle}
      />
      <FormField
        id={`trigger-action-${trigger.id}`}
        label="Acción"
        value={trigger.action}
        onChange={(value) => onUpdate({ action: value })}
        placeholder="Acción a ejecutar"
        icon={Play}
      />
    </div>
  )
}










