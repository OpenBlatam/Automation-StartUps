import { useState, useEffect } from 'react'
import { Button } from '../ui/button'
import { Textarea } from '../ui/textarea'
import { Badge } from '../ui/badge'
import { FileText } from 'lucide-react'
import { formatCommaSeparated, parseCommaSeparated } from '@/utils/data'

interface ContentNeedsEditorProps {
  contentNeeds: string[]
  onSave: (contentNeeds: string[]) => void
}

export function ContentNeedsEditor({ contentNeeds, onSave }: ContentNeedsEditorProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editingContent, setEditingContent] = useState(formatCommaSeparated(contentNeeds))

  useEffect(() => {
    if (!isEditing) {
      setEditingContent(formatCommaSeparated(contentNeeds))
    }
  }, [contentNeeds, isEditing])

  const handleSave = () => {
    onSave(parseCommaSeparated(editingContent))
    setIsEditing(false)
  }

  const handleCancel = () => {
    setEditingContent(formatCommaSeparated(contentNeeds))
    setIsEditing(false)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-semibold flex items-center gap-2">
          <FileText className="h-4 w-4 text-primary" />
          Necesidades de Contenido
        </h4>
        {!isEditing && (
          <Button variant="ghost" size="sm" onClick={() => setIsEditing(true)}>
            Editar
          </Button>
        )}
      </div>
      {isEditing ? (
        <div className="space-y-2">
          <Textarea
            value={editingContent}
            onChange={(e) => setEditingContent(e.target.value)}
            placeholder="Separar por comas: Blog post, Video tutorial, Case study..."
          />
          <div className="flex gap-2">
            <Button size="sm" onClick={handleSave}>
              Guardar
            </Button>
            <Button size="sm" variant="ghost" onClick={handleCancel}>
              Cancelar
            </Button>
          </div>
        </div>
      ) : (
            <div className="flex flex-wrap gap-2">
              {contentNeeds.length > 0 ? (
                contentNeeds.map((need, idx) => (
                  <Badge
                    key={idx}
                    variant="default"
                    className="cursor-default transition-smooth hover:scale-105"
                  >
                    {need}
                  </Badge>
                ))
              ) : (
                <span className="text-muted-foreground text-sm italic px-2">
                  No hay necesidades de contenido definidas
                </span>
              )}
            </div>
      )}
    </div>
  )
}

