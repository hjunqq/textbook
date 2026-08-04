/**
 * 前端API服务示例 - 前后端分离架构
 * 
 * 本示例展示了前端如何与后端API进行交互：
 * 1. RESTful API调用封装
 * 2. HTTP方法对应的操作
 * 3. 错误处理机制
 * 4. 请求响应拦截器
 */
class ApiService {
    
    /**
     * 构造函数 - 初始化基础URL和配置
     */
    constructor(baseURL) {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }
    
    /**
     * 设置认证令牌
     */
    setAuthToken(token) {
        this.defaultHeaders['Authorization'] = `Bearer ${token}`;
    }
    
    /**
     * GET请求 - 获取用户列表
     */
    async fetchUsers(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = `${this.baseURL}/api/users${queryString ? '?' + queryString : ''}`;
        
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: this.defaultHeaders
            });
            
            return await this.handleResponse(response);
        } catch (error) {
            throw this.handleError(error);
        }
    }
    
    /**
     * GET请求 - 获取单个用户
     */
    async fetchUserById(userId) {
        try {
            const response = await fetch(`${this.baseURL}/api/users/${userId}`, {
                method: 'GET',
                headers: this.defaultHeaders
            });
            
            return await this.handleResponse(response);
        } catch (error) {
            throw this.handleError(error);
        }
    }
    
    /**
     * POST请求 - 创建新用户
     */
    async createUser(userData) {
        try {
            const response = await fetch(`${this.baseURL}/api/users`, {
                method: 'POST',
                headers: this.defaultHeaders,
                body: JSON.stringify(userData)
            });
            
            return await this.handleResponse(response);
        } catch (error) {
            throw this.handleError(error);
        }
    }
    
    /**
     * PUT请求 - 更新用户信息
     */
    async updateUser(userId, userData) {
        try {
            const response = await fetch(`${this.baseURL}/api/users/${userId}`, {
                method: 'PUT',
                headers: this.defaultHeaders,
                body: JSON.stringify(userData)
            });
            
            return await this.handleResponse(response);
        } catch (error) {
            throw this.handleError(error);
        }
    }
    
    /**
     * DELETE请求 - 删除用户
     */
    async deleteUser(userId) {
        try {
            const response = await fetch(`${this.baseURL}/api/users/${userId}`, {
                method: 'DELETE',
                headers: this.defaultHeaders
            });
            
            return await this.handleResponse(response);
        } catch (error) {
            throw this.handleError(error);
        }
    }
    
    /**
     * 批量操作 - 批量删除用户
     */
    async batchDeleteUsers(userIds) {
        try {
            const response = await fetch(`${this.baseURL}/api/users/batch`, {
                method: 'DELETE',
                headers: this.defaultHeaders,
                body: JSON.stringify({ ids: userIds })
            });
            
            return await this.handleResponse(response);
        } catch (error) {
            throw this.handleError(error);
        }
    }
    
    /**
     * 文件上传 - 用户头像上传
     */
    async uploadUserAvatar(userId, file) {
        const formData = new FormData();
        formData.append('avatar', file);
        
        try {
            const response = await fetch(`${this.baseURL}/api/users/${userId}/avatar`, {
                method: 'POST',
                headers: {
                    'Authorization': this.defaultHeaders['Authorization']
                    // 注意：不要设置Content-Type，让浏览器自动设置
                },
                body: formData
            });
            
            return await this.handleResponse(response);
        } catch (error) {
            throw this.handleError(error);
        }
    }
    
    /**
     * 响应处理器
     */
    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: '请求失败' }));
            throw new Error(error.message || `HTTP ${response.status}`);
        }
        
        // 处理空响应（如DELETE操作）
        if (response.status === 204) {
            return null;
        }
        
        return await response.json();
    }
    
    /**
     * 错误处理器
     */
    handleError(error) {
        console.error('API请求错误:', error);
        
        // 网络错误
        if (!navigator.onLine) {
            return new Error('网络连接异常，请检查网络设置');
        }
        
        // 超时错误
        if (error.name === 'AbortError') {
            return new Error('请求超时，请重试');
        }
        
        return error;
    }
}

/**
 * 使用示例
 */

// 1. 创建API服务实例
const apiService = new ApiService('https://api.example.com');

// 2. 设置认证令牌（登录后）
const token = localStorage.getItem('auth_token');
if (token) {
    apiService.setAuthToken(token);
}

// 3. 使用API服务
async function demonstrateApiUsage() {
    try {
        // 获取用户列表
        const users = await apiService.fetchUsers({ page: 1, limit: 10 });
        console.log('用户列表:', users);
        
        // 创建新用户
        const newUser = await apiService.createUser({
            username: 'john_doe',
            email: 'john@example.com',
            phoneNumber: '13800138000'
        });
        console.log('新用户:', newUser);
        
        // 更新用户信息
        const updatedUser = await apiService.updateUser(newUser.id, {
            username: 'john_smith'
        });
        console.log('更新后用户:', updatedUser);
        
        // 删除用户
        await apiService.deleteUser(newUser.id);
        console.log('用户已删除');
        
    } catch (error) {
        console.error('操作失败:', error.message);
    }
}

/**
 * 高级功能：请求拦截器
 */
class AdvancedApiService extends ApiService {
    
    constructor(baseURL) {
        super(baseURL);
        this.requestQueue = [];
        this.isRefreshing = false;
    }
    
    /**
     * 请求拦截器 - 自动添加时间戳防止缓存
     */
    async fetch(url, options = {}) {
        // 添加时间戳参数
        const separator = url.includes('?') ? '&' : '?';
        const urlWithTimestamp = `${url}${separator}_t=${Date.now()}`;
        
        return await fetch(urlWithTimestamp, options);
    }
    
    /**
     * 令牌自动刷新
     */
    async fetchWithTokenRefresh(url, options = {}) {
        try {
            const response = await this.fetch(url, options);
            
            // 检查是否需要刷新令牌
            if (response.status === 401) {
                const newToken = await this.refreshAuthToken();
                
                // 重新设置令牌
                this.setAuthToken(newToken);
                
                // 重新发送原请求
                options.headers['Authorization'] = `Bearer ${newToken}`;
                return await this.fetch(url, options);
            }
            
            return response;
        } catch (error) {
            throw this.handleError(error);
        }
    }
    
    /**
     * 令牌刷新逻辑
     */
    async refreshAuthToken() {
        if (this.isRefreshing) {
            // 如果正在刷新，等待刷新完成
            return await this.waitForTokenRefresh();
        }
        
        this.isRefreshing = true;
        
        try {
            const refreshToken = localStorage.getItem('refresh_token');
            const response = await fetch(`${this.baseURL}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refreshToken })
            });
            
            const data = await response.json();
            
            // 保存新令牌
            localStorage.setItem('auth_token', data.accessToken);
            localStorage.setItem('refresh_token', data.refreshToken);
            
            return data.accessToken;
        } finally {
            this.isRefreshing = false;
        }
    }
    
    /**
     * 等待令牌刷新完成
     */
    waitForTokenRefresh() {
        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                if (!this.isRefreshing) {
                    clearInterval(checkInterval);
                    resolve(localStorage.getItem('auth_token'));
                }
            }, 100);
        });
    }
}

// 导出API服务类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ApiService, AdvancedApiService };
}