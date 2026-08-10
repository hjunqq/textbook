package edu.example.qingyuan;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.Date;
import java.util.List;

/** HS256 访问令牌的签发与校验（jjwt 0.11.x），与第5章口径一致。 */
public class JwtService {
    public static final String ISSUER = "qingyuan-teaching";
    private final javax.crypto.SecretKey key;
    private final Duration accessTtl;
    private final Clock clock;

    public JwtService(String base64Secret, Duration accessTtl, Clock clock) {
        this.key = Keys.hmacShaKeyFor(Decoders.BASE64.decode(base64Secret));
        this.accessTtl = accessTtl;
        this.clock = clock;
    }

    public String issue(String subject, List<String> authorities) {
        Instant now = clock.instant();
        return Jwts.builder()
                .setIssuer(ISSUER)
                .setSubject(subject)
                .claim("type", "access")
                .claim("authorities", authorities)
                .setIssuedAt(Date.from(now))
                .setExpiration(Date.from(now.plus(accessTtl)))
                .signWith(key, SignatureAlgorithm.HS256)
                .compact();
    }

    /** 签名、签发者、类型任一不符即抛 JwtException；过期由 jjwt 抛 ExpiredJwtException。 */
    public Claims parseAccess(String token) {
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(key)
                .requireIssuer(ISSUER)
                .setClock(() -> Date.from(clock.instant()))
                .build()
                .parseClaimsJws(token)
                .getBody();
        if (!"access".equals(claims.get("type", String.class)))
            throw new JwtException("token type is not access");
        return claims;
    }

    @SuppressWarnings("unchecked")
    public List<String> authorities(Claims claims) {
        return (List<String>) claims.get("authorities", List.class);
    }
}
