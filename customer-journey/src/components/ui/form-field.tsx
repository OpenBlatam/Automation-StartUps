import { Label } from './label'
import { Input } from './input'
import { Textarea } from './textarea'
import { Select } from './select'
import { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface FormFieldProps {
  id: string
  label: string
  value: string
  onChange: (value: string) => void
  placeholder?: string
  type?: 'input' | 'textarea' | 'select'
  icon?: LucideIcon
  options?: { value: string; label: string }[]
  required?: boolean
  className?: string
  error?: string
}

export function FormField({
  id,
  label,
  value,
  onChange,
  placeholder,
  type = 'input',
  icon: Icon,
  options,
  required,
  className,
  error,
}: FormFieldProps) {
  return (
    <div className={cn('space-y-1.5', className)}>
      <Label htmlFor={id} className="text-xs flex items-center gap-1.5">
        {Icon && <Icon className="h-3 w-3 text-muted-foreground" />}
        {label}
        {required && <span className="text-primary">*</span>}
      </Label>
      {type === 'textarea' ? (
        <Textarea
          id={id}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          required={required}
          className={cn(error && 'border-destructive focus-visible:ring-destructive')}
        />
      ) : type === 'select' && options ? (
        <Select
          id={id}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          required={required}
          className={cn(error && 'border-destructive focus-visible:ring-destructive')}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Select>
      ) : (
        <Input
          id={id}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          required={required}
          className={cn(error && 'border-destructive focus-visible:ring-destructive')}
        />
      )}
      {error && (
        <p className="text-xs text-destructive animate-fade-in">{error}</p>
      )}
    </div>
  )
}


