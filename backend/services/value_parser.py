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


# parse bedroom text like 3 BR or 4 bedrooms 
def parse_bedrooms(value):
    #return None for empty values
    if value is None:
        return None
    
    # convert to string and clean spaces
    text = str(value).strip().lower()

    if not text:
        return None

    # studio = 0 bedrooms
    if text == "studio" or "studio" in text:
        return 0

    # only accept real bedroom patterns
    patterns = [
        r"^(\d+)\s*(bed|beds|bedroom|bedrooms|br|bd)$",
        r"^(\d+)\s*-\s*(bed|beds|bedroom|bedrooms|br|bd)$",
        r"^(\d+)\s+(bed|beds|bedroom|bedrooms|br|bd)\s*$",
    ]

    for pattern in patterns:
        match = re.match(pattern, text)
        if match:
            return int(match.group(1))

    return None


# parse area like 120 sqm or 150.5
def parse_area(value):
    # return None for empty values
    if value is None:
        return None
    
    # convert to string and clean spaces
    text = str(value).strip().lower()

    # return None for blank text
    if not text:
        return None
    
     # remove commas
    text = text.replace(",", "")

    # find first number in the text
    import re
    numbers = re.findall(r"\d+\.?\d*", text)

    # return first number if found
    if numbers:
        return float(numbers[0])

    return None

    