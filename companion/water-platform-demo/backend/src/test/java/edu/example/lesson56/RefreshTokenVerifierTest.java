package edu.example.lesson56;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import io.jsonwebtoken.JwtBuilder;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import java.nio.charset.StandardCharsets;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Date;
import javax.crypto.SecretKey;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;

class RefreshTokenVerifierTest {
    private static final Instant NOW = Instant.parse("2026-07-01T00:00:00Z");
    private static final SecretKey KEY = Keys.hmacShaKeyFor(
            "teaching-only-refresh-key-0123456789".getBytes(StandardCharsets.UTF_8));
    private final RefreshTokenVerifier verifier = new RefreshTokenVerifier(KEY,
            "water-platform-teaching", Clock.fixed(NOW, ZoneOffset.UTC));

    private JwtBuilder claims() {
        return Jwts.builder().setIssuer("water-platform-teaching")
                .setSubject("duty01").setId("refresh-001").claim("type", "refresh")
                .setExpiration(Date.from(NOW.plusSeconds(60)));
    }

    private String sign(JwtBuilder builder) {
        return builder.signWith(KEY, SignatureAlgorithm.HS256).compact();
    }

    @Test
    void acceptsSignedUnexpiredRefreshToken() {
        var parsed = verifier.parse(sign(claims()));
        assertThat(parsed.getSubject()).isEqualTo("duty01");
        assertThat(parsed.getId()).isEqualTo("refresh-001");
    }

    @ParameterizedTest
    @ValueSource(longs = {-1, 0})
    void rejectsExpiredAndExactlyExpiringTokens(long seconds) {
        String token = sign(claims().setExpiration(Date.from(NOW.plusSeconds(seconds))));
        assertThatThrownBy(() -> verifier.parse(token)).isInstanceOf(JwtException.class);
    }

    @Test
    void rejectsMissingExpiration() {
        String token = sign(claims().setExpiration(null));
        assertThatThrownBy(() -> verifier.parse(token)).isInstanceOf(JwtException.class);
    }

    @Test
    void rejectsWrongIssuer() {
        String token = sign(claims().setIssuer("another-issuer"));
        assertThatThrownBy(() -> verifier.parse(token)).isInstanceOf(JwtException.class);
    }

    @Test
    void rejectsAccessTokenUsedAsRefreshToken() {
        String token = sign(claims().claim("type", "access"));
        assertThatThrownBy(() -> verifier.parse(token)).isInstanceOf(JwtException.class);
    }

    @Test
    void rejectsTamperedSignature() {
        String token = sign(claims());
        int signatureStart = token.lastIndexOf('.') + 1;
        char replacement = token.charAt(signatureStart) == 'A' ? 'B' : 'A';
        String tampered = token.substring(0, signatureStart) + replacement + token.substring(signatureStart + 1);
        assertThatThrownBy(() -> verifier.parse(tampered)).isInstanceOf(JwtException.class);
    }

    @Test
    void rejectsUnsignedClaims() {
        String token = claims().compact();
        assertThatThrownBy(() -> verifier.parse(token)).isInstanceOf(JwtException.class);
    }

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = {" "})
    void rejectsBlankSubject(String subject) {
        String token = sign(claims().setSubject(subject));
        assertThatThrownBy(() -> verifier.parse(token)).isInstanceOf(JwtException.class);
    }

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = {" "})
    void rejectsBlankTokenId(String id) {
        String token = sign(claims().setId(id));
        assertThatThrownBy(() -> verifier.parse(token)).isInstanceOf(JwtException.class);
    }
}
