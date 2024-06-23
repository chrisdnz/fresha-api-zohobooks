import { Session } from 'next-auth';
import { getSession } from 'next-auth/react';

export enum Method {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  DELETE = 'DELETE',
}

export const makeRequest = async (
  url: string,
  method: Method,
  body?: BodyInit
) => {
  const session = (await getSession()) as Session & { accessToken: string };
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${url}`, {
    method,
    headers: {
      Accept: 'application/json',
      Authorization: session.accessToken,
    },
    body,
  });
  return response;
};
