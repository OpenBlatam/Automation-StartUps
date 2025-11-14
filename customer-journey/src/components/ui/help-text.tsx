import { HelpCircle } from 'lucide-react'
import { Tooltip } from './tooltip'
import { cn } from '@/lib/utils'

interface HelpTextProps {
  text: string
  className?: string
  side?: 'top' | 'bottom' | 'left' | 'right'
}

export function HelpText({ text, className, side = 'top' }: HelpTextProps) {
  return (
    <Tooltip content={text} side={side}>
      <HelpCircle className={cn('h-3.5 w-3.5 text-muted-foreground cursor-help hover:text-primary transition-smooth', className)} />
    </Tooltip>
  )
}

