const API_ORIGIN = import.meta.env.VITE_API_ORIGIN || '';

async function request(path, options = {}) {
  const response = await fetch(`${API_ORIGIN}${path}`, {
    credentials: 'include',
    headers: { Accept: 'application/json', ...(options.body ? {'Content-Type': 'application/json'} : {}) },
    ...options,
  });
  if (!response.ok) {
    const error = new Error(`HTTP ${response.status}`);
    error.status = response.status;
    error.payload = await response.json().catch(() => ({}));
    throw error;
  }
  return response.status === 204 ? null : response.json();
}

export default {
  get: (path, params = {}) => request(`${path}?${new URLSearchParams(params)}`),
  post: (path, body) => request(path, {method: 'POST', body: JSON.stringify(body)}),
};
