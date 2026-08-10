// @vitest-environment jsdom
import {beforeEach, describe, expect, it} from 'vitest';
import {TOKEN_KEY, clearToken, getToken, isLoggedIn, setToken} from '../src/utils/auth';

describe('token contract', () => {
  beforeEach(() => sessionStorage.clear());

  it('uses one shared storage key across the app', () => {
    expect(TOKEN_KEY).toBe('access_token');
  });

  it('round-trips login state', () => {
    expect(isLoggedIn()).toBe(false);
    setToken('token-value');
    expect(getToken()).toBe('token-value');
    expect(isLoggedIn()).toBe(true);
    clearToken();
    expect(isLoggedIn()).toBe(false);
  });
});
