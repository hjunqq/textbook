<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { request, TOKEN_KEY } from '../api/request.js';

const route = useRoute();
const router = useRouter();
const account = ref('');
const password = ref('');
const errorMessage = ref('');

function safeRedirect(value) {
  return typeof value === 'string' && value.startsWith('/') && !value.startsWith('//')
    ? value : '/assets';
}
async function submit() {
  errorMessage.value = '';
  try {
    const result = await request('/api/auth/login', {
      method: 'POST', body: JSON.stringify({ username: account.value, password: password.value })
    });
    sessionStorage.setItem(TOKEN_KEY, result.accessToken);
    await router.replace(safeRedirect(route.query.redirect));
  } catch (error) {
    errorMessage.value = error.message || '登录失败，请稍后重试';
  }
}
</script>

<template>
  <form @submit.prevent="submit">
    <label>账号<input v-model.trim="account" autocomplete="username" required></label>
    <label>密码<input v-model="password" type="password" autocomplete="current-password" required></label>
    <button type="submit">登录</button>
    <p v-if="errorMessage" role="alert">{{ errorMessage }}</p>
  </form>
</template>
