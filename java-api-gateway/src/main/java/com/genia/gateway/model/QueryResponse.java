package com.genia.gateway.model;

import com.fasterxml.jackson.annotation.JsonProperty;

public class QueryResponse {
    
    private String response;
    
    @JsonProperty("tokens_used")
    private int tokensUsed;
    
    private String model;

    // Constructors
    public QueryResponse() {}
    
    public QueryResponse(String response, int tokensUsed, String model) {
        this.response = response;
        this.tokensUsed = tokensUsed;
        this.model = model;
    }

    // Getters and setters
    public String getResponse() { 
        return response; 
    }
    
    public void setResponse(String response) { 
        this.response = response; 
    }
    
    public int getTokensUsed() { 
        return tokensUsed; 
    }
    
    public void setTokensUsed(int tokensUsed) { 
        this.tokensUsed = tokensUsed; 
    }
    
    public String getModel() { 
        return model; 
    }
    
    public void setModel(String model) { 
        this.model = model; 
    }

    @Override
    public String toString() {
        return "QueryResponse{" +
                "response='" + response + '\'' +
                ", tokensUsed=" + tokensUsed +
                ", model='" + model + '\'' +
                '}';
    }
}