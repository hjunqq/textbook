package com.example.demo.controller;

import com.example.demo.dto.ApiResponse;
import com.example.demo.dto.UserDto;
import com.example.demo.dto.CreateUserRequest;
import com.example.demo.dto.UpdateUserRequest;
import com.example.demo.service.UserService;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import javax.validation.Valid;
import java.net.URI;
import java.util.List;

/**
 * RESTful API设计完整示例
 * 
 * 演示RESTful API的核心设计原则：
 * 1. 资源导向的URL设计
 * 2. HTTP方法语义的正确使用
 * 3. 统一的响应格式
 * 4. 状态码的恰当使用
 * 5. 版本管理和向后兼容
 * 6. 错误处理机制
 * 7. 分页和过滤支持
 */
@RestController
@RequestMapping("/api/v1")
@CrossOrigin(origins = "*", maxAge = 3600)
public class UserRestController {
    
    private final UserService userService;
    
    public UserRestController(UserService userService) {
        this.userService = userService;
    }
    
    /**
     * 获取用户列表 - GET /api/v1/users
     * 
     * RESTful设计原则：
     * - 使用GET方法获取资源集合
     * - 支持查询参数进行过滤和分页
     * - 返回200 OK状态码
     */
    @GetMapping("/users")
    public ResponseEntity<ApiResponse<Page<UserDto>>> getAllUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String department,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String keyword) {
        
        UserQueryRequest request = UserQueryRequest.builder()
                .page(page)
                .size(size)
                .department(department)
                .status(status)
                .keyword(keyword)
                .build();
                
        Page<UserDto> users = userService.getUsers(request);
        
        return ResponseEntity.ok(
            ApiResponse.success(users, "查询用户数据成功")
        );
    }
    
    /**
     * 获取单个用户 - GET /api/v1/users/{id}
     * 
     * RESTful设计原则：
     * - 使用路径参数标识具体资源
     * - 资源存在返回200，不存在返回404
     */
    @GetMapping("/users/{id}")
    public ResponseEntity<ApiResponse<UserDto>> getUserById(@PathVariable Long id) {
        UserDto user = userService.getUserById(id);
        return ResponseEntity.ok(
            ApiResponse.success(user, "获取用户详情成功")
        );
    }
    
    /**
     * 创建新用户 - POST /api/v1/users
     * 
     * RESTful设计原则：
     * - 使用POST方法创建资源
     * - 请求体包含资源数据
     * - 创建成功返回201 Created
     * - 响应头包含新资源的Location
     */
    @PostMapping("/users")
    public ResponseEntity<ApiResponse<UserDto>> createUser(
            @Valid @RequestBody CreateUserRequest request) {
        
        UserDto createdUser = userService.createUser(request);
        
        // 构建新资源的URI
        URI location = ServletUriComponentsBuilder
                .fromCurrentRequest()
                .path("/{id}")
                .buildAndExpand(createdUser.getId())
                .toUri();
                
        return ResponseEntity.created(location)
                .body(ApiResponse.success(createdUser, "用户创建成功"));
    }
    
    /**
     * 完整更新用户 - PUT /api/v1/users/{id}
     * 
     * RESTful设计原则：
     * - 使用PUT方法进行完整资源替换
     * - 请求体包含完整的资源表示
     * - 更新成功返回200 OK
     */
    @PutMapping("/users/{id}")
    public ResponseEntity<ApiResponse<UserDto>> updateUser(
            @PathVariable Long id, 
            @Valid @RequestBody UpdateUserRequest request) {
        
        UserDto updatedUser = userService.updateUser(id, request);
        return ResponseEntity.ok(
            ApiResponse.success(updatedUser, "用户更新成功")
        );
    }
    
    /**
     * 部分更新用户 - PATCH /api/v1/users/{id}
     * 
     * RESTful设计原则：
     * - 使用PATCH方法进行部分更新
     * - 只更新请求中包含的字段
     */
    @PatchMapping("/users/{id}")
    public ResponseEntity<ApiResponse<UserDto>> patchUser(
            @PathVariable Long id,
            @RequestBody UserPatchRequest request) {
        
        UserDto updatedUser = userService.patchUser(id, request);
        return ResponseEntity.ok(
            ApiResponse.success(updatedUser, "用户信息已更新")
        );
    }
    
    /**
     * 删除用户 - DELETE /api/v1/users/{id}
     * 
     * RESTful设计原则：
     * - 使用DELETE方法删除资源
     * - 删除成功返回204 No Content
     */
    @DeleteMapping("/users/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }
    
    /**
     * 批量删除用户 - DELETE /api/v1/users
     * 
     * RESTful设计原则：
     * - 使用查询参数传递ID列表
     * - 返回批量操作结果
     */
    @DeleteMapping("/users")
    public ResponseEntity<ApiResponse<BatchDeleteResult>> batchDeleteUsers(
            @RequestParam List<Long> ids) {
        
        BatchDeleteResult result = userService.batchDeleteUsers(ids);
        return ResponseEntity.ok(
            ApiResponse.success(result, "批量删除操作完成")
        );
    }
    
    /**
     * 用户搜索 - GET /api/v1/users/search
     * 
     * RESTful设计原则：
     * - 使用子资源表示特定操作
     * - 查询参数传递搜索条件
     */
    @GetMapping("/users/search")
    public ResponseEntity<ApiResponse<List<UserDto>>> searchUsers(
            @RequestParam String keyword,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        
        List<UserDto> users = userService.searchUsers(keyword, page, size);
        return ResponseEntity.ok(
            ApiResponse.success(users, "搜索完成")
        );
    }
    
    /**
     * 用户统计信息 - GET /api/v1/users/statistics
     * 
     * RESTful设计原则：
     * - 使用子资源返回聚合数据
     * - 适合不修改状态的计算操作
     */
    @GetMapping("/users/statistics")
    public ResponseEntity<ApiResponse<UserStatistics>> getUserStatistics() {
        UserStatistics stats = userService.getUserStatistics();
        return ResponseEntity.ok(
            ApiResponse.success(stats, "获取统计信息成功")
        );
    }
    
    /**
     * 激活用户 - POST /api/v1/users/{id}/activate
     * 
     * RESTful设计原则：
     * - 使用POST方法执行业务操作
     * - 子资源表示具体动作
     */
    @PostMapping("/users/{id}/activate")
    public ResponseEntity<ApiResponse<UserDto>> activateUser(@PathVariable Long id) {
        UserDto user = userService.activateUser(id);
        return ResponseEntity.ok(
            ApiResponse.success(user, "用户已激活")
        );
    }
    
    /**
     * 重置用户密码 - POST /api/v1/users/{id}/reset-password
     * 
     * RESTful设计原则：
     * - 安全敏感操作使用POST方法
     * - 返回操作结果而非敏感信息
     */
    @PostMapping("/users/{id}/reset-password")
    public ResponseEntity<ApiResponse<PasswordResetResult>> resetPassword(
            @PathVariable Long id) {
        
        PasswordResetResult result = userService.resetPassword(id);
        return ResponseEntity.ok(
            ApiResponse.success(result, "密码重置成功")
        );
    }
    
    /**
     * 获取用户权限 - GET /api/v1/users/{id}/permissions
     * 
     * RESTful设计原则：
     * - 使用子资源访问关联数据
     * - 保持URL层次结构清晰
     */
    @GetMapping("/users/{id}/permissions")
    public ResponseEntity<ApiResponse<List<PermissionDto>>> getUserPermissions(
            @PathVariable Long id) {
        
        List<PermissionDto> permissions = userService.getUserPermissions(id);
        return ResponseEntity.ok(
            ApiResponse.success(permissions, "获取用户权限成功")
        );
    }
    
    /**
     * 更新用户权限 - PUT /api/v1/users/{id}/permissions
     * 
     * RESTful设计原则：
     * - 使用PUT方法完整替换子资源
     * - 请求体包含完整的权限列表
     */
    @PutMapping("/users/{id}/permissions")
    public ResponseEntity<ApiResponse<List<PermissionDto>>> updateUserPermissions(
            @PathVariable Long id,
            @Valid @RequestBody UpdatePermissionsRequest request) {
        
        List<PermissionDto> permissions = userService.updateUserPermissions(id, request);
        return ResponseEntity.ok(
            ApiResponse.success(permissions, "权限更新成功")
        );
    }
}

/**
 * API版本管理示例 - V2版本控制器
 * 展示如何处理API演进和向后兼容
 */
@RestController
@RequestMapping("/api/v2")
@CrossOrigin(origins = "*", maxAge = 3600)
public class UserRestV2Controller {
    
    private final UserService userService;
    
    public UserRestV2Controller(UserService userService) {
        this.userService = userService;
    }
    
    /**
     * V2版本的用户列表接口
     * 新增：
     * - 更丰富的过滤条件
     * - 响应缓存控制
     * - 更详细的元数据
     */
    @GetMapping("/users")
    public ResponseEntity<ApiResponse<PagedResponse<UserV2Dto>>> getAllUsersV2(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String department,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String createdDateFrom,
            @RequestParam(required = false) String createdDateTo,
            @RequestParam(defaultValue = "createdDate") String sortBy,
            @RequestParam(defaultValue = "desc") String sortDir) {
        
        UserQueryV2Request request = UserQueryV2Request.builder()
                .page(page)
                .size(size)
                .department(department)
                .status(status)
                .keyword(keyword)
                .createdDateFrom(createdDateFrom)
                .createdDateTo(createdDateTo)
                .sortBy(sortBy)
                .sortDir(sortDir)
                .build();
                
        PagedResponse<UserV2Dto> response = userService.getUsersV2(request);
        
        return ResponseEntity.ok()
                .cacheControl(CacheControl.maxAge(Duration.ofMinutes(5)))
                .body(ApiResponse.success(response, "查询用户数据成功"));
    }
    
    /**
     * V2版本支持更丰富的用户创建选项
     */
    @PostMapping("/users")
    public ResponseEntity<ApiResponse<UserV2Dto>> createUserV2(
            @Valid @RequestBody CreateUserV2Request request) {
        
        UserV2Dto createdUser = userService.createUserV2(request);
        
        URI location = ServletUriComponentsBuilder
                .fromCurrentRequest()
                .path("/{id}")
                .buildAndExpand(createdUser.getId())
                .toUri();
                
        return ResponseEntity.created(location)
                .body(ApiResponse.success(createdUser, "用户创建成功"));
    }
}

/**
 * 统一响应格式
 * 确保所有API端点返回一致的数据结构
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
class ApiResponse<T> {
    private boolean success;
    private String message;
    private T data;
    private String errorCode;
    private Long timestamp;
    private String requestId;
    private ApiMetadata metadata;
    
    public ApiResponse() {
        this.timestamp = System.currentTimeMillis();
        // 从MDC获取请求ID用于追踪
        this.requestId = MDC.get("requestId");
    }
    
    public static <T> ApiResponse<T> success(T data, String message) {
        ApiResponse<T> response = new ApiResponse<>();
        response.setSuccess(true);
        response.setData(data);
        response.setMessage(message);
        return response;
    }
    
    public static <T> ApiResponse<T> success(T data, String message, ApiMetadata metadata) {
        ApiResponse<T> response = success(data, message);
        response.setMetadata(metadata);
        return response;
    }
    
    public static <T> ApiResponse<T> error(String errorCode, String message) {
        ApiResponse<T> response = new ApiResponse<>();
        response.setSuccess(false);
        response.setErrorCode(errorCode);
        response.setMessage(message);
        return response;
    }
    
    public static <T> ApiResponse<T> error(String errorCode, String message, T errorDetails) {
        ApiResponse<T> response = error(errorCode, message);
        response.setData(errorDetails);
        return response;
    }
    
    // Getter和Setter方法
    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }
    
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    
    public T getData() { return data; }
    public void setData(T data) { this.data = data; }
    
    public String getErrorCode() { return errorCode; }
    public void setErrorCode(String errorCode) { this.errorCode = errorCode; }
    
    public Long getTimestamp() { return timestamp; }
    public void setTimestamp(Long timestamp) { this.timestamp = timestamp; }
    
    public String getRequestId() { return requestId; }
    public void setRequestId(String requestId) { this.requestId = requestId; }
    
    public ApiMetadata getMetadata() { return metadata; }
    public void setMetadata(ApiMetadata metadata) { this.metadata = metadata; }
}

/**
 * 分页响应的专门包装
 * 提供丰富的分页元数据
 */
class PagedResponse<T> {
    private List<T> content;
    private PageMetadata page;
    
    public static <T> PagedResponse<T> from(Page<T> springPage) {
        PagedResponse<T> response = new PagedResponse<>();
        response.setContent(springPage.getContent());
        
        PageMetadata pageInfo = new PageMetadata();
        pageInfo.setNumber(springPage.getNumber());
        pageInfo.setSize(springPage.getSize());
        pageInfo.setTotalElements(springPage.getTotalElements());
        pageInfo.setTotalPages(springPage.getTotalPages());
        pageInfo.setHasNext(springPage.hasNext());
        pageInfo.setHasPrevious(springPage.hasPrevious());
        pageInfo.setFirst(springPage.isFirst());
        pageInfo.setLast(springPage.isLast());
        pageInfo.setEmpty(springPage.isEmpty());
        
        response.setPage(pageInfo);
        return response;
    }
    
    // Getter和Setter方法
    public List<T> getContent() { return content; }
    public void setContent(List<T> content) { this.content = content; }
    
    public PageMetadata getPage() { return page; }
    public void setPage(PageMetadata page) { this.page = page; }
}

/**
 * API元数据
 * 包含API调用的额外信息
 */
class ApiMetadata {
    private String version;
    private Long executionTime;
    private String serverInstance;
    private Map<String, Object> debug;
    
    // Getter和Setter方法
    public String getVersion() { return version; }
    public void setVersion(String version) { this.version = version; }
    
    public Long getExecutionTime() { return executionTime; }
    public void setExecutionTime(Long executionTime) { this.executionTime = executionTime; }
    
    public String getServerInstance() { return serverInstance; }
    public void setServerInstance(String serverInstance) { this.serverInstance = serverInstance; }
    
    public Map<String, Object> getDebug() { return debug; }
    public void setDebug(Map<String, Object> debug) { this.debug = debug; }
}

/**
 * 分页元数据
 */
class PageMetadata {
    private int number;
    private int size;
    private long totalElements;
    private int totalPages;
    private boolean hasNext;
    private boolean hasPrevious;
    private boolean first;
    private boolean last;
    private boolean empty;
    
    // Getter和Setter方法
    public int getNumber() { return number; }
    public void setNumber(int number) { this.number = number; }
    
    public int getSize() { return size; }
    public void setSize(int size) { this.size = size; }
    
    public long getTotalElements() { return totalElements; }
    public void setTotalElements(long totalElements) { this.totalElements = totalElements; }
    
    public int getTotalPages() { return totalPages; }
    public void setTotalPages(int totalPages) { this.totalPages = totalPages; }
    
    public boolean isHasNext() { return hasNext; }
    public void setHasNext(boolean hasNext) { this.hasNext = hasNext; }
    
    public boolean isHasPrevious() { return hasPrevious; }
    public void setHasPrevious(boolean hasPrevious) { this.hasPrevious = hasPrevious; }
    
    public boolean isFirst() { return first; }
    public void setFirst(boolean first) { this.first = first; }
    
    public boolean isLast() { return last; }
    public void setLast(boolean last) { this.last = last; }
    
    public boolean isEmpty() { return empty; }
    public void setEmpty(boolean empty) { this.empty = empty; }
}

/**
 * 支持类 - 用户查询请求
 */
class UserQueryRequest {
    private int page;
    private int size;
    private String department;
    private String status;
    private String keyword;
    
    public static UserQueryRequestBuilder builder() {
        return new UserQueryRequestBuilder();
    }
    
    public static class UserQueryRequestBuilder {
        private UserQueryRequest request = new UserQueryRequest();
        
        public UserQueryRequestBuilder page(int page) { request.page = page; return this; }
        public UserQueryRequestBuilder size(int size) { request.size = size; return this; }
        public UserQueryRequestBuilder department(String department) { request.department = department; return this; }
        public UserQueryRequestBuilder status(String status) { request.status = status; return this; }
        public UserQueryRequestBuilder keyword(String keyword) { request.keyword = keyword; return this; }
        
        public UserQueryRequest build() { return request; }
    }
    
    // Getter方法
    public int getPage() { return page; }
    public int getSize() { return size; }
    public String getDepartment() { return department; }
    public String getStatus() { return status; }
    public String getKeyword() { return keyword; }
}

/**
 * 支持类 - 批量删除结果
 */
class BatchDeleteResult {
    private int totalRequested;
    private int successfullyDeleted;
    private int failed;
    private List<String> errors;
    
    public BatchDeleteResult(int totalRequested, int successfullyDeleted, int failed, List<String> errors) {
        this.totalRequested = totalRequested;
        this.successfullyDeleted = successfullyDeleted;
        this.failed = failed;
        this.errors = errors;
    }
    
    // Getter方法
    public int getTotalRequested() { return totalRequested; }
    public int getSuccessfullyDeleted() { return successfullyDeleted; }
    public int getFailed() { return failed; }
    public List<String> getErrors() { return errors; }
}