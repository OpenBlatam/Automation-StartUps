import { useState, useCallback } from 'react'
import type { ToastProps } from '@/components/ui/toast'

export interface Toast extends Omit<ToastProps, 'onClose'> {
  id: string
}

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([])

  const toast = useCallback(
    (props: Omit<Toast, 'id'>) => {
      const id = `toast-${Date.now()}-${Math.random()}`
      const newToast: Toast = { ...props, id }
      setToasts((prev) => [...prev, newToast])

      setTimeout(() => {
        dismiss(id)
      }, 5000)
    },
    []
  )

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const success = useCallback(
    (title: string, description?: string) => {
      toast({ title, description, variant: 'success' })
    },
    [toast]
  )

  const error = useCallback(
    (title: string, description?: string) => {
      toast({ title, description, variant: 'error' })
    },
    [toast]
  )

  const info = useCallback(
    (title: string, description?: string) => {
      toast({ title, description, variant: 'info' })
    },
    [toast]
  )

  return {
    toasts,
    toast,
    dismiss,
    success,
    error,
    info,
  }
}




