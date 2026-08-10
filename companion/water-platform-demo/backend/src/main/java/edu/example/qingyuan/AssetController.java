package edu.example.qingyuan;

import java.time.OffsetDateTime;
import java.util.List;
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
}
