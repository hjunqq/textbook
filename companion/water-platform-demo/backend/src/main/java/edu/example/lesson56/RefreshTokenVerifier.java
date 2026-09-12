package edu.example.lesson56;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import java.time.Clock;
import java.time.Instant;
import java.util.Date;
import java.util.Objects;
import javax.crypto.SecretKey;

/** jjwt 0.11.x：只验证刷新令牌，轮换与撤销记录由调用方在事务中处理。 */
public final class RefreshTokenVerifier {
    private final SecretKey key;
    private final String issuer;
    private final Clock clock;

    public RefreshTokenVerifier(SecretKey key, String issuer, Clock clock) {
        this.key = Objects.requireNonNull(key);
        if (issuer == null || issuer.isBlank()) throw new IllegalArgumentException("issuer is required");
        this.issuer = issuer;
        this.clock = Objects.requireNonNull(clock);
    }

    public Claims parse(String token) {
        Instant now = clock.instant();
        Claims claims = Jwts.parserBuilder().setSigningKey(key)
                .requireIssuer(issuer).require("type", "refresh")
                .setClock(() -> Date.from(now)).build()
                .parseClaimsJws(token).getBody();
        Date expiry = claims.getExpiration();
        if (expiry == null || !expiry.toInstant().isAfter(now))
            throw new JwtException("refresh token must have a future expiration");
        if (claims.getSubject() == null || claims.getSubject().isBlank())
            throw new JwtException("refresh token subject is required");
        if (claims.getId() == null || claims.getId().isBlank())
            throw new JwtException("refresh token jti is required");
        return claims;
    }
}
