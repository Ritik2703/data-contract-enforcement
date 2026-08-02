import yaml
from datetime import datetime
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, datediff, current_date, count

class DataContract:
    def __init__(self, contract_file: str):
        with open(contract_file) as f:
            self.contract = yaml.safe_load(f)
    
    def validate_schema(self, df) -> bool:
        for col_name, col_type in self.contract['schema'].items():
            if col_name not in df.columns:
                raise ValueError(f"Missing: {col_name}")
        return True
    
    def validate_sla(self, df) -> bool:
        count = df.count()
        min_rows = self.contract['sla'].get('min_rows', 0)
        if count < min_rows:
            raise ValueError(f"SLA breach: {count} < {min_rows}")
        return True
    
    def monitor(self, df) -> dict:
        return {
            'row_count': df.count(),
            'schema_valid': self.validate_schema(df),
            'sla_valid': self.validate_sla(df),
            'timestamp': datetime.utcnow().isoformat()
        }
