package com.example.demo.service;

import com.example.demo.repository.UserRepository;
import com.example.demo.service.EmailService;
import com.example.demo.service.ValidationService;
import com.example.demo.entity.User;
import com.example.demo.dto.UserDto;
import org.springframework.stereotype.Service;

import java.util.Objects;

/**
 * 构造器注入示例
 * 
 * 演示Spring依赖注入的最佳实践：
 * 1. 构造器注入的强制性和不可变性
 * 2. 依赖验证机制
 * 3. final字段保证线程安全
 * 4. 清晰的依赖关系声明
 */
@Service
public class UserService {
    
    // 必需依赖声明为final，确保不可变性
    private final UserRepository userRepository;
    private final EmailService emailService;
    private final ValidationService validationService;
    
    /**
     * 构造器注入 - Spring推荐方式
     * 
     * 优势：
     * - 强制性：缺少依赖时对象无法创建
     * - 不可变性：依赖可以声明为final
     * - 线程安全：不可变对象天然线程安全
     * - 依赖验证：可在构造函数中验证依赖
     */
    public UserService(UserRepository userRepository, 
                      EmailService emailService,
                      ValidationService validationService) {
        // 依赖验证 - 确保关键依赖不为null
        Objects.requireNonNull(userRepository, "UserRepository cannot be null");
        Objects.requireNonNull(emailService, "EmailService cannot be null");
        Objects.requireNonNull(validationService, "ValidationService cannot be null");
        
        this.userRepository = userRepository;
        this.emailService = emailService;
        this.validationService = validationService;
    }
    
    /**
     * 业务方法示例 - 创建用户
     */
    public User createUser(UserDto userDto) {
        // 1. 使用注入的验证服务
        validationService.validate(userDto);
        
        // 2. 创建用户实体
        User user = new User();
        user.setUsername(userDto.getUsername());
        user.setEmail(userDto.getEmail());
        user.setPhoneNumber(userDto.getPhoneNumber());
        
        // 3. 使用注入的数据访问服务
        User savedUser = userRepository.save(user);
        
        // 4. 使用注入的邮件服务
        emailService.sendWelcomeEmail(savedUser);
        
        return savedUser;
    }
    
    /**
     * 批量操作示例
     */
    public void createUsers(java.util.List<UserDto> userDtos) {
        for (UserDto dto : userDtos) {
            try {
                createUser(dto);
            } catch (Exception e) {
                // 记录错误，继续处理其他用户
                System.err.println("Failed to create user: " + dto.getUsername() + ", error: " + e.getMessage());
            }
        }
    }
    
    /**
     * 查询方法示例
     */
    public User findUserById(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("User not found: " + id));
    }
    
    /**
     * 更新方法示例
     */
    public User updateUser(Long id, UserDto userDto) {
        // 验证输入
        validationService.validate(userDto);
        
        // 查找现有用户
        User existingUser = findUserById(id);
        
        // 更新字段
        existingUser.setUsername(userDto.getUsername());
        existingUser.setEmail(userDto.getEmail());
        existingUser.setPhoneNumber(userDto.getPhoneNumber());
        
        // 保存更新
        return userRepository.save(existingUser);
    }
    
    /**
     * 删除方法示例
     */
    public boolean deleteUser(Long id) {
        if (userRepository.existsById(id)) {
            userRepository.deleteById(id);
            return true;
        }
        return false;
    }
}

/**
 * 支持类 - 用户数据传输对象
 */
class UserDto {
    private String username;
    private String email;
    private String phoneNumber;
    
    // 构造函数
    public UserDto(String username, String email, String phoneNumber) {
        this.username = username;
        this.email = email;
        this.phoneNumber = phoneNumber;
    }
    
    // Getter和Setter方法
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    
    public String getPhoneNumber() { return phoneNumber; }
    public void setPhoneNumber(String phoneNumber) { this.phoneNumber = phoneNumber; }
}