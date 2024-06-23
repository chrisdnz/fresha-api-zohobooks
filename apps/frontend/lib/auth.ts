import NextAuth from 'next-auth';
import Zoho from 'next-auth/providers/zoho';

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [Zoho],
  callbacks: {
    jwt({ token, account, user }) {
      if (user) {
        token.id = user.id;
      }
      if (account) {
        token.accessToken = account.access_token;
      }

      return token;
    },
    session({ session, token }: { session: any; token: any }) {
      session.accessToken = token.accessToken;
      return session;
    },
  },
});
