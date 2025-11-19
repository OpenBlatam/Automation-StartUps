import { useState, useCallback } from 'react'

export function useClipboard<T>() {
  const [copiedItem, setCopiedItem] = useState<T | null>(null)

  const copy = useCallback((item: T) => {
    setCopiedItem(item)
    // Store in sessionStorage for persistence across components
    try {
      sessionStorage.setItem('clipboard', JSON.stringify(item))
    } catch (error) {
      console.warn('Failed to save to clipboard:', error)
    }
  }, [])

  const paste = useCallback((): T | null => {
    try {
      const item = sessionStorage.getItem('clipboard')
      if (item) {
        return JSON.parse(item) as T
      }
    } catch (error) {
      console.warn('Failed to read from clipboard:', error)
    }
    return copiedItem
  }, [copiedItem])

  const clear = useCallback(() => {
    setCopiedItem(null)
    try {
      sessionStorage.removeItem('clipboard')
    } catch (error) {
      console.warn('Failed to clear clipboard:', error)
    }
  }, [])

  return { copy, paste, clear, hasCopied: copiedItem !== null }
}









