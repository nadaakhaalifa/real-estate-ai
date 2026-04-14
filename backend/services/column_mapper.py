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
        "update date": "last_updated_at",
        "project": "compound_name",
        "park": "compound_name",

        "unit type": "unit_type",
        "usage type": "unit_type",
        "category": "unit_type",
        "design type": "unit_type",

        "unit code": "unit_code",
        "unit id": "unit_code",
        "unit name": "unit_code",
        "unit #": "unit_code",

        "unit price": "price_total",
        "original price": "price_total",
        "nominal price": "price_total",

        "price/m2": "price_per_m2",
        "indoor price per meter": "price_per_m2",
        "outdoor price per meter": "outdoor_price_per_m2",
        "covered terrace price per meter": "covered_terrace_price_per_m2",

        "number of bedrooms": "bedrooms",
        "no. of bedrooms": "bedrooms",

        "built up area": "area_m2",
        "builtup area": "area_m2",
        "bua": "area_m2",

        "garden area": "garden_area_m2",
        "garden area (sq. m)": "garden_area_m2",

        "roof area": "roof_area_m2",
        "penthouse area": "roof_area_m2",

        "total land area (sq. m)": "land_area_m2",
        "land area": "land_area_m2",

        "outdoor area": "outdoor_area_m2",
        "covered terraces area": "covered_terrace_area_m2",

        "floor": "floor_number",
        "floor #": "floor_number",

        "delivery year": "delivery_date",
        "delivery status": "delivery_status",
        "building status": "unit_status",
        "unit status": "unit_status",

        "finishing option": "finishing_status",

        "phase": "phase",
        "building": "building",
        "buil#": "building",
        "entrance": "entrance",
        "grand total (pricing structure)": "price_total",
        "total finishing price": "finishing_price",
        "unit total with finishing price": "price_total_with_finishing",

        "planned delivery date": "delivery_date",
        "actual delivery date": "actual_delivery_date",

        "built area  (pricing structure)": "area_m2",
        "land area  (pricing structure)": "land_area_m2",
        "roof area  (pricing structure)": "roof_area_m2",
        "penthouse area  (pricing structure)": "penthouse_area_m2",
        "semi covered roof area  (pricing structure)": "semi_covered_roof_area_m2",
        "garden / outdoor area (pricing structure)": "outdoor_area_m2",
        "garage area  (pricing structure)": "garage_area_m2",
        "storage area  (pricing structure)": "storage_area_m2",
        "extra builtup area  (pricing structure)": "extra_builtup_area_m2",

        "stage": "stage",
        "completion progress": "completion_progress",
        "finishing specs": "finishing_status"
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
        
    