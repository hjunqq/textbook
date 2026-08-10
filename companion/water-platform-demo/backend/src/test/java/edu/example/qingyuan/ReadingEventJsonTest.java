package edu.example.qingyuan;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import java.time.OffsetDateTime;
import org.junit.jupiter.api.Test;

/** 事件契约测试：字段名与类型一旦漂移，消费者会在这里先失败。 */
class ReadingEventJsonTest {
    private final ObjectMapper mapper = new ObjectMapper().registerModule(new JavaTimeModule());

    @Test
    void deserializesContractPayload() throws Exception {
        String json = """
                {"eventId":"EV-1001","assetId":"DAM-A-PZ-07",
                 "occurredAt":"2026-08-08T08:00:00+08:00","version":1,
                 "value":118.6,"unit":"kPa","quality":"valid","source":"gateway-01"}""";
        ReadingEvent event = mapper.readValue(json, ReadingEvent.class);
        assertThat(event.eventId()).isEqualTo("EV-1001");
        assertThat(event.assetId()).isEqualTo("DAM-A-PZ-07");
        assertThat(event.occurredAt()).isEqualTo(OffsetDateTime.parse("2026-08-08T08:00:00+08:00"));
        assertThat(event.quality()).isEqualTo("valid");
    }

    @Test
    void missingValueMapsToNullForMissingQuality() throws Exception {
        String json = """
                {"eventId":"EV-1002","assetId":"DAM-A-PZ-07",
                 "occurredAt":"2026-08-08T08:05:00+08:00","version":1,
                 "value":null,"unit":"kPa","quality":"missing","source":"gateway-01"}""";
        ReadingEvent event = mapper.readValue(json, ReadingEvent.class);
        assertThat(event.value()).isNull();
        assertThat(event.quality()).isEqualTo("missing");
    }
}
