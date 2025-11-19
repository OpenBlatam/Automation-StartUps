import { HelpCircle } from 'lucide-react'
import { Tooltip } from './tooltip'
import { cn } from '@/lib/utils'

interface HelpTextProps {
  text: string
  className?: string
}

export function HelpText({ text, className }: HelpTextProps) {
  return (
    <Tooltip content={text} side="right">
      <HelpCircle className={cn('h-3.5 w-3.5 text-muted-foreground cursor-help', className)} />
    </Tooltip>
  )
}
