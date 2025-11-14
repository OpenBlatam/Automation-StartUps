import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Select } from './ui/select'
import { Badge } from './ui/badge'
import { Plus, Trash2, Settings, CheckCircle2 } from 'lucide-react'
import type { ScoreThreshold, AutomationRule } from '@/types/lead-scoring'

interface ScoreThresholdsProps {
  thresholds: ScoreThreshold[]
  onAdd: (threshold: Omit<ScoreThreshold, 'id'>) => void
  onUpdate: (id: string, threshold: Partial<ScoreThreshold>) => void
  onDelete: (id: string) => void
}

export function ScoreThresholds({
  thresholds,
  onAdd,
  onUpdate,
  onDelete,
}: ScoreThresholdsProps) {
  const [isAdding, setIsAdding] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    minScore: 0,
    maxScore: 100,
    label: '',
    color: '#8b5cf6',
  })

  const handleSubmit = () => {
    if (editingId) {
      onUpdate(editingId, formData)
      setEditingId(null)
    } else {
      onAdd({ ...formData, automationRules: [] })
    }
    setIsAdding(false)
    setFormData({
      minScore: 0,
      maxScore: 100,
      label: '',
      color: '#8b5cf6',
    })
  }

  const sortedThresholds = [...thresholds].sort((a, b) => a.minScore - b.minScore)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Score Thresholds</h2>
          <p className="text-muted-foreground">Define score ranges and automation rules</p>
        </div>
        <Button
          onClick={() => {
            setIsAdding(true)
            setEditingId(null)
            setFormData({
              minScore: 0,
              maxScore: 100,
              label: '',
              color: '#8b5cf6',
            })
          }}
          variant="premium"
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Threshold
        </Button>
      </div>

      {isAdding && (
        <Card className="border-primary/50 shadow-elegant">
          <CardHeader>
            <CardTitle>{editingId ? 'Edit Threshold' : 'Add New Threshold'}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="minScore">Min Score</Label>
                <Input
                  id="minScore"
                  type="number"
                  value={formData.minScore}
                  onChange={(e) => setFormData({ ...formData, minScore: parseInt(e.target.value) || 0 })}
                />
              </div>
              <div>
                <Label htmlFor="maxScore">Max Score</Label>
                <Input
                  id="maxScore"
                  type="number"
                  value={formData.maxScore}
                  onChange={(e) => setFormData({ ...formData, maxScore: parseInt(e.target.value) || 100 })}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="label">Label</Label>
                <Input
                  id="label"
                  value={formData.label}
                  onChange={(e) => setFormData({ ...formData, label: e.target.value })}
                  placeholder="e.g., Hot Lead"
                />
              </div>
              <div>
                <Label htmlFor="color">Color</Label>
                <Input
                  id="color"
                  type="color"
                  value={formData.color}
                  onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSubmit} variant="premium">
                {editingId ? 'Update' : 'Add'} Threshold
              </Button>
              <Button
                onClick={() => {
                  setIsAdding(false)
                  setEditingId(null)
                }}
                variant="outline"
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="space-y-4">
        {sortedThresholds.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">No thresholds defined. Add one to get started.</p>
            </CardContent>
          </Card>
        ) : (
          sortedThresholds.map((threshold) => {
            const enabledRules = threshold.automationRules.filter(r => r.enabled).length
            return (
              <Card key={threshold.id} className="hover:border-primary/50 transition-colors">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div
                        className="h-4 w-4 rounded-full"
                        style={{ backgroundColor: threshold.color }}
                      />
                      <CardTitle>{threshold.label}</CardTitle>
                      <Badge variant="secondary">
                        {threshold.minScore} - {threshold.maxScore} points
                      </Badge>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => onDelete(threshold.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <CardDescription>
                    {enabledRules > 0 ? (
                      <span className="flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4 text-success" />
                        {enabledRules} automation rule{enabledRules !== 1 ? 's' : ''} active
                      </span>
                    ) : (
                      'No automation rules configured'
                    )}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                      <Settings className="mr-2 h-4 w-4" />
                      Configure Rules
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )
          })
        )}
      </div>
    </div>
  )
}




