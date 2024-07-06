'use client';

import { MoreHorizontal } from 'lucide-react';

import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useInvoices } from '@/lib/hooks/invoices';
import { HNLCurrency } from '@/lib/utils';

export default function InvoicesTable() {
  const { data } = useInvoices();
  return (
    <Card className="w-full">
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Payment No.</TableHead>
              <TableHead>Client</TableHead>
              <TableHead>Method</TableHead>
              <TableHead>Total Sale</TableHead>
              <TableHead>Created at</TableHead>
              <TableHead>
                <span className="sr-only">Actions</span>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {/* TODO: Correct type here */}
            {/* {data?.map((transaction: any) => (
              <TableRow key={transaction["Payment no."]}>
                <TableCell>{transaction["Payment no."]}</TableCell>
                <TableCell>{transaction["Client"]}</TableCell>
                <TableCell>{transaction["Payment method"]}</TableCell>
                <TableCell>{HNLCurrency(transaction["Payment amount"])}</TableCell>
                <TableCell>{transaction["Sale date"]}</TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button aria-haspopup="true" size="icon" variant="ghost">
                        <MoreHorizontal className="h-4 w-4" />
                        <span className="sr-only">Toggle menu</span>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuLabel>Actions</DropdownMenuLabel>
                      <DropdownMenuItem>Save</DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))} */}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
