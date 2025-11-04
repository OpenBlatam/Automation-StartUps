/**
 * Componente de Dashboard para Tickets de Soporte
 * 
 * Muestra métricas en tiempo real, gráficos y visualizaciones
 */
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface DashboardData {
  metrics: {
    total_tickets: number;
    chatbot_resolved: number;
    pending: number;
    critical_urgent: number;
    avg_first_response_minutes: number | null;
    chatbot_resolution_rate: string;
  };
  trends: Array<{
    hour: string;
    ticket_count: number;
    chatbot_resolved_count: number;
  }>;
  priority_distribution: Array<{
    priority: string;
    count: number;
  }>;
  top_categories: Array<{
    category: string;
    count: number;
  }>;
  top_agents: Array<{
    agent_name: string;
    tickets_handled: number;
    avg_resolution_minutes: number | null;
    avg_satisfaction: number | null;
  }>;
  recent_feedback: Array<{
    ticket_id: string;
    satisfaction_score: number;
    feedback_text: string | null;
    submitted_at: string;
    subject: string;
    agent_name: string | null;
  }>;
}

export default function TicketDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('24h');

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 60000); // Actualizar cada minuto
    return () => clearInterval(interval);
  }, [period]);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`/api/support/dashboard?period=${period}`);
      if (!response.ok) throw new Error('Failed to fetch');
      const dashboardData = await response.json();
      setData(dashboardData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-6">Cargando dashboard...</div>;
  }

  if (!data) {
    return <div className="p-6 text-red-500">Error cargando datos</div>;
  }

  const { metrics, trends, priority_distribution, top_categories, top_agents, recent_feedback } = data;

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard de Soporte</h1>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="px-4 py-2 border rounded"
        >
          <option value="24h">Últimas 24 horas</option>
          <option value="7d">Últimos 7 días</option>
          <option value="30d">Últimos 30 días</option>
        </select>
      </div>

      {/* Métricas Principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Total Tickets</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{metrics.total_tickets}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Resueltos por Chatbot</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{metrics.chatbot_resolved}</div>
            <div className="text-sm text-gray-500">
              {metrics.chatbot_resolution_rate}% tasa de resolución
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pendientes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-600">{metrics.pending}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Críticos/Urgentes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">{metrics.critical_urgent}</div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Resumen</TabsTrigger>
          <TabsTrigger value="trends">Tendencias</TabsTrigger>
          <TabsTrigger value="agents">Agentes</TabsTrigger>
          <TabsTrigger value="feedback">Feedback</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Distribución por Prioridad</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {priority_distribution.map((item) => (
                    <div key={item.priority} className="flex justify-between">
                      <span className="capitalize">{item.priority}</span>
                      <span className="font-bold">{item.count}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Categorías</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {top_categories.map((item) => (
                    <div key={item.category} className="flex justify-between">
                      <span>{item.category}</span>
                      <span className="font-bold">{item.count}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Tendencias por Hora</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 overflow-x-auto">
                {/* Aquí iría un gráfico de línea con una librería como recharts */}
                <div className="text-sm text-gray-500">
                  {trends.length} puntos de datos
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="agents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Top Agentes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {top_agents.map((agent) => (
                  <div key={agent.agent_name} className="border-b pb-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-bold">{agent.agent_name}</div>
                        <div className="text-sm text-gray-500">
                          {agent.tickets_handled} tickets manejados
                        </div>
                      </div>
                      <div className="text-right">
                        {agent.avg_satisfaction && (
                          <div className="text-lg font-bold">
                            {agent.avg_satisfaction.toFixed(1)}/5
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="feedback" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Feedback Reciente</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recent_feedback.map((fb) => (
                  <div key={fb.ticket_id} className="border-b pb-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <div className="font-bold">{fb.ticket_id}</div>
                        <div className="text-sm text-gray-500">{fb.subject}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold">
                          {fb.satisfaction_score}/5
                        </div>
                      </div>
                    </div>
                    {fb.feedback_text && (
                      <div className="text-sm text-gray-700 mt-2">{fb.feedback_text}</div>
                    )}
                    {fb.agent_name && (
                      <div className="text-xs text-gray-500 mt-1">
                        Agente: {fb.agent_name}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

