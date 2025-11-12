/**
 * Componente de Dashboard para Troubleshooting
 * Dashboard visual en tiempo real con métricas y gráficos
 */

'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface TroubleshootingMetrics {
  active_sessions: number;
  resolved_last_hour: number;
  escalated_last_hour: number;
  avg_resolution_time_minutes: number;
  unique_problems_24h: number;
  avg_rating_24h: number;
}

interface TopProblem {
  detected_problem_id: string;
  detected_problem_title: string;
  count: number;
  resolved_count: number;
}

interface ActiveSession {
  session_id: string;
  customer_email: string;
  detected_problem_title: string;
  current_step: number;
  total_steps: number;
  status: string;
}

export default function TroubleshootingDashboard() {
  const [metrics, setMetrics] = useState<TroubleshootingMetrics | null>(null);
  const [topProblems, setTopProblems] = useState<TopProblem[]>([]);
  const [activeSessions, setActiveSessions] = useState<ActiveSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    fetchMetrics();
    
    if (autoRefresh) {
      const interval = setInterval(fetchMetrics, 30000); // Cada 30 segundos
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/support/troubleshooting/realtime');
      const data = await response.json();
      
      setMetrics(data.metrics);
      setTopProblems(data.top_problems || []);
      setActiveSessions(data.active_sessions || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching metrics:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-6">Cargando métricas...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard de Troubleshooting</h1>
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
            className="rounded"
          />
          <span>Auto-refresh (30s)</span>
        </label>
      </div>

      {/* Métricas Principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Sesiones Activas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.active_sessions || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              En este momento
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Resueltas (última hora)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {metrics?.resolved_last_hour || 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Última hora
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Escaladas (última hora)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {metrics?.escalated_last_hour || 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Última hora
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tiempo Promedio
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics?.avg_resolution_time_minutes?.toFixed(1) || '0'} min
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Resolución promedio
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="problems" className="space-y-4">
        <TabsList>
          <TabsTrigger value="problems">Problemas Más Comunes</TabsTrigger>
          <TabsTrigger value="sessions">Sesiones Activas</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="problems" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Top Problemas (últimas 24h)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {topProblems.length === 0 ? (
                  <p className="text-muted-foreground">No hay datos disponibles</p>
                ) : (
                  topProblems.map((problem, index) => (
                    <div key={problem.detected_problem_id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="text-lg font-bold text-muted-foreground">#{index + 1}</span>
                          <h3 className="font-semibold">{problem.detected_problem_title}</h3>
                        </div>
                        <div className="mt-2 flex items-center space-x-4 text-sm text-muted-foreground">
                          <span>Total: {problem.count}</span>
                          <span>Resueltas: {problem.resolved_count}</span>
                          <span>
                            Tasa: {((problem.resolved_count / problem.count) * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                      <div className="w-32">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${(problem.resolved_count / problem.count) * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sessions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Sesiones Activas</CardTitle>
            </CardHeader>
            <CardContent>
              {activeSessions.length === 0 ? (
                <p className="text-muted-foreground">No hay sesiones activas</p>
              ) : (
                <div className="space-y-2">
                  {activeSessions.map((session) => (
                    <div key={session.session_id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">{session.customer_email}</p>
                          <p className="text-sm text-muted-foreground">
                            {session.detected_problem_title}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium">
                            Paso {session.current_step} de {session.total_steps}
                          </p>
                          <p className="text-xs text-muted-foreground capitalize">
                            {session.status}
                          </p>
                        </div>
                      </div>
                      <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${(session.current_step / session.total_steps) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Métricas Adicionales</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Problemas Únicos (24h)</p>
                  <p className="text-2xl font-bold">{metrics?.unique_problems_24h || 0}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Rating Promedio (24h)</p>
                  <p className="text-2xl font-bold">
                    {metrics?.avg_rating_24h ? metrics.avg_rating_24h.toFixed(1) : 'N/A'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}



