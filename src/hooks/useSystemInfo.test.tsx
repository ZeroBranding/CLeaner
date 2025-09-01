import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import axios from 'axios';
vi.mock('axios');

function createAxiosMock() {
  return {
    get: vi.fn(),
    post: vi.fn(),
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  };
}
const axiosMockInstance = createAxiosMock();
(axios.create as unknown as vi.Mock).mockReturnValue(axiosMockInstance);

import { useSystemInfo } from './useSystemInfo';

function createWrapper() {
  const queryClient = new QueryClient();
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe('useSystemInfo hook', () => {
  it('fetches system information', async () => {
    const data = { os: 'linux' };
    axiosMockInstance.get.mockResolvedValueOnce({ data });

    const { result } = renderHook(() => useSystemInfo(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(data);
    expect(axiosMockInstance.get).toHaveBeenCalledWith('/system/info');
  });
});