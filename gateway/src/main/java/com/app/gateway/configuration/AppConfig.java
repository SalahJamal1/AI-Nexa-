package com.app.gateway.configuration;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.security.OAuthFlow;
import io.swagger.v3.oas.models.security.OAuthFlows;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.server.mvc.filter.BeforeFilterFunctions;
import org.springframework.cloud.gateway.server.mvc.predicate.GatewayRequestPredicates;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.servlet.function.RouterFunction;
import org.springframework.web.servlet.function.ServerResponse;

import java.util.List;

import static org.springframework.cloud.gateway.server.mvc.handler.GatewayRouterFunctions.route;
import static org.springframework.cloud.gateway.server.mvc.handler.HandlerFunctions.http;

@Configuration
@RequiredArgsConstructor
public class AppConfig {

    @Value("${services.vision-ai.uri:http://localhost:8001}")
    private String visionAiUri;

    @Value("${services.resume-intelligence.uri:http://localhost:8002}")
    private String resumeIntelligenceUri;

    @Value("${services.recruitment.uri:http://localhost:8003}")
    private String recruitmentUri;

    @Value("${keycloak.base-uri:http://127.0.0.1:8080}")
    private String keycloakBaseUri;

    @Bean
    public RouterFunction<ServerResponse> gatewayRouterFunctions() {
        return route("VISION-AI")
                .route(GatewayRequestPredicates.path("/api/v1/vision/**"), http())
                .before(BeforeFilterFunctions.uri(visionAiUri))
                .build()
                .and(route("RESUME-INTELLIGENCE")
                        .route(GatewayRequestPredicates.path("/api/v1/resume/**"), http())
                        .before(BeforeFilterFunctions.uri(resumeIntelligenceUri))
                        .build())
                .and(route("AI Hiring Assistant")
                        .route(GatewayRequestPredicates.path("/api/v1/recruitment/**"), http())
                        .before(BeforeFilterFunctions.uri(recruitmentUri))
                        .build());
    }

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .components(
                        new Components()
                                .addSecuritySchemes(
                                        "keycloak",
                                        new SecurityScheme()
                                                .type(SecurityScheme.Type.OAUTH2)
                                                .flows(
                                                        new OAuthFlows()
                                                                .authorizationCode(
                                                                        new OAuthFlow()
                                                                                .authorizationUrl(
                                                                                        keycloakBaseUri + "/realms/ai-agentic/protocol/openid-connect/auth"
                                                                                )
                                                                                .tokenUrl(
                                                                                        keycloakBaseUri + "/realms/ai-agentic/protocol/openid-connect/token"
                                                                                )
                                                                )
                                                )
                                )
                )
                .addSecurityItem(
                        new SecurityRequirement()
                                .addList("keycloak")
                );
    }

    @Bean
    @Primary
    public CorsConfigurationSource corsConfigurationSource() {
        var configuration = new CorsConfiguration();
        var source = new UrlBasedCorsConfigurationSource();
        configuration.setAllowCredentials(true);
        configuration.setAllowedMethods(List.of("GET", "OPTIONS", "POST", "DELETE", "PATCH", "PUT"));
        configuration.setAllowedOrigins(List.of("http://localhost:3000"));
        configuration.setAllowedHeaders(List.of("*"));
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
