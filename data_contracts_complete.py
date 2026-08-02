"""Data Contracts - Complete Production Implementation"""
import logging
import yaml
from typing import Dict, List, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class DataContract:
    def __init__(self, contract_file: str):
        try:
            with open(contract_file) as f:
                self.contract = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Contract load failed: {e}")
            raise
    
    def validate_schema(self, data: Dict) -> Tuple[bool, List[str]]:
        errors = []
        try:
            for col, expected_type in self.contract.get('schema', {}).items():
                if col not in data:
                    errors.append(f"Missing column: {col}")
                elif not self._type_check(data[col], expected_type):
                    errors.append(f"Type mismatch for {col}")
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            errors.append(str(e))
        
        return len(errors) == 0, errors
    
    def validate_sla(self, record_count: int, freshness_hours: float) -> Tuple[bool, List[str]]:
        errors = []
        
        min_rows = self.contract.get('sla', {}).get('min_rows', 0)
        max_age = self.contract.get('sla', {}).get('max_age_hours', 24)
        
        if record_count < min_rows:
            errors.append(f"Row count SLA breach: {record_count} < {min_rows}")
        
        if freshness_hours > max_age:
            errors.append(f"Freshness SLA breach: {freshness_hours}h > {max_age}h")
        
        return len(errors) == 0, errors
    
    def _type_check(self, value: Any, expected_type: str) -> bool:
        type_map = {'string': str, 'int': int, 'float': float, 'bool': bool}
        return isinstance(value, type_map.get(expected_type, object))
    
    def get_contract(self) -> Dict:
        return self.contract

class SLAMonitor:
    def __init__(self, contract: DataContract):
        self.contract = contract
        self.metrics = []
    
    def track_metric(self, metric_name: str, value: any):
        self.metrics.append({
            'name': metric_name,
            'value': value,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def report(self) -> Dict:
        return {
            'metrics_tracked': len(self.metrics),
            'latest': self.metrics[-1] if self.metrics else None,
            'history': self.metrics
        }
