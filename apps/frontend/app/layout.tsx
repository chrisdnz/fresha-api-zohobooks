import { Inter as FontSans } from 'next/font/google';

import { cn } from '@/lib/utils';

import './global.css';
import Providers from "@/components/context/providers";

const fontSans = FontSans({ subsets: ['latin'], variable: '--font-sans' });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={cn(
          'min-h-screen bg-background font-sans antialiased',
          fontSans.variable
        )}
      >
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
