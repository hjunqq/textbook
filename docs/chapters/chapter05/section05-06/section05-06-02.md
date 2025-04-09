# 5.6.2 持续集成与持续部署

## CI/CD概述

持续集成/持续部署(CI/CD)是现代软件开发的核心实践，通过自动化构建、测试和部署流程，提高软件交付的速度和质量。

## 持续集成(CI)

1. **CI核心实践**
   - 频繁提交代码
   - 自动构建
   - 自动测试
   - 代码质量检查
   - 构建产物归档

2. **常用CI工具**
   - Jenkins
   - GitLab CI/CD
   - GitHub Actions
   - Azure DevOps

3. **CI流程示例**
   ```
   代码提交 -> 触发构建 -> 编译代码 -> 运行单元测试
   -> 静态代码分析 -> 打包应用 -> 构建报告
   ```

## 持续部署(CD)

1. **CD核心实践**
   - 环境自动化配置
   - 自动化部署流程
   - 灰度发布/金丝雀发布
   - 自动化回滚机制
   - 部署前后自动化测试

2. **常用CD工具**
   - Spinnaker
   - Argo CD
   - Jenkins X
   - Octopus Deploy

3. **CD流程示例**
   ```
   构建完成 -> 部署测试环境 -> 自动化测试 -> 手动审批
   -> 部署预生产环境 -> 集成测试 -> 手动审批 -> 部署生产环境
   -> 线上巡检 -> 监控告警
   ```

## GitHub Actions CI/CD示例

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up JDK 17
      uses: actions/setup-java@v2
      with:
        java-version: '17'
        distribution: 'adopt'
        
    - name: Build with Maven
      run: mvn -B package --file pom.xml
      
    - name: Run Tests
      run: mvn test
      
    - name: SonarQube Analysis
      run: mvn sonar:sonar -Dsonar.projectKey=water-monitoring -Dsonar.host.url=${{ secrets.SONAR_URL }} -Dsonar.login=${{ secrets.SONAR_TOKEN }}
      
    - name: Build Docker Image
      run: docker build -t waterplatform/monitoring-service:${{ github.sha }} .
      
    - name: Push Docker Image
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push waterplatform/monitoring-service:${{ github.sha }}
        
  deploy-dev:
    needs: build
    runs-on: ubuntu-latest
    environment: development
    
    steps:
    - name: Deploy to Dev Environment
      uses: digitalocean/action-doctl@v2
      with:
        token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
        
    - run: doctl kubernetes cluster kubeconfig save water-platform-dev
    
    - name: Update Deployment
      run: |
        kubectl set image deployment/monitoring-service monitoring-service=waterplatform/monitoring-service:${{ github.sha }} --namespace=dev
        kubectl rollout status deployment/monitoring-service --namespace=dev
        
  deploy-prod:
    needs: deploy-dev
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - name: Deploy to Production
      uses: digitalocean/action-doctl@v2
      with:
        token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
        
    - run: doctl kubernetes cluster kubeconfig save water-platform-prod
    
    - name: Update Deployment
      run: |
        kubectl set image deployment/monitoring-service monitoring-service=waterplatform/monitoring-service:${{ github.sha }} --namespace=prod
        kubectl rollout status deployment/monitoring-service --namespace=prod
```

## 自动化测试

1. **单元测试**
   ```java
   @SpringBootTest
   public class WaterLevelServiceTest {
       
       @MockBean
       private WaterLevelRepository repository;
       
       @Autowired
       private WaterLevelService service;
       
       @Test
       public void testWarningLevelDetection() {
           // 模拟数据
           WaterLevelData data = new WaterLevelData();
           data.setStationId("ST001");
           data.setWaterLevel(105.5);
           data.setMeasurementTime(LocalDateTime.now());
           
           // 模拟站点
           WaterStation station = new WaterStation();
           station.setId("ST001");
           station.setName("测试站点");
           station.setWarningLevel(100.0);
           
           // 设置模拟行为
           when(repository.findLatestByStationId("ST001")).thenReturn(data);
           when(stationRepository.findById("ST001")).thenReturn(Optional.of(station));
           
           // 执行测试
           boolean result = service.isAboveWarningLevel("ST001");
           
           // 验证结果
           assertTrue(result);
           verify(repository, times(1)).findLatestByStationId("ST001");
       }
   }
   ```

2. **集成测试**
   ```java
   @SpringBootTest
   @AutoConfigureMockMvc
   public class WaterLevelControllerTest {
       
       @Autowired
       private MockMvc mockMvc;
       
       @MockBean
       private WaterLevelService service;
       
       @Test
       public void testGetLatestWaterLevel() throws Exception {
           // 模拟服务响应
           WaterLevelDTO dto = new WaterLevelDTO();
           dto.setStationId("ST001");
           dto.setWaterLevel(105.5);
           dto.setMeasurementTime(LocalDateTime.now());
           
           when(service.getLatestWaterLevel("ST001")).thenReturn(dto);
           
           // 执行请求并验证
           mockMvc.perform(get("/api/water-levels/latest")
                   .param("stationId", "ST001")
                   .accept(MediaType.APPLICATION_JSON))
                   .andExpect(status().isOk())
                   .andExpect(jsonPath("$.stationId").value("ST001"))
                   .andExpect(jsonPath("$.waterLevel").value(105.5));
       }
   }
   ``` 