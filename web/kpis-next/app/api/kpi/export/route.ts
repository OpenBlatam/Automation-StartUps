import { NextRequest, NextResponse } from 'next/server';
import { fetchSummary, fetchRevenue24h, fetchAging, fetchRevenue } from '@/lib/kpi';
import { arrayToCSV, generateExcelXML } from '@/lib/excel';

export const runtime = 'nodejs';

/**
 * GET /api/kpi/export
 * Export KPI data to Excel or CSV
 * Query params: format (excel|csv), type (summary|revenue|aging|full)
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const format = searchParams.get('format') || 'excel'; // excel, csv
    const exportType = searchParams.get('type') || 'full'; // summary, revenue, aging, full
    const period = searchParams.get('period') || 'daily'; // daily, monthly

    let data: any[] = [];
    let filename = '';

    switch (exportType) {
      case 'summary':
        const summary = await fetchSummary();
        data = [
          { metric: 'Revenue (última hora)', value: summary.revenue_last_hour },
          { metric: 'Revenue (24h)', value: summary.revenue_24h },
          ...summary.leads_by_priority_today.map(l => ({
            metric: `Leads ${l.priority || 'unknown'}`,
            value: l.count
          })),
        ];
        filename = `kpi-summary-${new Date().toISOString().split('T')[0]}`;
        break;

      case 'revenue':
        const revenue = await fetchRevenue(period === 'monthly' ? 'monthly' : 'daily');
        data = revenue.map(r => ({
          periodo: r.period,
          facturas: r.invoice_count,
          revenue: r.revenue,
          impuestos: r.taxes,
          subtotal: r.subtotal,
        }));
        filename = `kpi-revenue-${period}-${new Date().toISOString().split('T')[0]}`;
        break;

      case 'aging':
        const aging = await fetchAging();
        data = aging.map(a => ({
          bucket: a.bucket,
          facturas: a.invoice_count,
          monto_total: a.total_amount,
        }));
        filename = `kpi-aging-${new Date().toISOString().split('T')[0]}`;
        break;

      case 'full':
      default:
        const [summaryFull, series, agingFull, revenueFull] = await Promise.all([
          fetchSummary(),
          fetchRevenue24h(),
          fetchAging(),
          fetchRevenue('daily'),
        ]);

        // Combine all data
        data = [
          // Summary
          { section: 'Resumen', metric: 'Revenue (última hora)', value: summaryFull.revenue_last_hour },
          { section: 'Resumen', metric: 'Revenue (24h)', value: summaryFull.revenue_24h },
          ...summaryFull.leads_by_priority_today.map(l => ({
            section: 'Resumen',
            metric: `Leads ${l.priority || 'unknown'}`,
            value: l.count
          })),
          // Revenue timeseries
          ...series.map(s => ({
            section: 'Revenue 24h',
            hora: s.time,
            revenue: s.revenue,
          })),
          // Aging
          ...agingFull.map(a => ({
            section: 'A/R Aging',
            bucket: a.bucket,
            facturas: a.invoice_count,
            monto: a.total_amount,
          })),
          // Revenue daily
          ...revenueFull.map(r => ({
            section: 'Revenue Diario',
            periodo: r.period,
            facturas: r.invoice_count,
            revenue: r.revenue,
          })),
        ];
        filename = `kpi-full-${new Date().toISOString().split('T')[0]}`;
        break;
    }

    if (format === 'csv') {
      const csvContent = arrayToCSV(data);
      return new Response(csvContent, {
        headers: {
          'Content-Type': 'text/csv;charset=utf-8',
          'Content-Disposition': `attachment; filename="${filename}.csv"`,
        },
      });
    } else {
      // Excel XML format
      const excelContent = generateExcelXML(data, {
        filename: `${filename}.xls`,
        sheetName: 'KPIs',
      });
      return new Response(excelContent, {
        headers: {
          'Content-Type': 'application/vnd.ms-excel',
          'Content-Disposition': `attachment; filename="${filename}.xls"`,
        },
      });
    }
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to export data' },
      { status: 500 }
    );
  }
}


