import { Map } from 'lucide-react'

export function AppLogo() {
  return (
    <div className="flex items-center gap-3">
      <div className="h-10 w-10 rounded-lg bg-gradient-primary flex items-center justify-center">
        <Map className="h-6 w-6 text-primary-foreground" />
      </div>
      <div>
        <h1 className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
          Customer Journey Mapper
        </h1>
        <p className="text-sm text-muted-foreground">
          Mapea el viaje completo del cliente desde el primer contacto hasta la compra
        </p>
      </div>
    </div>
  )
}










