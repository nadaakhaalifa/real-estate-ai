import re 

# parse price text like 1.5M or 1200000 [messy prices]
# converts it into a clean number
def parse_price(value):
    #return None for empty values
    if value is None:
        return None
    
    # convert to string and clean spaces
    text = str(value).strip().lower()
    
    #return None for blank text 
    if not text:
        return None
    
    # remove commas
    text = text.replace(",", "")
    
    #handle million format
    if "m" in text:
        number = re.findall(r"\d+\.?\d*", text) #regex
        if number:
            return float(number[0]) * 1_000_000
        
    #handle normal numbers
    number = re.findall(r"\d+\.?\d*", text)
    if number:
        return float (number[0])
    
    return None
        