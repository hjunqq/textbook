package edu.example.qingyuan;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface ReadingRepository extends JpaRepository<ReadingEntity, ReadingEntity.ReadingId> {
    /** [from, to)：相邻查询窗口的共同边界只出现在后一个窗口。 */
    @Query("""
            select r from ReadingEntity r where r.id.assetId = :assetId
            and r.id.occurredAt >= :from and r.id.occurredAt < :to
            order by r.id.occurredAt, r.id.version
            """)
    List<ReadingEntity> findInWindow(@Param("assetId") String assetId,
            @Param("from") OffsetDateTime from, @Param("to") OffsetDateTime to);
    boolean existsByEventId(String eventId);

    /** 契约 GET /api/assets/{id}/readings/latest：同一时刻可能有多个版本，取版本号最大的那条。 */
    Optional<ReadingEntity> findFirstByIdAssetIdOrderByIdOccurredAtDescIdVersionDesc(String assetId);
}
