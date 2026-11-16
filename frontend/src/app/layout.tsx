import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Veloxa CXO Cockpit | Executive Intelligence',
  description: 'Grounded executive decision cockpit for Veloxa Technologies',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#0B0F17] text-slate-100 min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
