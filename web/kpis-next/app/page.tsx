import dynamic from 'next/dynamic';

const Dashboard = dynamic(() => import('@/components/Dashboard'), { ssr: false });

export default function Page() {
	return (
		<main>
			<h1>KPIs en tiempo real</h1>
			<Dashboard />
		</main>
	);
}
