"""Utility helper functions"""
import uuid
import hashlib
import json
import time
from typing import Any, Dict
from datetime import datetime
from functools import wraps

from app.utils.logger import logger


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID"""
    unique_id = str(uuid.uuid4())
    return f"{prefix}_{unique_id}" if prefix else unique_id


def log_timing(func):
    """Decorator to log execution time of async functions"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        func_name = func.__name__
        
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"⏱️  {func_name} completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"⏱️  {func_name} failed after {duration:.2f}s: {e}")
            raise
    
    return wrapper


def hash_content(content: str) -> str:
    """Generate SHA256 hash of content"""
    return hashlib.sha256(content.encode()).hexdigest()


def sanitize_text(text: str, max_length: int = None) -> str:
    """Sanitize and optionally truncate text"""
    # Remove null bytes and other problematic characters
    sanitized = text.replace('\x00', '')
    
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    
    return sanitized


def format_timestamp(dt: datetime = None) -> str:
    """Format datetime to ISO format"""
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()


def safe_json_loads(data: str, default: Any = None) -> Any:
    """Safely parse JSON with a default fallback"""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def chunk_text(text: str, chunk_size: int = 10000, overlap: int = 200) -> list:
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks


def calculate_score(checks: list, weight_field: str = "weight") -> float:
    """Calculate weighted average score"""
    if not checks:
        return 0.0
    
    total_weight = sum(check.get(weight_field, 1) for check in checks)
    if total_weight == 0:
        return 0.0
    
    weighted_sum = sum(
        check.get("score", 0) * check.get(weight_field, 1)
        for check in checks
    )
    
    return round(weighted_sum / total_weight, 2)


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result
