## 4.5 Vue基础框架开发

<!--
教材内容修改指导原则（2024年更新）：

1. 内容详实化原则：
   - 每个技术标签/概念都要有详细的功能解释和使用场景说明
   - 不能只有简短描述，必须包含：定义、特点、优势、适用场景
   - 解释要在代码示例之前，先理论后实践

2. 语言表达多样化原则：
   - 避免重复使用"智慧水利平台"等固定短语
   - 使用多样化表达：水利监测平台、监测系统、水利系统、数据监测系统等
   - 保持专业性的同时提升可读性

3. 代码示例实用化原则：
   - 代码要短小精悍，每个概念单独展示
   - 包含必要的属性和配置参数
   - 添加适当的注释说明
   - 提供完整但不冗长的示例

4. 教学结构规范化原则：
   - 采用"解释说明 + 代码示例"的结构
   - 重要概念用**重点内容**标注
   - 相关概念用表格形式总结
   - 章节末尾提供总结和过渡

5. 专业应用场景化原则：
   - 所有示例都要结合水利行业实际应用
   - 强调技术在实际项目中的价值
   - 提供具体的使用场景描述
-->

Vue.js是构建现代水利监测平台前端界面的核心技术框架。作为一款渐进式JavaScript框架，Vue以其简洁的API、出色的性能和灵活的架构设计，特别适合开发复杂的水利数据管理系统。在智慧水利领域，Vue.js能够优雅地处理大量实时监测数据的展示、复杂的用户交互逻辑以及多样化的数据可视化需求。

现代前端开发已从传统的jQuery DOM操作模式进化为组件化、数据驱动的开发范式。Vue.js通过引入MVVM（Model-View-ViewModel）架构模式，实现了数据与视图的双向绑定，大大提升了开发效率和代码可维护性。对于水利监测系统而言，这意味着当传感器数据发生变化时，相关的图表、仪表盘和预警信息能够自动更新，无需手动操作DOM元素。

本节将深入探讨Vue.js框架的核心概念和开发方法，从前端框架的选择原则出发，详细讲解Vue.js的MVVM模式、响应式数据绑定、组件化开发以及路由和状态管理等关键技术。通过丰富的水利行业实例，帮助读者掌握使用Vue.js构建现代化水利监测平台的完整技能。

!!! info "Vue.js学习重点"
    
    在学习Vue.js框架之前，我们需要理解现代前端框架解决的核心问题：如何高效地管理应用状态、如何组织复杂的用户界面、如何提升开发效率和代码可维护性。

## 4.5.1 前端框架演进与选择

### 前端开发的历史演进

现代前端开发经历了从静态网页到动态应用的深刻变革。在Web技术发展的早期阶段，网页主要以展示静态内容为主，HTML负责结构，CSS负责样式，JavaScript仅用于简单的交互效果。随着互联网应用复杂度的不断增加，特别是像水利监测系统这样需要处理大量动态数据的应用，传统的开发模式逐渐显露出局限性。

**传统Web开发模式的局限性**包括：

- **DOM操作复杂度高**：手动操作DOM元素容易出错，代码难以维护

  传统Web开发采用命令式编程模式，要求开发者明确指定每一步操作：查找DOM节点、修改属性、更新内容、处理事件等。这种方式在处理复杂的数据变化和界面更新时会产生大量重复、易错的代码。

  考虑一个实际的用户管理界面需求：当用户点击"删除用户"按钮时，需要完成以下一系列DOM操作：

  ```javascript
  // 传统方式需要逐步操作每个相关元素
  function deleteUser(userId) {
    // 1. 从用户列表中移除该行
    const userRow = document.getElementById('user-' + userId);
    userRow.parentNode.removeChild(userRow);
    
    // 2. 更新用户总数显示
    const totalCount = document.getElementById('total-users');
    const currentCount = parseInt(totalCount.textContent) - 1;
    totalCount.textContent = currentCount;
    
    // 3. 更新分页信息
    const currentPage = Math.ceil(currentCount / pageSize);
    document.getElementById('current-page').textContent = currentPage;
    
    // 4. 如果当前页没有数据了，跳转到上一页
    if (currentCount % pageSize === 0 && currentPage > 1) {
      loadPage(currentPage - 1);
    }
    
    // 5. 更新权限统计（如果被删除的是管理员）
    if (user.role === 'admin') {
      const adminCount = document.getElementById('admin-count');
      adminCount.textContent = parseInt(adminCount.textContent) - 1;
    }
    
    // 6. 显示操作成功提示
    showToast('用户删除成功');
    
    // 7. 如果删除的是当前用户，需要额外处理
    if (userId === currentUserId) {
      logout();
    }
  }
  ```

  这种做法存在严重问题。首先是**操作步骤繁琐且容易出错**：开发者必须记住并正确执行每一个更新步骤，任何遗漏都会导致界面状态不一致。比如忘记更新用户总数，或者忘记处理分页逻辑，用户就会看到错误的信息。

  其次是**代码维护困难**：当界面结构发生变化时（比如用户列表改为卡片布局），所有相关的DOM选择器和操作代码都需要重新编写。如果产品经理要求在删除用户时添加确认对话框，或者需要记录操作日志，就要在多个地方插入新的代码逻辑。

  最严重的是**错误定位复杂**：当用户报告"删除用户后页面显示有问题"时，开发者需要检查上述所有步骤，任何一个环节都可能是问题所在。而且这些操作往往有时序依赖关系，A操作失败可能导致B操作的执行环境发生变化，使得错误传播和定位变得非常困难。

- **代码组织困难**：缺乏模块化机制，大型项目结构混乱

  传统Web开发缺乏有效的模块化机制，导致代码组织混乱。开发者往往将不同层次的逻辑混合在一起：数据获取、业务处理、界面更新、事件响应都写在同一个文件中，形成高度耦合的代码结构。

  以一个真实的电商网站购物车功能为例，传统开发方式可能产生如下代码：

  ```javascript
  // cart.js - 所有购物车功能混合在一个文件中
  
  // 全局变量散布各处
  var cartItems = [];
  var totalPrice = 0;
  var discountRate = 0;
  var shippingFee = 10;
  
  // 数据获取函数
  function loadCartData() {
    $.ajax({
      url: '/api/cart',
      success: function(data) {
        cartItems = data.items;
        updateCartDisplay();
        calculateTotal();
        updateShippingInfo();
        checkCouponValidity();
      }
    });
  }
  
  // UI更新函数
  function updateCartDisplay() {
    var html = '';
    for (var i = 0; i < cartItems.length; i++) {
      html += '<div class="cart-item" id="item-' + cartItems[i].id + '">';
      html += '<span>' + cartItems[i].name + '</span>';
      html += '<input type="number" value="' + cartItems[i].quantity + '" onchange="updateQuantity(' + cartItems[i].id + ', this.value)">';
      html += '<button onclick="removeItem(' + cartItems[i].id + ')">删除</button>';
      html += '</div>';
    }
    document.getElementById('cart-list').innerHTML = html;
  }
  
  // 业务逻辑函数
  function calculateTotal() {
    totalPrice = 0;
    for (var i = 0; i < cartItems.length; i++) {
      totalPrice += cartItems[i].price * cartItems[i].quantity;
    }
    totalPrice = totalPrice * (1 - discountRate) + shippingFee;
    document.getElementById('total-price').textContent = '￥' + totalPrice.toFixed(2);
  }
  
  // 事件处理函数
  function updateQuantity(itemId, newQuantity) {
    // 业务逻辑
    for (var i = 0; i < cartItems.length; i++) {
      if (cartItems[i].id === itemId) {
        cartItems[i].quantity = parseInt(newQuantity);
        break;
      }
    }
    
    // UI更新
    calculateTotal();
    updateInventoryWarning(itemId);
    saveToLocalStorage();
    
    // 数据同步
    $.post('/api/cart/update', {
      itemId: itemId,
      quantity: newQuantity
    });
  }
  ```

  这种代码组织方式存在以下严重问题：

  **功能耦合严重**：数据处理、界面渲染、事件响应、API调用都混合在一起。修改价格计算逻辑可能意外影响到界面渲染，调整界面布局可能破坏事件绑定。

  **全局状态污染**：大量全局变量使得状态管理变得混乱。`cartItems`、`totalPrice`等变量可能在任何地方被修改，很难追踪状态变化的来源和影响范围。

  **代码复用困难**：购物车的计算逻辑、界面组件、数据处理等功能无法独立使用。如果要在其他页面实现类似的商品列表功能，只能复制粘贴部分代码，然后进行大量修改。

  **测试和调试困难**：由于功能高度耦合，很难对单个功能进行独立测试。要测试价格计算是否正确，必须同时准备DOM环境、模拟AJAX请求、设置全局变量等。

  **团队协作冲突**：多个开发者同时修改同一个大文件时，容易产生代码冲突。而且由于缺乏清晰的模块边界，很难进行合理的任务分工。

- **数据同步问题**：界面状态与数据状态不一致，需要大量同步代码

  在传统Web开发中，最令开发者头痛的问题之一就是数据同步。当同一份数据需要在页面的多个位置显示时，保持这些显示的一致性变得极其困难。问题的核心在于缺乏统一的数据源管理机制。

  以一个在线聊天应用为例，当用户的在线状态发生变化时，需要同步更新的地方包括：

  ```javascript
  // 传统方式：手动同步所有相关显示
  function updateUserOnlineStatus(userId, isOnline) {
    // 1. 更新好友列表中的状态图标
    const friendItem = document.querySelector(`#friend-${userId} .status-icon`);
    if (friendItem) {
      friendItem.className = isOnline ? 'status-online' : 'status-offline';
    }
    
    // 2. 更新聊天窗口标题栏的状态
    const chatTitle = document.querySelector(`#chat-${userId} .user-status`);
    if (chatTitle) {
      chatTitle.textContent = isOnline ? '在线' : '离线';
    }
    
    // 3. 更新群聊中的成员列表
    const groupMembers = document.querySelectorAll(`.group-member[data-user="${userId}"]`);
    groupMembers.forEach(member => {
      member.setAttribute('data-status', isOnline ? 'online' : 'offline');
    });
    
    // 4. 更新顶部在线人数统计
    const onlineCount = document.querySelector('#online-count');
    if (onlineCount) {
      const current = parseInt(onlineCount.textContent);
      onlineCount.textContent = isOnline ? current + 1 : current - 1;
    }
    
    // 5. 更新个人资料页面的状态
    const profileStatus = document.querySelector(`#profile-${userId} .status`);
    if (profileStatus) {
      profileStatus.textContent = isOnline ? '当前在线' : '最后在线：刚刚';
    }
  }
  ```

  这种手动同步方式存在严重问题：

  **遗漏更新风险高**：开发者必须记住所有使用该数据的地方。当添加新功能时（比如在消息气泡旁显示发送者状态），很容易忘记在状态更新函数中添加相应的同步逻辑。

  **状态不一致难以发现**：用户可能看到好友列表显示"在线"，但聊天窗口显示"离线"。这种不一致往往只在特定操作序列下出现，很难重现和调试。

  **代码重复和冗余**：每种数据类型都需要编写类似的同步函数。用户头像、昵称、签名等信息的更新都要写一套类似的代码。

  **时序问题复杂**：如果多个数据同时变化（比如用户既改了头像又改了昵称），必须确保更新的顺序正确，避免出现中间状态。

  **性能问题突出**：每次数据变化都可能触发大量DOM查询和更新操作，即使某些元素当前不可见或不需要更新。

  更严重的是，当业务逻辑复杂化时，数据之间可能存在依赖关系。比如用户状态变化可能影响群组的活跃度计算，群组活跃度又影响推荐算法的权重。这种联动关系使得同步逻辑变得极其复杂，任何一个环节出错都可能产生连锁反应。

- **开发效率低下**：重复编写类似功能，缺乏代码复用机制

  传统Web开发的低效率主要体现在大量重复性工作上。由于缺乏有效的抽象和组件化机制，开发者经常需要为相似的功能重新编写代码，这不仅浪费时间，还容易引入错误。

  以一个企业管理系统的表格功能为例，系统中可能需要多个数据表格：员工列表、部门列表、项目列表、财务记录等。传统开发方式下，每个表格都需要独立实现：

  ```javascript
  // 员工列表表格
  function createEmployeeTable(employees) {
    var html = '<table class="employee-table">';
    html += '<thead><tr>';
    html += '<th onclick="sortEmployees(\'name\')">姓名 <span id="name-sort">↕</span></th>';
    html += '<th onclick="sortEmployees(\'department\')">部门 <span id="dept-sort">↕</span></th>';
    html += '<th onclick="sortEmployees(\'salary\')">薪资 <span id="salary-sort">↕</span></th>';
    html += '<th>操作</th>';
    html += '</tr></thead><tbody>';
    
    for (var i = 0; i < employees.length; i++) {
      html += '<tr>';
      html += '<td>' + employees[i].name + '</td>';
      html += '<td>' + employees[i].department + '</td>';
      html += '<td>' + employees[i].salary + '</td>';
      html += '<td><button onclick="editEmployee(' + employees[i].id + ')">编辑</button>';
      html += '<button onclick="deleteEmployee(' + employees[i].id + ')">删除</button></td>';
      html += '</tr>';
    }
    html += '</tbody></table>';
    
    // 分页控制
    html += '<div class="pagination">';
    for (var page = 1; page <= Math.ceil(employees.length / 10); page++) {
      html += '<button onclick="loadEmployeePage(' + page + ')">' + page + '</button>';
    }
    html += '</div>';
    
    document.getElementById('employee-container').innerHTML = html;
  }
  
  // 项目列表表格 - 几乎相同的代码结构
  function createProjectTable(projects) {
    var html = '<table class="project-table">';
    html += '<thead><tr>';
    html += '<th onclick="sortProjects(\'name\')">项目名 <span id="name-sort">↕</span></th>';
    html += '<th onclick="sortProjects(\'status\')">状态 <span id="status-sort">↕</span></th>';
    html += '<th onclick="sortProjects(\'deadline\')">截止日期 <span id="deadline-sort">↕</span></th>';
    html += '<th>操作</th>';
    html += '</tr></thead><tbody>';
    
    for (var i = 0; i < projects.length; i++) {
      html += '<tr>';
      html += '<td>' + projects[i].name + '</td>';
      html += '<td>' + projects[i].status + '</td>';
      html += '<td>' + projects[i].deadline + '</td>';
      html += '<td><button onclick="editProject(' + projects[i].id + ')">编辑</button>';
      html += '<button onclick="deleteProject(' + projects[i].id + ')">删除</button></td>';
      html += '</tr>';
    }
    html += '</tbody></table>';
    
    // 相同的分页代码
    html += '<div class="pagination">';
    for (var page = 1; page <= Math.ceil(projects.length / 10); page++) {
      html += '<button onclick="loadProjectPage(' + page + ')">' + page + '</button>';
    }
    html += '</div>';
    
    document.getElementById('project-container').innerHTML = html;
  }
  ```

  这种重复开发模式存在以下问题：

  **大量重复代码**：表格的HTML结构、排序逻辑、分页功能在每个实现中都基本相同，但需要重复编写。这不仅浪费开发时间，还会导致代码库膨胀。

  **维护成本高昂**：当需要修改表格样式或功能时（比如改变分页按钮的样式，或添加批量操作功能），必须在每个表格实现中都进行相同的修改。

  **错误重复传播**：如果某个表格实现中存在Bug（比如排序逻辑错误），这个错误很可能在复制粘贴到其他表格时被重复引入。

  **功能不一致**：由于是手动复制和修改，不同表格的行为可能存在细微差异，导致用户体验不一致。

  **新功能开发缓慢**：每次添加新的列表页面时，都需要重新实现整套表格功能，即使核心逻辑几乎相同。

  **技能学习重复**：团队新成员需要理解多个相似但不同的实现，学习成本高，而且容易在不同实现之间产生混淆。

  这种低效率问题在复杂项目中会被显著放大。一个中等规模的Web应用可能包含几十个类似的界面组件，如果没有有效的复用机制，开发团队会把大量时间浪费在重复劳动上，而不是专注于业务逻辑和用户体验的优化。

在实际的业务开发中，这些问题往往同时出现，相互影响，使得传统开发模式难以应对现代Web应用的复杂需求。例如，当需要在一个项目管理系统中同时更新任务状态、团队统计和进度图表时，传统方式需要分别操作多个DOM元素，编写大量同步代码，代码组织混乱且容易出错。

```javascript
// 传统jQuery方式更新水利监测数据（示例）
function updateWaterLevel(stationId, newLevel) {
    // 更新图表
    $('#chart-' + stationId).updateChart(newLevel);
    // 更新表格
    $('#table-row-' + stationId + ' .water-level').text(newLevel + 'm');
    // 更新预警状态
    if (newLevel > 5.0) {
        $('#warning-' + stationId).addClass('alert-danger').text('高水位警告');
    }
    // 更新统计数据
    $('#total-stations').text(calculateActiveStations());
}
```

这种方式的问题在于，每次数据更新都需要手动操作多个DOM元素，代码分散且难以维护。当监测站点增加或界面结构调整时，需要修改大量相关代码。

### 现代前端框架的优势

现代前端框架通过引入**声明式编程**、**组件化架构**和**数据驱动**等理念，从根本上解决了传统开发模式的问题：

```vue
<!-- Vue.js方式处理水利监测数据更新 -->
<template>
  <div class="water-station-monitor">
    <!-- 数据变化时，界面自动更新 -->
    <water-level-chart :data="stationData.level" :station-id="stationId" />
    <data-table :rows="tableData" />
    <alert-panel :status="warningStatus" :level="stationData.level" />
    <statistics-summary :total="totalActiveStations" />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

// 响应式数据，变化时自动更新相关视图
const stationData = ref({
  level: 4.2,
  flowRate: 15.8,
  temperature: 18.5
})

// 计算属性，依赖数据变化时自动重新计算
const warningStatus = computed(() => {
  return stationData.value.level > 5.0 ? 'danger' : 'normal'
})

// 监听数据变化，执行相关逻辑
watch(() => stationData.value.level, (newLevel) => {
  if (newLevel > 5.0) {
    triggerWarningAlert(newLevel)
  }
})
</script>
```

### 主流前端框架对比分析

在选择前端框架时，我们需要从多个维度进行综合评估。目前主流的前端框架主要包括React、Angular和Vue.js，它们各有特点和适用场景：

| 对比维度 | React | Angular | Vue.js |
|---------|-------|---------|---------|
| **学习曲线** | 中等 | 较陡峭 | 较平缓 |
| **开发理念** | 函数式编程 | 面向对象 | 渐进式 |
| **生态系统** | 丰富但分散 | 完整统一 | 精选集成 |
| **性能表现** | 优秀 | 良好 | 优秀 |
| **文档质量** | 良好 | 详细 | 优秀 |
| **社区活跃度** | 非常高 | 高 | 高 |
| **企业采用度** | 很高 | 高 | 较高 |

对于**水利监测平台**的特定需求，我们需要考虑以下因素：

**1. 开发团队技术背景**
- 团队规模通常中等，需要较短的学习周期
- 多数开发者具备HTML、CSS、JavaScript基础
- 需要快速上手并投入生产开发

**2. 项目复杂度与维护性**
- 水利系统通常需要长期维护和功能迭代
- 业务逻辑相对固定，界面变化频繁
- 需要良好的代码组织和模块化支持

**3. 性能要求**
- 需要处理大量实时监测数据
- 要求流畅的用户交互体验
- 支持数据可视化和地图展示

### Vue.js的选择优势

**Vue.js特别适合水利监测平台开发**的原因包括：

**1. 渐进式架构设计**

Vue.js的**渐进式**特性意味着可以根据项目需求逐步引入框架特性。对于水利系统，可以从简单的数据绑定开始，逐步增加组件化、路由管理等高级功能：

```html
<!-- 最简单的Vue应用 - 监测数据展示 -->
<div id="water-monitor">
  <h2>{{ stationName }}监测站</h2>
  <p>当前水位: <strong>{{ waterLevel }}米</strong></p>
  <p>流量: {{ flowRate }}立方米/秒</p>
  <button @click="refreshData">刷新数据</button>
</div>

<script>
const { createApp, ref } = Vue

createApp({
  setup() {
    const stationName = ref('黄河下游监测点')
    const waterLevel = ref(4.25)
    const flowRate = ref(1580)
    
    const refreshData = () => {
      // 模拟获取新数据
      waterLevel.value = (Math.random() * 2 + 3).toFixed(2)
      flowRate.value = Math.floor(Math.random() * 500 + 1200)
    }
    
    return {
      stationName,
      waterLevel,
      flowRate,
      refreshData
    }
  }
}).mount('#water-monitor')
</script>
```

**2. 优秀的文档和学习资源**

Vue.js拥有清晰详细的中文文档，为中国的水利行业开发者提供了良好的学习条件。官方文档不仅包含完整的API说明，还提供了大量实际应用示例。

**3. 丰富的生态系统**

Vue生态系统为水利监测平台提供了完整的技术栈支持：

- **Vue Router**: 单页面应用路由管理
- **Vuex/Pinia**: 应用状态管理
- **Element Plus**: 企业级UI组件库
- **ECharts**: 数据可视化图表
- **Vue CLI/Vite**: 开发工具链

**4. 适合团队协作**

Vue.js的单文件组件(.vue)格式将模板、逻辑和样式封装在一个文件中，便于团队成员理解和维护：

```vue
<!-- WaterLevelGauge.vue - 水位表盘组件 -->
<template>
  <div class="water-gauge">
    <div class="gauge-container">
      <svg class="gauge-svg" viewBox="0 0 200 200">
        <circle 
          cx="100" 
          cy="100" 
          r="80" 
          fill="none" 
          stroke="#e0e6ed" 
          stroke-width="8"
        />
        <circle 
          cx="100" 
          cy="100" 
          r="80" 
          fill="none" 
          :stroke="gaugeColor" 
          stroke-width="8"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="dashOffset"
          transform="rotate(-90 100 100)"
        />
      </svg>
      <div class="gauge-text">
        <div class="water-level">{{ level.toFixed(1) }}m</div>
        <div class="gauge-label">水位</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// 组件属性定义
const props = defineProps({
  level: {
    type: Number,
    required: true,
    default: 0
  },
  maxLevel: {
    type: Number,
    default: 10
  },
  warningLevel: {
    type: Number,
    default: 8
  }
})

// 计算属性 - 表盘显示逻辑
const circumference = computed(() => 2 * Math.PI * 80)
const dashOffset = computed(() => {
  const percentage = (props.level / props.maxLevel) * 100
  return circumference.value - (percentage / 100) * circumference.value
})

const gaugeColor = computed(() => {
  if (props.level > props.warningLevel) return '#ff4757'  // 红色预警
  if (props.level > props.warningLevel * 0.8) return '#ffa502'  // 橙色警告
  return '#2ed573'  // 绿色正常
})
</script>

<style scoped>
.water-gauge {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.gauge-container {
  position: relative;
  width: 200px;
  height: 200px;
}

.gauge-svg {
  width: 100%;
  height: 100%;
}

.gauge-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.water-level {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.gauge-label {
  font-size: 14px;
  color: #7f8c8d;
}

/* 水利系统专用颜色方案 */
.gauge-container {
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
}
</style>
```

!!! tip "框架选择建议"
    
    对于水利监测平台项目，推荐选择Vue.js的原因：
    
    1. **学习成本低**：团队能够快速掌握并投入开发
    2. **维护友好**：代码结构清晰，便于长期维护
    3. **生态丰富**：有完整的水利行业相关组件和工具支持
    4. **性能优秀**：能够满足实时数据处理和展示需求
    5. **社区活跃**：有持续的技术支持和版本更新

在下一小节中，我们将深入学习Vue.js的核心概念和MVVM架构模式，为实际开发做好理论准备。

## 4.5.2 Vue.js核心概念与MVVM模式

### Vue.js框架概述

**Vue.js**（发音类似"view"）是一款**用于构建用户界面的渐进式JavaScript框架**。由尤雨溪在2014年创建，Vue.js的设计目标是通过尽可能简单的API实现响应式的数据绑定和组合的视图组件。在智慧水利系统开发中，Vue.js能够帮助开发者高效地构建复杂的数据监控界面、实时图表展示和交互式控制面板。

**Vue.js的核心设计理念**包括：

1. **渐进式增强**：可以从简单的页面增强开始，逐步构建复杂应用
2. **声明式渲染**：通过模板语法声明式地描述界面结构
3. **响应式数据绑定**：数据变化自动更新相关视图
4. **组件化开发**：将复杂界面拆分为可复用的组件

让我们通过一个水利监测系统的实际场景来理解Vue.js的核心特性：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>水利监测站数据展示</title>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <style>
        .monitoring-dashboard {
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            font-family: '微软雅黑', sans-serif;
        }
        .station-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
            background: #f9f9f9;
        }
        .data-row {
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
        }
        .warning { background-color: #ffe6e6; border-color: #ff9999; }
        .normal { background-color: #e6f7ff; border-color: #91d5ff; }
        .btn {
            background: #1890ff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div id="water-monitoring-app">
        <div class="monitoring-dashboard">
            <h1>{{ systemTitle }}</h1>
            
            <!-- 实时数据展示 -->
            <div class="station-card" 
                 :class="getStationStatus(station)" 
                 v-for="station in monitoringStations" 
                 :key="station.id">
                <h3>{{ station.name }}</h3>
                
                <div class="data-row">
                    <span>水位:</span>
                    <strong>{{ station.waterLevel.toFixed(2) }} 米</strong>
                </div>
                
                <div class="data-row">
                    <span>流量:</span>
                    <strong>{{ station.flowRate.toFixed(1) }} 立方米/秒</strong>
                </div>
                
                <div class="data-row">
                    <span>状态:</span>
                    <span :style="{ color: station.waterLevel > 5 ? 'red' : 'green' }">
                        {{ station.waterLevel > 5 ? '警戒水位' : '正常' }}
                    </span>
                </div>
                
                <div class="data-row">
                    <span>更新时间:</span>
                    <span>{{ formatTime(station.lastUpdate) }}</span>
                </div>
                
                <button class="btn" @click="refreshStationData(station.id)">
                    刷新数据
                </button>
            </div>
            
            <!-- 系统统计信息 -->
            <div class="station-card">
                <h3>系统概览</h3>
                <div class="data-row">
                    <span>监测站总数:</span>
                    <strong>{{ totalStations }}</strong>
                </div>
                <div class="data-row">
                    <span>正常运行:</span>
                    <strong>{{ normalStations }}</strong>
                </div>
                <div class="data-row">
                    <span>预警站点:</span>
                    <strong>{{ warningStations }}</strong>
                </div>
            </div>
        </div>
    </div>

    <script>
        const { createApp, ref, computed } = Vue
        
        createApp({
            setup() {
                // 响应式数据定义
                const systemTitle = ref('智慧水利监测系统')
                const monitoringStations = ref([
                    {
                        id: 1,
                        name: '黄河小浪底监测站',
                        waterLevel: 4.25,
                        flowRate: 1580.5,
                        lastUpdate: new Date()
                    },
                    {
                        id: 2,
                        name: '长江三峡监测站',
                        waterLevel: 6.80,
                        flowRate: 2450.3,
                        lastUpdate: new Date()
                    },
                    {
                        id: 3,
                        name: '珠江口监测站',
                        waterLevel: 3.15,
                        flowRate: 890.7,
                        lastUpdate: new Date()
                    }
                ])
                
                // 计算属性 - 自动计算统计数据
                const totalStations = computed(() => {
                    return monitoringStations.value.length
                })
                
                const warningStations = computed(() => {
                    return monitoringStations.value.filter(station => station.waterLevel > 5).length
                })
                
                const normalStations = computed(() => {
                    return totalStations.value - warningStations.value
                })
                
                // 方法定义
                const refreshStationData = (stationId) => {
                    const station = monitoringStations.value.find(s => s.id === stationId)
                    if (station) {
                        // 模拟获取新数据
                        station.waterLevel = (Math.random() * 4 + 2).toFixed(2) * 1
                        station.flowRate = (Math.random() * 1000 + 500).toFixed(1) * 1
                        station.lastUpdate = new Date()
                    }
                }
                
                const getStationStatus = (station) => {
                    return station.waterLevel > 5 ? 'warning' : 'normal'
                }
                
                const formatTime = (date) => {
                    return date.toLocaleTimeString('zh-CN')
                }
                
                return {
                    systemTitle,
                    monitoringStations,
                    totalStations,
                    normalStations,
                    warningStations,
                    refreshStationData,
                    getStationStatus,
                    formatTime
                }
            }
        }).mount('#water-monitoring-app')
    </script>
</body>
</html>
```

这个示例展示了Vue.js的几个核心特性：

1. **响应式数据**：当`monitoringStations`数组中的数据发生变化时，相关的界面元素自动更新
2. **计算属性**：`totalStations`、`warningStations`等统计数据根据基础数据自动计算
3. **声明式渲染**：使用`v-for`指令声明式地渲染监测站列表
4. **事件处理**：通过`@click`绑定点击事件处理函数

### Vue.js的核心特性详解

**1. 声明式渲染**

传统命令式编程需要详细指定每一步操作，而Vue.js采用声明式渲染，开发者只需要描述**期望的最终状态**，Vue会自动处理如何达到这个状态：

```vue
<!-- 声明式：描述想要的结果 -->
<template>
  <div class="water-quality-panel">
    <h2>水质监测数据</h2>
    <div v-if="isLoading" class="loading">数据加载中...</div>
    <div v-else>
      <div class="quality-item" v-for="item in waterQualityData" :key="item.parameter">
        <span class="parameter">{{ item.parameter }}:</span>
        <span 
          class="value" 
          :class="{ 'exceeded': item.value > item.standard }"
        >
          {{ item.value }} {{ item.unit }}
        </span>
        <span class="standard">(标准值: {{ item.standard }}{{ item.unit }})</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isLoading = ref(true)
const waterQualityData = ref([])

onMounted(async () => {
  // 模拟API调用
  setTimeout(() => {
    waterQualityData.value = [
      { parameter: 'pH值', value: 7.2, standard: 7.0, unit: '' },
      { parameter: '溶解氧', value: 8.5, standard: 6.0, unit: 'mg/L' },
      { parameter: '氨氮', value: 0.3, standard: 0.5, unit: 'mg/L' },
      { parameter: '总磷', value: 0.08, standard: 0.1, unit: 'mg/L' }
    ]
    isLoading.value = false
  }, 1500)
})
</script>

<style scoped>
.water-quality-panel {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.quality-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.parameter {
  font-weight: bold;
  color: #2c3e50;
}

.value {
  font-size: 18px;
  color: #27ae60;
}

.value.exceeded {
  color: #e74c3c;
  font-weight: bold;
}

.standard {
  color: #7f8c8d;
  font-size: 12px;
}

.loading {
  text-align: center;
  color: #7f8c8d;
  padding: 40px;
}
</style>
```

**2. 响应式数据绑定**

Vue.js的响应式系统能够**自动追踪数据依赖关系**，当数据发生变化时，所有依赖这些数据的DOM元素、计算属性和侦听器都会自动更新：

```vue
<template>
  <div class="reservoir-dashboard">
    <h2>{{ reservoirName }}水库监控</h2>
    
    <!-- 水库基础数据 -->
    <div class="data-grid">
      <div class="data-card">
        <h3>水位</h3>
        <div class="value">{{ currentLevel.toFixed(2) }} 米</div>
        <div class="trend" :class="levelTrend">
          {{ levelTrend === 'rising' ? '↗ 上升' : levelTrend === 'falling' ? '↘ 下降' : '→ 稳定' }}
        </div>
      </div>
      
      <div class="data-card">
        <h3>库容</h3>
        <div class="value">{{ currentVolume }} 万立方米</div>
        <div class="percentage">{{ volumePercentage }}% 蓄水率</div>
      </div>
      
      <div class="data-card">
        <h3>入库流量</h3>
        <div class="value">{{ inflowRate }} 立方米/秒</div>
      </div>
      
      <div class="data-card">
        <h3>出库流量</h3>
        <div class="value">{{ outflowRate }} 立方米/秒</div>
      </div>
    </div>
    
    <!-- 控制面板 -->
    <div class="control-panel">
      <h3>模拟控制</h3>
      <div class="controls">
        <button @click="simulateRainfall" :disabled="isSimulating">模拟降雨</button>
        <button @click="adjustOutflow" :disabled="isSimulating">调节出水</button>
        <button @click="resetData">重置数据</button>
      </div>
      <div v-if="isSimulating" class="simulation-info">
        正在模拟中... {{ simulationProgress }}%
      </div>
    </div>
    
    <!-- 预警信息 -->
    <div v-if="warnings.length > 0" class="warnings">
      <h3>预警信息</h3>
      <div class="warning-item" v-for="warning in warnings" :key="warning.id">
        <span class="warning-level" :class="warning.level">{{ warning.level }}</span>
        <span class="warning-message">{{ warning.message }}</span>
        <span class="warning-time">{{ formatTime(warning.time) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

// 基础数据
const reservoirName = ref('三峡')
const currentLevel = ref(175.5)
const maxCapacity = ref(393000) // 万立方米
const isSimulating = ref(false)
const simulationProgress = ref(0)

// 流量数据
const inflowRate = ref(12000)
const outflowRate = ref(11500)

// 预警数据
const warnings = ref([])

// 计算属性 - 根据水位自动计算库容
const currentVolume = computed(() => {
  // 简化的库容计算公式
  const baseVolume = 221500 // 基础库容
  const levelFactor = (currentLevel.value - 145) * 1000 // 水位影响因子
  return Math.round(baseVolume + levelFactor)
})

// 计算属性 - 蓄水率
const volumePercentage = computed(() => {
  return Math.round((currentVolume.value / maxCapacity.value) * 100)
})

// 计算属性 - 水位变化趋势
const levelTrend = computed(() => {
  const netFlow = inflowRate.value - outflowRate.value
  if (netFlow > 100) return 'rising'
  if (netFlow < -100) return 'falling'
  return 'stable'
})

// 监听水位变化，触发预警
watch(currentLevel, (newLevel, oldLevel) => {
  if (newLevel > 180) {
    addWarning('danger', `水位过高: ${newLevel.toFixed(2)}米，接近最高水位`)
  } else if (newLevel > 175) {
    addWarning('warning', `水位较高: ${newLevel.toFixed(2)}米，需要关注`)
  }
  
  // 清除过期预警
  if (newLevel < 175 && warnings.value.some(w => w.level === 'warning')) {
    warnings.value = warnings.value.filter(w => w.level !== 'warning')
  }
}, { immediate: true })

// 监听蓄水率，触发相应操作
watch(volumePercentage, (percentage) => {
  if (percentage > 95) {
    addWarning('danger', '水库蓄水率超过95%，建议增加泄洪量')
  } else if (percentage < 30) {
    addWarning('info', '水库蓄水率低于30%，注意供水安全')
  }
})

// 方法定义
const simulateRainfall = async () => {
  if (isSimulating.value) return
  
  isSimulating.value = true
  simulationProgress.value = 0
  
  // 模拟降雨过程
  const interval = setInterval(() => {
    simulationProgress.value += 10
    inflowRate.value += Math.random() * 1000
    currentLevel.value += Math.random() * 0.1
    
    if (simulationProgress.value >= 100) {
      clearInterval(interval)
      isSimulating.value = false
      addWarning('info', '降雨模拟完成')
    }
  }, 500)
}

const adjustOutflow = () => {
  if (currentLevel.value > 175) {
    outflowRate.value += 2000
    addWarning('info', `已调节出库流量至 ${outflowRate.value} 立方米/秒`)
  } else {
    outflowRate.value = Math.max(8000, outflowRate.value - 1000)
    addWarning('info', `已调节出库流量至 ${outflowRate.value} 立方米/秒`)
  }
}

const resetData = () => {
  currentLevel.value = 175.5
  inflowRate.value = 12000
  outflowRate.value = 11500
  warnings.value = []
  addWarning('info', '数据已重置')
}

const addWarning = (level, message) => {
  const warning = {
    id: Date.now(),
    level,
    message,
    time: new Date()
  }
  warnings.value.unshift(warning)
  
  // 最多保留10条预警记录
  if (warnings.value.length > 10) {
    warnings.value = warnings.value.slice(0, 10)
  }
}

const formatTime = (date) => {
  return date.toLocaleTimeString('zh-CN')
}
</script>

<style scoped>
.reservoir-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.data-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
}

.data-card h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 16px;
}

.data-card .value {
  font-size: 24px;
  font-weight: bold;
  color: #3498db;
  margin: 10px 0;
}

.trend {
  font-size: 14px;
  padding: 5px 10px;
  border-radius: 12px;
  display: inline-block;
}

.trend.rising { background: #ffe6e6; color: #e74c3c; }
.trend.falling { background: #e6f7ff; color: #1890ff; }
.trend.stable { background: #f6ffed; color: #52c41a; }

.percentage {
  color: #7f8c8d;
  font-size: 14px;
}

.control-panel {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.controls {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.controls button {
  padding: 10px 20px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.controls button:hover:not(:disabled) {
  background: #40a9ff;
}

.controls button:disabled {
  background: #d9d9d9;
  cursor: not-allowed;
}

.simulation-info {
  margin-top: 15px;
  padding: 10px;
  background: #e6f7ff;
  border-radius: 4px;
  color: #1890ff;
}

.warnings {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.warning-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.warning-level {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.warning-level.danger { background: #ffe6e6; color: #e74c3c; }
.warning-level.warning { background: #fff7e6; color: #fa8c16; }
.warning-level.info { background: #e6f7ff; color: #1890ff; }

.warning-message {
  flex: 1;
  color: #2c3e50;
}

.warning-time {
  color: #7f8c8d;
  font-size: 12px;
}
</style>
```

这个水库监控示例展示了Vue.js响应式数据绑定的强大功能：

- **数据变化自动更新界面**：当`currentLevel`改变时，相关的显示、计算属性和样式都会自动更新
- **计算属性自动重新计算**：`currentVolume`和`volumePercentage`基于`currentLevel`自动计算
- **侦听器触发相应逻辑**：通过`watch`监听数据变化，触发预警逻辑

### MVVM架构模式深入理解

**MVVM（Model-View-ViewModel）**是Vue.js采用的核心架构模式。这种模式将应用分为三个层次：

| 层次 | 职责 | 在Vue中的体现 | 水利系统示例 |
|------|------|--------------|-------------|
| **Model** | 数据层，管理应用的数据和业务逻辑 | 响应式数据、API调用 | 监测站数据、水位信息 |
| **View** | 视图层，负责用户界面的展示 | Template模板 | 图表、表格、控制面板 |
| **ViewModel** | 视图模型层，连接Model和View | Vue组件实例 | 数据处理、事件处理逻辑 |

让我们通过一个水利数据管理的完整示例来理解MVVM模式：

```vue
<!-- WaterStationManager.vue - 水利监测站管理组件 -->
<template>
  <!-- View层：用户界面 -->
  <div class="station-manager">
    <header class="manager-header">
      <h1>水利监测站管理系统</h1>
      <div class="header-actions">
        <button @click="refreshAllData" :disabled="isLoading" class="btn btn-primary">
          {{ isLoading ? '刷新中...' : '刷新数据' }}
        </button>
        <button @click="showAddDialog = true" class="btn btn-success">添加监测站</button>
      </div>
    </header>

    <!-- 搜索和筛选 -->
    <div class="filter-section">
      <input 
        v-model="searchKeyword" 
        placeholder="搜索监测站名称..."
        class="search-input"
      />
      <select v-model="filterStatus" class="filter-select">
        <option value="">全部状态</option>
        <option value="normal">正常</option>
        <option value="warning">预警</option>
        <option value="offline">离线</option>
      </select>
    </div>

    <!-- 监测站列表 -->
    <div class="stations-grid">
      <div 
        v-for="station in filteredStations" 
        :key="station.id"
        class="station-card"
        :class="getStationStatusClass(station)"
      >
        <div class="station-header">
          <h3>{{ station.name }}</h3>
          <span class="status-badge" :class="station.status">
            {{ getStatusText(station.status) }}
          </span>
        </div>
        
        <div class="station-data">
          <div class="data-item">
            <span class="label">经度:</span>
            <span class="value">{{ station.longitude }}°</span>
          </div>
          <div class="data-item">
            <span class="label">纬度:</span>
            <span class="value">{{ station.latitude }}°</span>
          </div>
          <div class="data-item">
            <span class="label">水位:</span>
            <span class="value">{{ station.currentData.waterLevel }} m</span>
          </div>
          <div class="data-item">
            <span class="label">流量:</span>
            <span class="value">{{ station.currentData.flowRate }} m³/s</span>
          </div>
          <div class="data-item">
            <span class="label">更新时间:</span>
            <span class="value">{{ formatTime(station.lastUpdate) }}</span>
          </div>
        </div>
        
        <div class="station-actions">
          <button @click="viewDetails(station)" class="btn btn-info btn-sm">详情</button>
          <button @click="editStation(station)" class="btn btn-warning btn-sm">编辑</button>
          <button @click="deleteStation(station.id)" class="btn btn-danger btn-sm">删除</button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑监测站对话框 -->
    <div v-if="showAddDialog || editingStation" class="modal-overlay" @click.self="closeDialog">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ editingStation ? '编辑监测站' : '添加监测站' }}</h2>
          <button @click="closeDialog" class="close-btn">&times;</button>
        </div>
        
        <form @submit.prevent="saveStation" class="station-form">
          <div class="form-group">
            <label>监测站名称:</label>
            <input 
              v-model="stationForm.name" 
              type="text" 
              required 
              class="form-input"
            />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>经度:</label>
              <input 
                v-model.number="stationForm.longitude" 
                type="number" 
                step="0.000001"
                required 
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label>纬度:</label>
              <input 
                v-model.number="stationForm.latitude" 
                type="number" 
                step="0.000001"
                required 
                class="form-input"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label>描述:</label>
            <textarea 
              v-model="stationForm.description" 
              class="form-textarea"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? '保存中...' : '保存' }}
            </button>
            <button type="button" @click="closeDialog" class="btn btn-secondary">取消</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
// ViewModel层：业务逻辑和数据处理
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { WaterStationAPI } from '@/api/waterStation'

// Model层：数据模型
const stations = ref([]) // 监测站列表
const searchKeyword = ref('') // 搜索关键词
const filterStatus = ref('') // 状态筛选
const isLoading = ref(false) // 加载状态
const showAddDialog = ref(false) // 添加对话框显示状态
const editingStation = ref(null) // 正在编辑的监测站
const isSubmitting = ref(false) // 提交状态

// 表单数据模型
const stationForm = reactive({
  name: '',
  longitude: 0,
  latitude: 0,
  description: ''
})

// 计算属性：根据搜索和筛选条件过滤监测站
const filteredStations = computed(() => {
  let result = stations.value

  // 根据关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(station => 
      station.name.toLowerCase().includes(keyword)
    )
  }

  // 根据状态筛选
  if (filterStatus.value) {
    result = result.filter(station => station.status === filterStatus.value)
  }

  return result
})

// 计算属性：统计信息
const stationStats = computed(() => ({
  total: stations.value.length,
  normal: stations.value.filter(s => s.status === 'normal').length,
  warning: stations.value.filter(s => s.status === 'warning').length,
  offline: stations.value.filter(s => s.status === 'offline').length
}))

// 侦听器：监听搜索关键词变化
watch(searchKeyword, (newKeyword) => {
  console.log(`搜索关键词变更为: ${newKeyword}`)
  // 可以在这里添加搜索历史记录等逻辑
})

// 侦听器：监听监测站数据变化，自动保存到本地存储
watch(stations, (newStations) => {
  localStorage.setItem('waterStations', JSON.stringify(newStations))
}, { deep: true })

// ViewModel方法：业务逻辑处理
const refreshAllData = async () => {
  isLoading.value = true
  try {
    const response = await WaterStationAPI.getAllStations()
    stations.value = response.data
    
    // 模拟更新监测数据
    stations.value.forEach(station => {
      station.currentData = {
        waterLevel: (Math.random() * 5 + 2).toFixed(2),
        flowRate: (Math.random() * 1000 + 500).toFixed(1),
        temperature: (Math.random() * 10 + 15).toFixed(1)
      }
      station.lastUpdate = new Date()
      station.status = determineStationStatus(station)
    })
  } catch (error) {
    console.error('获取监测站数据失败:', error)
    // 使用模拟数据
    loadMockData()
  } finally {
    isLoading.value = false
  }
}

const loadMockData = () => {
  stations.value = [
    {
      id: 1,
      name: '黄河小浪底监测站',
      longitude: 112.4795,
      latitude: 34.9293,
      description: '黄河干流重要监测点',
      currentData: {
        waterLevel: 4.25,
        flowRate: 1580.5,
        temperature: 18.2
      },
      lastUpdate: new Date(),
      status: 'normal'
    },
    {
      id: 2,
      name: '长江三峡监测站',
      longitude: 111.0020,
      latitude: 30.8236,
      description: '长江上游关键监测站',
      currentData: {
        waterLevel: 6.80,
        flowRate: 2450.3,
        temperature: 16.8
      },
      lastUpdate: new Date(),
      status: 'warning'
    },
    {
      id: 3,
      name: '珠江口监测站',
      longitude: 113.5950,
      latitude: 22.1200,
      description: '珠江入海口监测点',
      currentData: {
        waterLevel: 3.15,
        flowRate: 890.7,
        temperature: 24.5
      },
      lastUpdate: new Date(),
      status: 'normal'
    }
  ]
}

const determineStationStatus = (station) => {
  const { waterLevel } = station.currentData
  if (!waterLevel) return 'offline'
  if (waterLevel > 5.0) return 'warning'
  return 'normal'
}

const viewDetails = (station) => {
  // 跳转到详情页面或显示详情弹窗
  console.log('查看监测站详情:', station)
}

const editStation = (station) => {
  editingStation.value = station
  Object.assign(stationForm, {
    name: station.name,
    longitude: station.longitude,
    latitude: station.latitude,
    description: station.description
  })
}

const deleteStation = async (stationId) => {
  if (confirm('确定要删除这个监测站吗？')) {
    try {
      await WaterStationAPI.deleteStation(stationId)
      stations.value = stations.value.filter(s => s.id !== stationId)
    } catch (error) {
      console.error('删除监测站失败:', error)
    }
  }
}

const saveStation = async () => {
  isSubmitting.value = true
  try {
    if (editingStation.value) {
      // 更新现有监测站
      const response = await WaterStationAPI.updateStation(editingStation.value.id, stationForm)
      const index = stations.value.findIndex(s => s.id === editingStation.value.id)
      if (index !== -1) {
        stations.value[index] = { ...stations.value[index], ...stationForm }
      }
    } else {
      // 创建新监测站
      const response = await WaterStationAPI.createStation(stationForm)
      stations.value.push({
        id: Date.now(), // 临时ID
        ...stationForm,
        currentData: {
          waterLevel: 0,
          flowRate: 0,
          temperature: 0
        },
        lastUpdate: new Date(),
        status: 'offline'
      })
    }
    closeDialog()
  } catch (error) {
    console.error('保存监测站失败:', error)
  } finally {
    isSubmitting.value = false
  }
}

const closeDialog = () => {
  showAddDialog.value = false
  editingStation.value = null
  Object.assign(stationForm, {
    name: '',
    longitude: 0,
    latitude: 0,
    description: ''
  })
}

// 工具方法
const getStationStatusClass = (station) => {
  return `status-${station.status}`
}

const getStatusText = (status) => {
  const statusMap = {
    normal: '正常',
    warning: '预警',
    offline: '离线'
  }
  return statusMap[status] || '未知'
}

const formatTime = (date) => {
  return date.toLocaleString('zh-CN')
}

// 生命周期钩子
onMounted(() => {
  // 加载本地存储的数据
  const savedStations = localStorage.getItem('waterStations')
  if (savedStations) {
    try {
      stations.value = JSON.parse(savedStations).map(station => ({
        ...station,
        lastUpdate: new Date(station.lastUpdate)
      }))
    } catch (error) {
      console.error('解析本地存储数据失败:', error)
    }
  }
  
  // 获取最新数据
  refreshAllData()
})
</script>

<style scoped>
/* View层样式：界面展示 */
.station-manager {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e8e8e8;
}

.manager-header h1 {
  color: #2c3e50;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-section {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.search-input, .filter-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-input {
  flex: 1;
  max-width: 300px;
}

.stations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.station-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.station-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.station-card.status-warning {
  border-left: 4px solid #fa8c16;
}

.station-card.status-offline {
  border-left: 4px solid #ff4757;
  opacity: 0.7;
}

.station-card.status-normal {
  border-left: 4px solid #52c41a;
}

.station-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.station-header h3 {
  margin: 0;
  color: #2c3e50;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.status-badge.normal {
  background: #f6ffed;
  color: #52c41a;
}

.status-badge.warning {
  background: #fff7e6;
  color: #fa8c16;
}

.status-badge.offline {
  background: #ffe6e6;
  color: #ff4757;
}

.station-data {
  margin-bottom: 15px;
}

.data-item {
  display: flex;
  justify-content: space-between;
  margin: 5px 0;
  padding: 5px 0;
}

.data-item .label {
  color: #7f8c8d;
  font-weight: 500;
}

.data-item .value {
  color: #2c3e50;
  font-weight: bold;
}

.station-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* 按钮样式 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #40a9ff;
}

.btn-success {
  background: #52c41a;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #73d13d;
}

.btn-warning {
  background: #fa8c16;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background: #ffa940;
}

.btn-danger {
  background: #ff4757;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #ff6b7a;
}

.btn-info {
  background: #1890ff;
  color: white;
}

.btn-secondary {
  background: #d9d9d9;
  color: #666;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e8e8e8;
}

.modal-header h2 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.station-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #2c3e50;
  font-weight: 500;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;
}
</style>
```

这个完整的示例展示了Vue.js中MVVM架构模式的实际应用：

**Model层**：
- `stations`: 监测站数据数组
- `stationForm`: 表单数据对象
- `searchKeyword`, `filterStatus`: 用户界面状态数据

**View层**：
- Template部分定义了用户界面结构
- 使用指令(`v-for`, `v-if`, `v-model`)声明式地描述界面逻辑
- 通过事件绑定(`@click`, `@submit`)响应用户操作

**ViewModel层**：
- 计算属性(`filteredStations`, `stationStats`)自动处理数据转换
- 侦听器(`watch`)监听数据变化并执行相应逻辑
- 方法(`refreshAllData`, `saveStation`)处理业务逻辑

### 数据双向绑定原理

Vue.js的**数据双向绑定**是MVVM模式的核心特性。它通过响应式系统实现了数据层(Model)与视图层(View)的自动同步：

**单向数据绑定流程**：
1. **数据变化** → **触发响应式更新** → **重新渲染视图**

**双向数据绑定流程**：
1. **数据变化** → **更新视图**
2. **用户输入** → **更新数据** → **更新其他相关视图**

```vue
<template>
  <div class="water-level-input-demo">
    <h2>水位数据录入演示</h2>
    
    <!-- 双向数据绑定示例 -->
    <div class="input-section">
      <div class="input-group">
        <label>水位值 (米):</label>
        <input 
          v-model.number="waterLevel" 
          type="number" 
          step="0.1"
          min="0"
          max="20"
          class="level-input"
        />
      </div>
      
      <div class="input-group">
        <label>监测站名称:</label>
        <select v-model="selectedStation" class="station-select">
          <option value="">请选择监测站</option>
          <option v-for="station in availableStations" :key="station.id" :value="station">
            {{ station.name }}
          </option>
        </select>
      </div>
      
      <div class="input-group">
        <label>备注:</label>
        <textarea 
          v-model="notes" 
          placeholder="请输入备注信息..."
          class="notes-textarea"
        ></textarea>
      </div>
    </div>
    
    <!-- 实时预览 -->
    <div class="preview-section">
      <h3>实时预览</h3>
      <div class="preview-card">
        <div class="preview-item">
          <strong>当前水位:</strong> 
          <span :class="getLevelClass(waterLevel)">{{ waterLevel || 0 }} 米</span>
        </div>
        <div class="preview-item">
          <strong>选中监测站:</strong> 
          <span>{{ selectedStation ? selectedStation.name : '未选择' }}</span>
        </div>
        <div class="preview-item" v-if="selectedStation">
          <strong>站点位置:</strong> 
          <span>{{ selectedStation.longitude }}°E, {{ selectedStation.latitude }}°N</span>
        </div>
        <div class="preview-item">
          <strong>预警状态:</strong> 
          <span :class="getWarningClass(waterLevel)">{{ getWarningText(waterLevel) }}</span>
        </div>
        <div class="preview-item" v-if="notes">
          <strong>备注信息:</strong> 
          <span>{{ notes }}</span>
        </div>
        <div class="preview-item">
          <strong>录入时间:</strong> 
          <span>{{ currentTime }}</span>
        </div>
      </div>
    </div>
    
    <!-- 数据同步演示 -->
    <div class="sync-demo">
      <h3>数据同步演示</h3>
      <p>在输入框中修改数据，观察下面的显示如何实时更新：</p>
      <div class="sync-display">
        <div class="gauge-wrapper">
          <div class="level-gauge">
            <div 
              class="gauge-fill" 
              :style="{ height: (waterLevel / 20 * 100) + '%' }"
            ></div>
            <div class="gauge-text">{{ waterLevel || 0 }}m</div>
          </div>
          <div class="gauge-label">水位表</div>
        </div>
        
        <div class="chart-wrapper">
          <div class="mini-chart">
            <div 
              v-for="(point, index) in chartData" 
              :key="index"
              class="chart-bar"
              :style="{ 
                height: (point / 20 * 100) + '%',
                background: point > 15 ? '#ff4757' : point > 10 ? '#ffa502' : '#2ed573'
              }"
            ></div>
          </div>
          <div class="chart-label">趋势图</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

// 响应式数据
const waterLevel = ref(5.2)
const selectedStation = ref(null)
const notes = ref('')
const currentTime = ref('')

// 模拟可用监测站数据
const availableStations = ref([
  { id: 1, name: '黄河小浪底监测站', longitude: 112.4795, latitude: 34.9293 },
  { id: 2, name: '长江三峡监测站', longitude: 111.0020, latitude: 30.8236 },
  { id: 3, name: '珠江口监测站', longitude: 113.5950, latitude: 22.1200 }
])

// 图表数据
const chartData = ref([3.2, 4.1, 5.8, 6.2, 5.9, 5.5, 5.2])

// 计算属性
const formattedLevel = computed(() => {
  return waterLevel.value ? waterLevel.value.toFixed(1) : '0.0'
})

// 侦听器 - 监听水位变化
watch(waterLevel, (newLevel, oldLevel) => {
  console.log(`水位从 ${oldLevel} 变化为 ${newLevel}`)
  
  // 更新图表数据（模拟实时数据更新）
  chartData.value.shift() // 移除第一个数据点
  chartData.value.push(newLevel || 0) // 添加新数据点
  
  // 触发预警检查
  checkWaterLevelWarning(newLevel)
})

// 侦听器 - 监听选中的监测站
watch(selectedStation, (newStation) => {
  if (newStation) {
    console.log(`选择了监测站: ${newStation.name}`)
    // 可以在这里加载该监测站的历史数据
  }
})

// 侦听器 - 监听所有表单数据变化
watch([waterLevel, selectedStation, notes], 
  ([level, station, noteText]) => {
    console.log('表单数据更新:', {
      waterLevel: level,
      station: station?.name || null,
      notes: noteText
    })
    
    // 自动保存到本地存储
    const formData = {
      waterLevel: level,
      stationId: station?.id || null,
      notes: noteText,
      timestamp: Date.now()
    }
    localStorage.setItem('waterLevelForm', JSON.stringify(formData))
  },
  { deep: true }
)

// 方法
const getLevelClass = (level) => {
  if (level > 15) return 'level-danger'
  if (level > 10) return 'level-warning' 
  return 'level-normal'
}

const getWarningClass = (level) => {
  if (level > 15) return 'warning-danger'
  if (level > 10) return 'warning-warning'
  return 'warning-normal'
}

const getWarningText = (level) => {
  if (level > 15) return '严重超标'
  if (level > 10) return '预警状态'
  return '正常'
}

const checkWaterLevelWarning = (level) => {
  if (level > 15) {
    console.warn('水位严重超标！需要立即处理')
    // 这里可以触发实际的预警逻辑
  } else if (level > 10) {
    console.warn('水位偏高，请注意监控')
  }
}

const updateCurrentTime = () => {
  currentTime.value = new Date().toLocaleString('zh-CN')
}

// 生命周期
let timeInterval = null

onMounted(() => {
  // 从本地存储恢复数据
  const savedData = localStorage.getItem('waterLevelForm')
  if (savedData) {
    try {
      const data = JSON.parse(savedData)
      waterLevel.value = data.waterLevel || 0
      if (data.stationId) {
        selectedStation.value = availableStations.value.find(s => s.id === data.stationId)
      }
      notes.value = data.notes || ''
    } catch (error) {
      console.error('恢复表单数据失败:', error)
    }
  }
  
  // 启动时间更新
  updateCurrentTime()
  timeInterval = setInterval(updateCurrentTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.water-level-input-demo {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.input-section {
  background: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #2c3e50;
}

.level-input, .station-select, .notes-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.level-input:focus, .station-select:focus, .notes-textarea:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.notes-textarea {
  resize: vertical;
  min-height: 80px;
}

.preview-section {
  background: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.preview-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 6px;
  border-left: 4px solid #1890ff;
}

.preview-item {
  margin: 10px 0;
  line-height: 1.6;
}

.level-normal { color: #52c41a; }
.level-warning { color: #fa8c16; }
.level-danger { color: #ff4757; }

.warning-normal { 
  background: #f6ffed; 
  color: #52c41a; 
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.warning-warning { 
  background: #fff7e6; 
  color: #fa8c16; 
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.warning-danger { 
  background: #ffe6e6; 
  color: #ff4757; 
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.sync-demo {
  background: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.sync-display {
  display: flex;
  gap: 40px;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
}

.gauge-wrapper, .chart-wrapper {
  text-align: center;
}

.level-gauge {
  width: 100px;
  height: 200px;
  background: #f0f0f0;
  border: 2px solid #ddd;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.gauge-fill {
  position: absolute;
  bottom: 0;
  width: 100%;
  background: linear-gradient(to top, #2ed573, #1890ff, #fa8c16, #ff4757);
  transition: height 0.3s ease;
}

.gauge-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-weight: bold;
  color: #2c3e50;
  background: rgba(255,255,255,0.9);
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 14px;
}

.gauge-label, .chart-label {
  margin-top: 10px;
  font-size: 14px;
  color: #7f8c8d;
  font-weight: 500;
}

.mini-chart {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 200px;
  width: 200px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
}

.chart-bar {
  flex: 1;
  min-height: 10px;
  border-radius: 2px;
  transition: height 0.3s ease;
}
</style>
```

这个双向绑定演示展示了Vue.js响应式系统的核心特性：

1. **输入框变化自动更新所有相关显示**
2. **计算属性根据依赖数据自动重新计算**
3. **侦听器监听特定数据变化并执行相关逻辑**
4. **视图与数据保持完全同步**

### 虚拟DOM概念与性能优化

**虚拟DOM（Virtual DOM）**是Vue.js实现高性能渲染的关键技术。它是真实DOM的JavaScript表示，Vue通过比较虚拟DOM的差异来最小化实际的DOM操作：

**虚拟DOM的工作流程：**

```javascript
// 1. 初始虚拟DOM表示
const initialVNode = {
  tag: 'div',
  props: { class: 'water-station' },
  children: [
    {
      tag: 'h3',
      props: {},
      children: '监测站A'
    },
    {
      tag: 'span',
      props: {},
      children: '水位: 4.5m'
    }
  ]
}

// 2. 数据更新后的虚拟DOM
const updatedVNode = {
  tag: 'div',
  props: { class: 'water-station' },
  children: [
    {
      tag: 'h3',
      props: {},
      children: '监测站A' // 未变化
    },
    {
      tag: 'span',
      props: {},
      children: '水位: 5.2m' // 已变化
    }
  ]
}

// 3. Vue进行diff算法比较，只更新变化的部分
// 只有水位显示的文本节点会被更新，其他部分保持不变
```

**虚拟DOM的优势：**

1. **性能优化**：批量更新，减少重绘和重排
2. **跨平台能力**：虚拟DOM可以渲染到不同平台
3. **开发体验**：声明式编程，无需手动操作DOM

在下一小节中，我们将学习Vue.js的基础语法和开发实践，包括模板语法、指令使用和事件处理等核心开发技能。

## 4.5.3 Vue基础语法与开发实践

### Vue实例创建与基础配置

在Vue 3中，应用的创建方式相比Vue 2有了重要变化。我们使用`createApp`函数来创建应用实例，这为水利监测系统提供了更好的模块化和可维护性支持。

**Vue 3应用创建的基本步骤：**

1. **导入Vue核心函数**
2. **创建应用实例**
3. **配置应用选项**
4. **挂载到DOM元素**

让我们通过一个完整的水利监测控制台应用来学习Vue实例的创建和配置：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>水利监测控制台</title>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <style>
        .monitoring-console {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            font-family: 'Microsoft YaHei', sans-serif;
        }
        
        .console-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .status-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #1890ff;
        }
        
        .error { border-left-color: #ff4757; }
        .warning { border-left-color: #ffa502; }
        .success { border-left-color: #2ed573; }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
            margin: 10px 0;
        }
        
        .metric-label {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        .control-panel {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .btn-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .btn-primary { background: #1890ff; color: white; }
        .btn-success { background: #2ed573; color: white; }
        .btn-warning { background: #ffa502; color: white; }
        .btn-danger { background: #ff4757; color: white; }
        
        .btn:hover { opacity: 0.8; transform: translateY(-1px); }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        
        .log-section {
            margin-top: 30px;
            background: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            height: 200px;
            overflow-y: auto;
            font-family: 'Consolas', monospace;
        }
        
        .log-entry {
            margin-bottom: 5px;
            font-size: 0.85em;
        }
        
        .log-timestamp { color: #95a5a6; }
        .log-info { color: #3498db; }
        .log-warning { color: #f39c12; }
        .log-error { color: #e74c3c; }
        .log-success { color: #27ae60; }
    </style>
</head>
<body>
    <div id="water-monitoring-console">
        <div class="monitoring-console">
            <!-- 控制台头部 -->
            <header class="console-header">
                <h1>{{ systemInfo.name }}</h1>
                <p>{{ systemInfo.description }}</p>
                <p>系统启动时间: {{ formatDate(systemInfo.startTime) }} | 运行时长: {{ uptime }}</p>
            </header>
            
            <!-- 状态监控面板 -->
            <div class="status-grid">
                <div class="status-card" :class="getCardClass('stations')">
                    <div class="metric-label">在线监测站</div>
                    <div class="metric-value">{{ metrics.onlineStations }} / {{ metrics.totalStations }}</div>
                    <div class="metric-label">
                        在线率: {{ stationOnlineRate }}%
                    </div>
                </div>
                
                <div class="status-card" :class="getCardClass('dataFlow')">
                    <div class="metric-label">数据流量</div>
                    <div class="metric-value">{{ metrics.dataFlow }} MB/h</div>
                    <div class="metric-label">
                        {{ metrics.dataFlow > 100 ? '高负载' : '正常' }}
                    </div>
                </div>
                
                <div class="status-card" :class="getCardClass('alerts')">
                    <div class="metric-label">活跃预警</div>
                    <div class="metric-value">{{ metrics.activeAlerts }}</div>
                    <div class="metric-label">
                        最近更新: {{ formatTime(metrics.lastAlertTime) }}
                    </div>
                </div>
                
                <div class="status-card" :class="getCardClass('storage')">
                    <div class="metric-label">存储使用率</div>
                    <div class="metric-value">{{ metrics.storageUsage }}%</div>
                    <div class="metric-label">
                        剩余: {{ 100 - metrics.storageUsage }}%
                    </div>
                </div>
            </div>
            
            <!-- 控制面板 -->
            <div class="control-panel">
                <h3>系统控制</h3>
                <div class="btn-group">
                    <button 
                        class="btn btn-primary" 
                        @click="refreshSystemData"
                        :disabled="isLoading"
                    >
                        {{ isLoading ? '刷新中...' : '刷新数据' }}
                    </button>
                    
                    <button 
                        class="btn btn-success" 
                        @click="startDataCollection"
                        :disabled="dataCollectionActive"
                    >
                        {{ dataCollectionActive ? '采集中...' : '开始数据采集' }}
                    </button>
                    
                    <button 
                        class="btn btn-warning" 
                        @click="pauseDataCollection"
                        :disabled="!dataCollectionActive"
                    >
                        暂停采集
                    </button>
                    
                    <button 
                        class="btn btn-danger" 
                        @click="clearAllAlerts"
                        :disabled="metrics.activeAlerts === 0"
                    >
                        清除所有预警
                    </button>
                </div>
            </div>
            
            <!-- 系统日志 -->
            <div class="log-section">
                <h4 style="margin-top: 0;">系统日志 (最新{{ systemLogs.length }}条)</h4>
                <div v-for="log in systemLogs" :key="log.id" class="log-entry">
                    <span class="log-timestamp">[{{ formatTime(log.timestamp) }}]</span>
                    <span :class="'log-' + log.level">{{ log.message }}</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 使用解构赋值导入Vue 3的API
        const { createApp, ref, reactive, computed, watch, onMounted, onUnmounted } = Vue
        
        // 创建Vue应用实例
        const app = createApp({
            // setup函数是Composition API的入口
            setup() {
                // ===== 响应式数据定义 =====
                
                // 系统基本信息
                const systemInfo = reactive({
                    name: '智慧水利监测控制台',
                    description: '实时监控全流域水利设施运行状态',
                    startTime: new Date(),
                    version: '2.0.1'
                })
                
                // 系统指标数据
                const metrics = reactive({
                    totalStations: 156,
                    onlineStations: 142,
                    dataFlow: 85.6,
                    activeAlerts: 3,
                    storageUsage: 67,
                    lastAlertTime: new Date()
                })
                
                // 系统状态
                const isLoading = ref(false)
                const dataCollectionActive = ref(true)
                const uptime = ref('00:00:00')
                
                // 系统日志
                const systemLogs = ref([
                    {
                        id: 1,
                        timestamp: new Date(),
                        level: 'info',
                        message: '系统启动完成，开始数据采集'
                    },
                    {
                        id: 2,
                        timestamp: new Date(Date.now() - 30000),
                        level: 'warning',
                        message: '监测站 #045 数据传输延迟'
                    },
                    {
                        id: 3,
                        timestamp: new Date(Date.now() - 60000),
                        level: 'success',
                        message: '数据库备份完成'
                    }
                ])
                
                // ===== 计算属性 =====
                
                // 计算监测站在线率
                const stationOnlineRate = computed(() => {
                    if (metrics.totalStations === 0) return 0
                    return Math.round((metrics.onlineStations / metrics.totalStations) * 100)
                })
                
                // 计算系统整体状态
                const systemStatus = computed(() => {
                    const onlineRate = stationOnlineRate.value
                    const alertCount = metrics.activeAlerts
                    
                    if (onlineRate < 80 || alertCount > 5) return 'error'
                    if (onlineRate < 95 || alertCount > 2) return 'warning'
                    return 'success'
                })
                
                // ===== 侦听器 =====
                
                // 监听系统指标变化
                watch(() => metrics.activeAlerts, (newCount, oldCount) => {
                    if (newCount > oldCount) {
                        addLog('warning', `新增预警信息，当前共有 ${newCount} 条活跃预警`)
                    } else if (newCount < oldCount) {
                        addLog('success', `预警信息已处理，当前剩余 ${newCount} 条活跃预警`)
                    }
                })
                
                // 监听在线监测站数量变化
                watch(() => metrics.onlineStations, (newCount) => {
                    const rate = Math.round((newCount / metrics.totalStations) * 100)
                    if (rate < 80) {
                        addLog('error', `监测站在线率降至 ${rate}%，请检查网络连接`)
                    } else if (rate >= 95) {
                        addLog('success', `监测站在线率恢复至 ${rate}%`)
                    }
                })
                
                // ===== 方法定义 =====
                
                // 刷新系统数据
                const refreshSystemData = async () => {
                    isLoading.value = true
                    addLog('info', '开始刷新系统数据...')
                    
                    // 模拟API调用延迟
                    await new Promise(resolve => setTimeout(resolve, 1500))
                    
                    try {
                        // 模拟数据更新
                        metrics.onlineStations = Math.floor(Math.random() * 20) + 140
                        metrics.dataFlow = Math.round((Math.random() * 50 + 60) * 10) / 10
                        metrics.activeAlerts = Math.floor(Math.random() * 5)
                        metrics.storageUsage = Math.floor(Math.random() * 30) + 50
                        metrics.lastAlertTime = new Date()
                        
                        addLog('success', '系统数据刷新完成')
                    } catch (error) {
                        addLog('error', `数据刷新失败: ${error.message}`)
                    } finally {
                        isLoading.value = false
                    }
                }
                
                // 开始数据采集
                const startDataCollection = () => {
                    dataCollectionActive.value = true
                    addLog('success', '数据采集服务已启动')
                    
                    // 模拟数据采集过程
                    const collectionInterval = setInterval(() => {
                        if (!dataCollectionActive.value) {
                            clearInterval(collectionInterval)
                            return
                        }
                        
                        // 随机更新数据流量
                        metrics.dataFlow = Math.round((metrics.dataFlow + (Math.random() - 0.5) * 10) * 10) / 10
                        metrics.dataFlow = Math.max(0, Math.min(200, metrics.dataFlow))
                    }, 3000)
                }
                
                // 暂停数据采集
                const pauseDataCollection = () => {
                    dataCollectionActive.value = false
                    addLog('warning', '数据采集服务已暂停')
                }
                
                // 清除所有预警
                const clearAllAlerts = () => {
                    const clearedCount = metrics.activeAlerts
                    metrics.activeAlerts = 0
                    addLog('info', `已清除 ${clearedCount} 条预警信息`)
                }
                
                // 添加系统日志
                const addLog = (level, message) => {
                    const newLog = {
                        id: Date.now(),
                        timestamp: new Date(),
                        level,
                        message
                    }
                    
                    systemLogs.value.unshift(newLog)
                    
                    // 限制日志数量，保留最新50条
                    if (systemLogs.value.length > 50) {
                        systemLogs.value = systemLogs.value.slice(0, 50)
                    }
                }
                
                // 获取状态卡片样式类
                const getCardClass = (type) => {
                    switch (type) {
                        case 'stations':
                            return stationOnlineRate.value < 80 ? 'error' : 
                                   stationOnlineRate.value < 95 ? 'warning' : 'success'
                        case 'dataFlow':
                            return metrics.dataFlow > 150 ? 'error' : 
                                   metrics.dataFlow > 100 ? 'warning' : 'success'
                        case 'alerts':
                            return metrics.activeAlerts > 5 ? 'error' : 
                                   metrics.activeAlerts > 2 ? 'warning' : 'success'
                        case 'storage':
                            return metrics.storageUsage > 90 ? 'error' : 
                                   metrics.storageUsage > 80 ? 'warning' : 'success'
                        default:
                            return ''
                    }
                }
                
                // 格式化日期
                const formatDate = (date) => {
                    return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN')
                }
                
                // 格式化时间
                const formatTime = (date) => {
                    return date.toLocaleTimeString('zh-CN')
                }
                
                // 更新运行时长
                const updateUptime = () => {
                    const now = new Date()
                    const diff = now - systemInfo.startTime
                    const hours = Math.floor(diff / (1000 * 60 * 60))
                    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
                    const seconds = Math.floor((diff % (1000 * 60)) / 1000)
                    
                    uptime.value = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
                }
                
                // ===== 生命周期钩子 =====
                
                let uptimeTimer = null
                
                onMounted(() => {
                    // 组件挂载后执行
                    addLog('info', '监控控制台界面加载完成')
                    
                    // 启动运行时长计时器
                    uptimeTimer = setInterval(updateUptime, 1000)
                    
                    // 初始化数据采集
                    if (dataCollectionActive.value) {
                        startDataCollection()
                    }
                })
                
                onUnmounted(() => {
                    // 组件卸载前清理
                    if (uptimeTimer) {
                        clearInterval(uptimeTimer)
                    }
                    addLog('info', '监控控制台正在关闭')
                })
                
                // ===== 返回给模板使用的数据和方法 =====
                return {
                    // 响应式数据
                    systemInfo,
                    metrics,
                    isLoading,
                    dataCollectionActive,
                    uptime,
                    systemLogs,
                    
                    // 计算属性
                    stationOnlineRate,
                    systemStatus,
                    
                    // 方法
                    refreshSystemData,
                    startDataCollection,
                    pauseDataCollection,
                    clearAllAlerts,
                    getCardClass,
                    formatDate,
                    formatTime
                }
            }
        })
        
        // 全局配置
        app.config.globalProperties.$version = '2.0.1'
        app.config.errorHandler = (err, instance, info) => {
            console.error('Vue应用错误:', err)
            console.error('组件实例:', instance)
            console.error('错误信息:', info)
        }
        
        // 挂载应用到DOM
        app.mount('#water-monitoring-console')
    </script>
</body>
</html>
```

这个完整的控制台应用展示了Vue 3应用创建的各个方面：

**1. 应用实例创建**：
- 使用`createApp()`创建应用实例
- 通过`setup()`函数配置Composition API
- 使用`mount()`挂载到DOM元素

**2. 响应式数据管理**：
- `ref()`创建基本类型的响应式数据
- `reactive()`创建对象类型的响应式数据
- 数据变化自动触发视图更新

**3. 计算属性和侦听器**：
- `computed()`创建依赖其他数据的计算属性
- `watch()`监听数据变化并执行相应逻辑

**4. 生命周期管理**：
- `onMounted()`在组件挂载后执行初始化逻辑
- `onUnmounted()`在组件卸载前清理资源

### 响应式数据声明与管理

Vue 3的Composition API为响应式数据管理提供了更灵活和强大的方式。在水利监测系统中，我们需要处理各种类型的数据：传感器读数、设备状态、用户配置等。

**响应式数据的类型和使用场景：**

```vue
<template>
  <div class="sensor-data-management">
    <h2>传感器数据管理</h2>
    
    <!-- 基础数据展示 -->
    <div class="data-section">
      <h3>实时监测数据</h3>
      <div class="sensor-grid">
        <div v-for="sensor in sensorList" :key="sensor.id" class="sensor-card">
          <h4>{{ sensor.name }}</h4>
          <div class="sensor-value">
            <span class="value">{{ sensor.currentValue }}</span>
            <span class="unit">{{ sensor.unit }}</span>
          </div>
          <div class="sensor-status" :class="getSensorStatus(sensor)">
            {{ getSensorStatusText(sensor) }}
          </div>
          <div class="last-update">
            更新于: {{ formatTime(sensor.lastUpdate) }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- 数据配置 -->
    <div class="config-section">
      <h3>监测配置</h3>
      <form @submit.prevent="saveConfiguration">
        <div class="config-group">
          <label>采样间隔 (秒):</label>
          <input 
            v-model.number="config.samplingInterval" 
            type="number" 
            min="1" 
            max="3600"
            class="config-input"
          />
        </div>
        
        <div class="config-group">
          <label>数据保留期 (天):</label>
          <input 
            v-model.number="config.dataRetentionDays" 
            type="number" 
            min="1" 
            max="3650"
            class="config-input"
          />
        </div>
        
        <div class="config-group">
          <label>预警阈值设置:</label>
          <div class="threshold-settings">
            <div v-for="(threshold, key) in config.alertThresholds" :key="key">
              <span>{{ getThresholdLabel(key) }}:</span>
              <input 
                v-model.number="threshold.min" 
                type="number" 
                step="0.1"
                placeholder="最小值"
                class="threshold-input"
              />
              <span> ~ </span>
              <input 
                v-model.number="threshold.max" 
                type="number" 
                step="0.1"
                placeholder="最大值"
                class="threshold-input"
              />
              <span>{{ getThresholdUnit(key) }}</span>
            </div>
          </div>
        </div>
        
        <div class="config-group">
          <label>启用功能:</label>
          <div class="feature-toggles">
            <label class="toggle-item">
              <input 
                v-model="config.features.autoAlert" 
                type="checkbox"
              />
              自动预警
            </label>
            <label class="toggle-item">
              <input 
                v-model="config.features.dataBackup" 
                type="checkbox"
              />
              数据备份
            </label>
            <label class="toggle-item">
              <input 
                v-model="config.features.remoteMonitoring" 
                type="checkbox"
              />
              远程监控
            </label>
          </div>
        </div>
        
        <button type="submit" class="btn btn-primary" :disabled="isSaving">
          {{ isSaving ? '保存中...' : '保存配置' }}
        </button>
      </form>
    </div>
    
    <!-- 统计信息 -->
    <div class="stats-section">
      <h3>数据统计</h3>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">总传感器数</div>
          <div class="stat-value">{{ totalSensors }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">在线传感器</div>
          <div class="stat-value">{{ onlineSensors }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">异常传感器</div>
          <div class="stat-value">{{ abnormalSensors }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">数据完整率</div>
          <div class="stat-value">{{ dataIntegrityRate }}%</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, toRefs, nextTick } from 'vue'

// ===== 基本响应式数据 =====

// ref() - 用于基本类型数据
const isSaving = ref(false)
const lastSyncTime = ref(new Date())

// reactive() - 用于对象类型数据
const sensorList = reactive([
  {
    id: 'WL001',
    name: '水位传感器-1号泵站',
    currentValue: 4.25,
    unit: 'm',
    threshold: { min: 2.0, max: 6.0 },
    lastUpdate: new Date(),
    status: 'normal'
  },
  {
    id: 'FL002', 
    name: '流量传感器-主干道',
    currentValue: 1580.5,
    unit: 'm³/s',
    threshold: { min: 500, max: 2000 },
    lastUpdate: new Date(),
    status: 'normal'
  },
  {
    id: 'PR003',
    name: '压力传感器-出水口',
    currentValue: 0.85,
    unit: 'MPa',
    threshold: { min: 0.1, max: 1.0 },
    lastUpdate: new Date(),
    status: 'warning'
  },
  {
    id: 'TM004',
    name: '水温传感器-入水口',
    currentValue: 18.2,
    unit: '°C',
    threshold: { min: 5.0, max: 35.0 },
    lastUpdate: new Date(),
    status: 'normal'
  }
])

// 复杂对象的响应式管理
const config = reactive({
  samplingInterval: 30,
  dataRetentionDays: 365,
  alertThresholds: {
    waterLevel: { min: 2.0, max: 6.0 },
    flowRate: { min: 500, max: 2000 },
    pressure: { min: 0.1, max: 1.0 },
    temperature: { min: 5.0, max: 35.0 }
  },
  features: {
    autoAlert: true,
    dataBackup: true,
    remoteMonitoring: false
  }
})

// ===== 计算属性 - 自动处理数据统计 =====

const totalSensors = computed(() => {
  return sensorList.length
})

const onlineSensors = computed(() => {
  return sensorList.filter(sensor => 
    sensor.status === 'normal' || sensor.status === 'warning'
  ).length
})

const abnormalSensors = computed(() => {
  return sensorList.filter(sensor => sensor.status === 'error').length
})

const dataIntegrityRate = computed(() => {
  if (totalSensors.value === 0) return 100
  const validSensors = sensorList.filter(sensor => 
    sensor.currentValue !== null && sensor.currentValue !== undefined
  ).length
  return Math.round((validSensors / totalSensors.value) * 100)
})

// ===== 响应式数据的监听和处理 =====

// 深度监听传感器数据变化
watch(sensorList, (newList) => {
  console.log('传感器数据已更新:', newList.length)
  // 检查是否有新的异常
  const errors = newList.filter(s => s.status === 'error')
  if (errors.length > 0) {
    console.warn('发现异常传感器:', errors.map(s => s.name))
  }
}, { deep: true })

// 监听配置变化并自动保存
watch(config, (newConfig) => {
  console.log('配置已更改:', newConfig)
  // 可以在这里实现自动保存逻辑
  localStorage.setItem('sensorConfig', JSON.stringify(newConfig))
}, { deep: true })

// 监听特定配置项
watch(() => config.samplingInterval, (newInterval) => {
  console.log(`采样间隔变更为: ${newInterval} 秒`)
  // 重新设置数据采集定时器
  setupDataCollection(newInterval)
})

// 监听预警功能开关
watch(() => config.features.autoAlert, (enabled) => {
  if (enabled) {
    console.log('自动预警功能已启用')
    startAlertSystem()
  } else {
    console.log('自动预警功能已关闭')
    stopAlertSystem()
  }
})

// ===== 数据操作方法 =====

const updateSensorData = (sensorId, newValue) => {
  const sensor = sensorList.find(s => s.id === sensorId)
  if (sensor) {
    sensor.currentValue = newValue
    sensor.lastUpdate = new Date()
    sensor.status = determineSensorStatus(sensor)
  }
}

const determineSensorStatus = (sensor) => {
  const { currentValue, threshold } = sensor
  if (currentValue < threshold.min || currentValue > threshold.max) {
    return 'warning'
  }
  // 可以添加更复杂的状态判断逻辑
  return 'normal'
}

const saveConfiguration = async () => {
  isSaving.value = true
  try {
    // 模拟保存到服务器
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 应用新配置
    applyNewConfiguration()
    
    console.log('配置保存成功')
  } catch (error) {
    console.error('配置保存失败:', error)
  } finally {
    isSaving.value = false
  }
}

const applyNewConfiguration = () => {
  // 更新传感器阈值
  sensorList.forEach(sensor => {
    const thresholdKey = getSensorThresholdKey(sensor.id)
    if (config.alertThresholds[thresholdKey]) {
      sensor.threshold = { ...config.alertThresholds[thresholdKey] }
      sensor.status = determineSensorStatus(sensor)
    }
  })
}

const getSensorThresholdKey = (sensorId) => {
  if (sensorId.startsWith('WL')) return 'waterLevel'
  if (sensorId.startsWith('FL')) return 'flowRate'
  if (sensorId.startsWith('PR')) return 'pressure'
  if (sensorId.startsWith('TM')) return 'temperature'
  return 'waterLevel'
}

// ===== 工具方法 =====

const getSensorStatus = (sensor) => {
  return `status-${sensor.status}`
}

const getSensorStatusText = (sensor) => {
  const statusMap = {
    normal: '正常',
    warning: '预警',
    error: '故障',
    offline: '离线'
  }
  return statusMap[sensor.status] || '未知'
}

const getThresholdLabel = (key) => {
  const labelMap = {
    waterLevel: '水位',
    flowRate: '流量',
    pressure: '压力',
    temperature: '温度'
  }
  return labelMap[key] || key
}

const getThresholdUnit = (key) => {
  const unitMap = {
    waterLevel: 'm',
    flowRate: 'm³/s',
    pressure: 'MPa',
    temperature: '°C'
  }
  return unitMap[key] || ''
}

const formatTime = (date) => {
  return date.toLocaleTimeString('zh-CN')
}

// ===== 数据采集和监控功能 =====

let dataCollectionTimer = null
let alertSystemActive = false

const setupDataCollection = (interval) => {
  if (dataCollectionTimer) {
    clearInterval(dataCollectionTimer)
  }
  
  dataCollectionTimer = setInterval(() => {
    // 模拟传感器数据更新
    sensorList.forEach(sensor => {
      // 生成随机变化的数据
      const baseValue = sensor.currentValue
      const variation = (Math.random() - 0.5) * 0.1 * baseValue
      const newValue = Math.max(0, baseValue + variation)
      
      updateSensorData(sensor.id, Math.round(newValue * 100) / 100)
    })
    
    lastSyncTime.value = new Date()
  }, interval * 1000)
}

const startAlertSystem = () => {
  alertSystemActive = true
  console.log('预警系统已启动')
}

const stopAlertSystem = () => {
  alertSystemActive = false  
  console.log('预警系统已停止')
}

// ===== 生命周期管理 =====

import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
  // 加载保存的配置
  const savedConfig = localStorage.getItem('sensorConfig')
  if (savedConfig) {
    try {
      const parsedConfig = JSON.parse(savedConfig)
      Object.assign(config, parsedConfig)
    } catch (error) {
      console.error('加载配置失败:', error)
    }
  }
  
  // 启动数据采集
  setupDataCollection(config.samplingInterval)
  
  if (config.features.autoAlert) {
    startAlertSystem()
  }
})

onUnmounted(() => {
  if (dataCollectionTimer) {
    clearInterval(dataCollectionTimer)
  }
  stopAlertSystem()
})
</script>

<style scoped>
.sensor-data-management {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.data-section, .config-section, .stats-section {
  background: white;
  border-radius: 8px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.sensor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.sensor-card {
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  padding: 20px;
  background: #fafafa;
}

.sensor-card h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.sensor-value {
  font-size: 24px;
  font-weight: bold;
  margin: 10px 0;
}

.sensor-value .value {
  color: #1890ff;
}

.sensor-value .unit {
  font-size: 16px;
  color: #7f8c8d;
  margin-left: 5px;
}

.sensor-status {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  display: inline-block;
  margin: 10px 0;
}

.status-normal { background: #f6ffed; color: #52c41a; }
.status-warning { background: #fff7e6; color: #fa8c16; }
.status-error { background: #ffe6e6; color: #ff4757; }
.status-offline { background: #f0f0f0; color: #999; }

.last-update {
  font-size: 12px;
  color: #999;
}

.config-group {
  margin-bottom: 25px;
}

.config-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #2c3e50;
}

.config-input, .threshold-input {
  width: 120px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.threshold-settings > div {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 10px 0;
}

.feature-toggles {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.toggle-item {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  background: #fafafa;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #2c3e50;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #40a9ff;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
```

这个传感器数据管理示例展示了Vue 3响应式数据的各种使用方法：

**1. 数据类型选择**：
- `ref()`: 用于基本类型（数字、字符串、布尔值）
- `reactive()`: 用于对象和数组类型

**2. 数据监听**：
- `watch()`: 监听特定数据变化
- 深度监听(`{ deep: true }`): 监听对象内部属性变化

**3. 计算属性**：
- 基于基础数据自动计算统计信息
- 数据变化时自动重新计算

### 模板语法与数据绑定

Vue.js的模板语法基于HTML，但扩展了强大的数据绑定功能。对于水利监测系统，模板语法让我们能够优雅地处理动态数据展示、用户交互和条件渲染等需求。

**Vue模板语法的核心特性包括：**

1. **插值表达式** - 将数据绑定到文本内容
2. **属性绑定** - 动态设置HTML属性
3. **条件渲染** - 根据条件显示或隐藏元素
4. **列表渲染** - 循环显示数据列表
5. **事件绑定** - 响应用户操作

让我们通过一个完整的水利数据可视化仪表盘来学习这些语法特性：

```vue
<template>
  <!-- 水利监测数据仪表盘 -->
  <div class="water-monitoring-dashboard">
    <!-- 页面头部 - 插值表达式示例 -->
    <header class="dashboard-header">
      <h1>{{ dashboardTitle }}</h1>
      <div class="header-info">
        <span class="location">{{ currentLocation }}</span>
        <span class="datetime">{{ formatDateTime(currentTime) }}</span>
        <span class="weather" :class="weatherClass">
          {{ weatherInfo.description }} {{ weatherInfo.temperature }}°C
        </span>
      </div>
    </header>

    <!-- 系统状态指示器 - 条件渲染示例 -->
    <div class="system-status">
      <div 
        class="status-indicator" 
        :class="systemStatusClass"
        :title="systemStatusTooltip"
      >
        <!-- v-if/v-else-if/v-else 条件渲染 -->
        <span v-if="systemStatus === 'healthy'" class="status-icon">✓/span>
        <span v-else-if="systemStatus === 'warning'" class="status-icon">⚠</span>
        <span v-else-if="systemStatus === 'error'" class="status-icon">✓/span>
        <span v-else class="status-icon">?</span>
        
        <span class="status-text">{{ systemStatusText }}</span>
      </div>
      
      <!-- v-show 条件显示 -->
      <div v-show="showDetailedStatus" class="detailed-status">
        <p>在线监测站: {{ onlineStations }} / {{ totalStations }}</p>
        <p>数据完整率: {{ dataIntegrityRate }}%</p>
        <p>最后更新: {{ formatTime(lastUpdateTime) }}</p>
      </div>
    </div>

    <!-- 监测点数据网格 - 列表渲染示例 -->
    <div class="monitoring-grid">
      <h2>实时监测数据</h2>
      
      <!-- v-for 基础列表渲染 -->
      <div class="grid-container">
        <div 
          v-for="station in filteredStations" 
          :key="station.id"
          class="station-card"
          :class="getStationCardClass(station)"
          @click="selectStation(station)"
        >
          <!-- 复合数据绑定 -->
          <div class="station-header">
            <h3>{{ station.name }}</h3>
            <span 
              class="station-id"
              :style="{ color: station.status === 'online' ? '#52c41a' : '#ff4757' }"
            >
              #{{ station.id }}
            </span>
          </div>
          
          <!-- 动态属性绑定 -->
          <div class="station-data">
            <div 
              v-for="(value, key) in station.measurements" 
              :key="key"
              class="data-item"
            >
              <span class="data-label">{{ getMeasurementLabel(key) }}:</span>
              <span 
                class="data-value" 
                :class="getValueStatusClass(key, value)"
                :title="`正常范围: ${getValueRange(key)}`"
              >
                {{ formatValue(key, value) }}
              </span>
            </div>
          </div>
          
          <!-- 条件渲染的预警信息 -->
          <div v-if="station.alerts && station.alerts.length > 0" class="station-alerts">
            <div 
              v-for="alert in station.alerts" 
              :key="alert.id"
              class="alert-item"
              :class="`alert-${alert.level}`"
            >
              <span class="alert-icon">{{ getAlertIcon(alert.level) }}</span>
              <span class="alert-message">{{ alert.message }}</span>
            </div>
          </div>
          
          <!-- 操作按钮组 -->
          <div class="station-actions">
            <button 
              class="btn btn-sm"
              :class="{ 'btn-primary': !station.isMonitoring, 'btn-warning': station.isMonitoring }"
              @click.stop="toggleMonitoring(station)"
              :disabled="station.status === 'offline'"
            >
              {{ station.isMonitoring ? '停止监控' : '开始监控' }}
            </button>
            
            <button 
              class="btn btn-sm btn-info"
              @click.stop="viewHistory(station)"
            >
              历史数据
            </button>
          </div>
        </div>
      </div>
      
      <!-- 条件渲染的空状态 -->
      <div v-if="filteredStations.length === 0" class="empty-state">
        <div class="empty-icon">📊</div>
        <h3>暂无监测数据</h3>
        <p v-if="searchKeyword">
          未找到包含"{{ searchKeyword }}"的监测站
        </p>
        <p v-else>
          当前没有在线的监测站点
        </p>
        <button class="btn btn-primary" @click="refreshData">刷新数据</button>
      </div>
    </div>

    <!-- 数据筛选控制栏 -->
    <div class="filter-controls">
      <h3>数据筛选</h3>
      
      <!-- v-model 双向数据绑定 -->
      <div class="filter-group">
        <label>搜索监测站:</label>
        <input 
          v-model="searchKeyword" 
          type="text"
          placeholder="输入监测站名称或ID..."
          class="search-input"
          @input="handleSearchInput"
        />
      </div>
      
      <div class="filter-group">
        <label>状态筛选:</label>
        <select v-model="selectedStatus" class="status-filter">
          <option value="">全部状态</option>
          <option value="online">在线</option>
          <option value="offline">离线</option>
          <option value="warning">预警</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>区域筛选:</label>
        <div class="region-checkboxes">
          <label 
            v-for="region in availableRegions" 
            :key="region"
            class="checkbox-label"
          >
            <input 
              type="checkbox" 
              :value="region"
              v-model="selectedRegions"
              @change="handleRegionChange"
            />
            {{ region }}
          </label>
        </div>
      </div>
      
      <div class="filter-group">
        <label>数据类型:</label>
        <div class="data-type-radios">
          <label 
            v-for="dataType in dataTypes" 
            :key="dataType.value"
            class="radio-label"
          >
            <input 
              type="radio" 
              :value="dataType.value"
              v-model="selectedDataType"
            />
            {{ dataType.label }}
          </label>
        </div>
      </div>
    </div>

    <!-- 高级数据表格 - 复杂列表渲染 -->
    <div class="data-table-section" v-if="showDataTable">
      <h3>详细数据表格</h3>
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th 
                v-for="column in tableColumns" 
                :key="column.key"
                :class="{ 'sortable': column.sortable }"
                @click="column.sortable && sortBy(column.key)"
              >
                {{ column.title }}
                <span 
                  v-if="column.sortable"
                  class="sort-indicator"
                  :class="getSortClass(column.key)"
                >
                  {{ getSortIcon(column.key) }}
                </span>
              </th>
            </tr>
          </thead>
          <tbody>
            <!-- 嵌套v-for和条件渲染 -->
            <template v-for="station in paginatedTableData" :key="station.id">
              <tr 
                class="station-row"
                :class="{ 'selected': selectedTableRows.includes(station.id) }"
                @click="toggleTableRowSelection(station.id)"
              >
                <td>{{ station.name }}</td>
                <td>{{ station.id }}</td>
                <td>
                  <span 
                    class="status-badge"
                    :class="`status-${station.status}`"
                  >
                    {{ station.status }}
                  </span>
                </td>
                <td>{{ station.location }}</td>
                <td>{{ formatTime(station.lastUpdate) }}</td>
                <td>
                  <div class="table-actions">
                    <button 
                      class="btn-icon" 
                      @click.stop="editStation(station)"
                      title="编辑"
                    >
                      ✏️
                    </button>
                    <button 
                      class="btn-icon" 
                      @click.stop="deleteStation(station.id)"
                      title="删除"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
              
              <!-- 展开行 - 条件渲染详细信息 -->
              <tr 
                v-if="expandedRows.includes(station.id)"
                class="expanded-row"
              >
                <td :colspan="tableColumns.length">
                  <div class="expanded-content">
                    <div class="measurement-details">
                      <h4>测量数据详情</h4>
                      <div class="measurement-grid">
                        <div 
                          v-for="(value, key) in station.measurements"
                          :key="key"
                          class="measurement-item"
                        >
                          <span class="measurement-name">{{ getMeasurementLabel(key) }}</span>
                          <span class="measurement-value">{{ formatValue(key, value) }}</span>
                          <div 
                            class="measurement-trend"
                            :class="getTrendClass(station.trends[key])"
                          >
                            {{ getTrendIcon(station.trends[key]) }} 
                            {{ station.trends[key] }}%
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
        
        <!-- 分页控制 - 动态生成页码 -->
        <div class="pagination" v-if="totalPages > 1">
          <button 
            class="page-btn"
            :disabled="currentPage === 1"
            @click="changePage(currentPage - 1)"
          >
            上一页
          </button>
          
          <span 
            v-for="page in visiblePageNumbers" 
            :key="page"
            class="page-number"
            :class="{ 'active': page === currentPage }"
            @click="changePage(page)"
          >
            {{ page }}
          </span>
          
          <button 
            class="page-btn"
            :disabled="currentPage === totalPages"
            @click="changePage(currentPage + 1)"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 实时图表展示 - 动态样式绑定 -->
    <div class="charts-section">
      <h3>数据趋势图表</h3>
      <div class="chart-container">
        <!-- 模拟图表数据展示 -->
        <div 
          v-for="chartData in chartDataSets" 
          :key="chartData.id"
          class="chart-item"
          :style="getChartStyle(chartData)"
        >
          <h4>{{ chartData.title }}</h4>
          <div class="chart-visualization">
            <!-- 简单的柱状图实现 -->
            <div class="chart-bars">
              <div 
                v-for="(dataPoint, index) in chartData.data.slice(-10)"
                :key="index"
                class="chart-bar"
                :style="{ 
                  height: (dataPoint.value / chartData.maxValue * 100) + '%',
                  backgroundColor: getBarColor(dataPoint.value, chartData)
                }"
                :title="`${dataPoint.label}: ${dataPoint.value}${chartData.unit}`"
              ></div>
            </div>
            
            <div class="chart-info">
              <span class="current-value">
                当前值: {{ chartData.currentValue }}{{ chartData.unit }}
              </span>
              <span 
                class="trend-indicator"
                :class="chartData.trend"
              >
                {{ getTrendText(chartData.trend) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onMounted } from 'vue'

// ===== 基础数据定义 =====
const dashboardTitle = ref('智慧水利综合监测平台')
const currentLocation = ref('黄河流域监测中心')
const currentTime = ref(new Date())
const showDetailedStatus = ref(true)
const showDataTable = ref(true)

// 搜索和筛选
const searchKeyword = ref('')
const selectedStatus = ref('')
const selectedRegions = ref([])
const selectedDataType = ref('all')

// 表格状态
const selectedTableRows = ref([])
const expandedRows = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const sortField = ref('')
const sortDirection = ref('asc')

// 系统状态数据
const systemStatus = ref('healthy') // healthy, warning, error, unknown
const onlineStations = ref(45)
const totalStations = ref(50)
const dataIntegrityRate = ref(96.8)
const lastUpdateTime = ref(new Date())

// 天气信息
const weatherInfo = reactive({
  description: '晴',
  temperature: 25,
  condition: 'sunny'
})

// 监测站数据
const monitoringStations = reactive([
  {
    id: 'HH001',
    name: '黄河小浪底监测站',
    status: 'online',
    location: '河南省洛阳市',
    isMonitoring: true,
    measurements: {
      waterLevel: 4.25,
      flowRate: 1580.5,
      pressure: 0.85,
      temperature: 18.2
    },
    trends: {
      waterLevel: 2.3,
      flowRate: -1.8,
      pressure: 0.5,
      temperature: 1.2
    },
    alerts: [
      { id: 1, level: 'warning', message: '水位接近警戒线' }
    ],
    lastUpdate: new Date()
  },
  {
    id: 'CJ002',
    name: '长江三峡监测站',
    status: 'online',
    location: '湖北省宜昌市',
    isMonitoring: true,
    measurements: {
      waterLevel: 6.80,
      flowRate: 2450.3,
      pressure: 1.25,
      temperature: 16.8
    },
    trends: {
      waterLevel: -0.8,
      flowRate: 3.2,
      pressure: -0.3,
      temperature: -0.5
    },
    alerts: [],
    lastUpdate: new Date()
  },
  {
    id: 'ZJ003',
    name: '珠江口监测站',
    status: 'warning',
    location: '广东省广州市',
    isMonitoring: false,
    measurements: {
      waterLevel: 3.15,
      flowRate: 890.7,
      pressure: 0.65,
      temperature: 24.5
    },
    trends: {
      waterLevel: 1.5,
      flowRate: -2.1,
      pressure: 0.8,
      temperature: 0.3
    },
    alerts: [
      { id: 2, level: 'error', message: '数据传输异常' }
    ],
    lastUpdate: new Date(Date.now() - 300000) // 5分钟前
  }
])

// 筛选选项数据
const availableRegions = ref(['华北', '华中', '华南', '西北', '西南'])
const dataTypes = ref([
  { value: 'all', label: '全部数据' },
  { value: 'water', label: '水位数据' },
  { value: 'flow', label: '流量数据' },
  { value: 'quality', label: '水质数据' }
])

// 表格配置
const tableColumns = ref([
  { key: 'name', title: '监测站名称', sortable: true },
  { key: 'id', title: 'ID', sortable: true },
  { key: 'status', title: '状态', sortable: true },
  { key: 'location', title: '位置', sortable: false },
  { key: 'lastUpdate', title: '最后更新', sortable: true },
  { key: 'actions', title: '操作', sortable: false }
])

// 图表数据
const chartDataSets = reactive([
  {
    id: 'waterLevel',
    title: '水位变化趋势',
    unit: 'm',
    maxValue: 10,
    currentValue: 4.25,
    trend: 'rising',
    data: [
      { label: '1h前', value: 4.1 },
      { label: '2h前', value: 4.15 },
      { label: '3h前', value: 4.08 },
      { label: '4h前', value: 4.12 },
      { label: '5h前', value: 4.18 },
      { label: '6h前', value: 4.22 },
      { label: '现在', value: 4.25 }
    ]
  },
  {
    id: 'flowRate',
    title: '流量变化趋势',
    unit: 'm³/s',
    maxValue: 3000,
    currentValue: 1580.5,
    trend: 'falling',
    data: [
      { label: '1h前', value: 1620 },
      { label: '2h前', value: 1605 },
      { label: '3h前', value: 1595 },
      { label: '4h前', value: 1588 },
      { label: '5h前', value: 1592 },
      { label: '6h前', value: 1585 },
      { label: '现在', value: 1580.5 }
    ]
  }
])

// ===== 计算属性 =====

// 系统状态相关计算
const systemStatusClass = computed(() => `status-${systemStatus.value}`)
const systemStatusText = computed(() => {
  const statusMap = {
    healthy: '系统正常',
    warning: '系统预警',
    error: '系统故障',
    unknown: '状态未知'
  }
  return statusMap[systemStatus.value] || '未知状态'
})

const systemStatusTooltip = computed(() => {
  return `在线率: ${Math.round(onlineStations.value / totalStations.value * 100)}%, 完整率: ${dataIntegrityRate.value}%`
})

const weatherClass = computed(() => {
  return `weather-${weatherInfo.condition}`
})

// 数据筛选计算
const filteredStations = computed(() => {
  let result = [...monitoringStations]
  
  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(station => 
      station.name.toLowerCase().includes(keyword) ||
      station.id.toLowerCase().includes(keyword)
    )
  }
  
  // 按状态筛选
  if (selectedStatus.value) {
    result = result.filter(station => station.status === selectedStatus.value)
  }
  
  // 按区域筛选
  if (selectedRegions.value.length > 0) {
    result = result.filter(station => 
      selectedRegions.value.some(region => station.location.includes(region))
    )
  }
  
  return result
})

// 表格分页计算
const totalPages = computed(() => {
  return Math.ceil(filteredStations.value.length / pageSize.value)
})

const paginatedTableData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredStations.value.slice(start, end)
})

const visiblePageNumbers = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  // 简单的分页逻辑：显示当前页前后2页
  const start = Math.max(1, current - 2)
  const end = Math.min(total, current + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// ===== 方法定义 =====

// 格式化方法
const formatDateTime = (date) => {
  return date.toLocaleString('zh-CN')
}

const formatTime = (date) => {
  return date.toLocaleTimeString('zh-CN')
}

const formatValue = (key, value) => {
  const formatMap = {
    waterLevel: `${value} m`,
    flowRate: `${value} m³/s`,
    pressure: `${value} MPa`,
    temperature: `${value} °C`
  }
  return formatMap[key] || `${value}`
}

const getMeasurementLabel = (key) => {
  const labelMap = {
    waterLevel: '水位',
    flowRate: '流量',
    pressure: '压力',
    temperature: '水温'
  }
  return labelMap[key] || key
}

const getValueRange = (key) => {
  const rangeMap = {
    waterLevel: '2.0 - 8.0 m',
    flowRate: '500 - 3000 m³/s',
    pressure: '0.1 - 1.5 MPa',
    temperature: '5 - 30 °C'
  }
  return rangeMap[key] || ''
}

// 状态判断方法
const getStationCardClass = (station) => {
  return `card-${station.status}`
}

const getValueStatusClass = (key, value) => {
  // 简单的阈值判断
  const thresholds = {
    waterLevel: { min: 2.0, max: 8.0 },
    flowRate: { min: 500, max: 3000 },
    pressure: { min: 0.1, max: 1.5 },
    temperature: { min: 5, max: 30 }
  }
  
  const threshold = thresholds[key]
  if (!threshold) return ''
  
  if (value < threshold.min || value > threshold.max) {
    return 'value-warning'
  }
  return 'value-normal'
}

const getAlertIcon = (level) => {
  const iconMap = {
    info: 'ℹ️',
    warning: '⚠️',
    error: '❌'
  }
  return iconMap[level] || '📢'
}

// 交互处理方法
const selectStation = (station) => {
  console.log('选中监测站:', station.name)
  // 这里可以实现选中逻辑
}

const toggleMonitoring = (station) => {
  station.isMonitoring = !station.isMonitoring
  console.log(`${station.name} 监控状态: ${station.isMonitoring ? '开启' : '关闭'}`)
}

const viewHistory = (station) => {
  console.log('查看历史数据:', station.name)
  // 实现历史数据查看逻辑
}

const refreshData = () => {
  console.log('刷新数据')
  // 模拟数据刷新
  monitoringStations.forEach(station => {
    station.lastUpdate = new Date()
  })
}

const handleSearchInput = () => {
  currentPage.value = 1 // 搜索时重置到第一页
}

const handleRegionChange = () => {
  currentPage.value = 1 // 筛选时重置到第一页
}

// 表格操作方法
const toggleTableRowSelection = (stationId) => {
  const index = selectedTableRows.value.indexOf(stationId)
  if (index > -1) {
    selectedTableRows.value.splice(index, 1)
  } else {
    selectedTableRows.value.push(stationId)
  }
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const sortBy = (field) => {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'asc'
  }
  // 实现排序逻辑
}

const getSortClass = (field) => {
  if (sortField.value !== field) return ''
  return sortDirection.value === 'asc' ? 'sort-asc' : 'sort-desc'
}

const getSortIcon = (field) => {
  if (sortField.value !== field) return '↕️'
  return sortDirection.value === 'asc' ? '↑' : '↓'
}

const editStation = (station) => {
  console.log('编辑监测站:', station.name)
}

const deleteStation = (stationId) => {
  if (confirm('确定要删除这个监测站吗？')) {
    const index = monitoringStations.findIndex(s => s.id === stationId)
    if (index > -1) {
      monitoringStations.splice(index, 1)
    }
  }
}

// 图表相关方法
const getChartStyle = (chartData) => {
  return {
    borderLeft: `4px solid ${chartData.trend === 'rising' ? '#52c41a' : '#ff4757'}`
  }
}

const getBarColor = (value, chartData) => {
  const percentage = value / chartData.maxValue
  if (percentage > 0.8) return '#ff4757'
  if (percentage > 0.6) return '#ffa502'
  return '#1890ff'
}

const getTrendClass = (trend) => {
  if (trend > 0) return 'trend-up'
  if (trend < 0) return 'trend-down'
  return 'trend-stable'
}

const getTrendIcon = (trend) => {
  if (trend > 0) return '↗'
  if (trend < 0) return '↘'
  return '→'
}

const getTrendText = (trend) => {
  if (trend === 'rising') return '上升趋势'
  if (trend === 'falling') return '下降趋势'
  return '平稳'
}

// ===== 生命周期和数据监听 =====

// 监听搜索关键词变化
watch(searchKeyword, () => {
  currentPage.value = 1
})

// 定时更新当前时间
let timeUpdateTimer = null

onMounted(() => {
  // 启动时间更新定时器
  timeUpdateTimer = setInterval(() => {
    currentTime.value = new Date()
  }, 1000)
  
  // 模拟定期数据更新
  setInterval(() => {
    // 随机更新一些数据
    monitoringStations.forEach(station => {
      if (Math.random() > 0.7) { // 30% 概率更新数据
        Object.keys(station.measurements).forEach(key => {
          const current = station.measurements[key]
          const variation = (Math.random() - 0.5) * 0.1 * current
          station.measurements[key] = Math.max(0, current + variation)
        })
        station.lastUpdate = new Date()
      }
    })
  }, 5000)
})

// 清理定时器
import { onUnmounted } from 'vue'

onUnmounted(() => {
  if (timeUpdateTimer) {
    clearInterval(timeUpdateTimer)
  }
})
</script>

<style scoped>
/* 基础样式 */
.water-monitoring-dashboard {
  max-width: 1600px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Microsoft YaHei', sans-serif;
}

/* 头部样式 */
.dashboard-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 10px;
  margin-bottom: 30px;
}

.dashboard-header h1 {
  margin: 0 0 15px 0;
  font-size: 2.5em;
}

.header-info {
  display: flex;
  gap: 30px;
  align-items: center;
  flex-wrap: wrap;
}

.header-info > span {
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9em;
}

.weather.weather-sunny { color: #f39c12; }
.weather.weather-cloudy { color: #95a5a6; }
.weather.weather-rainy { color: #3498db; }

/* 系统状态样式 */
.system-status {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
}

.status-indicator.status-healthy {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.status-indicator.status-warning {
  background: #fff7e6;
  color: #fa8c16;
  border: 1px solid #ffd591;
}

.status-indicator.status-error {
  background: #ffe6e6;
  color: #ff4757;
  border: 1px solid #ffb3b3;
}

.status-icon {
  font-size: 1.2em;
  font-weight: bold;
}

.detailed-status {
  margin-top: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 0.9em;
}

.detailed-status p {
  margin: 5px 0;
}

/* 监测网格样式 */
.monitoring-grid {
  background: white;
  border-radius: 8px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.station-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 20px;
  background: #fafafa;
  transition: all 0.3s;
  cursor: pointer;
}

.station-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.station-card.card-online {
  border-left: 4px solid #52c41a;
}

.station-card.card-warning {
  border-left: 4px solid #fa8c16;
}

.station-card.card-offline {
  border-left: 4px solid #ff4757;
  opacity: 0.7;
}

.station-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.station-header h3 {
  margin: 0;
  color: #2c3e50;
}

.station-id {
  font-family: monospace;
  font-size: 0.9em;
  font-weight: bold;
}

.station-data {
  margin-bottom: 15px;
}

.data-item {
  display: flex;
  justify-content: space-between;
  margin: 8px 0;
  align-items: center;
}

.data-label {
  color: #7f8c8d;
  font-weight: 500;
}

.data-value {
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 4px;
}

.data-value.value-normal {
  color: #27ae60;
  background: #e8f5e8;
}

.data-value.value-warning {
  color: #e67e22;
  background: #fdf2e9;
}

.station-alerts {
  margin: 15px 0;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  margin: 5px 0;
  border-radius: 4px;
  font-size: 0.9em;
}

.alert-info { background: #e6f7ff; color: #1890ff; }
.alert-warning { background: #fff7e6; color: #fa8c16; }
.alert-error { background: #ffe6e6; color: #ff4757; }

.station-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85em;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 0.8em;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn-warning {
  background: #fa8c16;
  color: white;
}

.btn-info {
  background: #17a2b8;
  color: white;
}

.btn:hover:not(:disabled) {
  opacity: 0.8;
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.empty-icon {
  font-size: 4em;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 20px 0 10px 0;
  color: #2c3e50;
}

.empty-state p {
  margin: 10px 0;
  font-size: 0.9em;
}

/* 筛选控制栏样式 */
.filter-controls {
  background: white;
  border-radius: 8px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.filter-group {
  margin-bottom: 20px;
}

.filter-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #2c3e50;
}

.search-input, .status-filter {
  width: 100%;
  max-width: 300px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.region-checkboxes, .data-type-radios {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.checkbox-label, .radio-label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  font-weight: normal;
}

/* 数据表格样式 */
.data-table-section {
  background: white;
  border-radius: 8px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e8e8e8;
}

.data-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.data-table th.sortable:hover {
  background: #e9ecef;
}

.sort-indicator {
  margin-left: 5px;
  font-size: 0.8em;
}

.station-row {
  transition: background-color 0.2s;
}

.station-row:hover {
  background: #f8f9fa;
}

.station-row.selected {
  background: #e6f7ff;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  font-weight: bold;
  text-transform: uppercase;
}

.status-online {
  background: #f6ffed;
  color: #52c41a;
}

.status-warning {
  background: #fff7e6;
  color: #fa8c16;
}

.status-offline {
  background: #ffe6e6;
  color: #ff4757;
}

.table-actions {
  display: flex;
  gap: 5px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.2s;
}

.btn-icon:hover {
  background: #f0f0f0;
}

.expanded-row td {
  background: #f8f9fa;
  border-top: none;
}

.expanded-content {
  padding: 20px;
}

.measurement-details h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.measurement-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.measurement-item {
  background: white;
  padding: 15px;
  border-radius: 6px;
  border-left: 3px solid #1890ff;
}

.measurement-name {
  display: block;
  font-size: 0.9em;
  color: #7f8c8d;
  margin-bottom: 5px;
}

.measurement-value {
  display: block;
  font-size: 1.2em;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.measurement-trend {
  font-size: 0.8em;
}

.trend-up { color: #52c41a; }
.trend-down { color: #ff4757; }
.trend-stable { color: #7f8c8d; }

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 5px;
  margin-top: 20px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #f0f0f0;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-number {
  padding: 8px 12px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.page-number:hover {
  background: #f0f0f0;
}

.page-number.active {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}

/* 图表样式 */
.charts-section {
  background: white;
  border-radius: 8px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.chart-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
  margin-top: 20px;
}

.chart-item {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 20px;
  background: #fafafa;
}

.chart-item h4 {
  margin: 0 0 20px 0;
  color: #2c3e50;
}

.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  height: 150px;
  margin-bottom: 15px;
  padding: 10px;
  background: white;
  border-radius: 4px;
}

.chart-bar {
  flex: 1;
  min-height: 10px;
  border-radius: 2px;
  transition: all 0.3s;
  cursor: pointer;
}

.chart-bar:hover {
  opacity: 0.8;
}

.chart-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.current-value {
  font-weight: bold;
  color: #2c3e50;
}

.trend-indicator {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  font-weight: bold;
}

.trend-indicator.rising {
  background: #f6ffed;
  color: #52c41a;
}

.trend-indicator.falling {
  background: #ffe6e6;
  color: #ff4757;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-info {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .grid-container {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    grid-template-columns: 1fr;
  }
  
  .region-checkboxes, .data-type-radios {
    flex-direction: column;
  }
}
</style>
```

这个完整的水利监测仪表盘示例展示了Vue.js模板语法的所有核心特性：

**1. 插值表达式**：
- `{{ dashboardTitle }}` - 简单文本插值
- `{{ formatDateTime(currentTime) }}` - 方法调用插值

**2. 属性绑定**：
- `:class="systemStatusClass"` - 动态class绑定
- `:style="getChartStyle(chartData)"` - 动态样式绑定
- `:disabled="station.status === 'offline'"` - 条件属性绑定

**3. 条件渲染**：
- `v-if/v-else-if/v-else` - 条件分支渲染
- `v-show` - 条件显示（保持DOM结构）

**4. 列表渲染**：
- `v-for="station in filteredStations"` - 数组循环
- `v-for="(value, key) in station.measurements"` - 对象循环
- 嵌套循环和复杂数据结构处理

**5. 事件处理**：
- `@click="selectStation(station)"` - 点击事件
- `@click.stop` - 事件修饰符
- `@submit.prevent` - 表单提交防止默认行为

**6. 双向数据绑定**：
- `v-model="searchKeyword"` - 文本输入绑定
- `v-model="selectedRegions"` - 多选框绑定
- `v-model.number` - 数值类型修饰符

这些模板语法特性为水利监测系统提供了强大的数据展示和用户交互能力，能够优雅地处理复杂的业务逻辑和界面需求。

## 4.5.4 组件化开发与单页面应用

### Vue组件系统概述

**组件化开发**是现代前端框架的核心理念，它将复杂的用户界面拆分为独立、可复用的组件。在智慧水利系统中，组件化开发能够显著提升开发效率、代码维护性和团队协作效率。通过组件系统，我们可以构建如监测站卡片、数据图表、预警面板等可复用的界面模块。

**Vue组件的核心特性：**

1. **独立性**：每个组件拥有独立的作用域和生命周期
2. **可复用性**：同一组件可在多处使用，降低代码重复
3. **可组合性**：小组件组合成大组件，构建复杂应用
4. **可维护性**：单一职责原则，便于测试和维护

## 4.5.5 路由管理与状态管理

### Vue Router路由系统

Vue Router是Vue.js的官方路由管理器，负责管理单页面应用的页面切换。在智慧水利平台中，不同功能模块（监测站管理、数据分析、预警系统）都需要独立的页面，路由系统可以优雅地组织这些页面。

#### 路由配置基础

路由配置定义了URL路径与页面组件的对应关系：

```javascript
// router/index.js - 路由配置核心结构
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // 基础路由配置
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }  // 元信息：无需登录
  },
  {
    path: '/',
    component: Layout,  // 布局组件
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '仪表盘', requiresAuth: true }
      },
      {
        path: '/stations',
        name: 'StationManagement',
        component: StationManagement,
        meta: { title: '监测站管理', requiresAuth: true }
      },
      // 动态路由 - 路径参数
      {
        path: '/stations/:stationId',
        name: 'StationDetail',
        component: StationDetail,
        meta: { title: '监测站详情', requiresAuth: true }
      }
    ]
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(), // HTML5 History模式
  routes
})
```

**关键概念说明：**
- **嵌套路由**：`children`配置子路由，适合有公共布局的页面
- **动态路由**：`:stationId`是路径参数，可匹配`/stations/WS001`等
- **路由元信息**：`meta`存储自定义数据，如权限要求、页面标题

#### 路由守卫与权限控制

路由守卫用于控制页面访问权限，确保用户只能访问有权限的页面：

```javascript
// 全局前置守卫 - 在每次路由跳转前执行
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || '智慧水利平台'
  
  // 权限检查
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next('/login')  // 未登录跳转到登录页
  } else {
    next()  // 允许访问
  }
})
```

#### 组件中使用路由

在组件中可以通过编程式导航跳转页面：

```vue
<!-- StationManagement.vue 组件中的路由使用 -->
<template>
  <div class="station-management">
    <!-- 声明式路由导航 -->
    <router-link to="/dashboard">返回首页</router-link>
    
    <!-- 带参数的路由链接 -->
    <router-link 
      :to="{ name: 'StationDetail', params: { stationId: station.id } }"
    >
      查看详情
    </router-link>
    
    <!-- 点击事件触发编程式导航 -->
    <button @click="navigateToAnalysis">数据分析</button>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()  // 路由实例
const route = useRoute()    // 当前路由信息

// 编程式导航方法
const navigateToAnalysis = () => {
  router.push({
    name: 'DataAnalysis',
    query: { stationIds: selectedStations.value }  // 查询参数
  })
}

// 获取路由参数
const stationId = route.params.stationId
const fromPage = route.query.from
</script>
```

**编程式导航的几种方式：**
- `router.push()`：跳转到新页面，会在历史记录中添加记录
- `router.replace()`：替换当前页面，不会在历史记录中留下记录  
- `router.go(n)`：在历史记录中前进或后退n步

### Pinia状态管理

Pinia是Vue 3推荐的状态管理库，用于管理应用的全局状态。在智慧水利平台中，用户信息、监测站数据、系统配置等都适合用状态管理来处理。

#### 为什么需要状态管理？

在复杂应用中，多个组件可能需要共享同一份数据。如果只用组件通信，会造成：
- 兄弟组件间通信困难
- 数据传递链路过长
- 状态难以追踪和调试

状态管理提供了一个集中式的数据存储，所有组件都可以访问和修改。

#### 创建Store

以用户信息管理为例：

```javascript
// stores/user.js - 用户状态管理
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // ===== 状态数据 =====
  const userInfo = ref(null)
  const token = ref(localStorage.getItem('token') || '')
  const permissions = ref([])
  
  // ===== 计算属性 =====
  const isAuthenticated = computed(() => {
    return !!token.value && !!userInfo.value
  })
  
  const userName = computed(() => {
    return userInfo.value?.name || '未知用户'
  })
  
  // ===== 操作方法 =====
  const login = async (credentials) => {
    try {
      const response = await authAPI.login(credentials)
      if (response.success) {
        token.value = response.data.token
        userInfo.value = response.data.user
        permissions.value = response.data.permissions
        
        // 保存到本地存储
        localStorage.setItem('token', token.value)
        return { success: true }
      }
    } catch (error) {
      return { success: false, message: '登录失败' }
    }
  }
  
  const logout = () => {
    token.value = ''
    userInfo.value = null
    permissions.value = []
    localStorage.removeItem('token')
  }
  
  const hasPermission = (permission) => {
    return permissions.value.includes(permission)
  }
  
  // 返回公开的状态和方法
  return {
    userInfo, token, permissions,
    isAuthenticated, userName,
    login, logout, hasPermission
  }
})
```

**Store的三个核心部分：**
1. **状态（State）**：存储数据，使用`ref()`或`reactive()`
2. **计算属性（Getters）**：基于状态的派生数据，使用`computed()`
3. **动作（Actions）**：修改状态的方法，可以是异步的

#### 在组件中使用Store

```vue
<template>
  <div class="user-panel">
    <div v-if="userStore.isAuthenticated">
      欢迎，{{ userStore.userName }}！
      <button @click="handleLogout">退出登录</button>
    </div>
    <div v-else>
      <button @click="showLogin = true">登录</button>
    </div>
  </div>
</template>

<script setup>
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>
```

通过状态管理，用户信息可以在整个应用中共享，任何组件都能访问登录状态、用户权限等信息。

#### 监测站数据管理Store

针对水利监测站的复杂数据管理需求：

```javascript
// stores/station.js - 监测站状态管理
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { stationAPI } from '@/api/station'

export const useStationStore = defineStore('station', () => {
  // ===== 状态数据 =====
  const stations = ref([])
  const selectedStation = ref(null)
  const loading = ref(false)
  
  // ===== 计算属性 =====
  const onlineStations = computed(() => {
    return stations.value.filter(station => station.status === 'online')
  })
  
  const statusStatistics = computed(() => ({
    total: stations.value.length,
    online: stations.value.filter(s => s.status === 'online').length,
    offline: stations.value.filter(s => s.status === 'offline').length,
    warning: stations.value.filter(s => s.status === 'warning').length
  }))
  
  // ===== 操作方法 =====
  const loadStations = async () => {
    loading.value = true
    try {
      const response = await stationAPI.getStations()
      if (response.success) {
        stations.value = response.data.stations
      }
    } catch (error) {
      console.error('加载监测站失败:', error)
    } finally {
      loading.value = false
    }
  }
  
  const updateStationData = (stationId, newData) => {
    const index = stations.value.findIndex(s => s.id === stationId)
    if (index > -1) {
      stations.value[index] = { ...stations.value[index], ...newData }
    }
  }
  
  const selectStation = (stationId) => {
    selectedStation.value = stations.value.find(s => s.id === stationId)
  }
  
  return {
    // 状态
    stations, selectedStation, loading,
    // 计算属性
    onlineStations, statusStatistics,
    // 方法
    loadStations, updateStationData, selectStation
  }
})
```

**在组件中使用监测站Store：**

```vue
<template>
  <div class="dashboard">
    <div class="statistics">
      <div class="stat-item">
        <h3>总监测站</h3>
        <div class="value">{{ stationStore.statusStatistics.total }}</div>
      </div>
      <div class="stat-item">
        <h3>在线监测站</h3>
        <div class="value">{{ stationStore.statusStatistics.online }}</div>
      </div>
    </div>
    
    <div class="station-list">
      <div 
        v-for="station in stationStore.stations" 
        :key="station.id"
        @click="stationStore.selectStation(station.id)"
      >
        {{ station.name }} - {{ station.status }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useStationStore } from '@/stores/station'

const stationStore = useStationStore()

onMounted(() => {
  stationStore.loadStations()
})
</script>
```

### Vue.js开发最佳实践

在智慧水利平台开发过程中，遵循最佳实践能够确保代码质量、提升开发效率并保障系统的长期可维护性。

#### 组件设计原则

**1. 单一职责原则**

每个组件应该只负责一个明确的功能。例如，水位监控组件只处理水位数据显示，不应该包含用户权限验证或网络请求逻辑。

```vue
<!-- 好的做法：专注于水位显示 -->
<template>
  <div class="water-level-display">
    <div class="current-level">{{ level }} 米</div>
    <div class="status" :class="statusClass">{{ statusText }}</div>
  </div>
</template>

<script setup>
// 只处理水位显示逻辑
const props = defineProps({
  level: { type: Number, required: true },
  threshold: { type: Number, default: 5.0 }
})

const statusClass = computed(() => 
  props.level > props.threshold ? 'warning' : 'normal'
)
</script>
```

**2. 合理的组件粒度**

组件粒度要适中，既不能过度拆分导致组件碎片化，也不能过于庞大难以维护：

- **基础组件**：按钮、输入框、图标等通用元素
- **业务组件**：监测站卡片、数据图表等业务单元  
- **页面组件**：完整的功能页面，组合多个业务组件

**3. 清晰的组件接口**

使用TypeScript或详细的PropTypes定义组件接口：

```javascript
// 清晰定义组件属性
const props = defineProps({
  stationData: {
    type: Object,
    required: true,
    validator: (value) => value.id && value.name
  },
  editable: {
    type: Boolean,
    default: false
  }
})

// 明确定义事件
const emit = defineEmits(['update', 'delete', 'select'])
```

#### 状态管理策略

**数据流向原则**：遵循单向数据流，避免多个数据源造成状态混乱。

- **组件内部状态**：使用`ref()`或`reactive()`管理组件私有数据
- **跨组件状态**：使用Pinia Store管理共享数据
- **临时状态**：优先考虑Props/Events进行组件间通信

```javascript
// 状态层次规划示例
const componentState = ref({})      // 组件级：表单输入、UI状态
const businessStore = useStationStore() // 应用级：业务数据、用户信息
const globalStore = useAppStore()   // 全局级：主题、语言设置
```

#### 性能优化策略

**1. 计算属性优化**

将复杂计算逻辑从模板移到计算属性中：

```javascript
// 优化前：模板中直接计算
// <div>{{ stations.filter(s => s.status === 'online').length }}</div>

// 优化后：使用计算属性
const onlineStationsCount = computed(() => 
  stations.value.filter(s => s.status === 'online').length
)
```

**2. 列表渲染优化**

为`v-for`提供稳定的key值，避免不必要的重新渲染：

```vue
<!-- 使用稳定的ID作为key -->
<station-card 
  v-for="station in stations" 
  :key="station.id"  
  :station="station"
/>
```

**3. 组件懒加载**

对于大型页面组件，使用懒加载减少初始包大小：

```javascript
const routes = [
  {
    path: '/analysis',
    name: 'DataAnalysis',
    // 路由级别的懒加载
    component: () => import('@/views/DataAnalysis.vue')
  }
]
```

### 章节总结

通过本节的学习，我们全面掌握了Vue.js在智慧水利平台开发中的核心技术：

**1. 技术理论基础**
- 理解了前端框架的演进历程和Vue.js的选择优势
- 掌握了MVVM架构模式和响应式数据绑定原理
- 学习了虚拟DOM的工作机制和性能优化价值

**2. 开发实践技能**
- 熟练掌握Vue实例创建、模板语法和数据绑定
- 深入理解组件化开发思想和最佳实践
- 掌握Vue Router路由管理和Pinia状态管理

**3. 水利行业应用**
- 通过监测站管理、数据可视化等实际场景学习Vue.js应用
- 理解了如何将技术框架与业务需求相结合
- 掌握了复杂业务逻辑的前端实现方法

**4. 项目开发准备**
- 建立了完整的Vue.js开发知识体系
- 形成了规范的代码组织和项目结构理念
- 具备了开发现代化水利监测平台前端的技术基础

这些知识为后续章节的深入学习和实际项目开发奠定了坚实基础。在下一章中，我们将学习如何将这些前端技术与后端服务进行整合，构建完整的智慧水利系统架构。

!!! tip "学习建议"
    
    Vue.js作为现代前端开发的核心技术，建议：
    
    1. **多练习**：通过实际编写代码来加深理解
    2. **重视基础**：响应式系统和组件化思想是关键
    3. **关注实践**：结合水利行业实际需求进行学习
    4. **持续学习**：关注Vue.js生态系统的最新发展
````
        station.id.toLowerCase().includes(keyword) ||
        station.location?.toLowerCase().includes(keyword)
      )
    }
    
    return filtered
  }
  
  // 订阅实时数据
  const subscribeRealTimeData = (stationId, callback) => {
    if (subscriptions.value.has(stationId)) {
      // 已有订阅，添加回调
      subscriptions.value.get(stationId).callbacks.push(callback)
    } else {
      // 新建订阅
      const websocket = new WebSocket(`${import.meta.env.VITE_WS_URL}/stations/${stationId}/realtime`)
      
      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        
        // 更新本地数据
        const index = stations.value.findIndex(s => s.id === stationId)
        if (index > -1) {
          stations.value[index].measurements = data.measurements
          stations.value[index].lastUpdate = data.timestamp
        }
        
        // 执行回调函数
        const subscription = subscriptions.value.get(stationId)
        if (subscription) {
          subscription.callbacks.forEach(cb => cb(data))
        }
      }
      
      websocket.onerror = (error) => {
        console.error(`WebSocket错误 (${stationId}):`, error)
      }
      
      websocket.onclose = () => {
        console.log(`WebSocket连接关闭 (${stationId})`)
        subscriptions.value.delete(stationId)
      }
      
      subscriptions.value.set(stationId, {
        websocket,
        callbacks: [callback]
      })
    }
  }
  
  // 取消实时数据订阅
  const unsubscribeRealTimeData = (stationId, callback = null) => {
    const subscription = subscriptions.value.get(stationId)
    if (!subscription) return
    
    if (callback) {
      // 移除特定回调
      const index = subscription.callbacks.indexOf(callback)
      if (index > -1) {
        subscription.callbacks.splice(index, 1)
      }
      
      // 如果没有回调了，关闭连接
      if (subscription.callbacks.length === 0) {
        subscription.websocket.close()
        subscriptions.value.delete(stationId)
      }
    } else {
      // 关闭整个连接
      subscription.websocket.close()
      subscriptions.value.delete(stationId)
    }
  }
  
  // 更新筛选条件
  const updateFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
  }
  
  // 重置状态
  const resetState = () => {
    stations.value = []
    selectedStation.value = null
    loading.value = false
    error.value = null
    pagination.value = { current: 1, pageSize: 12, total: 0 }
    filters.value = { status: [], region: '', stationType: '', keyword: '' }
    
    // 关闭所有WebSocket连接
    subscriptions.value.forEach((subscription) => {
      subscription.websocket.close()
    })
    subscriptions.value.clear()
  }
  
  // 返回store接口
  return {
    // 状态
    stations: readonly(stations),
    selectedStation: readonly(selectedStation),
    loading: readonly(loading),
    error: readonly(error),
    pagination: readonly(pagination),
    filters,
    lastUpdateTime: readonly(lastUpdateTime),
    
    // 计算属性
    totalCount,
    onlineStations,
    offlineStations,
    warningStations,
    errorStations,
    statusStatistics,
    regions,
    stationTypes,
    
    // 方法
    loadStations,
    getStationById,
    createStation,
    updateStation,
    deleteStation,
    refreshStationData,
    getFilteredStations,
    subscribeRealTimeData,
    unsubscribeRealTimeData,
    updateFilters,
    resetState
  }
})
```

通过以上完整的Vue.js基础框架开发教程，我们深入学习了Vue.js在智慧水利平台开发中的应用。从框架演进历程到核心概念，从基础语法到组件化开发，再到路由管理和状态管理，形成了完整的Vue.js开发知识体系。

这些内容为后续章节的深入学习和实际项目开发奠定了坚实的基础，帮助开发者掌握现代化前端开发的核心技术和最佳实践。
