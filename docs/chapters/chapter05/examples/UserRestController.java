package com.example.demo.controller;

import com.example.demo.entity.User;
import com.example.demo.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import javax.validation.constraints.Min;
import java.util.List;
import java.util.Optional;

/**
 * 用户管理REST控制器
 * 
 * 演示Spring Boot Web开发的核心功能：
 * 1. RESTful API设计
 * 2. HTTP方法映射
 * 3. 请求参数处理
 * 4. 响应数据格式化
 * 5. 异常处理
 */
@RestController
@RequestMapping("/api/users")
@Validated
public class UserRestController {

    private final UserService userService;

    /**
     * 构造器注入（推荐方式）
     */
    @Autowired
    public UserRestController(UserService userService) {
        this.userService = userService;
    }

    /**
     * 获取所有用户 - GET /api/users
     * 
     * @param page 页码（可选，默认为0）
     * @param size 每页大小（可选，默认为10）
     * @return 用户列表
     */
    @GetMapping
    public ResponseEntity<List<User>> getAllUsers(
            @RequestParam(defaultValue = "0") @Min(0) int page,
            @RequestParam(defaultValue = "10") @Min(1) int size) {
        
        List<User> users = userService.getAllUsers(page, size);
        return ResponseEntity.ok(users);
    }

    /**
     * 根据ID获取用户 - GET /api/users/{id}
     * 
     * @param id 用户ID
     * @return 用户信息
     */
    @GetMapping("/{id}")
    public ResponseEntity<User> getUserById(@PathVariable @Min(1) Long id) {
        Optional<User> user = userService.getUserById(id);
        return user.map(ResponseEntity::ok)
                  .orElse(ResponseEntity.notFound().build());
    }

    /**
     * 创建新用户 - POST /api/users
     * 
     * @param user 用户信息
     * @return 创建的用户
     */
    @PostMapping
    public ResponseEntity<User> createUser(@Valid @RequestBody User user) {
        User createdUser = userService.createUser(user);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdUser);
    }

    /**
     * 更新用户信息 - PUT /api/users/{id}
     * 
     * @param id 用户ID
     * @param user 更新的用户信息
     * @return 更新后的用户
     */
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(
            @PathVariable @Min(1) Long id,
            @Valid @RequestBody User user) {
        
        Optional<User> updatedUser = userService.updateUser(id, user);
        return updatedUser.map(ResponseEntity::ok)
                         .orElse(ResponseEntity.notFound().build());
    }

    /**
     * 删除用户 - DELETE /api/users/{id}
     * 
     * @param id 用户ID
     * @return 删除结果
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable @Min(1) Long id) {
        boolean deleted = userService.deleteUser(id);
        return deleted ? ResponseEntity.noContent().build()
                      : ResponseEntity.notFound().build();
    }

    /**
     * 批量删除用户 - DELETE /api/users
     * 
     * @param ids 用户ID列表
     * @return 批量删除结果
     */
    @DeleteMapping
    public ResponseEntity<BatchDeleteResult> batchDeleteUsers(@RequestBody List<Long> ids) {
        BatchDeleteResult result = userService.batchDeleteUsers(ids);
        return ResponseEntity.ok(result);
    }

    /**
     * 搜索用户 - GET /api/users/search
     * 
     * @param keyword 搜索关键词
     * @param page 页码
     * @param size 每页大小
     * @return 搜索结果
     */
    @GetMapping("/search")
    public ResponseEntity<List<User>> searchUsers(
            @RequestParam String keyword,
            @RequestParam(defaultValue = "0") @Min(0) int page,
            @RequestParam(defaultValue = "10") @Min(1) int size) {
        
        List<User> users = userService.searchUsers(keyword, page, size);
        return ResponseEntity.ok(users);
    }

    /**
     * 获取用户统计信息 - GET /api/users/stats
     * 
     * @return 统计信息
     */
    @GetMapping("/stats")
    public ResponseEntity<UserStats> getUserStats() {
        UserStats stats = userService.getUserStats();
        return ResponseEntity.ok(stats);
    }

    /**
     * 更新用户状态 - PATCH /api/users/{id}/status
     * 
     * @param id 用户ID
     * @param status 新状态
     * @return 更新结果
     */
    @PatchMapping("/{id}/status")
    public ResponseEntity<User> updateUserStatus(
            @PathVariable @Min(1) Long id,
            @RequestParam String status) {
        
        Optional<User> user = userService.updateUserStatus(id, status);
        return user.map(ResponseEntity::ok)
                  .orElse(ResponseEntity.notFound().build());
    }
}

/**
 * 批量删除结果
 */
@Data
public class BatchDeleteResult {
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
}

/**
 * 用户统计信息
 */
@Data
public class UserStats {
    private long totalUsers;
    private long activeUsers;
    private long inactiveUsers;
    private long newUsersThisMonth;
    
    public UserStats(long totalUsers, long activeUsers, long inactiveUsers, long newUsersThisMonth) {
        this.totalUsers = totalUsers;
        this.activeUsers = activeUsers;
        this.inactiveUsers = inactiveUsers;
        this.newUsersThisMonth = newUsersThisMonth;
    }
}