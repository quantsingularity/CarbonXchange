"""
Utility functions for CarbonXchange Backend
Implements scalability and performance optimization utilities
"""

import functools
import json
import logging
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional, Optional
import redis
from flask import current_app, request
from sqlalchemy import text
from sqlalchemy.orm import Query
from src.models import db

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis-based caching manager"""

    def __init__(self, redis_client: Any = None) -> None:
        self.redis_client = redis_client or self._get_redis_client()

    def _get_redis_client(self) -> Any:
        """Get Redis client from app config"""
        try:
            redis_url = current_app.config.get("REDIS_URL", "redis://localhost:6379/0")
            return redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            return None

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        if not self.redis_client:
            return False
        try:
            serialized_value = json.dumps(value, default=str)
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            return False
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        if not self.redis_client:
            return 0
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Cache invalidate pattern error for {pattern}: {e}")
        return 0


cache_manager = CacheManager()


def cached(ttl: int = 3600, key_prefix: str = "") -> Any:
    """Decorator for caching function results"""

    def decorator(func: Callable) -> Callable:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator


class DatabaseOptimizer:
    """Database optimization utilities"""

    @staticmethod
    def add_pagination(
        query: Query, page: int = 1, per_page: int = 20, max_per_page: int = 100
    ) -> Dict:
        """Add pagination to SQLAlchemy query"""
        page = max(1, page)
        per_page = min(max_per_page, max(1, per_page))
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        return {
            "items": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_prev": has_prev,
                "has_next": has_next,
                "prev_page": page - 1 if has_prev else None,
                "next_page": page + 1 if has_next else None,
            },
        }

    @staticmethod
    def optimize_query_with_indexes(
        model_class: Any, filters: Dict, order_by: Optional[str] = None
    ) -> Any:
        """Build optimized query with proper index usage"""
        query = db.session.query(model_class)
        for field, value in filters.items():
            if hasattr(model_class, field):
                if isinstance(value, list):
                    query = query.filter(getattr(model_class, field).in_(value))
                else:
                    query = query.filter(getattr(model_class, field) == value)
        if order_by and hasattr(model_class, order_by):
            query = query.order_by(getattr(model_class, order_by))
        return query

    @staticmethod
    def bulk_insert_optimized(
        model_class: Any, data_list: List[Dict], batch_size: int = 1000
    ) -> Any:
        """Optimized bulk insert with batching"""
        total_inserted = 0
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i : i + batch_size]
            try:
                db.session.bulk_insert_mappings(model_class, batch)
                db.session.commit()
                total_inserted += len(batch)
            except Exception as e:
                logger.error(f"Bulk insert error for batch {i // batch_size + 1}: {e}")
                db.session.rollback()
                raise
        return total_inserted

    @staticmethod
    def execute_raw_query_with_params(
        query: str, params: Optional[Dict] = None
    ) -> List[Dict]:
        """Execute raw SQL query with parameters safely"""
        try:
            result = db.session.execute(text(query), params or {})
            columns = result.keys()
            rows = []
            for row in result:
                rows.append(dict(zip(columns, row)))
            return rows
        except Exception as e:
            logger.error(f"Raw query execution error: {e}")
            raise


class PerformanceMonitor:
    """Performance monitoring utilities"""

    @staticmethod
    def time_function(func: Callable) -> Callable:
        """Decorator to measure function execution time"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = (time.time() - start_time) * 1000
                logger.info(
                    f"Function {func.__name__} executed in {execution_time:.2f}ms"
                )

        return wrapper

    @staticmethod
    def log_slow_queries(threshold_ms: float = 1000) -> Any:
        """Log slow database queries"""

        def decorator(func: Callable) -> Callable:

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                if execution_time > threshold_ms:
                    logger.warning(
                        f"Slow query detected in {func.__name__}: {execution_time:.2f}ms"
                    )
                return result

            return wrapper

        return decorator


class DataSerializer:
    """Data serialization utilities for API responses"""

    @staticmethod
    def serialize_decimal(obj: Any) -> Any:
        """Serialize Decimal objects to float"""
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    @staticmethod
    def serialize_datetime(obj: Any) -> Any:
        """Serialize datetime objects to ISO format"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    @staticmethod
    def serialize_model_list(
        models: List, include_sensitive: bool = False
    ) -> List[Dict]:
        """Serialize list of SQLAlchemy models"""
        return [
            (
                model.to_dict(include_sensitive=include_sensitive)
                if hasattr(model, "to_dict")
                else str(model)
            )
            for model in models
        ]

    @staticmethod
    def paginated_response(
        paginated_data: Dict, serializer_func: Optional[Callable] = None
    ) -> Dict:
        """Create standardized paginated API response"""
        items = paginated_data["items"]
        if serializer_func:
            items = [serializer_func(item) for item in items]
        elif hasattr(items[0], "to_dict") if items else False:
            items = [item.to_dict() for item in items]
        return {
            "data": items,
            "pagination": paginated_data["pagination"],
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": getattr(request, "id", None),
            },
        }


class BackgroundTaskManager:
    """Background task management utilities"""

    @staticmethod
    def queue_task(task_name: str, *args, **kwargs) -> Any:
        """Queue a background task (Celery integration placeholder)"""
        logger.info(
            f"Queuing background task: {task_name} with args: {args}, kwargs: {kwargs}"
        )

    @staticmethod
    def schedule_periodic_task(
        task_name: str, interval_seconds: int, *args, **kwargs
    ) -> Any:
        """Schedule a periodic background task"""
        logger.info(
            f"Scheduling periodic task: {task_name} every {interval_seconds} seconds"
        )


class HealthChecker:
    """System health checking utilities"""

    @staticmethod
    def check_database_health() -> Dict:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            db.session.execute(text("SELECT 1"))
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    @staticmethod
    def check_redis_health() -> Dict:
        """Check Redis connectivity and performance"""
        try:
            start_time = time.time()
            cache_manager.redis_client.ping()
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    @staticmethod
    def get_system_metrics() -> Dict:
        """Get basic system metrics"""
        import psutil

        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {
                "error": "Unable to retrieve system metrics",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


class RateLimiter:
    """Custom rate limiting utilities"""

    def __init__(self, redis_client: Any = None) -> None:
        self.redis_client = redis_client or cache_manager.redis_client

    def is_rate_limited(self, key: str, limit: int, window_seconds: int) -> bool:
        """Check if rate limit is exceeded using sliding window"""
        if not self.redis_client:
            return False
        try:
            now = time.time()
            pipeline = self.redis_client.pipeline()
            pipeline.zremrangebyscore(key, 0, now - window_seconds)
            pipeline.zcard(key)
            pipeline.zadd(key, {str(now): now})
            pipeline.expire(key, window_seconds)
            results = pipeline.execute()
            current_count = results[1]
            return current_count >= limit
        except Exception as e:
            logger.error(f"Rate limiting error for key {key}: {e}")
            return False


def generate_api_key() -> str:
    """Generate secure API key"""
    import secrets

    return f"cx_{secrets.token_urlsafe(32)}"


def validate_api_request(required_fields: List[str], data: Dict) -> tuple:
    """Validate API request data"""
    missing_fields = [
        field for field in required_fields if field not in data or data[field] is None
    ]
    if missing_fields:
        return (False, f"Missing required fields: {', '.join(missing_fields)}")
    return (True, "Valid")


def format_currency(amount: Decimal, currency: str = "USD") -> str:
    """Format currency amount for display"""
    if currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def calculate_percentage_change(old_value: Decimal, new_value: Decimal) -> Decimal:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return Decimal("0")
    return (new_value - old_value) / old_value * 100


def validate_request_data(data: dict, required_fields: list) -> bool:
    """Validate that all required fields are present in request data"""
    if not data:
        return False
    for field in required_fields:
        if field not in data or data[field] is None:
            return False
        if isinstance(data[field], str) and (not data[field].strip()):
            return False
    return True


def handle_api_error(error: Exception) -> tuple:
    """Handle API errors and return appropriate response"""
    import logging
    from flask import current_app
    from werkzeug.exceptions import HTTPException

    logger = logging.getLogger(__name__)
    if isinstance(error, HTTPException):
        return (
            {
                "error": error.description,
                "code": error.code,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            error.code,
        )
    logger.error(f"Unexpected API error: {str(error)}", exc_info=True)
    if current_app.config.get("ENV") == "production":
        return (
            {
                "error": "Internal server error",
                "code": 500,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            500,
        )
    else:
        return (
            {
                "error": str(error),
                "code": 500,
                "type": type(error).__name__,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            500,
        )


def paginate_query(
    query: Any, page: int = 1, per_page: int = 20, max_per_page: int = 100
) -> Any:
    """Enhanced pagination with result wrapper"""

    class PaginationResult:

        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None

    page = max(1, int(page))
    per_page = min(max(1, int(per_page)), max_per_page)
    total = query.count()
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()
    return PaginationResult(items, page, per_page, total)
