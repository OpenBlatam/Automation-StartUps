import { Button } from '../ui/button'
import { Zap, Plus, Clipboard } from 'lucide-react'
import { AutomationTriggerItem } from './AutomationTriggerItem'
import { EmptyListState } from './EmptyListState'
import { Tooltip } from '../ui/tooltip'
import type { AutomationTrigger } from '@/types/journey'

interface AutomationTriggerListProps {
  triggers: AutomationTrigger[]
  onAdd: () => void
  onUpdate: (id: string, updates: Partial<AutomationTrigger>) => void
  onRemove: (id: string) => void
  onCopy?: (id: string) => void
  onPaste?: () => void
}

export function AutomationTriggerList({
  triggers,
  onAdd,
  onUpdate,
  onRemove,
  onCopy,
  onPaste,
}: AutomationTriggerListProps) {
  const hasCopied = typeof window !== 'undefined' && sessionStorage.getItem('copied-trigger') !== null

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h4 className="font-semibold flex items-center gap-2">
          <Zap className="h-4 w-4 text-primary" />
          Triggers de Automatización ({triggers.length})
        </h4>
        <div className="flex items-center gap-2">
          {onPaste && hasCopied && (
            <Tooltip content="Pegar trigger copiado">
              <Button onClick={onPaste} variant="outline" size="sm">
                <Clipboard className="h-4 w-4 mr-2" />
                Pegar
              </Button>
            </Tooltip>
          )}
          <Button onClick={onAdd} variant="outline" size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Agregar Trigger
          </Button>
        </div>
      </div>
      {triggers.length === 0 ? (
        <EmptyListState
          icon={Zap}
          title="No hay triggers de automatización"
          description="Agrega triggers para automatizar acciones en esta etapa"
          actionLabel="Agregar primer trigger"
          onAction={onAdd}
        />
      ) : (
        <div className="space-y-3">
          {triggers.map((trigger) => (
            <AutomationTriggerItem
              key={trigger.id}
              trigger={trigger}
              onUpdate={(updates) => onUpdate(trigger.id, updates)}
              onRemove={() => onRemove(trigger.id)}
              onCopy={onCopy ? () => onCopy(trigger.id) : undefined}
            />
          ))}
        </div>
      )}
    </div>
  )
}

