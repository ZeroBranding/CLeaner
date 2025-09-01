"""
Performance Optimizer Module

Optimiert die Anwendungsleistung durch intelligentes Caching,
Lazy Loading, und Resource Management.
"""

import asyncio
import functools
import hashlib
import pickle
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import threading
import multiprocessing as mp
import psutil
import numpy as np


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    value: Any
    timestamp: float
    access_count: int = 0
    size_bytes: int = 0
    ttl: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl


class LRUCache:
    """Thread-safe LRU cache with size limit"""
    
    def __init__(self, max_size: int = 128, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        self.current_memory = 0
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if entry.is_expired():
                    del self.cache[key]
                    self.current_memory -= entry.size_bytes
                    self.misses += 1
                    return None
                
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                entry.access_count += 1
                self.hits += 1
                return entry.value
            
            self.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Set value in cache"""
        with self.lock:
            # Calculate size
            try:
                size_bytes = len(pickle.dumps(value))
            except:
                size_bytes = 1024  # Default size if serialization fails
            
            # Check memory limit
            if size_bytes > self.max_memory_bytes:
                return  # Value too large for cache
            
            # Evict items if necessary
            while (len(self.cache) >= self.max_size or 
                   self.current_memory + size_bytes > self.max_memory_bytes):
                if not self.cache:
                    break
                    
                # Remove least recently used
                oldest_key, oldest_entry = self.cache.popitem(last=False)
                self.current_memory -= oldest_entry.size_bytes
            
            # Add new entry
            entry = CacheEntry(
                value=value,
                timestamp=time.time(),
                size_bytes=size_bytes,
                ttl=ttl
            )
            
            if key in self.cache:
                self.current_memory -= self.cache[key].size_bytes
            
            self.cache[key] = entry
            self.current_memory += size_bytes
    
    def clear(self):
        """Clear cache"""
        with self.lock:
            self.cache.clear()
            self.current_memory = 0
            self.hits = 0
            self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0
            
            return {
                "size": len(self.cache),
                "memory_mb": self.current_memory / (1024 * 1024),
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "total_requests": total_requests
            }


def memoize(maxsize: int = 128, ttl: Optional[float] = None):
    """Decorator for memoization with TTL support"""
    cache = LRUCache(max_size=maxsize)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = hashlib.md5(
                f"{func.__name__}:{args}:{kwargs}".encode()
            ).hexdigest()
            
            # Check cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Calculate result
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(key, result, ttl)
            
            return result
        
        wrapper.cache = cache
        return wrapper
    
    return decorator


class AsyncCache:
    """Async-compatible cache for coroutines"""
    
    def __init__(self, max_size: int = 128):
        self.cache = LRUCache(max_size=max_size)
        self.pending: Dict[str, asyncio.Future] = {}
        self.lock = asyncio.Lock()
    
    async def get_or_compute(self, key: str, compute_func: Callable, 
                            ttl: Optional[float] = None) -> Any:
        """Get from cache or compute asynchronously"""
        # Check cache first
        result = self.cache.get(key)
        if result is not None:
            return result
        
        async with self.lock:
            # Check if computation is already pending
            if key in self.pending:
                return await self.pending[key]
            
            # Start new computation
            future = asyncio.Future()
            self.pending[key] = future
        
        try:
            # Compute result
            if asyncio.iscoroutinefunction(compute_func):
                result = await compute_func()
            else:
                result = await asyncio.to_thread(compute_func)
            
            # Store in cache
            self.cache.set(key, result, ttl)
            
            # Set future result
            future.set_result(result)
            
            return result
        except Exception as e:
            future.set_exception(e)
            raise
        finally:
            # Remove from pending
            async with self.lock:
                self.pending.pop(key, None)


class ResourcePool:
    """Resource pool for managing expensive resources"""
    
    def __init__(self, factory: Callable, max_size: int = 10):
        self.factory = factory
        self.max_size = max_size
        self.available: List[Any] = []
        self.in_use: List[Any] = []
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
    
    def acquire(self, timeout: Optional[float] = None) -> Any:
        """Acquire a resource from the pool"""
        with self.not_empty:
            while not self.available and len(self.in_use) >= self.max_size:
                if not self.not_empty.wait(timeout):
                    raise TimeoutError("Failed to acquire resource")
            
            if self.available:
                resource = self.available.pop()
            else:
                resource = self.factory()
            
            self.in_use.append(resource)
            return resource
    
    def release(self, resource: Any):
        """Release a resource back to the pool"""
        with self.not_empty:
            if resource in self.in_use:
                self.in_use.remove(resource)
                self.available.append(resource)
                self.not_empty.notify()
    
    def clear(self):
        """Clear all resources"""
        with self.lock:
            self.available.clear()
            self.in_use.clear()


class LazyLoader:
    """Lazy loading for expensive objects"""
    
    def __init__(self, loader_func: Callable):
        self.loader_func = loader_func
        self._value = None
        self._loaded = False
        self._lock = threading.Lock()
    
    @property
    def value(self) -> Any:
        """Get the lazily loaded value"""
        if not self._loaded:
            with self._lock:
                if not self._loaded:
                    self._value = self.loader_func()
                    self._loaded = True
        return self._value
    
    def reset(self):
        """Reset the lazy loader"""
        with self._lock:
            self._value = None
            self._loaded = False


class BatchProcessor:
    """Process items in batches for better performance"""
    
    def __init__(self, process_func: Callable, batch_size: int = 100, 
                 max_wait_time: float = 1.0):
        self.process_func = process_func
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.items: List[Any] = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.processing = False
        self.processor_thread = None
    
    def add(self, item: Any):
        """Add item for batch processing"""
        with self.condition:
            self.items.append(item)
            
            if not self.processing:
                self.processing = True
                self.processor_thread = threading.Thread(target=self._process_batches)
                self.processor_thread.daemon = True
                self.processor_thread.start()
            
            self.condition.notify()
    
    def _process_batches(self):
        """Process items in batches"""
        last_process_time = time.time()
        
        while self.processing:
            with self.condition:
                # Wait for items or timeout
                while not self.items and self.processing:
                    timeout = self.max_wait_time - (time.time() - last_process_time)
                    if timeout <= 0 or not self.condition.wait(timeout):
                        break
                
                # Check if we should process
                should_process = (
                    len(self.items) >= self.batch_size or
                    (self.items and time.time() - last_process_time >= self.max_wait_time)
                )
                
                if should_process and self.items:
                    # Get batch
                    batch = self.items[:self.batch_size]
                    self.items = self.items[self.batch_size:]
                else:
                    continue
            
            # Process batch outside lock
            if batch:
                try:
                    self.process_func(batch)
                except Exception as e:
                    print(f"Batch processing error: {e}")
                
                last_process_time = time.time()
    
    def flush(self):
        """Process all remaining items"""
        with self.condition:
            if self.items:
                self.process_func(self.items)
                self.items.clear()
    
    def stop(self):
        """Stop batch processing"""
        with self.condition:
            self.processing = False
            self.condition.notify()
        
        if self.processor_thread:
            self.processor_thread.join(timeout=5)


class PerformanceOptimizer:
    """Main performance optimizer for the application"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(PerformanceOptimizer, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Caches
        self.general_cache = LRUCache(max_size=256, max_memory_mb=200)
        self.async_cache = AsyncCache(max_size=128)
        
        # Thread pools
        self.thread_pool = ThreadPoolExecutor(
            max_workers=min(32, (mp.cpu_count() or 1) * 4)
        )
        self.process_pool = ProcessPoolExecutor(
            max_workers=mp.cpu_count() or 1
        )
        
        # Resource pools
        self.resource_pools: Dict[str, ResourcePool] = {}
        
        # Batch processors
        self.batch_processors: Dict[str, BatchProcessor] = {}
        
        # Performance metrics
        self.metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "thread_pool_tasks": 0,
            "process_pool_tasks": 0,
            "optimizations_applied": 0
        }
        
        self._initialized = True
    
    def optimize_memory(self):
        """Optimize memory usage"""
        import gc
        
        # Clear caches if memory usage is high
        memory_percent = psutil.virtual_memory().percent
        
        if memory_percent > 80:
            self.general_cache.clear()
            gc.collect()
            self.metrics["optimizations_applied"] += 1
            return True
        
        return False
    
    def optimize_cpu(self):
        """Optimize CPU usage"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        if cpu_percent > 90:
            # Reduce thread pool size temporarily
            self.thread_pool._max_workers = max(2, self.thread_pool._max_workers // 2)
            self.metrics["optimizations_applied"] += 1
            return True
        elif cpu_percent < 50:
            # Restore thread pool size
            self.thread_pool._max_workers = min(32, (mp.cpu_count() or 1) * 4)
        
        return False
    
    async def run_optimized(self, func: Callable, *args, use_cache: bool = True, 
                           cache_ttl: float = 300, **kwargs) -> Any:
        """Run function with optimizations"""
        # Create cache key
        cache_key = hashlib.md5(
            f"{func.__name__}:{args}:{kwargs}".encode()
        ).hexdigest()
        
        # Check cache if enabled
        if use_cache:
            result = self.general_cache.get(cache_key)
            if result is not None:
                self.metrics["cache_hits"] += 1
                return result
            self.metrics["cache_misses"] += 1
        
        # Run function
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            # Run in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.thread_pool, func, *args, **kwargs
            )
            self.metrics["thread_pool_tasks"] += 1
        
        # Cache result
        if use_cache:
            self.general_cache.set(cache_key, result, ttl=cache_ttl)
        
        return result
    
    def create_resource_pool(self, name: str, factory: Callable, 
                           max_size: int = 10) -> ResourcePool:
        """Create a resource pool"""
        pool = ResourcePool(factory, max_size)
        self.resource_pools[name] = pool
        return pool
    
    def get_resource_pool(self, name: str) -> Optional[ResourcePool]:
        """Get a resource pool by name"""
        return self.resource_pools.get(name)
    
    def create_batch_processor(self, name: str, process_func: Callable,
                              batch_size: int = 100) -> BatchProcessor:
        """Create a batch processor"""
        processor = BatchProcessor(process_func, batch_size)
        self.batch_processors[name] = processor
        return processor
    
    def get_batch_processor(self, name: str) -> Optional[BatchProcessor]:
        """Get a batch processor by name"""
        return self.batch_processors.get(name)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        cache_stats = self.general_cache.get_stats()
        
        return {
            "cache": cache_stats,
            "metrics": self.metrics,
            "thread_pool": {
                "max_workers": self.thread_pool._max_workers,
                "active_threads": len(self.thread_pool._threads)
            },
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "available_mb": psutil.virtual_memory().available / (1024 * 1024)
            },
            "cpu": {
                "percent": psutil.cpu_percent(interval=0.1),
                "count": mp.cpu_count()
            }
        }
    
    def cleanup(self):
        """Cleanup resources"""
        # Clear caches
        self.general_cache.clear()
        
        # Stop batch processors
        for processor in self.batch_processors.values():
            processor.stop()
        
        # Clear resource pools
        for pool in self.resource_pools.values():
            pool.clear()
        
        # Shutdown thread pools
        self.thread_pool.shutdown(wait=False)
        self.process_pool.shutdown(wait=False)


# Helper functions
def optimize_list_processing(items: List[Any], process_func: Callable,
                            chunk_size: int = 1000) -> List[Any]:
    """Process large lists in optimized chunks"""
    results = []
    
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        chunk_results = [process_func(item) for item in chunk]
        results.extend(chunk_results)
    
    return results


def profile_function(func: Callable) -> Callable:
    """Decorator to profile function performance"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        start_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        
        result = func(*args, **kwargs)
        
        end_time = time.perf_counter()
        end_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        
        print(f"[PROFILE] {func.__name__}:")
        print(f"  Time: {end_time - start_time:.4f}s")
        print(f"  Memory: {end_memory - start_memory:.2f}MB")
        
        return result
    
    return wrapper


# Singleton getter
def get_performance_optimizer() -> PerformanceOptimizer:
    """Get the singleton PerformanceOptimizer instance"""
    return PerformanceOptimizer()


__all__ = [
    "PerformanceOptimizer",
    "get_performance_optimizer",
    "LRUCache",
    "AsyncCache",
    "ResourcePool",
    "LazyLoader",
    "BatchProcessor",
    "memoize",
    "optimize_list_processing",
    "profile_function"
]