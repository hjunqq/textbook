package edu.example.qingyuan;

import jakarta.validation.constraints.NotBlank;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    public record LoginRequest(@NotBlank String username, @NotBlank String password) {}
    public record LoginResponse(String accessToken, long expiresInSeconds, List<String> authorities) {}

    private final UserDetailsService users;
    private final PasswordEncoder encoder;
    private final JwtService jwtService;

    public AuthController(UserDetailsService users, PasswordEncoder encoder, JwtService jwtService) {
        this.users = users; this.encoder = encoder; this.jwtService = jwtService;
    }

    /** 登录失败统一返回 401 与固定文案，不区分账号不存在与口令错误，避免账号枚举。 */
    @PostMapping("/login")
    public LoginResponse login(@RequestBody LoginRequest request) {
        UserDetails user;
        try {
            user = users.loadUserByUsername(request.username());
        } catch (UsernameNotFoundException notFound) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "用户名或密码错误");
        }
        if (!encoder.matches(request.password(), user.getPassword()))
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "用户名或密码错误");
        List<String> authorities = user.getAuthorities().stream()
                .map(a -> a.getAuthority()).toList();
        return new LoginResponse(jwtService.issue(user.getUsername(), authorities), 1800, authorities);
    }
}
