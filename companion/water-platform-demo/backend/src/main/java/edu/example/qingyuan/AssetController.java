package edu.example.qingyuan;

import java.time.OffsetDateTime;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/assets")
public class AssetController {
    public record AssetDto(String assetId, String displayName, String assetType, String unit) {
        static AssetDto from(AssetEntity e) {
            return new AssetDto(e.getAssetId(), e.getDisplayName(), e.getAssetType(), e.getUnit());
        }
    }
    public record ReadingDto(String assetId, OffsetDateTime occurredAt, Double value,
                             String unit, String quality, String eventId, int version) {
        static ReadingDto from(ReadingEntity e) {
            return new ReadingDto(e.getId().assetId(), e.getId().occurredAt(), e.getValue(),
                    e.getUnit(), e.getQuality(), e.getEventId(), e.getId().version());
        }
    }

    private final AssetRepository assets;
    private final ReadingService readings;

    public AssetController(AssetRepository assets, ReadingService readings) {
        this.assets = assets; this.readings = readings;
    }

    @GetMapping
    @PreAuthorize("hasAnyAuthority('DUTY','ANALYST','OPS')")
    public List<AssetDto> assets() {
        return assets.findByActiveTrueOrderByAssetId().stream().map(AssetDto::from).toList();
    }

    @GetMapping("/{assetId}/readings")
    @PreAuthorize("hasAnyAuthority('DUTY','ANALYST','OPS')")
    public List<ReadingDto> readings(@PathVariable String assetId,
                                     @RequestParam OffsetDateTime from,
                                     @RequestParam OffsetDateTime to) {
        return readings.find(assetId, from, to).stream().map(ReadingDto::from).toList();
    }

    /**
     * 契约 GET /api/assets/{id}/readings/latest（8.1 节 tab:api-contract）。
     * 对象不存在 404，对象存在但没有观测 204——两者必须分开，
     * 否则第4章的页面无法区分“编码打错了”和“这个测点还没上报”。
     */
    @GetMapping("/{assetId}/readings/latest")
    @PreAuthorize("hasAnyAuthority('DUTY','ANALYST','OPS')")
    public ResponseEntity<ReadingDto> latest(@PathVariable String assetId) {
        if (!assets.existsById(assetId)) {
            throw new AssetNotFoundException(assetId);
        }
        return readings.latest(assetId)
                .map(ReadingDto::from)
                .map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.noContent().build());
    }

    /** 由全局异常处理翻译成契约错误体 {code:"ASSET_NOT_FOUND", message}。 */
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public static class AssetNotFoundException extends RuntimeException {
        public AssetNotFoundException(String assetId) { super("对象 " + assetId + " 不存在"); }
    }
}
