import dynamic from 'next/dynamic';

const EtlDashboard = dynamic(() => import('@/components/EtlDashboard'), { ssr: false });

export default function Page() {
  return (
    <main>
      <h1>ETL Metrics & Alerts</h1>
      <EtlDashboard />
    </main>
  );
}


