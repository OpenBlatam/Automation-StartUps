import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Share2, Link, Mail, Copy, Check } from 'lucide-react'
import { Tooltip } from '../ui/tooltip'
import { useState } from 'react'
import { Badge } from '../ui/badge'
import type { CustomerJourney } from '@/types/journey'

interface JourneyShareProps {
  journey: CustomerJourney
}

export function JourneyShare({ journey }: JourneyShareProps) {
  const [copied, setCopied] = useState(false)
  const [linkCopied, setLinkCopied] = useState(false)

  const shareUrl = typeof window !== 'undefined' 
    ? `${window.location.origin}${window.location.pathname}?journey=${journey.id}&persona=${journey.personaId}`
    : ''

  const handleCopyLink = async () => {
    if (navigator.clipboard && shareUrl) {
      try {
        await navigator.clipboard.writeText(shareUrl)
        setLinkCopied(true)
        setTimeout(() => setLinkCopied(false), 2000)
      } catch (err) {
        console.warn('Failed to copy link:', err)
      }
    }
  }

  const handleShareEmail = () => {
    const subject = encodeURIComponent(`Customer Journey: ${journey.persona.name}`)
    const body = encodeURIComponent(
      `Te comparto el Customer Journey para ${journey.persona.name}.\n\n` +
      `Ver journey: ${shareUrl}\n\n` +
      `Resumen:\n` +
      `- ${journey.stages.length} etapas\n` +
      `- ${journey.stages.reduce((sum, s) => sum + s.touchpoints.length, 0)} touchpoints\n` +
      `- ${journey.stages.reduce((sum, s) => sum + s.automationTriggers.length, 0)} triggers`
    )
    window.location.href = `mailto:?subject=${subject}&body=${body}`
  }

  const handleShareNative = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Customer Journey: ${journey.persona.name}`,
          text: `Revisa el Customer Journey para ${journey.persona.name}`,
          url: shareUrl,
        })
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          console.warn('Failed to share:', err)
        }
      }
    }
  }

  const handleCopyData = () => {
    const data = JSON.stringify(journey, null, 2)
    if (navigator.clipboard) {
      navigator.clipboard.writeText(data).then(() => {
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      })
    }
  }

  return (
    <Card className="bg-gradient-card border-primary/20 shadow-soft">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Share2 className="h-5 w-5 text-primary" />
          Compartir Journey
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Share Link */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Enlace de compartir</label>
          <div className="flex items-center gap-2">
            <div className="flex-1 p-2 rounded-md bg-card border border-border text-sm text-muted-foreground truncate">
              {shareUrl || 'Generando enlace...'}
            </div>
            <Tooltip content={linkCopied ? '¡Copiado!' : 'Copiar enlace'}>
              <Button
                variant="outline"
                size="icon"
                onClick={handleCopyLink}
                className="shrink-0"
              >
                {linkCopied ? (
                  <Check className="h-4 w-4 text-primary" />
                ) : (
                  <Link className="h-4 w-4" />
                )}
              </Button>
            </Tooltip>
          </div>
        </div>

        {/* Share Options */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Compartir por</label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {navigator.share && (
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={handleShareNative}
              >
                <Share2 className="h-4 w-4 mr-2" />
                Compartir nativo
              </Button>
            )}
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={handleShareEmail}
            >
              <Mail className="h-4 w-4 mr-2" />
              Email
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={handleCopyData}
            >
              {copied ? (
                <>
                  <Check className="h-4 w-4 mr-2 text-primary" />
                  Copiado
                </>
              ) : (
                <>
                  <Copy className="h-4 w-4 mr-2" />
                  Copiar datos
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Journey Info */}
        <div className="pt-3 border-t border-border">
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="outline" className="text-xs">
              {journey.stages.length} etapas
            </Badge>
            <Badge variant="outline" className="text-xs">
              {journey.stages.reduce((sum, s) => sum + s.touchpoints.length, 0)} TP
            </Badge>
            <Badge variant="outline" className="text-xs">
              {journey.stages.reduce((sum, s) => sum + s.automationTriggers.length, 0)} TR
            </Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

