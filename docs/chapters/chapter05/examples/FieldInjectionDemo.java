package com.example.demo.service;

import com.example.demo.service.ProductService;
import com.example.demo.service.InventoryService;
import com.example.demo.service.PaymentService;
import com.example.demo.service.NotificationService;
import com.example.demo.entity.Order;
import com.example.demo.entity.Product;
import com.example.demo.dto.OrderRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * 字段注入示例
 * 
 * 演示字段注入的特点：
 * 1. 代码简洁性 - 无需编写setter或构造函数
 * 2. 局限性分析 - 封装性、测试性、依赖隐藏等问题
 * 3. 实际使用场景和注意事项
 * 4. 与其他注入方式的对比
 * 
 * 注意：虽然字段注入简洁，但Spring官方推荐构造器注入
 */
@Service
public class OrderService {
    
    /**
     * 字段注入 - 直接在字段上使用@Autowired
     * 
     * 优点：
     * - 代码简洁，无需编写额外方法
     * - 快速开发，减少样板代码
     * 
     * 缺点：
     * - 破坏封装性（字段不能为private final）
     * - 依赖关系隐藏，难以理解和维护
     * - 测试困难，需要反射或Spring测试支持
     * - 容易创建循环依赖
     */
    @Autowired
    private ProductService productService;
    
    @Autowired
    private InventoryService inventoryService;
    
    @Autowired
    private PaymentService paymentService;
    
    @Autowired
    private NotificationService notificationService;
    
    // 可选依赖
    @Autowired(required = false)
    private AuditService auditService;
    
    /**
     * 订单处理主业务方法
     * 展示字段注入在业务逻辑中的使用
     */
    public Order processOrder(OrderRequest request) {
        try {
            // 1. 获取产品信息
            Product product = productService.getProduct(request.getProductId());
            if (product == null) {
                throw new IllegalArgumentException("Product not found: " + request.getProductId());
            }
            
            // 2. 检查库存并预留
            boolean stockReserved = inventoryService.reserveStock(product, request.getQuantity());
            if (!stockReserved) {
                throw new IllegalStateException("Insufficient stock for product: " + product.getName());
            }
            
            // 3. 处理支付
            boolean paymentProcessed = paymentService.processPayment(request.getPaymentInfo());
            if (!paymentProcessed) {
                // 支付失败，释放库存
                inventoryService.releaseStock(product, request.getQuantity());
                throw new IllegalStateException("Payment processing failed");
            }
            
            // 4. 创建订单
            Order order = new Order();
            order.setProductId(product.getId());
            order.setProductName(product.getName());
            order.setQuantity(request.getQuantity());
            order.setUnitPrice(product.getPrice());
            order.setTotalAmount(product.getPrice().multiply(new java.math.BigDecimal(request.getQuantity())));
            order.setCustomerId(request.getCustomerId());
            order.setOrderTime(System.currentTimeMillis());
            order.setStatus("CONFIRMED");
            
            // 5. 发送确认通知
            notificationService.sendOrderConfirmation(order);
            
            // 6. 审计日志（可选依赖）
            if (auditService != null) {
                auditService.logOrderCreation(order);
            }
            
            return order;
            
        } catch (Exception e) {
            // 异常处理和日志记录
            System.err.println("Order processing failed: " + e.getMessage());
            
            // 可选的审计记录
            if (auditService != null) {
                auditService.logOrderFailure(request, e.getMessage());
            }
            
            throw e;
        }
    }
    
    /**
     * 批量订单处理
     */
    public java.util.List<Order> processBatchOrders(java.util.List<OrderRequest> requests) {
        java.util.List<Order> successfulOrders = new java.util.ArrayList<>();
        java.util.List<String> failedOrders = new java.util.ArrayList<>();
        
        for (OrderRequest request : requests) {
            try {
                Order order = processOrder(request);
                successfulOrders.add(order);
            } catch (Exception e) {
                failedOrders.add("Order for product " + request.getProductId() + 
                               " failed: " + e.getMessage());
            }
        }
        
        // 记录批量处理结果
        System.out.println("Batch processing completed. Success: " + successfulOrders.size() + 
                          ", Failed: " + failedOrders.size());
        
        if (!failedOrders.isEmpty()) {
            failedOrders.forEach(System.err::println);
        }
        
        return successfulOrders;
    }
    
    /**
     * 取消订单
     */
    public boolean cancelOrder(String orderId) {
        try {
            // 这里简化处理，实际应用中需要更复杂的逻辑
            System.out.println("Cancelling order: " + orderId);
            
            // 发送取消通知
            notificationService.sendOrderCancellation(orderId);
            
            // 审计日志
            if (auditService != null) {
                auditService.logOrderCancellation(orderId);
            }
            
            return true;
        } catch (Exception e) {
            System.err.println("Order cancellation failed: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * 获取订单统计信息
     */
    public OrderStatistics getOrderStatistics() {
        // 使用注入的服务获取统计数据
        int totalProducts = productService.getTotalProductCount();
        int availableStock = inventoryService.getTotalAvailableStock();
        
        return new OrderStatistics(totalProducts, availableStock);
    }
    
    /**
     * 服务健康检查
     * 展示如何检查注入的依赖是否正常工作
     */
    public ServiceHealthStatus checkServiceHealth() {
        ServiceHealthStatus status = new ServiceHealthStatus();
        
        try {
            // 检查各个服务的健康状态
            status.setProductServiceHealthy(productService.healthCheck());
            status.setInventoryServiceHealthy(inventoryService.healthCheck());
            status.setPaymentServiceHealthy(paymentService.healthCheck());
            status.setNotificationServiceHealthy(notificationService.healthCheck());
            
            // 检查可选服务
            if (auditService != null) {
                status.setAuditServiceAvailable(true);
                status.setAuditServiceHealthy(auditService.healthCheck());
            } else {
                status.setAuditServiceAvailable(false);
                status.setAuditServiceHealthy(false);
            }
            
        } catch (Exception e) {
            System.err.println("Health check failed: " + e.getMessage());
            status.setOverallHealthy(false);
        }
        
        return status;
    }
}

/**
 * 支持类 - 审计服务接口
 */
interface AuditService {
    void logOrderCreation(Order order);
    void logOrderFailure(OrderRequest request, String errorMessage);
    void logOrderCancellation(String orderId);
    boolean healthCheck();
}

/**
 * 支持类 - 订单统计信息
 */
class OrderStatistics {
    private final int totalProducts;
    private final int availableStock;
    
    public OrderStatistics(int totalProducts, int availableStock) {
        this.totalProducts = totalProducts;
        this.availableStock = availableStock;
    }
    
    public int getTotalProducts() { return totalProducts; }
    public int getAvailableStock() { return availableStock; }
}

/**
 * 支持类 - 服务健康状态
 */
class ServiceHealthStatus {
    private boolean productServiceHealthy;
    private boolean inventoryServiceHealthy;
    private boolean paymentServiceHealthy;
    private boolean notificationServiceHealthy;
    private boolean auditServiceAvailable;
    private boolean auditServiceHealthy;
    private boolean overallHealthy = true;
    
    // Getter和Setter方法
    public boolean isProductServiceHealthy() { return productServiceHealthy; }
    public void setProductServiceHealthy(boolean productServiceHealthy) { this.productServiceHealthy = productServiceHealthy; }
    
    public boolean isInventoryServiceHealthy() { return inventoryServiceHealthy; }
    public void setInventoryServiceHealthy(boolean inventoryServiceHealthy) { this.inventoryServiceHealthy = inventoryServiceHealthy; }
    
    public boolean isPaymentServiceHealthy() { return paymentServiceHealthy; }
    public void setPaymentServiceHealthy(boolean paymentServiceHealthy) { this.paymentServiceHealthy = paymentServiceHealthy; }
    
    public boolean isNotificationServiceHealthy() { return notificationServiceHealthy; }
    public void setNotificationServiceHealthy(boolean notificationServiceHealthy) { this.notificationServiceHealthy = notificationServiceHealthy; }
    
    public boolean isAuditServiceAvailable() { return auditServiceAvailable; }
    public void setAuditServiceAvailable(boolean auditServiceAvailable) { this.auditServiceAvailable = auditServiceAvailable; }
    
    public boolean isAuditServiceHealthy() { return auditServiceHealthy; }
    public void setAuditServiceHealthy(boolean auditServiceHealthy) { this.auditServiceHealthy = auditServiceHealthy; }
    
    public boolean isOverallHealthy() { return overallHealthy; }
    public void setOverallHealthy(boolean overallHealthy) { this.overallHealthy = overallHealthy; }
}

/**
 * 支持类 - 订单请求
 */
class OrderRequest {
    private String productId;
    private int quantity;
    private String customerId;
    private PaymentInfo paymentInfo;
    
    // 构造函数和Getter/Setter方法
    public String getProductId() { return productId; }
    public void setProductId(String productId) { this.productId = productId; }
    
    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }
    
    public String getCustomerId() { return customerId; }
    public void setCustomerId(String customerId) { this.customerId = customerId; }
    
    public PaymentInfo getPaymentInfo() { return paymentInfo; }
    public void setPaymentInfo(PaymentInfo paymentInfo) { this.paymentInfo = paymentInfo; }
}

/**
 * 支持类 - 支付信息
 */
class PaymentInfo {
    private String paymentMethod;
    private String cardNumber;
    private java.math.BigDecimal amount;
    
    // Getter和Setter方法
    public String getPaymentMethod() { return paymentMethod; }
    public void setPaymentMethod(String paymentMethod) { this.paymentMethod = paymentMethod; }
    
    public String getCardNumber() { return cardNumber; }
    public void setCardNumber(String cardNumber) { this.cardNumber = cardNumber; }
    
    public java.math.BigDecimal getAmount() { return amount; }
    public void setAmount(java.math.BigDecimal amount) { this.amount = amount; }
}