package com.app.gateway.exception;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.AuthenticationException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.servlet.resource.NoResourceFoundException;

import java.time.LocalDateTime;

@Slf4j
@ControllerAdvice
public class HandelException {

    @ExceptionHandler(NoResourceFoundException.class)
    public ResponseEntity<ErrorDetails> handleNoResourceFound(NoResourceFoundException ex) {
        log.warn("Route not found: {}", ex.getMessage());
        return buildResponse(HttpStatus.NOT_FOUND, "No route found for this request");
    }

    @ExceptionHandler(HttpClientErrorException.class)
    public ResponseEntity<ErrorDetails> handleDownstreamClientError(HttpClientErrorException ex) {
        var status = HttpStatus.valueOf(ex.getStatusCode().value());
        log.warn("Downstream client error [{}]: {}", status, ex.getMessage());
        return buildResponse(status, ex.getMessage());
    }

    @ExceptionHandler(HttpServerErrorException.class)
    public ResponseEntity<ErrorDetails> handleDownstreamServerError(HttpServerErrorException ex) {
        log.error("Downstream server error: {}", ex.getMessage());
        return buildResponse(HttpStatus.BAD_GATEWAY, "Downstream service returned an error");
    }

    @ExceptionHandler(ResourceAccessException.class)
    public ResponseEntity<ErrorDetails> handleResourceAccessException(ResourceAccessException ex) {
        log.error("Downstream service unreachable: {}", ex.getMessage());
        return buildResponse(HttpStatus.SERVICE_UNAVAILABLE, "Downstream service is unavailable");
    }

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ErrorDetails> handleAccessDenied(AccessDeniedException ex) {
        log.warn("Access denied: {}", ex.getMessage());
        return buildResponse(HttpStatus.FORBIDDEN, ex.getMessage());
    }

    @ExceptionHandler(AuthenticationException.class)
    public ResponseEntity<ErrorDetails> handleAuthentication(AuthenticationException ex) {
        log.warn("Authentication failed: {}", ex.getMessage());
        return buildResponse(HttpStatus.UNAUTHORIZED, ex.getMessage());
    }

    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<ErrorDetails> handleRuntimeException(RuntimeException ex) {
        log.error("Unhandled runtime exception", ex);
        return buildResponse(HttpStatus.INTERNAL_SERVER_ERROR, ex.getMessage());
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorDetails> handleException(Exception ex) {
        log.error("Unhandled exception", ex);
        return buildResponse(HttpStatus.INTERNAL_SERVER_ERROR, ex.getMessage());
    }

    private ResponseEntity<ErrorDetails> buildResponse(HttpStatus status, String message) {
        var error = ErrorDetails.builder()
                .message(message)
                .status(status.getReasonPhrase())
                .timestamp(LocalDateTime.now())
                .build();
        return new ResponseEntity<>(error, status);
    }
}
