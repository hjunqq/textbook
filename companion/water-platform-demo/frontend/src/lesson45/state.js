// 同一时刻只处于一种状态，渲染函数只看状态不看网络
export const State = { LOADING: 'loading', READY: 'ready', EMPTY: 'empty', ERROR: 'error' };

export function render(el, view) {
  el.dataset.state = view.state;              // 便于 CSS 与测试断言
  const name = view.asset.displayName;
  switch (view.state) {
    case State.LOADING: el.textContent = `正在读取 ${name}…`; break;
    case State.EMPTY:   el.textContent = `${name}：暂无观测`; break;
    case State.READY: {
      const r = view.reading;
      el.textContent = r.quality === 'missing'
        ? `${name}：该时刻缺测`
        : `${name}：${r.value} ${r.unit}（质量 ${r.quality}）`;
      break;
    }
    case State.ERROR:   el.textContent = messageFor(view.error); break;
  }
}

export function messageFor(error) {
  switch (error.status) {
    case 400: return `参数有误：${error.body.field ?? ''} ${error.body.message ?? ''}`.trim();
    case 401: return '登录已失效，请重新登录';
    case 403: return '当前角色无权查看该对象';
    case 404: return '对象不存在，请返回列表';
    default:  return '服务暂时不可用，请稍后重试';
  }
}
