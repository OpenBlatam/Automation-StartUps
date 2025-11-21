import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { IconButton } from '../ui/icon-button'
import { X, UserPlus, AlertCircle } from 'lucide-react'
import { PersonaFormFields } from './PersonaFormFields'
import { parseCommaSeparated } from '@/utils/data'
import { validatePersonaForm } from '@/utils/validation'
import type { BuyerPersona } from '@/types/journey'

interface PersonaFormProps {
  onSubmit: (persona: Omit<BuyerPersona, 'id'>) => void
  onCancel: () => void
}

export function PersonaForm({ onSubmit, onCancel }: PersonaFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    demographics: '',
    painPoints: '',
    goals: '',
    purchaseTimeframe: '1-3 meses',
    channels: '',
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const validationErrors = validatePersonaForm(formData)
    
    if (validationErrors.length > 0) {
      const errorMap: Record<string, string> = {}
      validationErrors.forEach((error) => {
        errorMap[error.field] = error.message
      })
      setErrors(errorMap)
      return
    }

    setErrors({})
    onSubmit({
      name: formData.name,
      description: formData.description,
      demographics: formData.demographics,
      painPoints: parseCommaSeparated(formData.painPoints),
      goals: parseCommaSeparated(formData.goals),
      purchaseTimeframe: formData.purchaseTimeframe,
      channels: parseCommaSeparated(formData.channels),
    })
    setFormData({
      name: '',
      description: '',
      demographics: '',
      painPoints: '',
      goals: '',
      purchaseTimeframe: '1-3 meses',
      channels: '',
    })
  }

  return (
    <Card className="border-primary/50">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <UserPlus className="h-5 w-5 text-primary" />
            <CardTitle>Crear Nueva Persona</CardTitle>
          </div>
          <IconButton
            icon={X}
            onClick={onCancel}
            variant="ghost"
            size="icon"
            aria-label="Cancelar"
          />
        </div>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit}>
          {Object.keys(errors).length > 0 && (
            <div className="mb-4 p-3 rounded-md bg-destructive/10 border border-destructive/20 flex items-start gap-2 animate-fade-in">
              <AlertCircle className="h-4 w-4 text-destructive shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-destructive mb-1">
                  Por favor corrige los siguientes errores:
                </p>
                <ul className="text-sm text-destructive/80 space-y-1">
                  {Object.entries(errors).map(([field, message]) => (
                    <li key={field}>• {message}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
          <PersonaFormFields
            formData={formData}
            errors={errors}
            onChange={(field, value) => {
              setFormData({ ...formData, [field]: value })
              // Clear error when user starts typing
              if (errors[field]) {
                setErrors((prev) => {
                  const newErrors = { ...prev }
                  delete newErrors[field]
                  return newErrors
                })
              }
            }}
          />
          <div className="flex gap-2 mt-6">
            <Button type="submit" variant="default">
              Crear Persona
            </Button>
            <Button type="button" variant="ghost" onClick={onCancel}>
              Cancelar
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}

