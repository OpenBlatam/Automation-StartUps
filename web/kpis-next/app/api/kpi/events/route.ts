import { fetchRevenue24h, fetchSummary } from '@/lib/kpi';
import { generateAutoInsights, LLMProvider } from '@/lib/llm';

export const runtime = 'nodejs';

// Cache insights to avoid calling LLM too frequently
let lastInsight: { insight: string; timestamp: number } | null = null;
const INSIGHT_CACHE_TTL = 60000; // 1 minute

export async function GET() {
  const encoder = new TextEncoder();
  const enableLLM = process.env.ENABLE_LLM_INSIGHTS === '1' || process.env.ENABLE_LLM_INSIGHTS === 'true';
  const llmProvider = (process.env.DEFAULT_LLM_PROVIDER || 'openai') as LLMProvider;

  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      let closed = false;
      let insightCounter = 0; // Send insights every 6 updates (~1 minute)
      
      const send = async () => {
        if (closed) return;
        try {
          const [summary, series] = await Promise.all([fetchSummary(), fetchRevenue24h()]);
          
          // Generate LLM insights periodically (every 6 updates = ~1 minute)
          let insight: string | null = null;
          if (enableLLM) {
            insightCounter++;
            const shouldGenerateInsight = insightCounter >= 6 || 
              !lastInsight || 
              (Date.now() - lastInsight.timestamp) > INSIGHT_CACHE_TTL;
            
            if (shouldGenerateInsight) {
              try {
                insight = await generateAutoInsights(summary, series, llmProvider);
                lastInsight = { insight, timestamp: Date.now() };
                insightCounter = 0;
              } catch (e: any) {
                // Don't fail the whole stream if LLM fails
                console.error('LLM insight generation failed:', e);
              }
            } else if (lastInsight) {
              insight = lastInsight.insight;
            }
          }
          
          const payload = JSON.stringify({ 
            summary, 
            series, 
            insight,
            ts: Date.now() 
          });
          controller.enqueue(encoder.encode(`event: update\n`));
          controller.enqueue(encoder.encode(`data: ${payload}\n\n`));
        } catch (e: any) {
          controller.enqueue(encoder.encode(`event: error\n`));
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ error: e?.message || 'error' })}\n\n`));
        }
      };

      await send();
      const interval = setInterval(send, 10000);
      // @ts-ignore
      controller._interval = interval;
    },
    cancel(reason) {
      // @ts-ignore
      const interval = (this as any)._interval as NodeJS.Timer | undefined;
      if (interval) clearInterval(interval);
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
      'X-Accel-Buffering': 'no',
    },
  });
}



