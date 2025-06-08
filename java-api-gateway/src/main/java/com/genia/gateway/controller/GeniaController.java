package com.genia.gateway.controller;

import com.genia.gateway.model.QueryRequest;
import com.genia.gateway.model.QueryResponse;
import com.genia.gateway.service.GeniaService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/genia")
@CrossOrigin(origins = "*")
public class GeniaController {

    private static final Logger logger = LoggerFactory.getLogger(GeniaController.class);

    @Autowired
    private GeniaService geniaService;

    @PostMapping("/query")
    public ResponseEntity<QueryResponse> query(@Valid @RequestBody QueryRequest request) {
        logger.info("Received query request: {}", request.getPrompt());
        
        try {
            QueryResponse response = geniaService.processQuery(request);
            logger.info("Query processed successfully");
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("Error processing query: {}", e.getMessage(), e);
            return ResponseEntity.internalServerError()
                .body(new QueryResponse(
                    "Error: " + e.getMessage(), 
                    0, 
                    "error"
                ));
        }
    }

    @PostMapping("/query/mock")
    public ResponseEntity<QueryResponse> queryMock(@Valid @RequestBody QueryRequest request) {
        logger.info("Received mock query request: {}", request.getPrompt());
        
        try {
            QueryResponse response = geniaService.processQueryMock(request);
            logger.info("Mock query processed successfully");
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("Error processing mock query: {}", e.getMessage(), e);
            return ResponseEntity.internalServerError()
                .body(new QueryResponse(
                    "Error: " + e.getMessage(), 
                    0, 
                    "error"
                ));
        }
    }

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        logger.debug("Health check requested");
        return ResponseEntity.ok("Gateway is healthy");
    }

    @GetMapping("/status")
    public ResponseEntity<Object> status() {
        logger.debug("Status check requested");
        return ResponseEntity.ok(new Object() {
            public final String service = "GenIA API Gateway";
            public final String version = "1.0.0";
            public final String status = "running";
            public final long timestamp = System.currentTimeMillis();
        });
    }
}