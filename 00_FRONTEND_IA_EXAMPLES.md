---
title: "Frontend con IA - Ejemplos Prácticos"
category: "Frontend Development"
tags: ["ai", "frontend", "examples", "code"]
encoded_with: "utf-8"
created: "2025-01-27"
path: "00_FRONTEND_IA_EXAMPLES.md"
---

# 💻 Frontend con IA - Ejemplos Prácticos

<div align="center">

**Ejemplos de Código Real Generado con IA**

[![Examples](https://img.shields.io/badge/Examples-10+-green.svg)](#)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](#)

</div>

---

## 📋 Índice de Ejemplos

1. [Componente Card (V0.dev)](#ejemplo-1-componente-card-v0dev)
2. [Formulario de Contacto (V0.dev)](#ejemplo-2-formulario-de-contacto-v0dev)
3. [Dashboard Analytics (Bolt.new)](#ejemplo-3-dashboard-analytics-boltnew)
4. [Hook de Datos (BuildShip)](#ejemplo-4-hook-de-datos-buildship)
5. [Sistema de Notificaciones (Multi-herramienta)](#ejemplo-5-sistema-de-notificaciones)
6. [Tabla de Datos (V0.dev)](#ejemplo-6-tabla-de-datos-v0dev)
7. [Página de Settings (Bolt.new)](#ejemplo-7-página-de-settings-boltnew)
8. [Componente de Búsqueda (V0.dev)](#ejemplo-8-componente-de-búsqueda-v0dev)

---

## Ejemplo 1: Componente Card (V0.dev)

### **Prompt usado:**
```
Create a modern card component with:
- Header with title and optional icon
- Body content area
- Footer with action buttons
- Hover effects
- Responsive design
- Tailwind CSS styling
- TypeScript types
```

### **Código Generado:**
```tsx
// components/ui/card.tsx
import { LucideIcon } from 'lucide-react'
import { Button } from './button'

interface CardProps {
  title: string
  icon?: LucideIcon
  children: React.ReactNode
  footer?: React.ReactNode
  onAction?: () => void
  actionLabel?: string
}

export function Card({
  title,
  icon: Icon,
  children,
  footer,
  onAction,
  actionLabel = 'Action'
}: CardProps) {
  return (
    <div className="rounded-lg border bg-card text-card-foreground shadow-sm hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-center justify-between p-6 pb-4">
        <div className="flex items-center gap-2">
          {Icon && <Icon className="h-5 w-5 text-muted-foreground" />}
          <h3 className="text-lg font-semibold">{title}</h3>
        </div>
      </div>

      {/* Body */}
      <div className="px-6 py-4">
        {children}
      </div>

      {/* Footer */}
      {(footer || onAction) && (
        <div className="flex items-center justify-end gap-2 p-6 pt-4 border-t">
          {footer}
          {onAction && (
            <Button onClick={onAction} variant="outline">
              {actionLabel}
            </Button>
          )}
        </div>
      )}
    </div>
  )
}
```

### **Uso:**
```tsx
import { Card } from '@/components/ui/card'
import { TrendingUp } from 'lucide-react'

export default function Dashboard() {
  return (
    <Card
      title="Revenue"
      icon={TrendingUp}
      onAction={() => console.log('View details')}
      actionLabel="View Details"
    >
      <p className="text-3xl font-bold">$45,678</p>
      <p className="text-sm text-muted-foreground">+12.5% from last month</p>
    </Card>
  )
}
```

---

## Ejemplo 2: Formulario de Contacto (V0.dev)

### **Prompt usado:**
```
Create a contact form with:
- Fields: name, email, message
- Real-time validation with error messages
- Submit button with loading state
- Success/error toast notifications
- React Hook Form integration
- Zod validation schema
- Tailwind CSS styling
- TypeScript
```

### **Código Generado:**
```tsx
// components/forms/contact-form.tsx
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { toast } from 'sonner'

const contactSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  message: z.string().min(10, 'Message must be at least 10 characters')
})

type ContactFormData = z.infer<typeof contactSchema>

export function ContactForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm<ContactFormData>({
    resolver: zodResolver(contactSchema)
  })

  const onSubmit = async (data: ContactFormData) => {
    try {
      // Simular API call
      await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      
      toast.success('Message sent successfully!')
      reset()
    } catch (error) {
      toast.error('Failed to send message. Please try again.')
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Name */}
      <div>
        <label htmlFor="name" className="block text-sm font-medium mb-2">
          Name
        </label>
        <Input
          id="name"
          {...register('name')}
          placeholder="John Doe"
          className={errors.name ? 'border-red-500' : ''}
        />
        {errors.name && (
          <p className="text-sm text-red-500 mt-1">{errors.name.message}</p>
        )}
      </div>

      {/* Email */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium mb-2">
          Email
        </label>
        <Input
          id="email"
          type="email"
          {...register('email')}
          placeholder="john@example.com"
          className={errors.email ? 'border-red-500' : ''}
        />
        {errors.email && (
          <p className="text-sm text-red-500 mt-1">{errors.email.message}</p>
        )}
      </div>

      {/* Message */}
      <div>
        <label htmlFor="message" className="block text-sm font-medium mb-2">
          Message
        </label>
        <Textarea
          id="message"
          {...register('message')}
          placeholder="Your message here..."
          rows={5}
          className={errors.message ? 'border-red-500' : ''}
        />
        {errors.message && (
          <p className="text-sm text-red-500 mt-1">{errors.message.message}</p>
        )}
      </div>

      {/* Submit */}
      <Button type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? 'Sending...' : 'Send Message'}
      </Button>
    </form>
  )
}
```

---

## Ejemplo 3: Dashboard Analytics (Bolt.new)

### **Prompt usado:**
```
Build a complete analytics dashboard with:
- Header with title and date filter
- Four KPI cards showing key metrics
- Two line charts showing trends over time
- One bar chart for category comparison
- Data table with pagination and sorting
- Export to CSV functionality
- Responsive grid layout
- Dark mode support
- Use React, TypeScript, Tailwind CSS, and Chart.js
```

### **Estructura Generada:**
```tsx
// app/dashboard/analytics/page.tsx
'use client'

import { useState } from 'react'
import { AnalyticsCard } from '@/components/analytics/card'
import { LineChart } from '@/components/analytics/line-chart'
import { BarChart } from '@/components/analytics/bar-chart'
import { DataTable } from '@/components/analytics/data-table'
import { DateFilter } from '@/components/analytics/date-filter'
import { useAnalytics } from '@/hooks/useAnalytics'

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState('30d')
  const { data, isLoading } = useAnalytics(dateRange)

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
        <DateFilter value={dateRange} onChange={setDateRange} />
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <AnalyticsCard
          title="Total Users"
          value={data?.users || 0}
          change={data?.userGrowth || 0}
        />
        <AnalyticsCard
          title="Revenue"
          value={`$${data?.revenue || 0}`}
          change={data?.revenueGrowth || 0}
        />
        <AnalyticsCard
          title="Conversions"
          value={data?.conversions || 0}
          change={data?.conversionGrowth || 0}
        />
        <AnalyticsCard
          title="Avg. Session"
          value={`${data?.avgSession || 0}m`}
          change={data?.sessionGrowth || 0}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LineChart data={data?.trends} title="User Trends" />
        <LineChart data={data?.revenueTrends} title="Revenue Trends" />
      </div>

      <BarChart data={data?.categories} title="Category Comparison" />

      {/* Data Table */}
      <DataTable data={data?.tableData} />
    </div>
  )
}
```

---

## Ejemplo 4: Hook de Datos (BuildShip)

### **Workflow en BuildShip:**
```
1. Receive API request
2. Process with AI
3. Store in database
4. Return formatted data
```

### **Hook Generado:**
```tsx
// hooks/useAnalytics.ts
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

interface AnalyticsData {
  users: number
  revenue: number
  growth: number
  trends: Array<{ date: string; value: number }>
}

interface UseAnalyticsOptions {
  dateRange?: string
  enabled?: boolean
}

export function useAnalytics(options: UseAnalyticsOptions = {}) {
  const { dateRange = '30d', enabled = true } = options

  return useQuery<AnalyticsData>({
    queryKey: ['analytics', dateRange],
    queryFn: async () => {
      const { data } = await axios.get('/api/analytics', {
        params: { dateRange }
      })
      return data
    },
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false
  })
}
```

### **Uso:**
```tsx
import { useAnalytics } from '@/hooks/useAnalytics'

export function AnalyticsDashboard() {
  const { data, isLoading, error } = useAnalytics({ dateRange: '30d' })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error loading data</div>

  return (
    <div>
      <p>Users: {data?.users}</p>
      <p>Revenue: ${data?.revenue}</p>
    </div>
  )
}
```

---

## Ejemplo 5: Sistema de Notificaciones

### **Componente de Toast (V0.dev):**
```tsx
// components/ui/toast.tsx
'use client'

import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ToastProps {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  onDismiss: (id: string) => void
}

export function Toast({ id, type, title, message, onDismiss }: ToastProps) {
  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info
  }

  const colors = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  }

  const Icon = icons[type]

  return (
    <div
      className={cn(
        'rounded-lg border p-4 shadow-lg flex items-start gap-3 min-w-[300px]',
        colors[type]
      )}
    >
      <Icon className="h-5 w-5 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        <p className="font-semibold">{title}</p>
        {message && <p className="text-sm mt-1">{message}</p>}
      </div>
      <button
        onClick={() => onDismiss(id)}
        className="flex-shrink-0 hover:opacity-70"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  )
}
```

### **Hook de Notificaciones (BuildShip):**
```tsx
// hooks/useNotifications.ts
import { useState, useCallback } from 'react'
import { useWebSocket } from '@/hooks/useWebSocket'

interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
}

export function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const { socket } = useWebSocket()

  const addNotification = useCallback((notification: Omit<Notification, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9)
    setNotifications(prev => [...prev, { ...notification, id }])
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id))
    }, 5000)
  }, [])

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }, [])

  // Listen to WebSocket notifications
  socket?.on('notification', (data: Notification) => {
    addNotification(data)
  })

  return {
    notifications,
    addNotification,
    removeNotification
  }
}
```

### **Sistema Completo:**
```tsx
// components/notifications/notification-system.tsx
'use client'

import { Toast } from '@/components/ui/toast'
import { useNotifications } from '@/hooks/useNotifications'

export function NotificationSystem() {
  const { notifications, removeNotification } = useNotifications()

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {notifications.map(notification => (
        <Toast
          key={notification.id}
          {...notification}
          onDismiss={removeNotification}
        />
      ))}
    </div>
  )
}
```

---

## Ejemplo 6: Tabla de Datos (V0.dev)

### **Prompt usado:**
```
Create a data table component with:
- Sortable columns
- Pagination
- Row selection
- Search functionality
- Responsive design
- Tailwind CSS
- TypeScript
- Use @tanstack/react-table if needed
```

### **Código Generado:**
```tsx
// components/ui/data-table.tsx
'use client'

import { useState } from 'react'
import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  ColumnDef,
  flexRender
} from '@tanstack/react-table'
import { Button } from './button'
import { Input } from './input'
import { ArrowUpDown, ChevronLeft, ChevronRight } from 'lucide-react'

interface DataTableProps<T> {
  data: T[]
  columns: ColumnDef<T>[]
  searchable?: boolean
  selectable?: boolean
}

export function DataTable<T>({
  data,
  columns,
  searchable = true,
  selectable = false
}: DataTableProps<T>) {
  const [sorting, setSorting] = useState([])
  const [search, setSearch] = useState('')

  const filteredData = data.filter(item =>
    Object.values(item).some(value =>
      String(value).toLowerCase().includes(search.toLowerCase())
    )
  )

  const table = useReactTable({
    data: filteredData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    state: { sorting }
  })

  return (
    <div className="space-y-4">
      {/* Search */}
      {searchable && (
        <Input
          placeholder="Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-sm"
        />
      )}

      {/* Table */}
      <div className="rounded-md border">
        <table className="w-full">
          <thead>
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <th
                    key={header.id}
                    className="px-4 py-2 text-left font-medium"
                  >
                    {header.isPlaceholder ? null : (
                      <button
                        onClick={header.column.getToggleSortingHandler()}
                        className="flex items-center gap-2"
                      >
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                        <ArrowUpDown className="h-4 w-4" />
                      </button>
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map(row => (
              <tr key={row.id} className="border-t">
                {row.getVisibleCells().map(cell => (
                  <td key={cell.id} className="px-4 py-2">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1} to{' '}
          {Math.min(
            (table.getState().pagination.pageIndex + 1) *
              table.getState().pagination.pageSize,
            filteredData.length
          )}{' '}
          of {filteredData.length} results
        </p>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
```

---

## 📚 Más Ejemplos

Para más ejemplos prácticos, consulta:
- [Guía Completa de Arquitectura](./00_FRONTEND_IA_ALTERNATIVAS_ARCHITECTURE.md)
- [Diagramas Visuales](./00_FRONTEND_IA_DIAGRAMAS_VISUALES.md)

---

<div align="center">

**¿Necesitas un ejemplo específico?**  
**Revisa la documentación completa o genera uno con las herramientas de IA**

</div>












