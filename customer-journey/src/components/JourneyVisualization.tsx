import { useState, useMemo } from 'react'
import { Card, CardContent } from './ui/card'
import { Map, LayoutGrid, List } from 'lucide-react'
import { StageStats } from './journey/StageStats'
import { StageCardVisual } from './journey/StageCardVisual'
import { ExpandableStageCard } from './journey/ExpandableStageCard'
import { VisualizationHeader } from './journey/VisualizationHeader'
import { StageConnectionLine } from './journey/StageConnectionLine'
import { JourneyAnalytics } from './journey/JourneyAnalytics'
import { StageFilters, type StageFilter } from './journey/StageFilters'
import { StageSearch } from './journey/StageSearch'
import { QuickStats } from './journey/QuickStats'
import { JourneyTimeline } from './journey/JourneyTimeline'
import { JourneySummary } from './journey/JourneySummary'
import { StageComparison } from './journey/StageComparison'
import { JourneyInsights } from './journey/JourneyInsights'
import { ExportOptions } from './journey/ExportOptions'
import { JourneyShare } from './journey/JourneyShare'
import { JourneyShortcuts } from './journey/JourneyShortcuts'
import { JourneyPerformance } from './journey/JourneyPerformance'
import { JourneyEmptyState } from './journey/JourneyEmptyState'
import { JourneyCharts } from './journey/JourneyCharts'
import { JourneyTips } from './journey/JourneyTips'
import { JourneyAccessibility } from './journey/JourneyAccessibility'
import { JourneyStats } from './journey/JourneyStats'
import { JourneyHealth } from './journey/JourneyHealth'
import { JourneyOptimizer } from './journey/JourneyOptimizer'
import { JourneyHistory } from './journey/JourneyHistory'
import { Button } from './ui/button'
import { Tooltip } from './ui/tooltip'
import { useState } from 'react'
import { FileText, Clock, BarChart3, Lightbulb, Download, Share2, Keyboard, Gauge, Sparkles, Accessibility, Activity, Heart, History } from 'lucide-react'
import type { CustomerJourney } from '@/types/journey'

interface JourneyVisualizationProps {
  journey: CustomerJourney | null
  onExport?: (format: 'json' | 'csv') => void
  onAddPersona?: () => void
  onSwitchToBuilder?: () => void
}

export function JourneyVisualization({ journey, onExport, onAddPersona, onSwitchToBuilder }: JourneyVisualizationProps) {
  const [viewMode, setViewMode] = useState<'compact' | 'expanded'>('compact')
  const [activeFilter, setActiveFilter] = useState<StageFilter>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [showSummary, setShowSummary] = useState(true)
  const [showTimeline, setShowTimeline] = useState(false)
  const [showComparison, setShowComparison] = useState(false)
  const [showInsights, setShowInsights] = useState(true)
  const [showExport, setShowExport] = useState(false)
  const [showShare, setShowShare] = useState(false)
  const [showShortcuts, setShowShortcuts] = useState(false)
  const [showPerformance, setShowPerformance] = useState(false)
  const [showCharts, setShowCharts] = useState(false)
  const [showTips, setShowTips] = useState(false)
  const [showAccessibility, setShowAccessibility] = useState(false)
  const [showStats, setShowStats] = useState(false)
  const [showHealth, setShowHealth] = useState(false)
  const [showOptimizer, setShowOptimizer] = useState(false)
  const [showHistory, setShowHistory] = useState(false)

  const filteredStages = useMemo(() => {
    if (!journey) return []

    let stages = journey.stages

    // Apply filter
    if (activeFilter !== 'all') {
      stages = stages.filter((stage) => {
        switch (activeFilter) {
          case 'with-touchpoints':
            return stage.touchpoints.length > 0
          case 'with-triggers':
            return stage.automationTriggers.length > 0
          case 'with-content':
            return stage.contentNeeds.length > 0
          case 'empty':
            return (
              stage.touchpoints.length === 0 &&
              stage.automationTriggers.length === 0 &&
              stage.contentNeeds.length === 0
            )
          default:
            return true
        }
      })
    }

    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      stages = stages.filter(
        (stage) =>
          stage.name.toLowerCase().includes(query) ||
          stage.description.toLowerCase().includes(query) ||
          stage.touchpoints.some((tp) =>
            tp.name?.toLowerCase().includes(query) ||
            tp.channel?.toLowerCase().includes(query) ||
            tp.content?.toLowerCase().includes(query)
          ) ||
          stage.automationTriggers.some((trigger) =>
            trigger.name?.toLowerCase().includes(query) ||
            trigger.type?.toLowerCase().includes(query) ||
            trigger.condition?.toLowerCase().includes(query)
          ) ||
          stage.contentNeeds.some((content) => content.toLowerCase().includes(query))
      )
    }

    return stages
  }, [journey, activeFilter, searchQuery])

  const filterCounts = useMemo(() => {
    if (!journey) {
      return {
        all: 0,
        withTouchpoints: 0,
        withTriggers: 0,
        withContent: 0,
        empty: 0,
      }
    }

    return {
      all: journey.stages.length,
      withTouchpoints: journey.stages.filter((s) => s.touchpoints.length > 0).length,
      withTriggers: journey.stages.filter((s) => s.automationTriggers.length > 0).length,
      withContent: journey.stages.filter((s) => s.contentNeeds.length > 0).length,
      empty: journey.stages.filter(
        (s) =>
          s.touchpoints.length === 0 &&
          s.automationTriggers.length === 0 &&
          s.contentNeeds.length === 0
      ).length,
    }
  }, [journey])

  if (!journey) {
    return <JourneyEmptyState onAddPersona={onAddPersona} />
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <VisualizationHeader journey={journey} />
          <div className="flex items-center gap-2">
            <Tooltip content="Vista compacta">
              <Button
                variant={viewMode === 'compact' ? 'default' : 'outline'}
                size="icon"
                onClick={() => setViewMode('compact')}
                aria-label="Vista compacta"
              >
                <LayoutGrid className="h-4 w-4" />
              </Button>
            </Tooltip>
            <Tooltip content="Vista expandida con detalles">
              <Button
                variant={viewMode === 'expanded' ? 'default' : 'outline'}
                size="icon"
                onClick={() => setViewMode('expanded')}
                aria-label="Vista expandida"
              >
                <List className="h-4 w-4" />
              </Button>
            </Tooltip>
          </div>
        </div>
        <QuickStats journey={journey} />
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <StageSearch
            value={searchQuery}
            onChange={setSearchQuery}
            resultsCount={filteredStages.length}
            totalCount={journey.stages.length}
          />
          <StageFilters
            activeFilter={activeFilter}
            onFilterChange={setActiveFilter}
            counts={filterCounts}
          />
        </div>
      </div>

      <div className="relative">
        {viewMode === 'compact' && filteredStages.length > 0 && (
          <StageConnectionLine totalStages={filteredStages.length} />
        )}

        {filteredStages.length === 0 ? (
          <Card className="border-dashed bg-gradient-card animate-fade-in">
            <CardContent className="p-12 text-center">
              <p className="text-muted-foreground">
                No hay etapas que coincidan con el filtro seleccionado
              </p>
            </CardContent>
          </Card>
        ) : (
          <div
            className={`relative ${
              viewMode === 'compact'
                ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4'
                : 'space-y-4'
            }`}
          >
            {filteredStages.map((stage, index) =>
              viewMode === 'expanded' ? (
                <ExpandableStageCard
                  key={stage.id}
                  stage={stage}
                  index={index}
                  totalStages={filteredStages.length}
                />
              ) : (
                <StageCardVisual
                  key={stage.id}
                  stage={stage}
                  index={index}
                  totalStages={filteredStages.length}
                />
              )
            })}
          </div>
        )}
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        <div className="flex-1 space-y-6">
          <StageStats journey={journey} />
          <JourneyAnalytics journey={journey} />
          {showStats && <JourneyStats journey={journey} />}
          {showCharts && <JourneyCharts journey={journey} />}
          {showHealth && <JourneyHealth journey={journey} />}
          {showOptimizer && <JourneyOptimizer journey={journey} onOptimize={onSwitchToBuilder} />}
          {showPerformance && <JourneyPerformance journey={journey} />}
          {showComparison && <StageComparison journey={journey} />}
          {showInsights && <JourneyInsights journey={journey} />}
        </div>
        <div className="lg:w-80 space-y-6">
          <div className="grid grid-cols-2 gap-2 max-h-[600px] overflow-y-auto pr-2">
            <Button
              variant={showSummary ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowSummary(!showSummary)}
              className="w-full"
            >
              <FileText className="h-4 w-4 mr-1" />
              Resumen
            </Button>
            <Button
              variant={showTimeline ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowTimeline(!showTimeline)}
              className="w-full"
            >
              <Clock className="h-4 w-4 mr-1" />
              Timeline
            </Button>
            <Button
              variant={showComparison ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowComparison(!showComparison)}
              className="w-full"
            >
              <BarChart3 className="h-4 w-4 mr-1" />
              Comparar
            </Button>
            <Button
              variant={showInsights ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowInsights(!showInsights)}
              className="w-full"
            >
              <Lightbulb className="h-4 w-4 mr-1" />
              Insights
            </Button>
            <Button
              variant={showPerformance ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowPerformance(!showPerformance)}
              className="w-full"
            >
              <Gauge className="h-4 w-4 mr-1" />
              Rendimiento
            </Button>
            <Button
              variant={showShare ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowShare(!showShare)}
              className="w-full"
            >
              <Share2 className="h-4 w-4 mr-1" />
              Compartir
            </Button>
            {onExport && (
              <Button
                variant={showExport ? 'default' : 'outline'}
                size="sm"
                onClick={() => setShowExport(!showExport)}
                className="w-full"
              >
                <Download className="h-4 w-4 mr-1" />
                Exportar
              </Button>
            )}
            <Button
              variant={showCharts ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowCharts(!showCharts)}
              className="w-full"
            >
              <BarChart3 className="h-4 w-4 mr-1" />
              Gráficos
            </Button>
            <Button
              variant={showShortcuts ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowShortcuts(!showShortcuts)}
              className="w-full"
            >
              <Keyboard className="h-4 w-4 mr-1" />
              Atajos
            </Button>
            <Button
              variant={showTips ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowTips(!showTips)}
              className="w-full"
            >
              <Sparkles className="h-4 w-4 mr-1" />
              Tips
            </Button>
            <Button
              variant={showAccessibility ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowAccessibility(!showAccessibility)}
              className="w-full"
            >
              <Accessibility className="h-4 w-4 mr-1" />
              A11y
            </Button>
            <Button
              variant={showStats ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowStats(!showStats)}
              className="w-full"
            >
              <Activity className="h-4 w-4 mr-1" />
              Estadísticas
            </Button>
            <Button
              variant={showHealth ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowHealth(!showHealth)}
              className="w-full"
            >
              <Heart className="h-4 w-4 mr-1" />
              Salud
            </Button>
            <Button
              variant={showOptimizer ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowOptimizer(!showOptimizer)}
              className="w-full"
            >
              <Sparkles className="h-4 w-4 mr-1" />
              Optimizar
            </Button>
            <Button
              variant={showHistory ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowHistory(!showHistory)}
              className="w-full"
            >
              <History className="h-4 w-4 mr-1" />
              Historial
            </Button>
          </div>
          {showSummary && <JourneySummary journey={journey} />}
          {showTimeline && <JourneyTimeline journey={journey} />}
          {showShare && <JourneyShare journey={journey} />}
          {showExport && onExport && (
            <ExportOptions journey={journey} onExport={onExport} />
          )}
          {showShortcuts && <JourneyShortcuts />}
          {showTips && <JourneyTips />}
          {showAccessibility && <JourneyAccessibility />}
          {showStats && <JourneyStats journey={journey} />}
          {showHealth && <JourneyHealth journey={journey} />}
          {showOptimizer && <JourneyOptimizer journey={journey} onOptimize={onSwitchToBuilder} />}
          {showHistory && <JourneyHistory journey={journey} />}
        </div>
      </div>
    </div>
  )
}

