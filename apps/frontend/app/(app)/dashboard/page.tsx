import { Button } from '@/components/ui/button';

import { RefreshCcw } from 'lucide-react';
import InvoicesTable from './client';

export default function Page() {
  return (
    <main className="flex min-h-[calc(100vh_-_theme(spacing.16))] flex-1 flex-col gap-4 bg-muted/40 p-4 md:gap-8 md:p-10">
      <div className="mx-auto items-center flex w-full max-w-6xl gap-2">
        <h1 className="text-3xl font-semibold">All Invoices</h1>
        <div className="ml-auto flex items-center gap-2">
          <Button variant="outline" className="gap-1">
            <RefreshCcw className="h-3.5 w-3.5" />
            <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
              Sync
            </span>
          </Button>
        </div>
      </div>
      <div className="mx-auto flex flex-col w-full max-w-6xl items-start gap-6">
        <InvoicesTable />
      </div>
    </main>
  );
}
