import { Card, CardContent, CardFooter, CardHeader, CardTitle } from './card'
import { Button } from './button'
import { AlertTriangle } from 'lucide-react'

interface ConfirmDialogProps {
  isOpen: boolean
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  onConfirm: () => void
  onCancel: () => void
  variant?: 'default' | 'destructive'
}

export function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  onConfirm,
  onCancel,
  variant = 'default',
}: ConfirmDialogProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm animate-fade-in">
      <Card className="w-full max-w-md mx-4 shadow-hover animate-scale-in">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-full ${
              variant === 'destructive' ? 'bg-destructive/10' : 'bg-primary/10'
            }`}>
              <AlertTriangle className={`h-5 w-5 ${
                variant === 'destructive' ? 'text-destructive' : 'text-primary'
              }`} />
            </div>
            <CardTitle>{title}</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">{message}</p>
        </CardContent>
        <CardFooter className="flex justify-end gap-2">
          <Button variant="outline" onClick={onCancel}>
            {cancelText}
          </Button>
          <Button
            variant={variant === 'destructive' ? 'destructive' : 'default'}
            onClick={onConfirm}
          >
            {confirmText}
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}









