import {clearToken, getToken} from './auth';

const API_ORIGIN = import.meta.env.VITE_API_ORIGIN || '';

async function request(path, options = {}) {
  const headers = {Accept: 'application/json', ...(options.body ? {'Content-Type': 'application/json'} : {})};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${API_ORIGIN}${path}`, {...options, headers});
  if (response.status === 401 && !path.startsWith('/api/auth/')) {
    // 业务请求的 401 代表登录态失效；登录接口自身的 401 是口令错误，交回页面提示
    clearToken();
    const redirect = encodeURIComponent(location.pathname + location.search);
    location.assign(`/login?redirect=${redirect}`);
    throw Object.assign(new Error('UNAUTHORIZED'), {status: 401});
  }
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
