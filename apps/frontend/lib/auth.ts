import NextAuth from 'next-auth';
import Zoho from 'next-auth/providers/zoho';

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [Zoho]
});
