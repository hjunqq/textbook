package edu.example.qingyuan;

import static org.assertj.core.api.Assertions.assertThat;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.context.annotation.Import;

/** 在内存测试库执行真实 JPA 查询；不连接或修改工程数据库。 */
@DataJpaTest(showSql = false, properties = {
        "spring.datasource.url=jdbc:h2:mem:reading-window;MODE=PostgreSQL;NON_KEYWORDS=VALUE",
        "spring.datasource.driver-class-name=org.h2.Driver",
        "spring.jpa.hibernate.ddl-auto=create-drop"
})
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import(ReadingService.class)
class ReadingWindowTest {
    @Autowired ReadingRepository repository;
    @Autowired ReadingService service;

    private final OffsetDateTime start = OffsetDateTime.parse("2026-07-01T08:00:00+08:00");

    @BeforeEach
    void seed() {
        add("DAM-A-PZ-07", start.minusHours(1), "before");
        add("DAM-A-PZ-07", start, "start");
        add("DAM-A-PZ-07", start.plusMinutes(30), "inside");
        add("DAM-A-PZ-07", start.plusHours(1), "boundary");
        add("DAM-A-PZ-07", start.plusHours(2), "end");
        add("DAM-A-PZ-08", start, "other-asset");
        repository.flush();
    }

    @Test
    void includesFromExcludesToAndFiltersTheAsset() {
        assertThat(service.find("DAM-A-PZ-07", start, start.plusHours(1)))
                .extracting(ReadingEntity::getEventId).containsExactly("start", "inside");
    }

    @Test
    void adjacentWindowsDoNotRepeatTheirSharedBoundary() {
        var first = service.find("DAM-A-PZ-07", start, start.plusHours(1));
        var second = service.find("DAM-A-PZ-07", start.plusHours(1), start.plusHours(2));
        assertThat(second).extracting(ReadingEntity::getEventId).containsExactly("boundary");
        assertThat(first).extracting(ReadingEntity::getEventId).doesNotContain("boundary");
    }

    @Test
    void utcAndOffsetQueriesSelectTheSameInstants() {
        assertThat(service.find("DAM-A-PZ-07", OffsetDateTime.parse("2026-07-01T00:00:00Z"),
                OffsetDateTime.parse("2026-07-01T01:00:00Z")))
                .extracting(ReadingEntity::getEventId).containsExactly("start", "inside");
    }

    private void add(String assetId, OffsetDateTime time, String eventId) {
        repository.save(new ReadingEntity(new ReadingEntity.ReadingId(assetId, time, 1),
                eventId, new BigDecimal("180.0"), "kPa", "valid", "test"));
    }
}
