export function parseCommaSeparated(value: string): string[] {
  return value.split(',').map((item) => item.trim()).filter(Boolean)
}

export function formatCommaSeparated(items: string[]): string {
  return items.join(', ')
}

export function generateId(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}










