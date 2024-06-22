import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";

interface Props {
  children: React.ReactNode;
}

export default async function Layout({ children }: Props) {
  const session = await auth();

  if (!session?.user) {
    redirect('/');
  }

  return (
    <div className="flex min-h-screen w-full flex-col bg-muted/40">
      {children}
    </div>
  );
}
