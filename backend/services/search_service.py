def filter_units(units, min_price=None, max_price=None, bedrooms=None):
     filtered_units = []
     
     for unit in units:
        #skip if price is below minimum 
        if min_price is not None and unit["price_total"] is not None:
            if unit["price_total"] < min_price:
                continue
            
         # skip if price is above maximum
        if max_price is not None and unit["price_total"] is not None:
            if unit["price_total"] > max_price:
                continue
         # skip if bedrooms do not match
        if bedrooms is not None and unit["bedrooms"] is not None:
            if unit["bedrooms"] != bedrooms:
                continue

        filtered_units.append(unit)

     return filtered_units
    