import { useState, useEffect, useRef } from 'react'
import { IconButton } from '../ui/icon-button'
import { Copy, Trash2, MoreVertical } from 'lucide-react'
import { Card, CardContent } from '../ui/card'
import { Button } from '../ui/button'
import { ConfirmDialog } from '../ui/confirm-dialog'

interface PersonaActionsProps {
  onDuplicate: () => void
  onDelete: () => void
  personaName: string
}

export function PersonaActions({ onDuplicate, onDelete, personaName }: PersonaActionsProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false)
      }
    }

    if (isMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isMenuOpen])

  const handleDeleteClick = () => {
    setShowDeleteConfirm(true)
    setIsMenuOpen(false)
  }

  const handleConfirmDelete = () => {
    onDelete()
    setShowDeleteConfirm(false)
  }

  return (
    <div className="relative" ref={menuRef}>
      <IconButton
        icon={MoreVertical}
        variant="ghost"
        size="icon"
        onClick={() => setIsMenuOpen(!isMenuOpen)}
        aria-label="Opciones de persona"
        title="Más opciones"
      />

      {isMenuOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsMenuOpen(false)}
          />
          <Card className="absolute right-0 top-full mt-2 w-48 shadow-hover z-20 animate-scale-in">
            <CardContent className="p-2">
              <div className="space-y-1">
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => {
                    onDuplicate()
                    setIsMenuOpen(false)
                  }}
                >
                  <Copy className="h-4 w-4 mr-2" />
                  Duplicar
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start text-destructive hover:text-destructive hover:bg-destructive/10"
                  onClick={handleDeleteClick}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Eliminar
                </Button>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Eliminar Persona"
        message={`¿Estás seguro de que quieres eliminar "${personaName}"? Esta acción no se puede deshacer.`}
        confirmText="Eliminar"
        cancelText="Cancelar"
        variant="destructive"
        onConfirm={handleConfirmDelete}
        onCancel={() => setShowDeleteConfirm(false)}
      />
    </div>
  )
}

