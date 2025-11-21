export interface ValidationError {
  field: string
  message: string
}

export function validatePersonaForm(data: {
  name: string
  description: string
  demographics: string
  painPoints: string
  goals: string
  purchaseTimeframe: string
  channels: string
}): ValidationError[] {
  const errors: ValidationError[] = []

  if (!data.name.trim()) {
    errors.push({ field: 'name', message: 'El nombre es requerido' })
  } else if (data.name.trim().length < 3) {
    errors.push({ field: 'name', message: 'El nombre debe tener al menos 3 caracteres' })
  }

  if (!data.description.trim()) {
    errors.push({ field: 'description', message: 'La descripción es requerida' })
  } else if (data.description.trim().length < 10) {
    errors.push({ field: 'description', message: 'La descripción debe tener al menos 10 caracteres' })
  }

  return errors
}

export function validateTouchpoint(data: { name: string; channel: string; description: string }): ValidationError[] {
  const errors: ValidationError[] = []

  if (!data.name.trim()) {
    errors.push({ field: 'name', message: 'El nombre del touchpoint es requerido' })
  }

  if (!data.channel.trim()) {
    errors.push({ field: 'channel', message: 'El canal es requerido' })
  }

  return errors
}

export function validateTrigger(data: { name: string; type: string; description: string }): ValidationError[] {
  const errors: ValidationError[] = []

  if (!data.name.trim()) {
    errors.push({ field: 'name', message: 'El nombre del trigger es requerido' })
  }

  if (!data.type.trim()) {
    errors.push({ field: 'type', message: 'El tipo de trigger es requerido' })
  }

  return errors
}









