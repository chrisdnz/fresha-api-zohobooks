"use client";

import * as React from "react";
import { Button } from "./ui/button";
import { signIn } from "next-auth/react";
import { Loader2 } from "lucide-react";

export function UserAuthForm() {
  const [isLoading, setIsLoading] = React.useState(false);

  const signInWithZoho = async () => {
    setIsLoading(true);
    try {
      await signIn("zoho", {
        callbackUrl: "/dashboard",
      })
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <Button disabled={isLoading} onClick={signInWithZoho}>
        {isLoading && <Loader2 className="w-5 h-5 animate-spin" />}
        Login with Zoho
      </Button>
    </div>
  );
}
