# find original excel column by normalized field name 
def detect_column(normalized_columns,target_field):
    #loop through all mapped columns
    for original_name, normalized_name in normalized_columns.items():
        # return original excel column if target matches
        if normalized_name == target_field:
            return original_name
    return None
    