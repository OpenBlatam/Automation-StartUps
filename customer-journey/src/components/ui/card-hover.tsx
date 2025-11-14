import { cn } from '@/lib/utils'

interface CardHoverProps {
  children: React.ReactNode
  className?: string
}

export function CardHover({ children, className }: CardHoverProps) {
  return (
    <div
      className={cn(
        'group relative overflow-hidden rounded-lg transition-smooth',
        className
      )}
    >
      <div className="absolute inset-0 bg-gradient-primary opacity-0 transition-opacity duration-300 group-hover:opacity-5" />
      {children}
    </div>
  )
}




