import { Card, CardContent, CardDescription, CardTitle } from '../ui/card'
import { Map } from 'lucide-react'

export function EmptyState() {
  return (
    <Card className="border-dashed bg-gradient-card animate-fade-in">
      <CardContent className="p-12 text-center">
        <div className="h-16 w-16 mx-auto mb-6 rounded-full bg-gradient-primary/20 flex items-center justify-center animate-float">
          <Map className="h-8 w-8 text-primary" />
        </div>
        <CardTitle className="mb-3 text-xl">Selecciona un Buyer Persona</CardTitle>
        <CardDescription className="text-base">
          Elige o crea un buyer persona para comenzar a mapear su customer journey
        </CardDescription>
      </CardContent>
    </Card>
  )
}

