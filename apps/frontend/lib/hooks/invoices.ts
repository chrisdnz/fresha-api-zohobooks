import useSWR from 'swr';
import { Method, makeRequest } from '../makerequest';

export const useInvoices = () => {
  return useSWR('/api/v1/sales', async (url) => {
    const response = await makeRequest(url, Method.GET);
    const data = await response.json();
    return data;
  });
};
