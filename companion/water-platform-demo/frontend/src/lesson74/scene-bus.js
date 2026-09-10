// S5 阶段包：应用层的场景封装。
//
// 7.3 节清单“ECharts与Three.js对象的双向联动控制器”里有一句注释：
//   “scene 是应用层的场景封装对象（带事件总线），不是 THREE.Scene 本身——后者没有 on/off 接口”。
// 这个文件就是那个封装。它把三件事包起来：
//   1) 事件总线（on / off / emit），让联动控制器可以订阅 'select'；
//   2) focusAsset(assetId, occurredAt)，把某个测点高亮并记录时刻；
//   3) 释放，卸载页面时把监听器和材质一起清掉。
//
// 它不 import three：高亮只改 mesh.material.color，拾取结果由外部传入。
// 这样做的直接好处是——这个模块可以在没有 WebGL、没有浏览器的环境里被测试。

/** 高亮颜色：与 6.1 节绑定时的默认蓝 0x1565c0 区分开 */
const HIGHLIGHT = 0xffa000;
const NORMAL = 0x1565c0;

export function createSceneBus(bound) {
  const listeners = new Map();          // 事件名 -> Set<处理函数>
  let focused = null;                   // 当前高亮的 assetId
  let focusedAt = null;                 // 当前关注的时刻，供详情卡显示

  const bus = {
    on(event, handler) {
      if (!listeners.has(event)) listeners.set(event, new Set());
      listeners.get(event).add(handler);
      return bus;
    },
    off(event, handler) {
      listeners.get(event)?.delete(handler);
      return bus;
    },
    emit(event, payload) {
      // 复制一份再遍历：处理函数里调用 off 时不会破坏正在进行的迭代
      for (const handler of [...(listeners.get(event) ?? [])]) {
        // 本次分发中已经解绑的旧曲线处理器也不能继续响应。
        if (listeners.get(event)?.has(handler)) handler(payload);
      }
      return bus;
    },

    /**
     * 高亮某个测点。图表点击时由联动控制器调用。
     * 找不到对象返回 false——这通常意味着图表里有一条曲线，
     * 场景里却没有对应的球（台账缺坐标，或者绑定时被跳过了）。
     */
    focusAsset(assetId, occurredAt = null) {
      const mesh = bound.find(assetId);
      if (!mesh) return false;
      if (focused && focused !== assetId) {
        bound.find(focused)?.material.color.set(NORMAL);
      }
      mesh.material.color.set(HIGHLIGHT);
      focused = assetId;
      focusedAt = occurredAt;
      return true;
    },

    /** 用户点了三维对象：由拾取结果调用，向订阅者广播 select 事件。 */
    select(mesh) {
      if (!mesh?.userData?.assetId) return false;
      bus.focusAsset(mesh.userData.assetId);
      bus.emit('select', mesh);
      return true;
    },

    get focused() { return focused; },
    get focusedAt() { return focusedAt; },

    dispose() {
      if (focused) bound.find(focused)?.material.color.set(NORMAL);
      focused = null;
      focusedAt = null;
      listeners.clear();
    },
  };
  return bus;
}
