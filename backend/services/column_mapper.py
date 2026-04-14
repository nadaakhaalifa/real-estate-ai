# map different column names to standard schema
def normalize_columns(columns):
    #standard mapping
    mapping = {
        "developer": "developer_name",
        "project name": "compound_name",
        "area": "location",
        "sub area": "district",
        "delivery": "delivery_date",
        "finished": "finishing_status",
        "payment plan": "payment_plan",
        "update date": "last_updated_at"
    }
    
    normalized ={}
    
    for col in columns:
        # clean column name 
        clean_col = col.strip().lower()
        
        # map if exists
        if clean_col in mapping:
            normalized[col] = mapping[clean_col]
        else:
            normalized[col] = clean_col #fallback
    return normalized
        
    