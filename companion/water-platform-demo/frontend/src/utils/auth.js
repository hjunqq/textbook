// 令牌键名是前端各模块的共同契约（与第4章口径一致）
export const TOKEN_KEY = 'access_token';

export function getToken() { return sessionStorage.getItem(TOKEN_KEY); }
export function setToken(token) { sessionStorage.setItem(TOKEN_KEY, token); }
export function clearToken() { sessionStorage.removeItem(TOKEN_KEY); }
export function isLoggedIn() { return Boolean(getToken()); }
