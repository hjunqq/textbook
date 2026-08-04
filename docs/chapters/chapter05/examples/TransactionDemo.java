package com.example.demo.service;

import com.example.demo.entity.User;
import com.example.demo.entity.Order;
import com.example.demo.entity.OrderStatus;
import com.example.demo.repository.UserRepository;
import com.example.demo.repository.OrderRepository;
import com.example.demo.exception.BusinessException;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Isolation;
import org.springframework.beans.factory.annotation.Autowired;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.CompletableFuture;

/**
 * Spring事务管理完整示例
 * 
 * 演示事务管理的核心特性：
 * 1. 声明式事务管理
 * 2. 事务传播行为
 * 3. 事务隔离级别
 * 4. 事务回滚控制
 * 5. 批量操作事务
 * 6. 分布式事务处理
 * 7. 事务监听器
 */
@Service
@Transactional // 类级别事务，所有方法默认使用事务
public class OrderTransactionService {
    
    private final UserRepository userRepository;
    private final OrderRepository orderRepository;
    private final NotificationService notificationService;
    private final AuditService auditService;
    private final PaymentService paymentService;
    
    public OrderTransactionService(UserRepository userRepository,
                                 OrderRepository orderRepository,
                                 NotificationService notificationService,
                                 AuditService auditService,
                                 PaymentService paymentService) {
        this.userRepository = userRepository;
        this.orderRepository = orderRepository;
        this.notificationService = notificationService;
        this.auditService = auditService;
        this.paymentService = paymentService;
    }
    
    /**
     * 基本事务示例：创建订单
     * 使用默认事务配置
     */
    public Order createOrder(Long userId, BigDecimal amount, String description) {
        // 查找用户
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException("用户不存在: " + userId));
        
        // 创建订单
        Order order = new Order(user, amount, description);
        order.setStatus(OrderStatus.PENDING);
        
        // 保存订单
        Order savedOrder = orderRepository.save(order);
        
        // 记录审计日志
        auditService.logOrderCreation(savedOrder);
        
        return savedOrder;
    }
    
    /**
     * 事务回滚示例：订单处理失败时回滚
     * rollbackFor指定哪些异常触发回滚
     */
    @Transactional(rollbackFor = Exception.class)
    public Order processOrder(Long orderId) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new BusinessException("订单不存在: " + orderId));
        
        try {
            // 1. 验证订单状态
            if (order.getStatus() != OrderStatus.PENDING) {
                throw new BusinessException("订单状态不正确，当前状态: " + order.getStatus());
            }
            
            // 2. 处理支付
            PaymentResult paymentResult = paymentService.processPayment(
                order.getUser().getId(), 
                order.getTotalAmount()
            );
            
            if (!paymentResult.isSuccess()) {
                throw new BusinessException("支付失败: " + paymentResult.getErrorMessage());
            }
            
            // 3. 更新订单状态
            order.setStatus(OrderStatus.PROCESSING);
            Order updatedOrder = orderRepository.save(order);
            
            // 4. 发送通知（可能失败，但不应该回滚整个事务）
            try {
                notificationService.sendOrderProcessingNotification(updatedOrder);
            } catch (Exception e) {
                // 记录日志但不回滚事务
                System.err.println("发送通知失败: " + e.getMessage());
            }
            
            // 5. 记录审计日志
            auditService.logOrderProcessing(updatedOrder, paymentResult.getTransactionId());
            
            return updatedOrder;
            
        } catch (BusinessException e) {
            // 业务异常，回滚事务
            System.err.println("订单处理失败，事务回滚: " + e.getMessage());
            throw e;
        } catch (Exception e) {
            // 系统异常，包装后抛出，触发回滚
            throw new BusinessException("订单处理系统错误", e);
        }
    }
    
    /**
     * 批量操作事务示例
     * 处理多个订单，部分失败不影响其他订单
     */
    @Transactional(rollbackFor = Exception.class)
    public BatchProcessResult batchProcessOrders(List<Long> orderIds) {
        BatchProcessResult result = new BatchProcessResult();
        List<Order> successfulOrders = new ArrayList<>();
        List<String> failedOrders = new ArrayList<>();
        
        for (Long orderId : orderIds) {
            try {
                // 为每个订单创建独立的事务处理点
                Order processedOrder = processSingleOrder(orderId);
                successfulOrders.add(processedOrder);
                result.incrementSuccess();
                
            } catch (Exception e) {
                String errorMsg = "订单 " + orderId + " 处理失败: " + e.getMessage();
                failedOrders.add(errorMsg);
                result.incrementFailure();
                
                // 记录失败但继续处理其他订单
                System.err.println(errorMsg);
            }
        }
        
        // 批量保存成功的订单
        if (!successfulOrders.isEmpty()) {
            orderRepository.saveAll(successfulOrders);
        }
        
        // 记录批量操作结果
        auditService.logBatchOperation("ORDER_PROCESS", result);
        
        result.setSuccessfulOrders(successfulOrders);
        result.setFailedOrderMessages(failedOrders);
        
        return result;
    }
    
    /**
     * 事务传播行为示例：REQUIRES_NEW
     * 创建新的独立事务，即使外层事务回滚也不影响
     */
    @Transactional(propagation = Propagation.REQUIRES_NEW, rollbackFor = Exception.class)
    public void createAuditLog(String operation, String details) {
        AuditLog auditLog = new AuditLog();
        auditLog.setOperation(operation);
        auditLog.setDetails(details);
        auditLog.setTimestamp(LocalDateTime.now());
        
        // 这个操作会在独立的事务中执行
        // 即使调用方法的事务回滚，审计日志也会保存
        auditService.saveAuditLog(auditLog);
    }
    
    /**
     * 事务传播行为示例：MANDATORY
     * 必须在现有事务中执行，否则抛出异常
     */
    @Transactional(propagation = Propagation.MANDATORY)
    public void updateOrderInTransaction(Long orderId, OrderStatus newStatus) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new BusinessException("订单不存在"));
        
        order.setStatus(newStatus);
        orderRepository.save(order);
        
        // 这个方法必须在事务中调用，否则会抛出异常
    }
    
    /**
     * 只读事务示例
     * 用于查询操作，可以优化性能
     */
    @Transactional(readOnly = true, timeout = 30)
    public List<OrderSummary> getOrderSummary(Long userId, int days) {
        LocalDateTime startDate = LocalDateTime.now().minusDays(days);
        
        List<Order> orders = orderRepository.findByUserIdAndOrderDateAfter(userId, startDate);
        
        return orders.stream()
                .map(this::convertToSummary)
                .collect(Collectors.toList());
    }
    
    /**
     * 事务隔离级别示例：READ_COMMITTED
     * 避免脏读，但允许不可重复读
     */
    @Transactional(isolation = Isolation.READ_COMMITTED, rollbackFor = Exception.class)
    public OrderStatistics calculateOrderStatistics(String department) {
        // 查询部门用户
        List<User> users = userRepository.findByDepartment(department);
        
        OrderStatistics stats = new OrderStatistics();
        stats.setDepartment(department);
        stats.setTotalUsers(users.size());
        
        BigDecimal totalAmount = BigDecimal.ZERO;
        int totalOrders = 0;
        
        for (User user : users) {
            List<Order> userOrders = orderRepository.findByUser(user);
            totalOrders += userOrders.size();
            
            for (Order order : userOrders) {
                if (order.getTotalAmount() != null) {
                    totalAmount = totalAmount.add(order.getTotalAmount());
                }
            }
        }
        
        stats.setTotalOrders(totalOrders);
        stats.setTotalAmount(totalAmount);
        stats.setAverageOrderAmount(
            totalOrders > 0 ? totalAmount.divide(BigDecimal.valueOf(totalOrders), 2, BigDecimal.ROUND_HALF_UP) : BigDecimal.ZERO
        );
        
        return stats;
    }
    
    /**
     * 异步事务处理示例
     * 注意：异步方法中的事务是独立的
     */
    public CompletableFuture<Void> processOrderAsync(Long orderId) {
        return CompletableFuture.runAsync(() -> {
            try {
                // 异步处理中需要重新开启事务
                processOrderInNewTransaction(orderId);
            } catch (Exception e) {
                System.err.println("异步订单处理失败: " + e.getMessage());
            }
        });
    }
    
    @Transactional(propagation = Propagation.REQUIRES_NEW, rollbackFor = Exception.class)
    public void processOrderInNewTransaction(Long orderId) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new BusinessException("订单不存在"));
        
        // 模拟长时间处理
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        order.setStatus(OrderStatus.PROCESSING);
        orderRepository.save(order);
        
        createAuditLog("ASYNC_ORDER_PROCESS", "订单 " + orderId + " 异步处理完成");
    }
    
    /**
     * 分布式事务示例（简化版）
     * 涉及多个数据源或外部系统
     */
    @Transactional(rollbackFor = Exception.class)
    public void processDistributedOrder(OrderRequest request) {
        try {
            // 1. 本地数据库操作：创建订单
            Order order = createOrder(request.getUserId(), request.getAmount(), request.getDescription());
            
            // 2. 调用外部支付系统
            ExternalPaymentResult paymentResult = paymentService.processExternalPayment(
                order.getId(), 
                order.getTotalAmount()
            );
            
            if (!paymentResult.isSuccess()) {
                throw new BusinessException("外部支付处理失败: " + paymentResult.getError());
            }
            
            // 3. 调用外部库存系统
            ExternalInventoryResult inventoryResult = inventoryService.reserveItems(
                request.getItems()
            );
            
            if (!inventoryResult.isSuccess()) {
                // 需要补偿事务：回滚支付
                paymentService.refundPayment(paymentResult.getTransactionId());
                throw new BusinessException("库存预留失败: " + inventoryResult.getError());
            }
            
            // 4. 更新订单状态
            order.setStatus(OrderStatus.CONFIRMED);
            order.setExternalPaymentId(paymentResult.getTransactionId());
            order.setExternalInventoryId(inventoryResult.getReservationId());
            orderRepository.save(order);
            
            // 5. 记录分布式事务日志
            auditService.logDistributedTransaction(order.getId(), paymentResult, inventoryResult);
            
        } catch (Exception e) {
            // 分布式事务失败时的补偿逻辑
            System.err.println("分布式事务失败: " + e.getMessage());
            throw new BusinessException("订单处理失败，已回滚相关操作", e);
        }
    }
    
    // 私有辅助方法
    private Order processSingleOrder(Long orderId) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new BusinessException("订单不存在: " + orderId));
        
        order.setStatus(OrderStatus.PROCESSING);
        return orderRepository.save(order);
    }
    
    private OrderSummary convertToSummary(Order order) {
        OrderSummary summary = new OrderSummary();
        summary.setOrderId(order.getId());
        summary.setOrderNumber(order.getOrderNumber());
        summary.setTotalAmount(order.getTotalAmount());
        summary.setStatus(order.getStatus());
        summary.setOrderDate(order.getOrderDate());
        return summary;
    }
}

/**
 * 支持类 - 批量处理结果
 */
class BatchProcessResult {
    private int successCount = 0;
    private int failureCount = 0;
    private List<Order> successfulOrders;
    private List<String> failedOrderMessages;
    
    public void incrementSuccess() { successCount++; }
    public void incrementFailure() { failureCount++; }
    
    // Getter和Setter方法
    public int getSuccessCount() { return successCount; }
    public int getFailureCount() { return failureCount; }
    public List<Order> getSuccessfulOrders() { return successfulOrders; }
    public void setSuccessfulOrders(List<Order> successfulOrders) { this.successfulOrders = successfulOrders; }
    public List<String> getFailedOrderMessages() { return failedOrderMessages; }
    public void setFailedOrderMessages(List<String> failedOrderMessages) { this.failedOrderMessages = failedOrderMessages; }
}

/**
 * 支持类 - 订单统计
 */
class OrderStatistics {
    private String department;
    private int totalUsers;
    private int totalOrders;
    private BigDecimal totalAmount;
    private BigDecimal averageOrderAmount;
    
    // Getter和Setter方法
    public String getDepartment() { return department; }
    public void setDepartment(String department) { this.department = department; }
    
    public int getTotalUsers() { return totalUsers; }
    public void setTotalUsers(int totalUsers) { this.totalUsers = totalUsers; }
    
    public int getTotalOrders() { return totalOrders; }
    public void setTotalOrders(int totalOrders) { this.totalOrders = totalOrders; }
    
    public BigDecimal getTotalAmount() { return totalAmount; }
    public void setTotalAmount(BigDecimal totalAmount) { this.totalAmount = totalAmount; }
    
    public BigDecimal getAverageOrderAmount() { return averageOrderAmount; }
    public void setAverageOrderAmount(BigDecimal averageOrderAmount) { this.averageOrderAmount = averageOrderAmount; }
}

/**
 * 支持类 - 订单摘要
 */
class OrderSummary {
    private Long orderId;
    private String orderNumber;
    private BigDecimal totalAmount;
    private OrderStatus status;
    private LocalDateTime orderDate;
    
    // Getter和Setter方法
    public Long getOrderId() { return orderId; }
    public void setOrderId(Long orderId) { this.orderId = orderId; }
    
    public String getOrderNumber() { return orderNumber; }
    public void setOrderNumber(String orderNumber) { this.orderNumber = orderNumber; }
    
    public BigDecimal getTotalAmount() { return totalAmount; }
    public void setTotalAmount(BigDecimal totalAmount) { this.totalAmount = totalAmount; }
    
    public OrderStatus getStatus() { return status; }
    public void setStatus(OrderStatus status) { this.status = status; }
    
    public LocalDateTime getOrderDate() { return orderDate; }
    public void setOrderDate(LocalDateTime orderDate) { this.orderDate = orderDate; }
}

/**
 * 支持类 - 审计日志
 */
class AuditLog {
    private String operation;
    private String details;
    private LocalDateTime timestamp;
    
    // Getter和Setter方法
    public String getOperation() { return operation; }
    public void setOperation(String operation) { this.operation = operation; }
    
    public String getDetails() { return details; }
    public void setDetails(String details) { this.details = details; }
    
    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
}

/**
 * 支持类 - 订单请求
 */
class OrderRequest {
    private Long userId;
    private BigDecimal amount;
    private String description;
    private List<OrderItem> items;
    
    // Getter和Setter方法
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    
    public BigDecimal getAmount() { return amount; }
    public void setAmount(BigDecimal amount) { this.amount = amount; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    
    public List<OrderItem> getItems() { return items; }
    public void setItems(List<OrderItem> items) { this.items = items; }
}

/**
 * 支持类 - 订单项
 */
class OrderItem {
    private String productId;
    private int quantity;
    private BigDecimal price;
    
    // Getter和Setter方法
    public String getProductId() { return productId; }
    public void setProductId(String productId) { this.productId = productId; }
    
    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }
    
    public BigDecimal getPrice() { return price; }
    public void setPrice(BigDecimal price) { this.price = price; }
}

/**
 * 模拟外部支付结果
 */
class ExternalPaymentResult {
    private boolean success;
    private String transactionId;
    private String error;
    
    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }
    
    public String getTransactionId() { return transactionId; }
    public void setTransactionId(String transactionId) { this.transactionId = transactionId; }
    
    public String getError() { return error; }
    public void setError(String error) { this.error = error; }
}

/**
 * 模拟外部库存结果
 */
class ExternalInventoryResult {
    private boolean success;
    private String reservationId;
    private String error;
    
    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }
    
    public String getReservationId() { return reservationId; }
    public void setReservationId(String reservationId) { this.reservationId = reservationId; }
    
    public String getError() { return error; }
    public void setError(String error) { this.error = error; }
}