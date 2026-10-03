package edu.example.reservoir;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AssetRepository extends JpaRepository<AssetEntity, String> {
    List<AssetEntity> findByActiveTrueOrderByAssetId();
}
