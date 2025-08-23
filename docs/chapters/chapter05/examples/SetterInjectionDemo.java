package com.example.demo.service;

import com.example.demo.datasource.DataSource;
import com.example.demo.service.CacheService;
import com.example.demo.entity.Report;
import com.example.demo.entity.Data;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * Setter方法注入示例
 * 
 * 演示Spring依赖注入的灵活性特性：
 * 1. 可选依赖的处理方式
 * 2. 运行时依赖重配置
 * 3. 部分依赖注入的支持
 * 4. 灵活的初始化顺序
 */
@Service
public class ReportService {
    
    // 必需依赖
    private DataSource primaryDataSource;
    
    // 可选依赖
    private DataSource secondaryDataSource;
    private CacheService cacheService;
    
    /**
     * 必需依赖的setter注入
     * required = true (默认值)
     */
    @Autowired
    public void setPrimaryDataSource(DataSource primaryDataSource) {
        this.primaryDataSource = primaryDataSource;
        System.out.println("Primary data source configured: " + primaryDataSource.getClass().getSimpleName());
    }
    
    /**
     * 可选依赖的setter注入
     * required = false，依赖不存在时不会报错
     */
    @Autowired(required = false)
    public void setSecondaryDataSource(DataSource secondaryDataSource) {
        this.secondaryDataSource = secondaryDataSource;
        if (secondaryDataSource != null) {
            System.out.println("Secondary data source configured: " + secondaryDataSource.getClass().getSimpleName());
        } else {
            System.out.println("No secondary data source available");
        }
    }
    
    /**
     * 可选依赖的setter注入
     * 缓存服务可有可无
     */
    @Autowired(required = false)
    public void setCacheService(CacheService cacheService) {
        this.cacheService = cacheService;
        if (cacheService != null) {
            System.out.println("Cache service configured: " + cacheService.getClass().getSimpleName());
        } else {
            System.out.println("No cache service available");
        }
    }
    
    /**
     * 报告生成主要业务方法
     * 展示如何处理可选依赖
     */
    public Report generateReport(String reportType) {
        System.out.println("Generating report of type: " + reportType);
        
        // 1. 使用主数据源（必需依赖）
        Data primaryData = primaryDataSource.fetchData(reportType);
        System.out.println("Primary data fetched: " + primaryData.getRecordCount() + " records");
        
        // 2. 尝试使用辅助数据源（可选依赖）
        Data secondaryData = null;
        if (secondaryDataSource != null) {
            secondaryData = secondaryDataSource.fetchSupplementaryData(reportType);
            System.out.println("Secondary data fetched: " + secondaryData.getRecordCount() + " records");
        } else {
            System.out.println("Secondary data source not available, using primary data only");
        }
        
        // 3. 创建报告对象
        Report report = new Report(reportType, primaryData, secondaryData);
        report.setGeneratedTime(System.currentTimeMillis());
        
        // 4. 尝试缓存报告（可选依赖）
        if (cacheService != null) {
            String cacheKey = "report_" + reportType + "_" + System.currentTimeMillis();
            cacheService.cache(cacheKey, report);
            System.out.println("Report cached with key: " + cacheKey);
        } else {
            System.out.println("Cache service not available, report not cached");
        }
        
        return report;
    }
    
    /**
     * 批量报告生成
     */
    public java.util.List<Report> generateBatchReports(java.util.List<String> reportTypes) {
        java.util.List<Report> reports = new java.util.ArrayList<>();
        
        for (String reportType : reportTypes) {
            try {
                Report report = generateReport(reportType);
                reports.add(report);
            } catch (Exception e) {
                System.err.println("Failed to generate report: " + reportType + ", error: " + e.getMessage());
            }
        }
        
        return reports;
    }
    
    /**
     * 运行时重新配置依赖（Setter注入的优势）
     */
    public void reconfigureSecondaryDataSource(DataSource newDataSource) {
        this.secondaryDataSource = newDataSource;
        System.out.println("Secondary data source reconfigured at runtime");
    }
    
    /**
     * 获取配置状态
     */
    public ConfigurationStatus getConfigurationStatus() {
        return new ConfigurationStatus(
            primaryDataSource != null,
            secondaryDataSource != null,
            cacheService != null
        );
    }
    
    /**
     * 清理方法 - 在某些情况下需要手动清理可选依赖
     */
    public void cleanup() {
        if (cacheService != null) {
            cacheService.clear();
        }
        System.out.println("ReportService cleanup completed");
    }
}

/**
 * 配置状态类
 */
class ConfigurationStatus {
    private final boolean hasPrimaryDataSource;
    private final boolean hasSecondaryDataSource;
    private final boolean hasCacheService;
    
    public ConfigurationStatus(boolean hasPrimaryDataSource, 
                              boolean hasSecondaryDataSource, 
                              boolean hasCacheService) {
        this.hasPrimaryDataSource = hasPrimaryDataSource;
        this.hasSecondaryDataSource = hasSecondaryDataSource;
        this.hasCacheService = hasCacheService;
    }
    
    // Getter方法
    public boolean hasPrimaryDataSource() { return hasPrimaryDataSource; }
    public boolean hasSecondaryDataSource() { return hasSecondaryDataSource; }
    public boolean hasCacheService() { return hasCacheService; }
    
    @Override
    public String toString() {
        return String.format("ConfigurationStatus{primary=%s, secondary=%s, cache=%s}", 
                           hasPrimaryDataSource, hasSecondaryDataSource, hasCacheService);
    }
}

/**
 * 支持类 - 报告实体
 */
class Report {
    private String reportType;
    private Data primaryData;
    private Data secondaryData;
    private long generatedTime;
    
    public Report(String reportType, Data primaryData, Data secondaryData) {
        this.reportType = reportType;
        this.primaryData = primaryData;
        this.secondaryData = secondaryData;
    }
    
    // Getter和Setter方法
    public String getReportType() { return reportType; }
    public Data getPrimaryData() { return primaryData; }
    public Data getSecondaryData() { return secondaryData; }
    public long getGeneratedTime() { return generatedTime; }
    public void setGeneratedTime(long generatedTime) { this.generatedTime = generatedTime; }
}

/**
 * 支持类 - 数据实体
 */
class Data {
    private int recordCount;
    private String dataType;
    
    public Data(String dataType, int recordCount) {
        this.dataType = dataType;
        this.recordCount = recordCount;
    }
    
    public int getRecordCount() { return recordCount; }
    public String getDataType() { return dataType; }
}