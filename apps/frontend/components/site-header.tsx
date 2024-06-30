'use client';

import { ReceiptText } from 'lucide-react';
import Link from 'next/link';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { User } from 'lucide-react';
import { Button } from './ui/button';
import { User as UserType } from 'next-auth';
import { signOut } from 'next-auth/react';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useTheme } from 'next-themes';

const navItems = [
  { label: 'Dashboard', href: '/dashboard' },
  { label: 'Settings', href: '/settings' },
];

export const SiteHeader = ({ user }: { user: UserType }) => {
  const path = usePathname();
  const { setTheme, theme } = useTheme();
  return (
    <header className="z-10 sticky top-0 flex h-16 items-center justify-between gap-4 border-b bg-background px-4 md:px-6">
      <nav className="hidden flex-col gap-6 text-lg font-medium md:flex md:flex-row md:items-center md:gap-5 md:text-sm lg:gap-6">
        <Link
          href="#"
          className="flex items-center gap-2 text-lg font-semibold md:text-base"
        >
          <ReceiptText className="h-6 w-6" />
          <span className="font-bold">Invoices</span>
        </Link>
        {navItems.map((item) => (
          <Link
            key={item.label}
            href={item.href}
            className={cn(
              'text-muted-foreground transition-colors hover:text-foreground',
              path === item.href && 'text-foreground'
            )}
          >
            {item.label}
          </Link>
        ))}
      </nav>
      <div className="flex items-center gap-4 md:ml-auto md:gap-2 lg:gap-4">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              size="icon"
              className="overflow-hidden rounded-full"
            >
              <User className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>{user.email}</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => {
                setTheme(theme === 'dark' ? 'light' : 'dark');
              }}
            >
              Toggle Theme
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => signOut()}>
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};
