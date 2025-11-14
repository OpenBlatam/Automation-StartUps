interface StageConnectionLineProps {
  totalStages: number
}

export function StageConnectionLine({ totalStages }: StageConnectionLineProps) {
  return (
    <div className="absolute top-1/2 left-0 right-0 h-0.5 -translate-y-1/2 hidden md:block overflow-hidden">
      <div className="relative h-full">
        <div className="absolute inset-0 bg-gradient-primary opacity-20" />
        <div className="absolute inset-0 bg-gradient-primary opacity-30" />
        <div className="absolute inset-0 bg-gradient-primary opacity-40 animate-pulse" />
      </div>
    </div>
  )
}

