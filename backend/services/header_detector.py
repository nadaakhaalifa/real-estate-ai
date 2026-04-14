import pandas as pd


# detect the row that contains the real headers
def detect_header_row(file):
    # read excel without headers first
    df = pd.read_excel(file, header=None)

    # scan rows one by one
    for i, row in df.iterrows():
        # convert row cells to lowercase text
        row_values = [str(cell).lower() for cell in row]

        # if row contains a price-like header, use it
        if any("price" in cell for cell in row_values):
            return i

    # fallback to first row
    return 0