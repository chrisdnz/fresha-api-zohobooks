import useSWR from 'swr';
import { Method, makeRequest } from '../makerequest';

export const useTransactions = () => {
  return useSWR('/api/v1/zoho/transactions', async (url) => {
    const response = await makeRequest(url, Method.GET);
    const data = await response.json();
    return data;
  });
};
