package edu.example.qingyuan;

import java.time.OffsetDateTime;
import java.util.List;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/assets")
public class AssetController {
    public record Asset(String assetId, String displayName, String assetType, String unit) {}
    public record Reading(String assetId, OffsetDateTime occurredAt, Double value, String unit, String quality, String eventId, int version) {}

    @GetMapping
    @PreAuthorize("hasAnyAuthority('DUTY','ANALYST','OPS')")
    public List<Asset> assets() { return List.of(new Asset("DAM-A-PZ-07", "清源渗压07", "渗压", "kPa")); }

    @GetMapping("/{assetId}/readings")
    @PreAuthorize("hasAnyAuthority('DUTY','ANALYST','OPS')")
    public List<Reading> readings(@PathVariable String assetId, @RequestParam OffsetDateTime from, @RequestParam OffsetDateTime to, @RequestParam(defaultValue = "5m") String agg) {
        return List.of(); // Replace with the ReadingRepository query from Chapter 8.
    }
}
