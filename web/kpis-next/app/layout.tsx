export const metadata = { title: 'KPIs', description: 'KPIs en tiempo real' };

export default function RootLayout({ children }: { children: React.ReactNode }) {
	return (
		<html lang="es">
			<body style={{ fontFamily: 'system-ui,Arial', margin: 24 }}>{children}</body>
		</html>
	);
}
