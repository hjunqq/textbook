package com.example.demo.repository;

import com.example.demo.entity.User;
import com.example.demo.entity.Order;
import com.example.demo.entity.UserStatus;
import com.example.demo.entity.OrderStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

/**
 * Spring Data JPA Repository示例
 * 
 * 演示Repository模式的核心功能：
 * 1. 基础CRUD操作
 * 2. 方法名查询约定
 * 3. @Query自定义查询
 * 4. 分页和排序
 * 5. 原生SQL查询
 * 6. 统计查询
 * 7. 批量操作
 */

/**
 * 用户Repository接口
 * 继承JpaRepository获得基础CRUD功能
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    // ========== 方法名查询约定示例 ==========
    
    /**
     * 根据用户名查询用户
     * Spring Data JPA会自动生成实现
     */
    Optional<User> findByUsername(String username);
    
    /**
     * 根据邮箱查询用户
     * 支持忽略大小写
     */
    Optional<User> findByEmailIgnoreCase(String email);
    
    /**
     * 根据部门查询所有用户，按用户名排序
     */
    List<User> findByDepartmentOrderByUsername(String department);
    
    /**
     * 根据状态查询用户，支持分页
     */
    Page<User> findByStatus(UserStatus status, Pageable pageable);
    
    /**
     * 根据创建日期范围查询用户
     */
    List<User> findByCreatedDateBetween(LocalDate startDate, LocalDate endDate);
    
    /**
     * 查询用户名包含指定文本的用户
     */
    List<User> findByUsernameContainingIgnoreCase(String keyword);
    
    /**
     * 查询邮箱以指定域名结尾的用户
     */
    List<User> findByEmailEndingWith(String domain);
    
    /**
     * 根据部门和状态查询用户数量
     */
    long countByDepartmentAndStatus(String department, UserStatus status);
    
    /**
     * 检查用户名是否存在
     */
    boolean existsByUsername(String username);
    
    /**
     * 检查邮箱是否存在
     */
    boolean existsByEmail(String email);
    
    // ========== @Query JPQL查询示例 ==========
    
    /**
     * 使用JPQL查询活跃用户
     * 支持参数绑定
     */
    @Query("SELECT u FROM User u WHERE u.status = :status AND u.createdDate >= :sinceDate")
    List<User> findActiveUsersSince(
            @Param("status") UserStatus status,
            @Param("sinceDate") LocalDate sinceDate);
    
    /**
     * 使用JPQL进行复杂关联查询
     * 查询有订单的用户
     */
    @Query("SELECT DISTINCT u FROM User u JOIN u.orders o WHERE o.status = :orderStatus")
    List<User> findUsersWithOrdersInStatus(@Param("orderStatus") OrderStatus orderStatus);
    
    /**
     * 使用JPQL进行聚合查询
     * 查询每个部门的用户统计
     */
    @Query("SELECT u.department, COUNT(u) FROM User u GROUP BY u.department")
    List<Object[]> getUserCountByDepartment();
    
    /**
     * 使用JPQL进行复杂条件查询
     * 支持可选参数
     */
    @Query("SELECT u FROM User u WHERE " +
           "(:department IS NULL OR u.department = :department) AND " +
           "(:status IS NULL OR u.status = :status) AND " +
           "(:keyword IS NULL OR LOWER(u.fullName) LIKE LOWER(CONCAT('%', :keyword, '%')))")
    Page<User> findByComplexCriteria(
            @Param("department") String department,
            @Param("status") UserStatus status,
            @Param("keyword") String keyword,
            Pageable pageable);
    
    // ========== 原生SQL查询示例 ==========
    
    /**
     * 使用原生SQL查询
     * 适用于复杂的数据库特定查询
     */
    @Query(value = "SELECT * FROM users u WHERE " +
                  "u.email LIKE CONCAT('%@', :domain) " +
                  "ORDER BY u.created_date DESC " +
                  "LIMIT :limit", 
           nativeQuery = true)
    List<User> findUsersByEmailDomainNative(
            @Param("domain") String domain,
            @Param("limit") int limit);
    
    /**
     * 使用原生SQL进行统计查询
     */
    @Query(value = "SELECT " +
                  "DATE_FORMAT(created_date, '%Y-%m') as month, " +
                  "COUNT(*) as user_count " +
                  "FROM users " +
                  "WHERE created_date >= :startDate " +
                  "GROUP BY DATE_FORMAT(created_date, '%Y-%m') " +
                  "ORDER BY month",
           nativeQuery = true)
    List<Object[]> getUserRegistrationStatistics(@Param("startDate") LocalDate startDate);
    
    // ========== 修改操作示例 ==========
    
    /**
     * 批量更新用户状态
     * @Modifying注解用于修改操作
     */
    @Modifying
    @Query("UPDATE User u SET u.status = :newStatus WHERE u.department = :department")
    int updateStatusByDepartment(
            @Param("department") String department,
            @Param("newStatus") UserStatus newStatus);
    
    /**
     * 批量删除过期用户
     */
    @Modifying
    @Query("DELETE FROM User u WHERE u.status = :status AND u.createdDate < :beforeDate")
    int deleteInactiveUsersBefore(
            @Param("status") UserStatus status,
            @Param("beforeDate") LocalDate beforeDate);
}

/**
 * 订单Repository接口
 * 展示更复杂的查询场景
 */
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    
    /**
     * 根据用户查询订单
     */
    List<Order> findByUserOrderByOrderDateDesc(User user);
    
    /**
     * 根据用户ID查询订单，支持分页
     */
    Page<Order> findByUserId(Long userId, Pageable pageable);
    
    /**
     * 根据订单状态和日期范围查询
     */
    List<Order> findByStatusAndOrderDateBetween(
            OrderStatus status, 
            LocalDateTime startDate, 
            LocalDateTime endDate);
    
    /**
     * 查询总金额大于指定值的订单
     */
    List<Order> findByTotalAmountGreaterThanOrderByTotalAmountDesc(BigDecimal minAmount);
    
    /**
     * 使用JPQL查询用户的订单统计
     */
    @Query("SELECT new com.example.demo.dto.OrderStatistics(" +
           "o.user.id, " +
           "o.user.username, " +
           "COUNT(o), " +
           "COALESCE(SUM(o.totalAmount), 0), " +
           "COALESCE(AVG(o.totalAmount), 0)) " +
           "FROM Order o " +
           "WHERE o.orderDate >= :startDate " +
           "GROUP BY o.user.id, o.user.username " +
           "ORDER BY SUM(o.totalAmount) DESC")
    List<OrderStatistics> getOrderStatisticsByUser(@Param("startDate") LocalDateTime startDate);
    
    /**
     * 查询指定时间段内各状态的订单数量
     */
    @Query("SELECT o.status, COUNT(o) FROM Order o " +
           "WHERE o.orderDate BETWEEN :startDate AND :endDate " +
           "GROUP BY o.status")
    List<Object[]> getOrderCountByStatus(
            @Param("startDate") LocalDateTime startDate,
            @Param("endDate") LocalDateTime endDate);
    
    /**
     * 使用原生SQL查询月度订单趋势
     */
    @Query(value = "SELECT " +
                  "DATE_FORMAT(order_date, '%Y-%m') as order_month, " +
                  "COUNT(*) as order_count, " +
                  "SUM(total_amount) as total_amount, " +
                  "AVG(total_amount) as avg_amount " +
                  "FROM orders " +
                  "WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL :months MONTH) " +
                  "GROUP BY DATE_FORMAT(order_date, '%Y-%m') " +
                  "ORDER BY order_month DESC",
           nativeQuery = true)
    List<Object[]> getMonthlyOrderTrend(@Param("months") int months);
    
    /**
     * 查询用户的最新订单
     */
    @Query("SELECT o FROM Order o WHERE o.user.id = :userId " +
           "AND o.orderDate = (SELECT MAX(o2.orderDate) FROM Order o2 WHERE o2.user.id = :userId)")
    Optional<Order> findLatestOrderByUser(@Param("userId") Long userId);
    
    /**
     * 批量更新订单状态
     */
    @Modifying
    @Query("UPDATE Order o SET o.status = :newStatus " +
           "WHERE o.status = :currentStatus AND o.orderDate < :beforeDate")
    int updateExpiredOrders(
            @Param("currentStatus") OrderStatus currentStatus,
            @Param("newStatus") OrderStatus newStatus,
            @Param("beforeDate") LocalDateTime beforeDate);
}

/**
 * 自定义Repository接口
 * 用于复杂的动态查询
 */
public interface UserRepositoryCustom {
    
    /**
     * 动态条件查询
     */
    Page<User> findWithDynamicCriteria(UserSearchCriteria criteria, Pageable pageable);
    
    /**
     * 批量操作示例
     */
    int batchUpdateUserDepartment(List<Long> userIds, String newDepartment);
}

/**
 * 自定义Repository实现类
 * 使用EntityManager进行复杂查询
 */
@Repository
public class UserRepositoryCustomImpl implements UserRepositoryCustom {
    
    @PersistenceContext
    private EntityManager entityManager;
    
    @Override
    public Page<User> findWithDynamicCriteria(UserSearchCriteria criteria, Pageable pageable) {
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<User> query = cb.createQuery(User.class);
        Root<User> root = query.from(User.class);
        
        List<Predicate> predicates = new ArrayList<>();
        
        // 动态添加查询条件
        if (criteria.getDepartment() != null) {
            predicates.add(cb.equal(root.get("department"), criteria.getDepartment()));
        }
        
        if (criteria.getStatus() != null) {
            predicates.add(cb.equal(root.get("status"), criteria.getStatus()));
        }
        
        if (criteria.getKeyword() != null) {
            Predicate usernamePredicate = cb.like(
                cb.lower(root.get("username")), 
                "%" + criteria.getKeyword().toLowerCase() + "%"
            );
            Predicate fullNamePredicate = cb.like(
                cb.lower(root.get("fullName")), 
                "%" + criteria.getKeyword().toLowerCase() + "%"
            );
            predicates.add(cb.or(usernamePredicate, fullNamePredicate));
        }
        
        if (criteria.getCreatedDateFrom() != null) {
            predicates.add(cb.greaterThanOrEqualTo(
                root.get("createdDate"), criteria.getCreatedDateFrom()));
        }
        
        if (criteria.getCreatedDateTo() != null) {
            predicates.add(cb.lessThanOrEqualTo(
                root.get("createdDate"), criteria.getCreatedDateTo()));
        }
        
        // 应用查询条件
        if (!predicates.isEmpty()) {
            query.where(predicates.toArray(new Predicate[0]));
        }
        
        // 应用排序
        if (pageable.getSort().isSorted()) {
            List<javax.persistence.criteria.Order> orders = new ArrayList<>();
            pageable.getSort().forEach(sortOrder -> {
                if (sortOrder.isAscending()) {
                    orders.add(cb.asc(root.get(sortOrder.getProperty())));
                } else {
                    orders.add(cb.desc(root.get(sortOrder.getProperty())));
                }
            });
            query.orderBy(orders);
        }
        
        // 执行查询
        TypedQuery<User> typedQuery = entityManager.createQuery(query);
        typedQuery.setFirstResult((int) pageable.getOffset());
        typedQuery.setMaxResults(pageable.getPageSize());
        
        List<User> results = typedQuery.getResultList();
        long total = countWithDynamicCriteria(criteria);
        
        return new PageImpl<>(results, pageable, total);
    }
    
    private long countWithDynamicCriteria(UserSearchCriteria criteria) {
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<Long> query = cb.createQuery(Long.class);
        Root<User> root = query.from(User.class);
        
        query.select(cb.count(root));
        
        // 复用查询条件逻辑
        List<Predicate> predicates = buildPredicates(cb, root, criteria);
        if (!predicates.isEmpty()) {
            query.where(predicates.toArray(new Predicate[0]));
        }
        
        return entityManager.createQuery(query).getSingleResult();
    }
    
    @Override
    @Transactional
    public int batchUpdateUserDepartment(List<Long> userIds, String newDepartment) {
        String jpql = "UPDATE User u SET u.department = :department " +
                     "WHERE u.id IN :userIds";
        
        return entityManager.createQuery(jpql)
                .setParameter("department", newDepartment)
                .setParameter("userIds", userIds)
                .executeUpdate();
    }
    
    private List<Predicate> buildPredicates(CriteriaBuilder cb, Root<User> root, 
                                          UserSearchCriteria criteria) {
        List<Predicate> predicates = new ArrayList<>();
        
        if (criteria.getDepartment() != null) {
            predicates.add(cb.equal(root.get("department"), criteria.getDepartment()));
        }
        
        if (criteria.getStatus() != null) {
            predicates.add(cb.equal(root.get("status"), criteria.getStatus()));
        }
        
        // 其他条件构建逻辑...
        
        return predicates;
    }
}

/**
 * 用户搜索条件类
 */
class UserSearchCriteria {
    private String department;
    private UserStatus status;
    private String keyword;
    private LocalDate createdDateFrom;
    private LocalDate createdDateTo;
    
    // 构造函数和Getter/Setter方法
    public UserSearchCriteria() {}
    
    public String getDepartment() { return department; }
    public void setDepartment(String department) { this.department = department; }
    
    public UserStatus getStatus() { return status; }
    public void setStatus(UserStatus status) { this.status = status; }
    
    public String getKeyword() { return keyword; }
    public void setKeyword(String keyword) { this.keyword = keyword; }
    
    public LocalDate getCreatedDateFrom() { return createdDateFrom; }
    public void setCreatedDateFrom(LocalDate createdDateFrom) { this.createdDateFrom = createdDateFrom; }
    
    public LocalDate getCreatedDateTo() { return createdDateTo; }
    public void setCreatedDateTo(LocalDate createdDateTo) { this.createdDateTo = createdDateTo; }
}

/**
 * 订单统计DTO类
 */
class OrderStatistics {
    private Long userId;
    private String username;
    private Long orderCount;
    private BigDecimal totalAmount;
    private BigDecimal averageAmount;
    
    public OrderStatistics(Long userId, String username, Long orderCount, 
                          BigDecimal totalAmount, BigDecimal averageAmount) {
        this.userId = userId;
        this.username = username;
        this.orderCount = orderCount;
        this.totalAmount = totalAmount;
        this.averageAmount = averageAmount;
    }
    
    // Getter方法
    public Long getUserId() { return userId; }
    public String getUsername() { return username; }
    public Long getOrderCount() { return orderCount; }
    public BigDecimal getTotalAmount() { return totalAmount; }
    public BigDecimal getAverageAmount() { return averageAmount; }
}