package edu.example.qingyuan;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "asset")
public class AssetEntity {
    @Id private String assetId;
    private String assetType;
    private String displayName;
    private String unit;
    private boolean active = true;
    protected AssetEntity() {}
    public AssetEntity(String assetId, String assetType, String displayName, String unit) {
        this.assetId = assetId; this.assetType = assetType; this.displayName = displayName; this.unit = unit;
    }
    public String getAssetId() { return assetId; }
    public String getAssetType() { return assetType; }
    public String getDisplayName() { return displayName; }
    public String getUnit() { return unit; }
    public boolean isActive() { return active; }
}
