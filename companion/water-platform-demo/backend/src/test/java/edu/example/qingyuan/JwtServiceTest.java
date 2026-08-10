package edu.example.qingyuan;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.JwtException;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.List;
import org.junit.jupiter.api.Test;

class JwtServiceTest {
    private static final String SECRET =
            "cWluZ3l1YW4tdGVhY2hpbmctc2VjcmV0LTAxMjM0NTY3ODlhYmNkZWY=";
    private final Instant now = Instant.parse("2026-08-08T08:00:00Z");

    private JwtService serviceAt(Instant instant) {
        return new JwtService(SECRET, Duration.ofMinutes(30), Clock.fixed(instant, ZoneOffset.UTC));
    }

    @Test
    void issuedTokenRoundTripsSubjectAndAuthorities() {
        JwtService service = serviceAt(now);
        String token = service.issue("duty01", List.of("DUTY"));
        var claims = service.parseAccess(token);
        assertThat(claims.getSubject()).isEqualTo("duty01");
        assertThat(service.authorities(claims)).containsExactly("DUTY");
    }

    @Test
    void expiredTokenIsRejected() {
        String token = serviceAt(now).issue("duty01", List.of("DUTY"));
        JwtService later = serviceAt(now.plus(Duration.ofMinutes(31)));
        assertThatThrownBy(() -> later.parseAccess(token))
                .isInstanceOf(ExpiredJwtException.class);
    }

    @Test
    void tamperedTokenIsRejected() {
        JwtService service = serviceAt(now);
        String token = service.issue("duty01", List.of("DUTY"));
        String tampered = token.substring(0, token.length() - 3) + "abc";
        assertThatThrownBy(() -> service.parseAccess(tampered))
                .isInstanceOf(JwtException.class);
    }
}
