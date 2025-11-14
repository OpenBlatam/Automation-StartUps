import { useState } from 'react'
import { IconButton } from '../ui/icon-button'
import { Copy, Clipboard, Check } from 'lucide-react'
import { Tooltip } from '../ui/tooltip'

interface CopyPasteActionsProps {
  onCopy: () => void
  onPaste?: () => void
  hasCopied?: boolean
  canPaste?: boolean
}

export function CopyPasteActions({ onCopy, onPaste, hasCopied, canPaste }: CopyPasteActionsProps) {
  const [showCopied, setShowCopied] = useState(false)

  const handleCopy = () => {
    onCopy()
    setShowCopied(true)
    setTimeout(() => setShowCopied(false), 2000)
  }

  return (
    <div className="flex items-center gap-1">
      <Tooltip content={showCopied ? 'Copiado!' : 'Copiar'}>
        <IconButton
          icon={showCopied ? Check : Copy}
          variant="ghost"
          size="icon"
          onClick={handleCopy}
          aria-label="Copiar"
          className={showCopied ? 'text-primary' : ''}
        />
      </Tooltip>
      {onPaste && canPaste && (
        <Tooltip content="Pegar">
          <IconButton
            icon={Clipboard}
            variant="ghost"
            size="icon"
            onClick={onPaste}
            aria-label="Pegar"
          />
        </Tooltip>
      )}
    </div>
  )
}



