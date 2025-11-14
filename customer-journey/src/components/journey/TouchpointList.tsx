import { Button } from '../ui/button'
import { MessageSquare, Plus } from 'lucide-react'
import { TouchpointItem } from './TouchpointItem'
import { EmptyListState } from './EmptyListState'
import type { Touchpoint } from '@/types/journey'

interface TouchpointListProps {
  touchpoints: Touchpoint[]
  onAdd: () => void
  onUpdate: (id: string, updates: Partial<Touchpoint>) => void
  onRemove: (id: string) => void
  onCopy?: (id: string) => void
  onPaste?: () => void
}

export function TouchpointList({
  touchpoints,
  onAdd,
  onUpdate,
  onRemove,
  onCopy,
  onPaste,
}: TouchpointListProps) {
  const hasCopied = typeof window !== 'undefined' && sessionStorage.getItem('copied-touchpoint') !== null

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h4 className="font-semibold flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-primary" />
          Touchpoints ({touchpoints.length})
        </h4>
        <div className="flex items-center gap-2">
          {onPaste && hasCopied && (
            <Button onClick={onPaste} variant="outline" size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Pegar
            </Button>
          )}
          <Button onClick={onAdd} variant="outline" size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Agregar Touchpoint
          </Button>
        </div>
      </div>
      {touchpoints.length === 0 ? (
        <EmptyListState
          icon={MessageSquare}
          title="No hay touchpoints"
          description="Agrega touchpoints para definir los puntos de contacto con el cliente"
          actionLabel="Agregar primer touchpoint"
          onAction={onAdd}
        />
      ) : (
        <div className="space-y-3">
          {touchpoints.map((touchpoint) => (
            <TouchpointItem
              key={touchpoint.id}
              touchpoint={touchpoint}
              onUpdate={(updates) => onUpdate(touchpoint.id, updates)}
              onRemove={() => onRemove(touchpoint.id)}
              onCopy={onCopy ? () => onCopy(touchpoint.id) : undefined}
            />
          ))}
        </div>
      )}
    </div>
  )
}

