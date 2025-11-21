import { FormField } from '../ui/form-field'
import { MessageSquare, Globe, Clock, FileText } from 'lucide-react'
import type { Touchpoint } from '@/types/journey'

interface TouchpointFormFieldsProps {
  touchpoint: Touchpoint
  onUpdate: (updates: Partial<Touchpoint>) => void
}

export function TouchpointFormFields({
  touchpoint,
  onUpdate,
}: TouchpointFormFieldsProps) {
  return (
    <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-3">
      <FormField
        id={`touchpoint-name-${touchpoint.id}`}
        label="Nombre"
        value={touchpoint.name}
        onChange={(value) => onUpdate({ name: value })}
        placeholder="Nombre del touchpoint"
        icon={MessageSquare}
      />
      <FormField
        id={`touchpoint-channel-${touchpoint.id}`}
        label="Canal"
        value={touchpoint.channel}
        onChange={(value) => onUpdate({ channel: value })}
        placeholder="Email, LinkedIn, Web..."
        icon={Globe}
      />
      <FormField
        id={`touchpoint-timing-${touchpoint.id}`}
        label="Timing"
        value={touchpoint.timing}
        onChange={(value) => onUpdate({ timing: value })}
        placeholder="Día 1, Semana 2..."
        icon={Clock}
      />
      <div className="md:col-span-2">
        <FormField
          id={`touchpoint-content-${touchpoint.id}`}
          label="Contenido"
          value={touchpoint.content}
          onChange={(value) => onUpdate({ content: value })}
          placeholder="Contenido del mensaje..."
          type="textarea"
          icon={FileText}
        />
      </div>
    </div>
  )
}










