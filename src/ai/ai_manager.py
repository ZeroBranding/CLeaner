"""
🤖 AI Manager with Multi-Provider Support
Supports Llama3-8B (local), Gemini 1.5, Deepseek 3.1, and Groq API
Load balancing and intelligent provider selection
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import google.generativeai as genai
from groq import Groq
import ollama

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """Available AI providers"""
    OLLAMA_LOCAL = "ollama_local"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    GROQ = "groq"
    CLAUDE_OPUS = "claude_opus"  # Framework ready for Opus 4.1

@dataclass
class AIResponse:
    """AI response data structure"""
    content: str
    provider: AIProvider
    tokens_used: int
    response_time: float
    model: str
    success: bool
    error: Optional[str] = None

@dataclass
class ProviderConfig:
    """Provider configuration"""
    name: str
    api_key_required: bool
    local: bool
    models: List[str]
    rate_limit: int  # requests per minute
    cost_per_token: float
    quality_score: float  # 0-100

class AIProviderClient:
    """Base class for AI provider clients"""
    
    def __init__(self, config: ProviderConfig, api_key: Optional[str] = None):
        self.config = config
        self.api_key = api_key
        self.request_count = 0
        self.last_request_time = 0
        
    async def generate(self, prompt: str, model: str = None) -> AIResponse:
        """Generate response from AI provider"""
        raise NotImplementedError

class OllamaClient(AIProviderClient):
    """Local Ollama client for Llama3-8B"""
    
    async def generate(self, prompt: str, model: str = "llama3:8b") -> AIResponse:
        start_time = time.time()
        
        try:
            response = ollama.chat(model=model, messages=[
                {'role': 'user', 'content': prompt}
            ])
            
            response_time = time.time() - start_time
            
            return AIResponse(
                content=response['message']['content'],
                provider=AIProvider.OLLAMA_LOCAL,
                tokens_used=response.get('eval_count', 0),
                response_time=response_time,
                model=model,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return AIResponse(
                content="",
                provider=AIProvider.OLLAMA_LOCAL,
                tokens_used=0,
                response_time=time.time() - start_time,
                model=model,
                success=False,
                error=str(e)
            )

class GeminiClient(AIProviderClient):
    """Google Gemini 1.5 client"""
    
    def __init__(self, config: ProviderConfig, api_key: str):
        super().__init__(config, api_key)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
    async def generate(self, prompt: str, model: str = "gemini-1.5-pro") -> AIResponse:
        start_time = time.time()
        
        try:
            response = self.model.generate_content(prompt)
            response_time = time.time() - start_time
            
            return AIResponse(
                content=response.text,
                provider=AIProvider.GEMINI,
                tokens_used=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                response_time=response_time,
                model=model,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return AIResponse(
                content="",
                provider=AIProvider.GEMINI,
                tokens_used=0,
                response_time=time.time() - start_time,
                model=model,
                success=False,
                error=str(e)
            )

class GroqClient(AIProviderClient):
    """Groq API client"""
    
    def __init__(self, config: ProviderConfig, api_key: str):
        super().__init__(config, api_key)
        self.client = Groq(api_key=api_key)
        
    async def generate(self, prompt: str, model: str = "llama3-8b-8192") -> AIResponse:
        start_time = time.time()
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                temperature=0.7,
                max_tokens=1024
            )
            
            response_time = time.time() - start_time
            
            return AIResponse(
                content=chat_completion.choices[0].message.content,
                provider=AIProvider.GROQ,
                tokens_used=chat_completion.usage.total_tokens,
                response_time=response_time,
                model=model,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            return AIResponse(
                content="",
                provider=AIProvider.GROQ,
                tokens_used=0,
                response_time=time.time() - start_time,
                model=model,
                success=False,
                error=str(e)
            )

class DeepseekClient(AIProviderClient):
    """Deepseek 3.1 client"""
    
    async def generate(self, prompt: str, model: str = "deepseek-chat") -> AIResponse:
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'model': model,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.7,
                    'max_tokens': 1024
                }
                
                async with session.post(
                    'https://api.deepseek.com/v1/chat/completions',
                    headers=headers,
                    json=data
                ) as resp:
                    result = await resp.json()
                    response_time = time.time() - start_time
                    
                    if resp.status == 200:
                        return AIResponse(
                            content=result['choices'][0]['message']['content'],
                            provider=AIProvider.DEEPSEEK,
                            tokens_used=result['usage']['total_tokens'],
                            response_time=response_time,
                            model=model,
                            success=True
                        )
                    else:
                        raise Exception(f"API error: {result}")
                        
        except Exception as e:
            logger.error(f"Deepseek generation failed: {e}")
            return AIResponse(
                content="",
                provider=AIProvider.DEEPSEEK,
                tokens_used=0,
                response_time=time.time() - start_time,
                model=model,
                success=False,
                error=str(e)
            )

class AIManager(QObject):
    """Intelligent AI manager with load balancing and provider selection"""
    
    # Signals
    response_ready = pyqtSignal(AIResponse)
    provider_status_changed = pyqtSignal(str, bool)
    
    def __init__(self, db_manager=None):
        super().__init__()
        self.db_manager = db_manager
        self.providers: Dict[AIProvider, AIProviderClient] = {}
        self.provider_configs = self._init_provider_configs()
        self.provider_health: Dict[AIProvider, bool] = {}
        
        # Load balancing metrics
        self.provider_metrics: Dict[AIProvider, Dict[str, float]] = {}
        
        self._init_providers()
        
    def _init_provider_configs(self) -> Dict[AIProvider, ProviderConfig]:
        """Initialize provider configurations"""
        return {
            AIProvider.OLLAMA_LOCAL: ProviderConfig(
                name="Llama3-8B (Local)",
                api_key_required=False,
                local=True,
                models=["llama3:8b", "llama3:8b-instruct"],
                rate_limit=60,  # No real limit for local
                cost_per_token=0.0,
                quality_score=75.0
            ),
            AIProvider.GEMINI: ProviderConfig(
                name="Google Gemini 1.5",
                api_key_required=True,
                local=False,
                models=["gemini-1.5-pro", "gemini-1.5-flash"],
                rate_limit=60,
                cost_per_token=0.000125,
                quality_score=90.0
            ),
            AIProvider.GROQ: ProviderConfig(
                name="Groq (Free)",
                api_key_required=True,
                local=False,
                models=["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"],
                rate_limit=30,
                cost_per_token=0.0,  # Free tier
                quality_score=85.0
            ),
            AIProvider.DEEPSEEK: ProviderConfig(
                name="Deepseek 3.1",
                api_key_required=True,
                local=False,
                models=["deepseek-chat", "deepseek-coder"],
                rate_limit=60,
                cost_per_token=0.00014,
                quality_score=88.0
            ),
            AIProvider.CLAUDE_OPUS: ProviderConfig(
                name="Claude Opus 4.1 (Superior Design)",
                api_key_required=True,
                local=False,
                models=["claude-3-opus-20240229", "claude-4-opus-20241201"],
                rate_limit=50,
                cost_per_token=0.015,
                quality_score=95.0  # Highest quality, especially for design tasks
            )
        }
    
    def _init_providers(self):
        """Initialize AI provider clients"""
        # Always initialize Ollama (local)
        self.providers[AIProvider.OLLAMA_LOCAL] = OllamaClient(
            self.provider_configs[AIProvider.OLLAMA_LOCAL]
        )
        
        # Initialize cloud providers if API keys are available
        if self.db_manager:
            for provider in [AIProvider.GEMINI, AIProvider.GROQ, AIProvider.DEEPSEEK]:
                api_key = self.db_manager.get_api_key(provider.value)
                if api_key:
                    if provider == AIProvider.GEMINI:
                        self.providers[provider] = GeminiClient(
                            self.provider_configs[provider], api_key
                        )
                    elif provider == AIProvider.GROQ:
                        self.providers[provider] = GroqClient(
                            self.provider_configs[provider], api_key
                        )
                    elif provider == AIProvider.DEEPSEEK:
                        self.providers[provider] = DeepseekClient(
                            self.provider_configs[provider], api_key
                        )
        
        # Test provider health
        asyncio.create_task(self._test_provider_health())
        
    async def _test_provider_health(self):
        """Test health of all providers"""
        for provider, client in self.providers.items():
            try:
                response = await client.generate("Test message", model=client.config.models[0])
                self.provider_health[provider] = response.success
                self.provider_status_changed.emit(provider.value, response.success)
                
                if response.success:
                    logger.info(f"Provider {provider.value} is healthy")
                else:
                    logger.warning(f"Provider {provider.value} failed health check")
                    
            except Exception as e:
                self.provider_health[provider] = False
                self.provider_status_changed.emit(provider.value, False)
                logger.error(f"Health check failed for {provider.value}: {e}")
    
    def set_api_key(self, provider: str, api_key: str):
        """Set API key for a provider"""
        if self.db_manager:
            self.db_manager.store_api_key(provider, api_key)
            # Reinitialize providers
            self._init_providers()
    
    def select_best_provider(self, prompt: str, priority: str = "balanced") -> AIProvider:
        """Intelligent provider selection based on various factors"""
        available_providers = [p for p, healthy in self.provider_health.items() if healthy]
        
        if not available_providers:
            # Fallback to local if available
            if AIProvider.OLLAMA_LOCAL in self.providers:
                return AIProvider.OLLAMA_LOCAL
            else:
                raise Exception("No healthy AI providers available")
        
        if priority == "speed":
            # Prefer local first, then fastest cloud
            if AIProvider.OLLAMA_LOCAL in available_providers:
                return AIProvider.OLLAMA_LOCAL
            return min(available_providers, key=lambda p: self._get_avg_response_time(p))
            
        elif priority == "quality":
            # Prefer highest quality provider
            return max(available_providers, key=lambda p: self.provider_configs[p].quality_score)
            
        elif priority == "cost":
            # Prefer free providers
            free_providers = [p for p in available_providers 
                            if self.provider_configs[p].cost_per_token == 0.0]
            if free_providers:
                return max(free_providers, key=lambda p: self.provider_configs[p].quality_score)
            else:
                return min(available_providers, key=lambda p: self.provider_configs[p].cost_per_token)
        
        else:  # balanced
            # Balance between quality, speed, and cost
            scores = {}
            for provider in available_providers:
                config = self.provider_configs[provider]
                speed_score = 100 - self._get_avg_response_time(provider)
                cost_score = 100 if config.cost_per_token == 0 else max(0, 100 - config.cost_per_token * 10000)
                
                # Weighted score: 40% quality, 30% speed, 30% cost
                scores[provider] = (
                    config.quality_score * 0.4 + 
                    speed_score * 0.3 + 
                    cost_score * 0.3
                )
            
            return max(scores.keys(), key=lambda p: scores[p])
    
    def _get_avg_response_time(self, provider: AIProvider) -> float:
        """Get average response time for provider"""
        if provider not in self.provider_metrics:
            return 5.0  # Default assumption
        
        metrics = self.provider_metrics[provider]
        return metrics.get('avg_response_time', 5.0)
    
    async def generate_response(self, prompt: str, provider: AIProvider = None, 
                              model: str = None, priority: str = "balanced") -> AIResponse:
        """Generate AI response with intelligent provider selection"""
        
        if provider is None:
            provider = self.select_best_provider(prompt, priority)
        
        if provider not in self.providers:
            raise Exception(f"Provider {provider.value} not available")
        
        client = self.providers[provider]
        
        # Select model if not specified
        if model is None:
            model = client.config.models[0]
        
        # Check rate limiting
        if not self._check_rate_limit(provider):
            # Try fallback provider
            fallback_provider = self.select_best_provider(prompt, "speed")
            if fallback_provider != provider and self._check_rate_limit(fallback_provider):
                provider = fallback_provider
                client = self.providers[provider]
                model = client.config.models[0]
            else:
                raise Exception(f"Rate limit exceeded for {provider.value}")
        
        # Generate response
        response = await client.generate(prompt, model)
        
        # Update metrics
        self._update_provider_metrics(provider, response)
        
        # Store in database if available
        if self.db_manager and response.success:
            self.db_manager.store_conversation(
                session_id="current",
                user_message=prompt,
                ai_response=response.content,
                ai_provider=provider.value,
                tokens_used=response.tokens_used,
                response_time=response.response_time
            )
        
        return response
    
    def _check_rate_limit(self, provider: AIProvider) -> bool:
        """Check if provider is within rate limits"""
        config = self.provider_configs[provider]
        current_time = time.time()
        
        if provider not in self.provider_metrics:
            self.provider_metrics[provider] = {'last_request': 0, 'request_count': 0}
        
        metrics = self.provider_metrics[provider]
        
        # Reset counter if more than a minute has passed
        if current_time - metrics['last_request'] > 60:
            metrics['request_count'] = 0
        
        return metrics['request_count'] < config.rate_limit
    
    def _update_provider_metrics(self, provider: AIProvider, response: AIResponse):
        """Update provider performance metrics"""
        current_time = time.time()
        
        if provider not in self.provider_metrics:
            self.provider_metrics[provider] = {
                'request_count': 0,
                'total_response_time': 0,
                'total_requests': 0,
                'success_count': 0,
                'last_request': 0
            }
        
        metrics = self.provider_metrics[provider]
        metrics['request_count'] += 1
        metrics['total_requests'] += 1
        metrics['total_response_time'] += response.response_time
        metrics['last_request'] = current_time
        
        if response.success:
            metrics['success_count'] += 1
        
        # Calculate averages
        metrics['avg_response_time'] = metrics['total_response_time'] / metrics['total_requests']
        metrics['success_rate'] = metrics['success_count'] / metrics['total_requests']
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers"""
        status = {}
        
        for provider, config in self.provider_configs.items():
            metrics = self.provider_metrics.get(provider, {})
            
            status[provider.value] = {
                'name': config.name,
                'available': provider in self.providers,
                'healthy': self.provider_health.get(provider, False),
                'local': config.local,
                'quality_score': config.quality_score,
                'avg_response_time': metrics.get('avg_response_time', 0),
                'success_rate': metrics.get('success_rate', 0),
                'total_requests': metrics.get('total_requests', 0)
            }
        
        return status
    
    async def benchmark_providers(self, test_prompt: str = "Explain quantum computing in one sentence.") -> Dict[str, float]:
        """Benchmark all available providers"""
        results = {}
        
        for provider in self.providers.keys():
            if self.provider_health.get(provider, False):
                try:
                    response = await self.generate_response(test_prompt, provider)
                    if response.success:
                        # Score based on response time and quality
                        quality_score = self.provider_configs[provider].quality_score
                        speed_score = max(0, 100 - response.response_time * 10)
                        results[provider.value] = (quality_score + speed_score) / 2
                    else:
                        results[provider.value] = 0
                except Exception as e:
                    logger.error(f"Benchmark failed for {provider.value}: {e}")
                    results[provider.value] = 0
        
        return results
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models for each provider"""
        models = {}
        for provider, config in self.provider_configs.items():
            if provider in self.providers:
                models[provider.value] = config.models
        return models