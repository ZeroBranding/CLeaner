import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import create from 'zustand';
import { act } from '@testing-library/react';

// Wir müssen den tatsächlichen Store importieren nach dem Mocking von API
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

// Nun importieren wir den Store
import { useSystemStore } from './systemStore';

beforeEach(() => {
  axiosMockInstance.get.mockReset();
  axiosMockInstance.post.mockReset();
  useSystemStore.setState({}, true); // Store zurücksetzen
});

describe('useSystemStore', () => {
  it('initializes and fetches data', async () => {
    axiosMockInstance.get
      .mockResolvedValueOnce({ data: { os: 'linux' } }) // system/info
      .mockResolvedValueOnce({ data: { scans: [] } }) // scan/history
      .mockResolvedValueOnce({ data: { auto_scan_enabled: true, data_sharing_enabled: false } }); // settings

    await act(async () => {
      await useSystemStore.getState().initialize();
    });

    const state = useSystemStore.getState();
    expect(state.isInitialized).toBe(true);
    expect(state.systemInfo).toEqual({ os: 'linux' });
    expect(axiosMockInstance.get).toHaveBeenCalledTimes(3);
  });

  it('selects and deselects items', () => {
    const path = '/tmp/test.file';
    act(() => {
      useSystemStore.getState().selectItem(path);
    });
    expect(useSystemStore.getState().selectedItems).toContain(path);

    act(() => {
      useSystemStore.getState().deselectItem(path);
    });
    expect(useSystemStore.getState().selectedItems).not.toContain(path);
  });
});