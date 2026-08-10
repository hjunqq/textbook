<script setup>
import {ref} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import request from '../utils/request';
import {setToken} from '../utils/auth';

const route = useRoute();
const router = useRouter();
const username = ref('duty01');
const password = ref('');
const error = ref('');

function safeRedirect(value) {
  return typeof value === 'string' && value.startsWith('/') && !value.startsWith('//')
      ? value : '/monitoring';
}

async function submit() {
  error.value = '';
  try {
    const result = await request.post('/api/auth/login',
        {username: username.value, password: password.value});
    setToken(result.accessToken);
    await router.replace(safeRedirect(route.query.redirect));
  } catch (e) {
    error.value = e.status === 401 ? '用户名或密码错误' : '登录失败，请稍后重试';
  }
}
</script>

<template>
  <main class="login">
    <h1>清源水库安全监测平台</h1>
    <form @submit.prevent="submit">
      <label>账号<input v-model.trim="username" autocomplete="username" required></label>
      <label>密码<input v-model="password" type="password" autocomplete="current-password" required></label>
      <button type="submit">登录</button>
      <p v-if="error" role="alert">{{ error }}</p>
    </form>
    <p class="hint">教学账号：duty01/duty123（值班员）、analyst01/analyst123（专业分析员）、ops01/ops123（运维员）</p>
  </main>
</template>

<style scoped>.login{max-width:22rem;margin:10vh auto;display:grid;gap:1rem}form{display:grid;gap:.75rem}label{display:grid;gap:.25rem}.hint{color:#546e7a;font-size:.875rem}</style>
