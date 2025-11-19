import { FormField } from '../ui/form-field'
import { HelpText } from '../ui/help-text'
import { User, FileText, Users, AlertCircle, Target, Clock, Globe } from 'lucide-react'
import { PURCHASE_TIMEFRAMES } from '@/constants/journey'
import type { BuyerPersona } from '@/types/journey'

interface PersonaFormFieldsProps {
  formData: {
    name: string
    description: string
    demographics: string
    painPoints: string
    goals: string
    purchaseTimeframe: string
    channels: string
  }
  errors?: Record<string, string>
  onChange: (field: string, value: string) => void
}

const timeframeOptions = PURCHASE_TIMEFRAMES.map((timeframe) => ({
  value: timeframe,
  label: timeframe,
}))

export function PersonaFormFields({ formData, errors = {}, onChange }: PersonaFormFieldsProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-start gap-2">
        <div className="flex-1">
          <FormField
            id="name"
            label="Nombre"
            value={formData.name}
            onChange={(value) => onChange('name', value)}
            placeholder="Ej: Director de Marketing"
            icon={User}
            required
            error={errors.name}
          />
        </div>
        <div className="pt-6">
          <HelpText text="El nombre debe ser único y descriptivo para identificar fácilmente esta persona" />
        </div>
      </div>
      <div className="flex items-start gap-2">
        <div className="flex-1">
          <FormField
            id="description"
            label="Descripción"
            value={formData.description}
            onChange={(value) => onChange('description', value)}
            placeholder="Describe el perfil del buyer persona..."
            type="textarea"
            icon={FileText}
            required
            error={errors.description}
          />
        </div>
        <div className="pt-6">
          <HelpText text="Proporciona una descripción detallada del perfil, incluyendo su rol, responsabilidades y contexto" />
        </div>
      </div>
      <FormField
        id="demographics"
        label="Demografía"
        value={formData.demographics}
        onChange={(value) => onChange('demographics', value)}
        placeholder="Ej: 35-50 años, empresa mediana, sector tecnológico"
        icon={Users}
      />
      <FormField
        id="painPoints"
        label="Pain Points (separados por comas)"
        value={formData.painPoints}
        onChange={(value) => onChange('painPoints', value)}
        placeholder="Ej: Falta de tiempo, Presupuesto limitado, ROI difícil de medir"
        icon={AlertCircle}
      />
      <FormField
        id="goals"
        label="Objetivos (separados por comas)"
        value={formData.goals}
        onChange={(value) => onChange('goals', value)}
        placeholder="Ej: Aumentar leads, Mejorar conversión, Automatizar procesos"
        icon={Target}
      />
      <FormField
        id="purchaseTimeframe"
        label="Tiempo de Compra"
        value={formData.purchaseTimeframe}
        onChange={(value) => onChange('purchaseTimeframe', value)}
        type="select"
        options={timeframeOptions}
        icon={Clock}
      />
      <FormField
        id="channels"
        label="Canales (separados por comas)"
        value={formData.channels}
        onChange={(value) => onChange('channels', value)}
        placeholder="Ej: LinkedIn, Email, Web, Eventos"
        icon={Globe}
      />
    </div>
  )
}


