import { useEffect } from 'react'

interface KeyboardShortcuts {
  onSearch?: () => void
  onExport?: () => void
  onNewPersona?: () => void
  onToggleView?: () => void
  onEscape?: () => void
}

export function useKeyboardShortcuts({
  onSearch,
  onExport,
  onNewPersona,
  onToggleView,
  onEscape,
}: KeyboardShortcuts) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + K for search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        onSearch?.()
      }

      // Ctrl/Cmd + E for export
      if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault()
        onExport?.()
      }

      // Ctrl/Cmd + N for new persona
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault()
        onNewPersona?.()
      }

      // Ctrl/Cmd + V for toggle view
      if ((e.ctrlKey || e.metaKey) && e.key === 'v') {
        e.preventDefault()
        onToggleView?.()
      }

      // Escape key
      if (e.key === 'Escape') {
        onEscape?.()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onSearch, onExport, onNewPersona, onToggleView, onEscape])
}









