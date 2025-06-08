package com.genia.gateway.service;

import com.genia.gateway.model.QueryRequest;
import com.genia.gateway.model.QueryResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Service
public class GeniaService {

    private static final Logger logger = LoggerFactory.getLogger(GeniaService.class);

    @Value("${python.service.url:http://localhost:8000}")
    private String pythonServiceUrl;

    @Autowired
    private RestTemplate restTemplate;

    public QueryResponse processQuery(QueryRequest request) {
        logger.info("Processing query with Python service: {}", pythonServiceUrl);
        
        try {
            // Headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // Request entity
            HttpEntity<QueryRequest> entity = new HttpEntity<>(request, headers);
            
            // Call Python service (producción)
            String url = pythonServiceUrl + "/query";
            logger.debug("Calling Python service at: {}", url);
            
            ResponseEntity<QueryResponse> response = restTemplate.postForEntity(
                url,
                entity,
                QueryResponse.class
            );
            
            logger.info("Successfully received response from Python service");
            return response.getBody();
            
        } catch (ResourceAccessException e) {
            logger.error("Connection error to Python service: {}", e.getMessage());
            throw new RuntimeException("Python service is not available", e);
            
        } catch (HttpClientErrorException e) {
            logger.error("Client error from Python service: {} - {}", e.getStatusCode(), e.getResponseBodyAsString());
            throw new RuntimeException("Invalid request to Python service", e);
            
        } catch (HttpServerErrorException e) {
            logger.error("Server error from Python service: {} - {}", e.getStatusCode(), e.getResponseBodyAsString());
            throw new RuntimeException("Python service internal error", e);
            
        } catch (Exception e) {
            logger.error("Unexpected error calling Python service: {}", e.getMessage(), e);
            throw new RuntimeException("Unexpected error processing query", e);
        }
    }

    public QueryResponse processQueryMock(QueryRequest request) {
        logger.info("Processing mock query with Python service");
        
        try {
            // Headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // Request entity
            HttpEntity<QueryRequest> entity = new HttpEntity<>(request, headers);
            
            // Call Python service (mock endpoint)
            String url = pythonServiceUrl + "/query/mock";
            logger.debug("Calling Python mock service at: {}", url);
            
            ResponseEntity<QueryResponse> response = restTemplate.postForEntity(
                url,
                entity,
                QueryResponse.class
            );
            
            logger.info("Successfully received mock response from Python service");
            return response.getBody();
            
        } catch (Exception e) {
            logger.error("Error calling Python mock service: {}", e.getMessage(), e);
            
            // Fallback response if Python service is down
            return new QueryResponse(
                "[FALLBACK] Gateway mock response for: '" + request.getPrompt() + 
                "'. Python service is not available.",
                request.getPrompt().split(" ").length,
                "gateway-fallback"
            );
        }
    }
}