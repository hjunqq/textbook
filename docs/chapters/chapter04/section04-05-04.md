# 版本控制与协作工具

版本控制与协作工具是智慧水利平台前端开发团队协作的基础，能够确保代码安全、开发流程规范以及团队沟通顺畅。本文详细介绍智慧水利平台开发中使用的版本控制与协作工具。

## 1. Git工作流

Git是分布式版本控制系统，是智慧水利平台代码管理的核心工具。

### 1.1 Git基础配置

智慧水利平台开发的Git环境配置：

```bash
# 设置用户信息
git config --global user.name "开发者姓名"
git config --global user.email "developer@example.com"

# 设置默认编辑器
git config --global core.editor "code --wait"

# 设置默认分支名
git config --global init.defaultBranch main

# 配置换行符处理（Windows环境）
git config --global core.autocrlf true

# 配置中文文件名显示
git config --global core.quotepath false

# 配置凭证存储
git config --global credential.helper store

# 配置别名
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.ci commit
git config --global alias.br branch
git config --global alias.lg "log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
```

### 1.2 Git分支管理策略

智慧水利平台采用GitFlow作为分支管理策略：

#### 主要分支

- **main/master**：主分支，保存正式发布的历史
- **develop**：开发分支，保存开发中的最新功能

#### 辅助分支

- **feature/***：功能分支，用于开发新功能
- **release/***：发布分支，用于准备发布版本
- **hotfix/***：热修复分支，用于修复生产环境问题
- **bugfix/***：缺陷修复分支，用于修复开发环境问题

#### 分支命名规范

```
# 功能分支
feature/[模块名]-[功能描述]
# 示例：feature/water-monitoring-realtime-display

# 缺陷修复分支
bugfix/[模块名]-[问题描述]
# 示例：bugfix/water-level-calculation-error

# 热修复分支
hotfix/[版本号]-[问题描述]
# 示例：hotfix/v1.2.3-login-failure

# 发布分支
release/v[主版本号].[次版本号].[修订号]
# 示例：release/v1.2.0
```

### 1.3 Git工作流程

智慧水利平台标准开发流程：

#### 1. 克隆仓库

```bash
# 克隆主仓库
git clone https://github.com/org-name/smart-water-platform.git
cd smart-water-platform

# 设置上游仓库（如使用Fork工作流）
git remote add upstream https://github.com/main-org/smart-water-platform.git
```

#### 2. 创建功能分支

```bash
# 确保develop分支是最新的
git checkout develop
git pull origin develop

# 创建功能分支
git checkout -b feature/water-monitoring-dashboard
```

#### 3. 开发与提交

```bash
# 开发完成后，查看变更
git status
git diff

# 添加文件到暂存区
git add .

# 提交变更
git commit -m "feat: 添加水位实时监控仪表盘"
```

#### 4. 保持分支同步

```bash
# 同步上游变更
git checkout develop
git pull origin develop

# 将最新develop分支合并到功能分支
git checkout feature/water-monitoring-dashboard
git rebase develop
```

#### 5. 推送分支与创建PR

```bash
# 推送到远程仓库
git push origin feature/water-monitoring-dashboard

# 在GitHub/GitLab上创建Pull Request
# develop <- feature/water-monitoring-dashboard
```

#### 6. 代码审查与合并

```bash
# 根据审查意见修改代码
git add .
git commit -m "fix: 解决代码审查中的问题"
git push origin feature/water-monitoring-dashboard

# 代码审查通过后，合并到develop分支
# 在GitHub/GitLab上完成合并
```

#### 7. 版本发布

```bash
# 创建发布分支
git checkout develop
git checkout -b release/v1.2.0

# 最终测试与修复
git add .
git commit -m "fix: 修复发布前发现的问题"

# 合并到主分支
git checkout main
git merge --no-ff release/v1.2.0
git tag -a v1.2.0 -m "智慧水利平台 v1.2.0"
git push origin main --tags

# 合并回develop分支
git checkout develop
git merge --no-ff release/v1.2.0
git push origin develop

# 删除发布分支
git branch -d release/v1.2.0
```

### 1.4 提交信息规范

智慧水利平台采用Angular提交规范：

```
<类型>(<作用域>): <主题>

<正文>

<页脚>
```

#### 类型

- **feat**: 新功能
- **fix**: 修复Bug
- **docs**: 文档变更
- **style**: 代码格式变更（不影响代码运行）
- **refactor**: 代码重构
- **perf**: 性能优化
- **test**: 添加或修改测试代码
- **build**: 构建系统或外部依赖变更
- **ci**: CI配置变更
- **chore**: 其他变更（不修改src或测试文件）

#### 示例

```
feat(water-monitoring): 添加实时水位监控仪表盘

添加了实时显示水库水位的仪表盘组件，包括以下功能：
- 实时水位数值与历史对比
- 水位变化趋势图表
- 警戒水位提示

解决了 #123 需求
```

### 1.5 Git钩子

使用Git钩子确保代码质量和规范：

#### 安装Husky

```bash
# 安装husky和lint-staged
npm install --save-dev husky lint-staged @commitlint/cli @commitlint/config-conventional
```

#### 配置提交前检查

```json
// package.json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged",
      "commit-msg": "commitlint -E HUSKY_GIT_PARAMS"
    }
  },
  "lint-staged": {
    "src/**/*.{js,vue}": [
      "eslint --fix",
      "prettier --write",
      "git add"
    ]
  }
}
```

#### 提交信息检查

```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'body-max-line-length': [2, 'always', 100],
    'subject-case': [0],
    'scope-enum': [2, 'always', [
      'water-monitoring',
      'reservoir-management',
      'rainfall-analysis',
      'auth',
      'dashboard',
      'common',
      'deps'
    ]]
  }
};
```

### 1.6 智慧水利平台Git最佳实践

1. **频繁提交**：小步提交，保持每次提交功能聚焦
2. **提交前测试**：确保通过本地测试再提交
3. **保持分支同步**：定期将主分支合并到功能分支
4. **合理使用标签**：为重要版本创建标签
5. **不提交敏感信息**：使用.gitignore排除敏感文件
6. **使用.gitattributes**：统一文件格式和处理方式

```
# .gitattributes
*.js text eol=lf
*.vue text eol=lf
*.json text eol=lf
*.html text eol=lf
*.css text eol=lf
*.less text eol=lf
*.scss text eol=lf
*.md text eol=lf
*.svg text eol=lf
*.png binary
*.jpg binary
*.gif binary
*.woff binary
*.woff2 binary
```

## 2. CI/CD工具

持续集成与持续部署工具是智慧水利平台自动化构建、测试和部署的核心。

### 2.1 GitHub Actions

GitHub Actions是基于GitHub的CI/CD服务。

#### 智慧水利平台CI/CD工作流配置

```yaml
# .github/workflows/ci.yml
name: 智慧水利平台CI/CD

on:
  push:
    branches: [ main, develop, release/** ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    
    steps:
    - name: 检出代码
      uses: actions/checkout@v2
    
    - name: 设置Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'
        cache: 'npm'
    
    - name: 安装依赖
      run: npm ci
    
    - name: 运行代码检查
      run: npm run lint
    
    - name: 运行单元测试
      run: npm run test:unit
    
    - name: 构建应用
      run: npm run build
    
    - name: 上传构建产物
      uses: actions/upload-artifact@v2
      with:
        name: dist
        path: dist/
  
  deploy-dev:
    needs: build-and-test
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    
    steps:
    - name: 下载构建产物
      uses: actions/download-artifact@v2
      with:
        name: dist
        path: dist
    
    - name: 部署到开发环境
      uses: easingthemes/ssh-deploy@v2.2.11
      env:
        SSH_PRIVATE_KEY: ${{ secrets.DEV_SSH_PRIVATE_KEY }}
        ARGS: "-rltgoDzvO --delete"
        SOURCE: "dist/"
        REMOTE_HOST: ${{ secrets.DEV_HOST }}
        REMOTE_USER: ${{ secrets.DEV_USER }}
        TARGET: ${{ secrets.DEV_TARGET_DIR }}
  
  deploy-prod:
    needs: build-and-test
    if: startsWith(github.ref, 'refs/heads/release/') || github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - name: 下载构建产物
      uses: actions/download-artifact@v2
      with:
        name: dist
        path: dist
    
    - name: 部署到生产环境
      uses: easingthemes/ssh-deploy@v2.2.11
      env:
        SSH_PRIVATE_KEY: ${{ secrets.PROD_SSH_PRIVATE_KEY }}
        ARGS: "-rltgoDzvO --delete"
        SOURCE: "dist/"
        REMOTE_HOST: ${{ secrets.PROD_HOST }}
        REMOTE_USER: ${{ secrets.PROD_USER }}
        TARGET: ${{ secrets.PROD_TARGET_DIR }}
```

### 2.2 GitLab CI/CD

对于使用GitLab的团队，可配置GitLab CI/CD。

#### 智慧水利平台GitLab CI/CD配置

```yaml
# .gitlab-ci.yml
image: node:16-alpine

stages:
  - install
  - lint
  - test
  - build
  - deploy

variables:
  NPM_CONFIG_CACHE: "$CI_PROJECT_DIR/.npm"

cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .npm/
    - node_modules/

install:
  stage: install
  script:
    - npm ci

lint:
  stage: lint
  needs: ["install"]
  script:
    - npm run lint

test:
  stage: test
  needs: ["install"]
  script:
    - npm run test:unit
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'
  artifacts:
    paths:
      - coverage/
    expire_in: 1 week

build:
  stage: build
  needs: ["lint", "test"]
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

deploy-dev:
  stage: deploy
  needs: ["build"]
  dependencies:
    - build
  script:
    - apk add --no-cache rsync openssh
    - mkdir -p ~/.ssh
    - echo "$DEV_SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
    - chmod 600 ~/.ssh/id_rsa
    - echo -e "Host *\n\tStrictHostKeyChecking no\n\n" > ~/.ssh/config
    - rsync -avz --delete ./dist/ $DEV_USER@$DEV_HOST:$DEV_TARGET_DIR
  environment:
    name: development
    url: https://dev.water-platform.example.com
  only:
    - develop

deploy-prod:
  stage: deploy
  needs: ["build"]
  dependencies:
    - build
  script:
    - apk add --no-cache rsync openssh
    - mkdir -p ~/.ssh
    - echo "$PROD_SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
    - chmod 600 ~/.ssh/id_rsa
    - echo -e "Host *\n\tStrictHostKeyChecking no\n\n" > ~/.ssh/config
    - rsync -avz --delete ./dist/ $PROD_USER@$PROD_HOST:$PROD_TARGET_DIR
  environment:
    name: production
    url: https://water-platform.example.com
  when: manual
  only:
    - main
    - /^release\/.*$/
```

### 2.3 Jenkins

Jenkins是自托管的CI/CD服务器，适合私有部署环境。

#### 智慧水利平台Jenkins Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'node:16-alpine'
            args '-v /root/.npm:/root/.npm'
        }
    }
    
    environment {
        HOME = '.'
    }
    
    stages {
        stage('Install') {
            steps {
                sh 'npm ci'
            }
        }
        
        stage('Lint') {
            steps {
                sh 'npm run lint'
            }
        }
        
        stage('Test') {
            steps {
                sh 'npm run test:unit'
            }
        }
        
        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }
        
        stage('Deploy to Development') {
            when {
                branch 'develop'
            }
            steps {
                sshagent(['dev-ssh-key']) {
                    sh '''
                        rsync -avz --delete ./dist/ user@dev-server:/var/www/water-platform-dev/
                    '''
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                anyOf {
                    branch 'main'
                    branch pattern: "release/*", comparator: "REGEXP"
                }
            }
            steps {
                timeout(time: 1, unit: 'DAYS') {
                    input message: '确认部署到生产环境?', ok: '是的，部署!'
                }
                sshagent(['prod-ssh-key']) {
                    sh '''
                        rsync -avz --delete ./dist/ user@prod-server:/var/www/water-platform/
                    '''
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            slackSend channel: '#deployment', 
                      color: 'good', 
                      message: "构建成功: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        }
        failure {
            slackSend channel: '#deployment', 
                      color: 'danger', 
                      message: "构建失败: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        }
    }
}
```

### 2.4 Docker与容器化部署

使用Docker容器化部署智慧水利平台前端应用。

#### Dockerfile

```dockerfile
# 构建阶段
FROM node:16-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Nginx配置

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://backend-service:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # 缓存静态资源
    location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
    
    # 不缓存HTML
    location ~* \.html$ {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
}
```

#### Docker Compose配置

```yaml
# docker-compose.yml
version: '3'

services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - water-platform-network
  
  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DB_HOST=db
      - DB_USER=wateruser
      - DB_PASSWORD=securepassword
      - DB_NAME=waterdb
    depends_on:
      - db
    networks:
      - water-platform-network
  
  db:
    image: postgres:13
    volumes:
      - water-db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=wateruser
      - POSTGRES_PASSWORD=securepassword
      - POSTGRES_DB=waterdb
    networks:
      - water-platform-network

networks:
  water-platform-network:

volumes:
  water-db-data:
```

### 2.5 智慧水利平台CI/CD最佳实践

1. **环境分离**：开发、测试、生产环境明确分离
2. **自动测试**：提交代码后自动运行测试
3. **质量门禁**：设置质量标准，测试覆盖率低于标准不允许部署
4. **回滚机制**：提供快速回滚能力
5. **监控集成**：部署后自动检查应用健康状态
6. **通知机制**：构建和部署状态通知到团队

## 3. 团队协作工具

高效的团队协作需要借助专业工具，形成标准工作流程。

### 3.1 JIRA

JIRA是敏捷开发项目管理工具，用于需求管理、任务分配和缺陷跟踪。

#### 智慧水利平台JIRA工作流

1. **需求管理**
   - 创建史诗(Epic)：大型功能或模块
   - 创建故事(Story)：用户视角的需求
   - 创建任务(Task)：具体开发任务
   - 创建缺陷(Bug)：问题报告

2. **看板设置**
   ```
   待办 -> 开发中 -> 代码审查 -> 测试中 -> 验收 -> 已完成
   ```

3. **版本规划**
   - 设置版本里程碑
   - 规划每个迭代周期的工作量
   - 生成燃尽图追踪进度

4. **与Git集成**
   - 提交时引用JIRA编号：`git commit -m "feat: 添加水位监控功能 #WATER-123"`
   - 通过分支名自动关联：`feature/WATER-123-water-level-monitoring`

### 3.2 Confluence

Confluence是团队知识库和文档协作平台。

#### 智慧水利平台Confluence空间结构

1. **项目总览**
   - 项目介绍
   - 团队成员
   - 联系信息
   - 项目时间线

2. **需求文档**
   - 业务需求说明
   - 用户故事地图
   - 功能规格说明
   - 原型设计链接

3. **技术文档**
   - 系统架构
   - API设计
   - 数据模型
   - 技术选型说明
   - 开发规范

4. **流程指南**
   - 开发流程
   - 测试流程
   - 发布流程
   - 环境说明

5. **会议记录**
   - 需求评审
   - 技术评审
   - 每日站会
   - 迭代回顾

6. **知识库**
   - 常见问题
   - 技术分享
   - 学习资源
   - 问题解决方案

### 3.3 Slack/钉钉

即时通讯工具用于团队日常沟通。

#### 智慧水利平台沟通渠道设置

1. **通用频道**
   - #general：全员通知
   - #random：休闲交流

2. **项目频道**
   - #water-platform：项目总体讨论
   - #water-platform-dev：开发技术讨论
   - #water-platform-design：设计讨论
   - #water-platform-bugs：问题反馈

3. **自动通知集成**
   - GitHub/GitLab提交和PR通知
   - JIRA任务变更通知
   - CI/CD构建状态通知
   - 监控和告警通知

### 3.4 Code Review工具

代码审查确保代码质量和知识共享。

#### GitHub Pull Request

1. **PR模板**

```markdown
## 变更说明
<!-- 描述此PR的目的和解决的问题 -->

## 功能点
<!-- 列出实现的功能点 -->
- 功能1
- 功能2

## 关联的JIRA任务
<!-- 关联到JIRA任务 -->
WATER-123

## 测试用例
<!-- 描述如何测试此变更 -->
- [ ] 测试场景1
- [ ] 测试场景2

## 屏幕截图
<!-- 如适用，附上屏幕截图 -->

## 自测检查表
- [ ] 已添加适当的单元测试
- [ ] 所有测试通过
- [ ] 代码符合团队规范
- [ ] 已更新相关文档
```

2. **Code Review流程**
   - 创建PR后通知相关人员审查
   - 至少获得一个团队成员的批准
   - 修复所有审查中发现的问题
   - 通过所有自动化测试
   - 合并到目标分支

3. **Code Review最佳实践**
   - 聚焦于代码质量而非风格（风格由工具自动处理）
   - 提供具体和建设性的反馈
   - 及时回应审查请求
   - 鼓励知识分享

### 3.5 设计协作工具

前端开发需要与设计师密切协作。

#### Figma/Sketch

1. **设计系统管理**
   - 统一组件库
   - 色彩系统
   - 字体与排版
   - 图标集

2. **标注与协作**
   - 详细的组件规格
   - 响应式设计规则
   - 状态变化说明
   - 交互原型

3. **开发集成**
   - 从设计到代码的工具
   - 设计标记导出
   - 资源自动提取

### 3.6 智慧水利平台团队协作最佳实践

1. **透明开放**：项目信息对团队透明可见
2. **文档先行**：先写文档再开发
3. **异步协作**：减少实时会议，增加文档和异步沟通
4. **定期同步**：每日站会和每周总结
5. **工作量可视化**：任务进度对所有人可见
6. **持续改进**：定期回顾和优化工作流程

## 总结

版本控制与协作工具是智慧水利平台前端工程化的重要组成部分。Git工作流确保代码版本管理规范化；CI/CD工具实现构建和部署自动化；团队协作工具保证沟通顺畅和信息透明。

在实际开发中，应根据团队规模和项目特性，选择合适的工具组合，并制定清晰的工作流程。通过工具和流程的持续优化，可以显著提高团队协作效率，保证智慧水利平台前端项目的高质量交付。 