import { SiteHeader } from "@/components/site-header";
import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";

interface Props {
  children: React.ReactNode;
}

export const metadata = {
  title: "Dashboard: Invoices",
};

export default async function Layout({ children }: Props) {
  const session = await auth();

  if (!session?.user) {
    redirect('/');
  }

  return (
    <div className="flex min-h-screen w-full flex-col bg-muted/40">
      <div className="flex flex-col sm:gap-4">
        {session?.user && <SiteHeader user={session?.user} />}
        <main className="flex min-h-[calc(100vh-80px)] flex-1 flex-col gap-4 p-4 md:gap-8 md:p-10">
          {children}
        </main>
      </div>
    </div>
  );
}
