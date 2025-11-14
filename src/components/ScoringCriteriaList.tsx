import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Select } from './ui/select'
import { Badge } from './ui/badge'
import { Plus, Trash2, Edit2 } from 'lucide-react'
import type { ScoringCriteria } from '@/types/lead-scoring'

interface ScoringCriteriaListProps {
  criteria: ScoringCriteria[]
  onAdd: (criteria: Omit<ScoringCriteria, 'id'>) => void
  onUpdate: (id: string, criteria: Partial<ScoringCriteria>) => void
  onDelete: (id: string) => void
}

export function ScoringCriteriaList({
  criteria,
  onAdd,
  onUpdate,
  onDelete,
}: ScoringCriteriaListProps) {
  const [isAdding, setIsAdding] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    type: 'behavior' as 'behavior' | 'demographic',
    category: '',
    points: 0,
    description: '',
  })

  const handleSubmit = () => {
    if (editingId) {
      onUpdate(editingId, formData)
      setEditingId(null)
    } else {
      onAdd(formData)
    }
    setIsAdding(false)
    setFormData({
      name: '',
      type: 'behavior',
      category: '',
      points: 0,
      description: '',
    })
  }

  const handleEdit = (item: ScoringCriteria) => {
    setEditingId(item.id)
    setFormData({
      name: item.name,
      type: item.type,
      category: item.category,
      points: item.points,
      description: item.description || '',
    })
    setIsAdding(true)
  }

  const behaviorCriteria = criteria.filter(c => c.type === 'behavior')
  const demographicCriteria = criteria.filter(c => c.type === 'demographic')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Scoring Criteria</h2>
          <p className="text-muted-foreground">Define behaviors and demographics that contribute to lead scores</p>
        </div>
        <Button
          onClick={() => {
            setIsAdding(true)
            setEditingId(null)
            setFormData({
              name: '',
              type: 'behavior',
              category: '',
              points: 0,
              description: '',
            })
          }}
          variant="premium"
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Criteria
        </Button>
      </div>

      {isAdding && (
        <Card className="border-primary/50 shadow-elegant">
          <CardHeader>
            <CardTitle>{editingId ? 'Edit Criteria' : 'Add New Criteria'}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Visited pricing page"
                />
              </div>
              <div>
                <Label htmlFor="type">Type</Label>
                <Select
                  id="type"
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value as 'behavior' | 'demographic' })}
                >
                  <option value="behavior">Behavior</option>
                  <option value="demographic">Demographic</option>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="category">Category</Label>
                <Input
                  id="category"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  placeholder="e.g., Website Engagement"
                />
              </div>
              <div>
                <Label htmlFor="points">Points</Label>
                <Input
                  id="points"
                  type="number"
                  value={formData.points}
                  onChange={(e) => setFormData({ ...formData, points: parseInt(e.target.value) || 0 })}
                />
              </div>
            </div>
            <div>
              <Label htmlFor="description">Description (Optional)</Label>
              <Input
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Additional details..."
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSubmit} variant="premium">
                {editingId ? 'Update' : 'Add'} Criteria
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

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Behavior Criteria
              <Badge variant="secondary">{behaviorCriteria.length}</Badge>
            </CardTitle>
            <CardDescription>Website engagement and interaction behaviors</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {behaviorCriteria.length === 0 ? (
              <p className="text-sm text-muted-foreground">No behavior criteria yet. Add one to get started.</p>
            ) : (
              behaviorCriteria.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between rounded-lg border border-border bg-card p-4 hover:border-primary/50 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold">{item.name}</h4>
                      <Badge variant="default">{item.points} pts</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{item.category}</p>
                    {item.description && (
                      <p className="text-xs text-muted-foreground mt-1">{item.description}</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => handleEdit(item)}
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => onDelete(item.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Demographic Criteria
              <Badge variant="secondary">{demographicCriteria.length}</Badge>
            </CardTitle>
            <CardDescription>Company and contact attributes</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {demographicCriteria.length === 0 ? (
              <p className="text-sm text-muted-foreground">No demographic criteria yet. Add one to get started.</p>
            ) : (
              demographicCriteria.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between rounded-lg border border-border bg-card p-4 hover:border-primary/50 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold">{item.name}</h4>
                      <Badge variant="default">{item.points} pts</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{item.category}</p>
                    {item.description && (
                      <p className="text-xs text-muted-foreground mt-1">{item.description}</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => handleEdit(item)}
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => onDelete(item.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}




