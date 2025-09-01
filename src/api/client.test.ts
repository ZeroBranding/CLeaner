import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import api, { apiHelpers, endpoints } from './client';

vi.mock('axios');

// Hilfsfunktion, um Axios-Mock mit Interceptors zu erstellen
function createAxiosMock() {
  return {
    get: vi.fn(),
    post: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  };
}

const axiosMockInstance = createAxiosMock();
(axios.create as unknown as vi.Mock).mockReturnValue(axiosMockInstance);

beforeEach(() => {
  axiosMockInstance.get.mockReset();
  axiosMockInstance.post.mockReset();
});

describe('apiHelpers', () => {
  it('should call system info endpoint', async () => {
    const data = { os: 'linux' };
    axiosMockInstance.get.mockResolvedValue({ data });
    const response = await apiHelpers.getSystemInfo();
    expect(axiosMockInstance.get).toHaveBeenCalledWith(endpoints.systemInfo);
    expect(response.data).toEqual(data);
  });

  it('should start scan with correct payload', async () => {
    const categories = ['junk', 'cache'];
    axiosMockInstance.post.mockResolvedValue({ data: { ok: true } });
    await apiHelpers.startScan(categories, true);
    expect(axiosMockInstance.post).toHaveBeenCalledWith(endpoints.scanStart, {
      categories,
      enable_ai: true,
      user_id: 'default',
    });
  });

  it('should fetch scan status', async () => {
    axiosMockInstance.get.mockResolvedValue({ data: { status: 'running' } });
    await apiHelpers.getScanStatus(5);
    expect(axiosMockInstance.get).toHaveBeenCalledWith(endpoints.scanStatus(5));
  });
});