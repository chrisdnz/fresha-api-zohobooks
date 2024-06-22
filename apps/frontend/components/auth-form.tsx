import { Button } from "./ui/button";
import { signIn } from "@/lib/auth";

export function UserAuthForm() {
  const signInWithZoho = async () => {
    "use server"
    await signIn("zoho", {
      redirectTo: "/dashboard"
    });
  };

  return (
    <div className="flex flex-col gap-4">
      <form className="w-full" action={signInWithZoho}>
        <Button className="w-full" type="submit">
          Login with Zoho
        </Button>
      </form>
    </div>
  );
}
