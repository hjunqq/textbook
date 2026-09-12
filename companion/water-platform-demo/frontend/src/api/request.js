const API_BASE = import.meta.env.VITE_API_ORIGIN ?? '';   // 契约路径已含 /api 前缀
const DEFAULT_TIMEOUT = 10_000;
// 令牌键名是前端各模块的共同契约：请求封装、路由守卫、
// 登录页都从这里导入，避免"登录成功却处处 401"的隐蔽错误
export const TOKEN_KEY = 'access_token';

function accessToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}

export async function request(path, options = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(
    () => controller.abort(), options.timeoutMs ?? DEFAULT_TIMEOUT
  );
  const headers = new Headers(options.headers);
  headers.set('Accept', 'application/json');
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  const token = accessToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options, headers, signal: controller.signal
    });
    if (response.status === 401 && !path.startsWith('/api/auth/')) {
      // 业务请求的 401 才代表登录态失效；
      // 登录接口自身的 401 是"密码错误"，交回页面层提示
      sessionStorage.removeItem(TOKEN_KEY);
      const redirect = encodeURIComponent(location.pathname + location.search);
      location.assign(`/login?redirect=${redirect}`);
      throw new Error('UNAUTHORIZED');
    }
    if (!response.ok) throw new Error(`HTTP_${response.status}`);
    if (response.status === 204) return null;
    return response.json();
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('REQUEST_TIMEOUT', { cause: error });
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}
