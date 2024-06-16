import NextAuth from 'next-auth';
import ZohoProvider from 'next-auth/providers/zoho';

export const authOptions = {
  // Configure one or more authentication providers
  providers: [
    ZohoProvider({
      clientId: process.env.ZOHO_CLIENT_ID!,
      clientSecret: process.env.ZOHO_CLIENT_SECRET!,
    })
  ],
};

export default NextAuth(authOptions);
