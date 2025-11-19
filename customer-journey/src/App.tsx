import { useRef } from 'react'
import { BuyerPersonaSelector } from './components/BuyerPersonaSelector'
import { JourneyBuilder } from './components/journey/JourneyBuilder'
import { JourneyVisualization } from './components/JourneyVisualization'
import { Header } from './components/layout/Header'
import { Footer } from './components/layout/Footer'
import { Toaster } from './components/ui/Toaster'
import { KeyboardShortcutsHelp } from './components/layout/KeyboardShortcutsHelp'
import { useAppState } from './hooks/useAppState'
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'

function App() {
  const {
    viewMode,
    personas,
    journey,
    selectedPersona,
    toasts,
    setViewMode,
    handleSelectPersona,
    handleAddPersona,
    handleUpdateStage,
    handleExport,
    handleDuplicatePersona,
    handleDeletePersona,
    dismiss,
    showToast,
  } = useAppState()

  useKeyboardShortcuts({
    onExport: handleExport,
    onToggleView: () => {
      setViewMode(viewMode === 'builder' ? 'visualization' : 'builder')
    },
  })

  return (
    <div className="min-h-screen bg-background">
      <Header
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        journey={journey}
        onExport={handleExport}
      />
      <main className="container mx-auto px-4 py-8">
        {viewMode === 'builder' ? (
          <div className="space-y-8">
            <BuyerPersonaSelector
              personas={personas}
              selectedPersonaId={selectedPersona?.id ?? null}
              onSelectPersona={handleSelectPersona}
              onAddPersona={handleAddPersona}
              onDuplicatePersona={handleDuplicatePersona}
              onDeletePersona={handleDeletePersona}
            />
            <JourneyBuilder
              persona={selectedPersona}
              journey={journey}
              onUpdateStage={handleUpdateStage}
              onToast={showToast}
            />
          </div>
        ) : (
          <JourneyVisualization
            journey={journey}
            onExport={handleExport}
            onAddPersona={() => {
              setViewMode('builder')
              // El formulario se abrirá automáticamente en BuyerPersonaSelector
            }}
            onSwitchToBuilder={() => {
              setViewMode('builder')
            }}
          />
        )}
      </main>
      <Footer />
      <Toaster toasts={toasts} onDismiss={dismiss} />
      <KeyboardShortcutsHelp />
    </div>
  )
}

export default App

