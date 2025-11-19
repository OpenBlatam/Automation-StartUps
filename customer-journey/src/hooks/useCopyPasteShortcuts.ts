import { useEffect } from 'react'

interface UseCopyPasteShortcutsProps {
  onCopy?: () => void
  onPaste?: () => void
  enabled?: boolean
}

export function useCopyPasteShortcuts({
  onCopy,
  onPaste,
  enabled = true,
}: UseCopyPasteShortcutsProps) {
  useEffect(() => {
    if (!enabled) return

    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + C for copy
      if ((e.ctrlKey || e.metaKey) && e.key === 'c' && !e.shiftKey) {
        // Only trigger if not in an input/textarea
        const target = e.target as HTMLElement
        if (
          target.tagName !== 'INPUT' &&
          target.tagName !== 'TEXTAREA' &&
          !target.isContentEditable
        ) {
          e.preventDefault()
          onCopy?.()
        }
      }

      // Ctrl/Cmd + V for paste
      if ((e.ctrlKey || e.metaKey) && e.key === 'v' && !e.shiftKey) {
        // Only trigger if not in an input/textarea
        const target = e.target as HTMLElement
        if (
          target.tagName !== 'INPUT' &&
          target.tagName !== 'TEXTAREA' &&
          !target.isContentEditable
        ) {
          e.preventDefault()
          onPaste?.()
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onCopy, onPaste, enabled])
}

