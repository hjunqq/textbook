package com.example.demo.entity;

import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import javax.persistence.*;
import javax.validation.constraints.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

/**
 * JPA实体映射完整示例
 * 
 * 演示JPA实体设计的核心特性：
 * 1. 基本字段映射和约束
 * 2. 主键生成策略
 * 3. 关联关系映射
 * 4. 索引和性能优化
 * 5. 生命周期回调
 * 6. 审计功能
 */

/**
 * 用户实体类
 * 展示企业级实体设计的最佳实践
 */
@Entity
@Table(name = "users", 
       indexes = {
           @Index(name = "idx_username", columnList = "username", unique = true),
           @Index(name = "idx_email", columnList = "email"),
           @Index(name = "idx_department", columnList = "department"),
           @Index(name = "idx_created_date", columnList = "created_date")
       })
@EntityListeners(AuditingEntityListener.class)
public class User {
    
    /**
     * 主键配置
     * 使用自增策略，适合大多数关系数据库
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    /**
     * 用户名字段
     * - 唯一约束
     * - 非空约束
     * - 长度限制
     */
    @Column(name = "username", unique = true, nullable = false, length = 50)
    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 50, message = "用户名长度必须在3-50字符之间")
    private String username;
    
    /**
     * 邮箱字段
     * - 非空约束
     * - 邮箱格式验证
     */
    @Column(name = "email", nullable = false, length = 100)
    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;
    
    /**
     * 电话字段
     * - 可选字段
     * - 格式验证
     */
    @Column(name = "phone", length = 20)
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phone;
    
    /**
     * 全名字段
     */
    @Column(name = "full_name", length = 100)
    @Size(max = 100, message = "姓名长度不能超过100字符")
    private String fullName;
    
    /**
     * 部门字段
     * - 用于分组和权限控制
     */
    @Column(name = "department", length = 50)
    private String department;
    
    /**
     * 用户状态枚举
     * - 使用STRING类型存储，便于理解
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "status", length = 20)
    private UserStatus status = UserStatus.ACTIVE;
    
    /**
     * 创建日期
     * - 审计字段，自动填充
     */
    @CreatedDate
    @Column(name = "created_date", updatable = false)
    private LocalDate createdDate;
    
    /**
     * 最后修改时间
     * - 审计字段，自动更新
     */
    @LastModifiedDate
    @Column(name = "last_modified_time")
    private LocalDateTime lastModifiedTime;
    
    /**
     * 一对多关联关系
     * - 用户可以有多个订单
     * - 使用懒加载提高性能
     */
    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY, cascade = CascadeType.ALL)
    private List<Order> orders;
    
    /**
     * 多对多关联关系
     * - 用户可以有多个角色
     * - 定义中间表结构
     */
    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
        name = "user_roles",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "role_id")
    )
    private List<Role> roles;
    
    /**
     * JPA生命周期回调
     * 在持久化之前执行
     */
    @PrePersist
    protected void onCreate() {
        if (status == null) {
            status = UserStatus.ACTIVE;
        }
        if (createdDate == null) {
            createdDate = LocalDate.now();
        }
    }
    
    /**
     * JPA生命周期回调
     * 在更新之前执行
     */
    @PreUpdate
    protected void onUpdate() {
        lastModifiedTime = LocalDateTime.now();
    }
    
    // 默认构造函数
    public User() {}
    
    // 业务构造函数
    public User(String username, String email, String fullName) {
        this.username = username;
        this.email = email;
        this.fullName = fullName;
        this.status = UserStatus.ACTIVE;
        this.createdDate = LocalDate.now();
    }
    
    // Getter和Setter方法
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    
    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }
    
    public String getFullName() { return fullName; }
    public void setFullName(String fullName) { this.fullName = fullName; }
    
    public String getDepartment() { return department; }
    public void setDepartment(String department) { this.department = department; }
    
    public UserStatus getStatus() { return status; }
    public void setStatus(UserStatus status) { this.status = status; }
    
    public LocalDate getCreatedDate() { return createdDate; }
    public void setCreatedDate(LocalDate createdDate) { this.createdDate = createdDate; }
    
    public LocalDateTime getLastModifiedTime() { return lastModifiedTime; }
    public void setLastModifiedTime(LocalDateTime lastModifiedTime) { this.lastModifiedTime = lastModifiedTime; }
    
    public List<Order> getOrders() { return orders; }
    public void setOrders(List<Order> orders) { this.orders = orders; }
    
    public List<Role> getRoles() { return roles; }
    public void setRoles(List<Role> roles) { this.roles = roles; }
    
    // 业务方法
    public boolean isActive() {
        return UserStatus.ACTIVE.equals(status);
    }
    
    public void activate() {
        this.status = UserStatus.ACTIVE;
    }
    
    public void deactivate() {
        this.status = UserStatus.INACTIVE;
    }
    
    public void suspend() {
        this.status = UserStatus.SUSPENDED;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof User)) return false;
        User user = (User) o;
        return id != null && id.equals(user.getId());
    }
    
    @Override
    public int hashCode() {
        return getClass().hashCode();
    }
    
    @Override
    public String toString() {
        return String.format("User{id=%d, username='%s', email='%s', status='%s'}", 
                           id, username, email, status);
    }
}

/**
 * 用户状态枚举
 */
enum UserStatus {
    ACTIVE("激活"),
    INACTIVE("未激活"),
    SUSPENDED("已暂停"),
    DELETED("已删除");
    
    private final String description;
    
    UserStatus(String description) {
        this.description = description;
    }
    
    public String getDescription() {
        return description;
    }
}

/**
 * 订单实体类
 * 展示多对一关联关系
 */
@Entity
@Table(name = "orders",
       indexes = {
           @Index(name = "idx_user_id", columnList = "user_id"),
           @Index(name = "idx_order_date", columnList = "order_date"),
           @Index(name = "idx_status", columnList = "status")
       })
public class Order {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "order_number", unique = true, nullable = false)
    private String orderNumber;
    
    /**
     * 多对一关联关系
     * - 多个订单属于一个用户
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @Column(name = "order_date", nullable = false)
    private LocalDateTime orderDate;
    
    @Column(name = "total_amount", precision = 10, scale = 2)
    private BigDecimal totalAmount;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "status")
    private OrderStatus status = OrderStatus.PENDING;
    
    @Column(name = "description", length = 500)
    private String description;
    
    @PrePersist
    protected void onCreate() {
        if (orderDate == null) {
            orderDate = LocalDateTime.now();
        }
        if (orderNumber == null) {
            orderNumber = generateOrderNumber();
        }
    }
    
    private String generateOrderNumber() {
        return "ORD" + System.currentTimeMillis();
    }
    
    // 构造函数
    public Order() {}
    
    public Order(User user, BigDecimal totalAmount, String description) {
        this.user = user;
        this.totalAmount = totalAmount;
        this.description = description;
        this.status = OrderStatus.PENDING;
        this.orderDate = LocalDateTime.now();
    }
    
    // Getter和Setter方法（省略以节省篇幅）
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getOrderNumber() { return orderNumber; }
    public void setOrderNumber(String orderNumber) { this.orderNumber = orderNumber; }
    
    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }
    
    public LocalDateTime getOrderDate() { return orderDate; }
    public void setOrderDate(LocalDateTime orderDate) { this.orderDate = orderDate; }
    
    public BigDecimal getTotalAmount() { return totalAmount; }
    public void setTotalAmount(BigDecimal totalAmount) { this.totalAmount = totalAmount; }
    
    public OrderStatus getStatus() { return status; }
    public void setStatus(OrderStatus status) { this.status = status; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
}

/**
 * 订单状态枚举
 */
enum OrderStatus {
    PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED
}

/**
 * 角色实体类
 * 展示多对多关联关系的另一端
 */
@Entity
@Table(name = "roles")
public class Role {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "role_name", unique = true, nullable = false)
    private String roleName;
    
    @Column(name = "description")
    private String description;
    
    /**
     * 多对多关联关系的另一端
     * - 一个角色可以分配给多个用户
     */
    @ManyToMany(mappedBy = "roles", fetch = FetchType.LAZY)
    private List<User> users;
    
    // 构造函数
    public Role() {}
    
    public Role(String roleName, String description) {
        this.roleName = roleName;
        this.description = description;
    }
    
    // Getter和Setter方法
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getRoleName() { return roleName; }
    public void setRoleName(String roleName) { this.roleName = roleName; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    
    public List<User> getUsers() { return users; }
    public void setUsers(List<User> users) { this.users = users; }
}