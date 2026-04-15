# calculate how well a unit matches the search query
def calculate_score(unit, target_bedrooms=None, max_price=None):
    score = 0
    
    #bedroom match (exact match gets higher score)
    if target_bedrooms and unit.get("bedrooms"):
        if unit["bedrooms"] == target_bedrooms:
            score += 3
        else:
            score += 1
            
    # price closeness (closer to max_price is better)
    if max_price and unit.get("price_total"):
        diff = abs(max_price - unit["price_total"])
        score += max(0, 3 - (diff / max_price)) #converting numbers into % + The 3 is arbitrary [weight]
        
    return score 



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

    # calculate score for each filtered unit 
    for unit in filtered_units:
        unit["score"] = calculate_score(
            unit,
            target_bedrooms=bedrooms,
            max_price=max_price
        )
    # sort units by highest score first
    filtered_units.sort(key=lambda unit: unit["score"], reverse=True)

    return filtered_units