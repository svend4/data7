"""
Redis Caching Layer

Provides multi-level caching with Redis for performance optimization.
Implements cache-aside pattern with automatic invalidation.
"""

from typing import Optional, Any, Dict, List, Callable
from datetime import timedelta
import json
import hashlib
import asyncio
from functools import wraps
import redis.asyncio as redis
from app.middleware.prometheus import record_cache_operation, update_cache_hit_ratio


# ============================================================================
# Configuration
# ============================================================================

REDIS_URL = "redis://localhost:6379/0"  # TODO: Use environment variable
DEFAULT_TTL = 300  # 5 minutes


# ============================================================================
# Cache Patterns Configuration
# ============================================================================

CACHE_PATTERNS = {
    "agents_list": {
        "ttl": 60,  # 1 minute
        "key_pattern": "agents:list:{filter}",
        "invalidate_on": ["agent.created", "agent.updated", "agent.deleted"]
    },
    "agent_detail": {
        "ttl": 300,  # 5 minutes
        "key_pattern": "agent:{agent_id}",
        "invalidate_on": ["agent.updated", "agent.deleted"]
    },
    "tasks_list": {
        "ttl": 30,  # 30 seconds
        "key_pattern": "tasks:list:{filter}",
        "invalidate_on": ["task.created", "task.updated", "task.deleted"]
    },
    "task_detail": {
        "ttl": 60,  # 1 minute
        "key_pattern": "task:{task_id}",
        "invalidate_on": ["task.updated", "task.deleted"]
    },
    "system_health": {
        "ttl": 10,  # 10 seconds
        "key_pattern": "analytics:system_health",
        "invalidate_on": ["metrics.updated"]
    },
    "performance_metrics": {
        "ttl": 60,  # 1 minute
        "key_pattern": "analytics:performance",
        "invalidate_on": ["metrics.updated"]
    },
    "graph_analysis": {
        "ttl": 300,  # 5 minutes
        "key_pattern": "optimization:graph:{graph_id}:analysis",
        "invalidate_on": ["graph.updated", "graph.deleted"]
    },
    "optimization_result": {
        "ttl": 600,  # 10 minutes
        "key_pattern": "optimization:graph:{graph_id}:result:{strategy}",
        "invalidate_on": ["graph.updated", "graph.deleted"]
    },
    "alerts_list": {
        "ttl": 15,  # 15 seconds
        "key_pattern": "alerts:list:{filter}",
        "invalidate_on": ["alert.created", "alert.updated"]
    },
    "alert_stats": {
        "ttl": 120,  # 2 minutes
        "key_pattern": "alerts:stats:{timeframe}",
        "invalidate_on": ["alert.created", "alert.updated", "alert.resolved"]
    }
}


# ============================================================================
# Redis Client
# ============================================================================

class RedisClient:
    """
    Async Redis client wrapper.

    Provides connection pooling and error handling.
    """

    def __init__(self, url: str = REDIS_URL):
        self.url = url
        self._client: Optional[redis.Redis] = None
        self._lock = asyncio.Lock()

    async def get_client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self._client is None:
            async with self._lock:
                if self._client is None:
                    self._client = await redis.from_url(
                        self.url,
                        encoding="utf-8",
                        decode_responses=True,
                        max_connections=20
                    )
        return self._client

    async def close(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None


# Global Redis client
redis_client = RedisClient()


# ============================================================================
# Cache Manager
# ============================================================================

class CacheManager:
    """
    Cache manager for Redis operations.

    Provides get, set, delete, and invalidation operations.
    """

    def __init__(self):
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            client = await redis_client.get_client()
            value = await client.get(key)

            if value is not None:
                self.stats["hits"] += 1
                record_cache_operation("get", "hit")
                self._update_hit_ratio()
                return json.loads(value)
            else:
                self.stats["misses"] += 1
                record_cache_operation("get", "miss")
                self._update_hit_ratio()
                return None

        except Exception as e:
            print(f"Cache get error: {e}")
            record_cache_operation("get", "error")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None = default TTL)

        Returns:
            True if successful, False otherwise
        """
        try:
            client = await redis_client.get_client()
            serialized = json.dumps(value, default=str)

            if ttl is None:
                ttl = DEFAULT_TTL

            await client.setex(key, ttl, serialized)

            self.stats["sets"] += 1
            record_cache_operation("set", "success")
            return True

        except Exception as e:
            print(f"Cache set error: {e}")
            record_cache_operation("set", "error")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise
        """
        try:
            client = await redis_client.get_client()
            result = await client.delete(key)

            if result > 0:
                self.stats["deletes"] += 1
                record_cache_operation("delete", "success")
                return True

            return False

        except Exception as e:
            print(f"Cache delete error: {e}")
            record_cache_operation("delete", "error")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Key pattern (e.g., "agents:*")

        Returns:
            Number of keys deleted
        """
        try:
            client = await redis_client.get_client()

            # Scan for matching keys
            keys = []
            async for key in client.scan_iter(match=pattern):
                keys.append(key)

            # Delete keys
            if keys:
                deleted = await client.delete(*keys)
                self.stats["deletes"] += deleted
                record_cache_operation("delete_pattern", "success")
                return deleted

            return 0

        except Exception as e:
            print(f"Cache delete pattern error: {e}")
            record_cache_operation("delete_pattern", "error")
            return 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if exists, False otherwise
        """
        try:
            client = await redis_client.get_client()
            result = await client.exists(key)
            return result > 0

        except Exception as e:
            print(f"Cache exists error: {e}")
            return False

    async def get_ttl(self, key: str) -> int:
        """
        Get remaining TTL for key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds, -1 if no expiry, -2 if key doesn't exist
        """
        try:
            client = await redis_client.get_client()
            return await client.ttl(key)

        except Exception as e:
            print(f"Cache get_ttl error: {e}")
            return -2

    async def invalidate_by_event(self, event: str):
        """
        Invalidate cache entries based on event.

        Args:
            event: Event name (e.g., "agent.updated")
        """
        patterns_to_invalidate = []

        for pattern_name, config in CACHE_PATTERNS.items():
            if event in config.get("invalidate_on", []):
                # Extract key pattern without placeholders
                key_pattern = config["key_pattern"]

                # Replace placeholders with wildcard
                key_pattern = key_pattern.replace("{filter}", "*")
                key_pattern = key_pattern.replace("{agent_id}", "*")
                key_pattern = key_pattern.replace("{task_id}", "*")
                key_pattern = key_pattern.replace("{graph_id}", "*")
                key_pattern = key_pattern.replace("{strategy}", "*")
                key_pattern = key_pattern.replace("{timeframe}", "*")

                patterns_to_invalidate.append(key_pattern)

        # Delete matching keys
        for pattern in patterns_to_invalidate:
            await self.delete_pattern(pattern)

    def _update_hit_ratio(self):
        """Update cache hit ratio metric."""
        total = self.stats["hits"] + self.stats["misses"]
        if total > 0:
            ratio = self.stats["hits"] / total
            update_cache_hit_ratio("redis", ratio)

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Cache statistics
        """
        total = self.stats["hits"] + self.stats["misses"]
        hit_ratio = self.stats["hits"] / total if total > 0 else 0

        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "sets": self.stats["sets"],
            "deletes": self.stats["deletes"],
            "hit_ratio": hit_ratio,
            "total_requests": total
        }


# Global cache manager
cache_manager = CacheManager()


# ============================================================================
# Cache Decorator
# ============================================================================

def cached(
    pattern_name: str,
    key_builder: Optional[Callable] = None,
    ttl: Optional[int] = None
):
    """
    Decorator to cache function results.

    Args:
        pattern_name: Name of cache pattern in CACHE_PATTERNS
        key_builder: Function to build cache key from function arguments
        ttl: Time to live in seconds (overrides pattern TTL)

    Example:
        @cached("agents_list", key_builder=lambda filter: f"list:{filter}")
        async def get_agents(db, filter: str):
            return await db.query(Agent).filter(...).all()
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache pattern config
            pattern = CACHE_PATTERNS.get(pattern_name)
            if not pattern:
                # No cache pattern, just execute function
                return await func(*args, **kwargs)

            # Build cache key
            if key_builder:
                key_suffix = key_builder(*args, **kwargs)
                cache_key = pattern["key_pattern"].format(**{k: v for k, v in kwargs.items()})
                cache_key = cache_key.replace("{filter}", key_suffix)
            else:
                # Use default key based on function arguments
                args_str = str(args) + str(sorted(kwargs.items()))
                args_hash = hashlib.md5(args_str.encode()).hexdigest()
                cache_key = f"{func.__name__}:{args_hash}"

            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            cache_ttl = ttl if ttl is not None else pattern.get("ttl", DEFAULT_TTL)
            await cache_manager.set(cache_key, result, cache_ttl)

            return result

        return wrapper
    return decorator


# ============================================================================
# Cache Invalidation Helper
# ============================================================================

async def invalidate_cache(event: str):
    """
    Invalidate cache based on event.

    Args:
        event: Event name (e.g., "agent.updated")

    Example:
        await invalidate_cache("agent.updated")
    """
    await cache_manager.invalidate_by_event(event)


# ============================================================================
# Helper Functions
# ============================================================================

async def warm_cache():
    """
    Warm up cache with frequently accessed data.

    Should be called on application startup.
    """
    # TODO: Implement cache warming logic
    # Example: Pre-fetch and cache common queries
    pass


async def clear_all_cache():
    """Clear all cache entries."""
    await cache_manager.delete_pattern("*")


async def get_cache_info() -> Dict[str, Any]:
    """
    Get cache information.

    Returns:
        Cache statistics and configuration
    """
    stats = await cache_manager.get_stats()

    return {
        "stats": stats,
        "patterns": {
            name: {
                "ttl": config["ttl"],
                "invalidate_on": config["invalidate_on"]
            }
            for name, config in CACHE_PATTERNS.items()
        }
    }


# ============================================================================
# Application Lifecycle
# ============================================================================

async def init_redis():
    """
    Initialize Redis connection on application startup.
    
    Creates connection pool and tests connectivity.
    """
    global cache_manager
    
    try:
        # Test connection
        await cache_manager.get("__health_check__")
        print("✅ Redis connection successful")
        
        # Optionally warm cache
        # await warm_cache()
        
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        raise


async def close_redis():
    """
    Close Redis connections on application shutdown.
    
    Gracefully closes connection pool.
    """
    global cache_manager
    
    try:
        if cache_manager._redis_client._client:
            await cache_manager._redis_client._client.close()
            await cache_manager._redis_client._client.connection_pool.disconnect()
            print("✅ Redis connections closed")
    except Exception as e:
        print(f"⚠️  Error closing Redis connections: {e}")
