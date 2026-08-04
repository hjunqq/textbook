/**
 * 基础Servlet示例 - 用户管理
 * 
 * 本示例展示了Servlet的基本开发模式，包括：
 * 1. 类声明与注解配置
 * 2. 生命周期方法实现
 * 3. HTTP请求处理
 * 4. 响应数据生成
 */
@WebServlet("/api/users")
public class BasicUserServlet extends HttpServlet {
    
    private UserService userService;
    
    /**
     * 初始化方法 - 容器启动时调用一次
     */
    @Override
    public void init() throws ServletException {
        userService = new UserService();
        System.out.println("用户服务初始化完成");
    }
    
    /**
     * GET请求处理 - 查询用户数据
     */
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        
        // 1. 提取请求参数
        String userId = request.getParameter("userId");
        String page = request.getParameter("page");
        String limit = request.getParameter("limit");
        
        // 2. 参数验证
        if (userId != null && !userId.isEmpty()) {
            // 查询单个用户
            User user = userService.findById(Long.parseLong(userId));
            writeJsonResponse(response, user);
        } else {
            // 分页查询用户列表
            int pageNum = page != null ? Integer.parseInt(page) : 1;
            int pageSize = limit != null ? Integer.parseInt(limit) : 10;
            
            List<User> users = userService.findByPage(pageNum, pageSize);
            writeJsonResponse(response, users);
        }
    }
    
    /**
     * POST请求处理 - 创建新用户
     */
    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        
        // 1. 读取请求体数据
        String jsonData = readRequestBody(request);
        User user = parseJsonToUser(jsonData);
        
        // 2. 数据验证
        ValidationResult validation = validateUser(user);
        if (!validation.isValid()) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            writeJsonResponse(response, validation.getErrors());
            return;
        }
        
        // 3. 保存用户数据
        try {
            User savedUser = userService.save(user);
            response.setStatus(HttpServletResponse.SC_CREATED);
            writeJsonResponse(response, savedUser);
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            writeJsonResponse(response, "服务器内部错误");
        }
    }
    
    /**
     * PUT请求处理 - 更新用户信息
     */
    @Override
    protected void doPut(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        
        String userId = request.getParameter("userId");
        if (userId == null || userId.isEmpty()) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            writeJsonResponse(response, "用户ID不能为空");
            return;
        }
        
        String jsonData = readRequestBody(request);
        User user = parseJsonToUser(jsonData);
        user.setId(Long.parseLong(userId));
        
        User updatedUser = userService.update(user);
        writeJsonResponse(response, updatedUser);
    }
    
    /**
     * DELETE请求处理 - 删除用户
     */
    @Override
    protected void doDelete(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        
        String userId = request.getParameter("userId");
        if (userId == null || userId.isEmpty()) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            writeJsonResponse(response, "用户ID不能为空");
            return;
        }
        
        boolean deleted = userService.deleteById(Long.parseLong(userId));
        if (deleted) {
            response.setStatus(HttpServletResponse.SC_NO_CONTENT);
        } else {
            response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            writeJsonResponse(response, "用户不存在");
        }
    }
    
    /**
     * 销毁方法 - 容器关闭时调用
     */
    @Override
    public void destroy() {
        if (userService != null) {
            userService.close();
        }
        System.out.println("用户服务已关闭");
    }
    
    /**
     * 工具方法：读取请求体数据
     */
    private String readRequestBody(HttpServletRequest request) throws IOException {
        StringBuilder buffer = new StringBuilder();
        try (BufferedReader reader = request.getReader()) {
            String line;
            while ((line = reader.readLine()) != null) {
                buffer.append(line);
            }
        }
        return buffer.toString();
    }
    
    /**
     * 工具方法：写入JSON响应
     */
    private void writeJsonResponse(HttpServletResponse response, Object data) throws IOException {
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");
        
        String json = objectToJson(data);
        response.getWriter().write(json);
    }
    
    /**
     * 工具方法：JSON解析
     */
    private User parseJsonToUser(String json) {
        // 使用JSON库解析（如Jackson、Gson等）
        // 这里仅为示意，实际需要引入JSON处理库
        return new ObjectMapper().readValue(json, User.class);
    }
    
    /**
     * 工具方法：对象转JSON
     */
    private String objectToJson(Object obj) {
        // 使用JSON库序列化
        return new ObjectMapper().writeValueAsString(obj);
    }
    
    /**
     * 工具方法：数据验证
     */
    private ValidationResult validateUser(User user) {
        ValidationResult result = new ValidationResult();
        
        if (user.getUsername() == null || user.getUsername().length() < 3) {
            result.addError("用户名长度不能少于3个字符");
        }
        
        if (user.getEmail() == null || !isValidEmail(user.getEmail())) {
            result.addError("邮箱格式不正确");
        }
        
        return result;
    }
    
    /**
     * 工具方法：邮箱格式验证
     */
    private boolean isValidEmail(String email) {
        return email.contains("@") && email.contains(".");
    }
}

/**
 * 用户实体类
 */
class User {
    private Long id;
    private String username;
    private String email;
    private String phoneNumber;
    private Date createdAt;
    
    // 构造方法、getter和setter省略...
}

/**
 * 用户服务类
 */
class UserService {
    public User findById(Long id) { /* 实现省略 */ }
    public List<User> findByPage(int page, int limit) { /* 实现省略 */ }
    public User save(User user) { /* 实现省略 */ }
    public User update(User user) { /* 实现省略 */ }
    public boolean deleteById(Long id) { /* 实现省略 */ }
    public void close() { /* 实现省略 */ }
}

/**
 * 验证结果类
 */
class ValidationResult {
    private boolean valid = true;
    private List<String> errors = new ArrayList<>();
    
    public void addError(String error) {
        this.valid = false;
        this.errors.add(error);
    }
    
    public boolean isValid() { return valid; }
    public List<String> getErrors() { return errors; }
}