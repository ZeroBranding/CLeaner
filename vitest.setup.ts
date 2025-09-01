import '@testing-library/jest-dom';

// Stubs für env Variablen
globalThis.import_meta = { env: { DEV: false, VITE_API_URL: 'http://localhost:8000/api' } } as any;