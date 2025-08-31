# ChitraLeap Backend - AI-Powered Ad Generation

## Overview

ChitraLeap is a web application backend that leverages OpenAI's GPT-4 and DALL-E 3 models to automatically generate compelling advertising content for the Indian market. The system takes product descriptions, target audience information, promotional offers, and language preferences as input, then produces multiple ad copy variations along with culturally relevant images. Built with Flask, the backend serves as an API endpoint that can be integrated with various frontends, including Builder.io applications.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Flask Web Framework**: Chosen for its simplicity and rapid development capabilities. Flask provides a lightweight foundation that's ideal for API-focused applications without unnecessary overhead.
- **RESTful API Design**: Single POST endpoint (`/generate-ad`) follows REST principles for clear, predictable interactions.

### AI Integration Pattern
- **Dual OpenAI API Architecture**: The system uses a two-step AI generation process:
  1. **GPT-4 Turbo**: Generates structured ad copy and image prompts in JSON format
  2. **DALL-E 3**: Creates visual content based on the generated prompts
- **Structured Response Format**: Enforces JSON output from GPT-4 to ensure consistent, parseable responses for downstream processing.

### Configuration Management
- **Environment Variable Pattern**: Sensitive configuration (API keys) stored in `.env` files and accessed through `python-dotenv`
- **Fallback Mechanisms**: Default values provided for non-critical configuration like session secrets

### Cross-Origin Resource Sharing
- **Permissive CORS Policy**: Configured to accept requests from any origin (`origins="*"`) to support Builder.io frontend integration and development flexibility

### Error Handling Strategy
- **Graceful Degradation**: Try-catch blocks around external API calls to prevent application crashes
- **Logging Infrastructure**: Debug-level logging enabled for troubleshooting API interactions and request flow

### Request Processing Flow
1. **Input Validation**: Validates required fields in JSON payload
2. **Meta-Prompt Construction**: Builds culturally-aware prompts for Indian market advertising
3. **Sequential AI Processing**: GPT-4 call followed by multiple DALL-E 3 calls
4. **Response Aggregation**: Combines text and image outputs into unified JSON response

## External Dependencies

### AI Services
- **OpenAI API**: Primary dependency for content generation
  - GPT-4 Turbo model for text generation and prompt creation
  - DALL-E 3 model for image generation
  - Requires API key authentication

### Python Libraries
- **Flask**: Web framework for API endpoints and request handling
- **OpenAI Python SDK**: Official client library for OpenAI API interactions
- **Flask-CORS**: Cross-origin request support for frontend integration
- **python-dotenv**: Environment variable management from .env files

### Frontend Integration
- **Builder.io Compatibility**: CORS configuration specifically designed to work with Builder.io frontend applications
- **JSON API Interface**: Standard REST API that can integrate with any HTTP client

### Development Tools
- **Python Logging**: Built-in logging for debugging and monitoring
- **Environment-based Configuration**: Supports different configurations for development and production environments