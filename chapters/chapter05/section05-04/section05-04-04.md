# 5.4.4 RESTful API开发

## Controller层开发

**基本Controller**：
```java
package com.waterplatform.controller;

import com.waterplatform.dto.StationDTO;
import com.waterplatform.service.StationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/stations")
public class StationController {
    
    @Autowired
    private StationService stationService;
    
    @GetMapping
    public ResponseEntity<List<StationDTO>> getAllStations() {
        return ResponseEntity.ok(stationService.findAllStations());
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<StationDTO> getStationById(@PathVariable String id) {
        return stationService.findStationById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
    
    @PostMapping
    public ResponseEntity<StationDTO> createStation(@RequestBody StationDTO stationDTO) {
        return ResponseEntity.ok(stationService.createStation(stationDTO));
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<StationDTO> updateStation(
            @PathVariable String id, 
            @RequestBody StationDTO stationDTO) {
        return ResponseEntity.ok(stationService.updateStation(id, stationDTO));
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteStation(@PathVariable String id) {
        stationService.deleteStation(id);
        return ResponseEntity.noContent().build();
    }
}
```

## 数据访问层

**Entity类**：
```java
package com.waterplatform.entity;

import javax.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "water_level_data")
public class WaterLevelData {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "station_id", nullable = false)
    private String stationId;
    
    @Column(name = "water_level", nullable = false)
    private Double waterLevel;
    
    @Column(name = "measurement_time", nullable = false)
    private LocalDateTime measurementTime;
    
    @Column(name = "warning_level")
    private Boolean warningLevel;
    
    // 构造函数、getter、setter省略
}
```

**Repository接口**：
```java
package com.waterplatform.repository;

import com.waterplatform.entity.WaterLevelData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface WaterLevelRepository extends JpaRepository<WaterLevelData, Long> {
    
    List<WaterLevelData> findByStationIdOrderByMeasurementTimeDesc(String stationId);
    
    @Query("SELECT w FROM WaterLevelData w WHERE w.stationId = ?1 AND " +
           "w.measurementTime BETWEEN ?2 AND ?3 ORDER BY w.measurementTime")
    List<WaterLevelData> findByStationIdAndTimePeriod(
            String stationId, LocalDateTime startTime, LocalDateTime endTime);
    
    @Query("SELECT MAX(w.waterLevel) FROM WaterLevelData w WHERE " +
           "w.stationId = ?1 AND w.measurementTime BETWEEN ?2 AND ?3")
    Double findMaxWaterLevelInPeriod(
            String stationId, LocalDateTime startTime, LocalDateTime endTime);
}
```

## 服务层

**Service接口**：
```java
package com.waterplatform.service;

import com.waterplatform.dto.WaterLevelDTO;
import java.time.LocalDateTime;
import java.util.List;

public interface WaterLevelService {
    
    List<WaterLevelDTO> getRecentWaterLevels(String stationId, int limit);
    
    List<WaterLevelDTO> getWaterLevelsByPeriod(
            String stationId, LocalDateTime startTime, LocalDateTime endTime);
    
    WaterLevelDTO recordWaterLevel(WaterLevelDTO waterLevelDTO);
    
    boolean checkWarningLevel(String stationId);
}
```

**Service实现**：
```java
package com.waterplatform.service.impl;

import com.waterplatform.dto.WaterLevelDTO;
import com.waterplatform.entity.WaterLevelData;
import com.waterplatform.entity.WaterStation;
import com.waterplatform.repository.WaterLevelRepository;
import com.waterplatform.repository.WaterStationRepository;
import com.waterplatform.service.WaterLevelService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class WaterLevelServiceImpl implements WaterLevelService {
    
    @Autowired
    private WaterLevelRepository waterLevelRepository;
    
    @Autowired
    private WaterStationRepository stationRepository;
    
    @Override
    public List<WaterLevelDTO> getRecentWaterLevels(String stationId, int limit) {
        return waterLevelRepository.findByStationIdOrderByMeasurementTimeDesc(stationId)
                .stream()
                .limit(limit)
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    @Override
    public List<WaterLevelDTO> getWaterLevelsByPeriod(
            String stationId, LocalDateTime startTime, LocalDateTime endTime) {
        return waterLevelRepository.findByStationIdAndTimePeriod(stationId, startTime, endTime)
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    @Override
    public WaterLevelDTO recordWaterLevel(WaterLevelDTO dto) {
        WaterLevelData entity = convertToEntity(dto);
        
        // 检查是否超过警戒水位
        WaterStation station = stationRepository.findById(dto.getStationId())
                .orElseThrow(() -> new RuntimeException("水文站不存在"));
        
        if (dto.getWaterLevel() >= station.getWarningLevel()) {
            entity.setWarningLevel(true);
        } else {
            entity.setWarningLevel(false);
        }
        
        WaterLevelData saved = waterLevelRepository.save(entity);
        return convertToDTO(saved);
    }
    
    @Override
    public boolean checkWarningLevel(String stationId) {
        // 获取最新水位记录
        List<WaterLevelData> recentData = 
                waterLevelRepository.findByStationIdOrderByMeasurementTimeDesc(stationId);
        
        if (recentData.isEmpty()) {
            return false;
        }
        
        // 检查最新记录是否超过警戒水位
        return recentData.get(0).getWarningLevel();
    }
    
    // DTO转换方法
    private WaterLevelDTO convertToDTO(WaterLevelData entity) {
        WaterLevelDTO dto = new WaterLevelDTO();
        dto.setId(entity.getId());
        dto.setStationId(entity.getStationId());
        dto.setWaterLevel(entity.getWaterLevel());
        dto.setMeasurementTime(entity.getMeasurementTime());
        dto.setWarningLevel(entity.getWarningLevel());
        return dto;
    }
    
    private WaterLevelData convertToEntity(WaterLevelDTO dto) {
        WaterLevelData entity = new WaterLevelData();
        entity.setStationId(dto.getStationId());
        entity.setWaterLevel(dto.getWaterLevel());
        entity.setMeasurementTime(dto.getMeasurementTime());
        entity.setWarningLevel(dto.getWarningLevel());
        return entity;
    }
}
```

## 异常处理

**全局异常处理器**：
```java
package com.waterplatform.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import javax.validation.ConstraintViolationException;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleResourceNotFound(ResourceNotFoundException ex) {
        ErrorResponse error = new ErrorResponse(
                HttpStatus.NOT_FOUND.value(),
                ex.getMessage(),
                LocalDateTime.now()
        );
        return new ResponseEntity<>(error, HttpStatus.NOT_FOUND);
    }
    
    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<ErrorResponse> handleValidationExceptions(ConstraintViolationException ex) {
        Map<String, String> errors = new HashMap<>();
        ex.getConstraintViolations().forEach(violation -> {
            String fieldName = violation.getPropertyPath().toString();
            String errorMessage = violation.getMessage();
            errors.put(fieldName, errorMessage);
        });
        
        ErrorResponse error = new ErrorResponse(
                HttpStatus.BAD_REQUEST.value(),
                "输入数据验证失败",
                LocalDateTime.now(),
                errors
        );
        
        return new ResponseEntity<>(error, HttpStatus.BAD_REQUEST);
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneralException(Exception ex) {
        ErrorResponse error = new ErrorResponse(
                HttpStatus.INTERNAL_SERVER_ERROR.value(),
                "服务器内部错误",
                LocalDateTime.now()
        );
        return new ResponseEntity<>(error, HttpStatus.INTERNAL_SERVER_ERROR);
    }
}
```

## 数据校验

**使用Bean Validation**：
```java
package com.waterplatform.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.PastOrPresent;
import javax.validation.constraints.PositiveOrZero;
import java.time.LocalDateTime;

@Data
public class WaterLevelDTO {
    
    private Long id;
    
    @NotBlank(message = "站点ID不能为空")
    private String stationId;
    
    @NotNull(message = "水位值不能为空")
    @PositiveOrZero(message = "水位值不能为负数")
    private Double waterLevel;
    
    @NotNull(message = "测量时间不能为空")
    @PastOrPresent(message = "测量时间不能在未来")
    private LocalDateTime measurementTime;
    
    private Boolean warningLevel;
}
```

**在Controller中启用验证**：
```java
@PostMapping
public ResponseEntity<WaterLevelDTO> recordWaterLevel(
        @Valid @RequestBody WaterLevelDTO waterLevelDTO) {
    return ResponseEntity.ok(waterLevelService.recordWaterLevel(waterLevelDTO));
}
``` 