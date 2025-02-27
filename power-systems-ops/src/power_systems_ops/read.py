from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd


URL = "https://emsg2.tbm.tudelft.nl/cu-boulder-2025/index.jsp"

def login(email, password):

    ChromeDriverManager().install()
    # Setup the WebDriver and launch Chrome
    driver = webdriver.Chrome()

    # Open the webpage
    driver.get(URL)

    # Find the fields by name and send the email and password.
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)

    # Find the submit button and click it
    driver.find_element(By.NAME, "submit").click()

    # Enter the specific page.
    driver.find_element(By.LINK_TEXT, "View").click()

    return driver





TABLE_NAME_TO_KEY = {
    "Power plant portfolio": "dispatch",
    "Electricity generation and fuel consumption in the past round": "last_generation",
    "Electricity production per plant": "production",
    "Power plant availability": "availability",
    "Overview of power plants": "overview",
    "Power exchange results": "clearing_prices",
}



INDEX_NAMES = {
    "dispatch": "Name",
    "last_generation": "Plant",
    "availability": "Plant",
    "overview": "Plant name",
    "Fuel characteristics": "Fuel name",
    # "clearing_prices": "Period -- Round"
}

SOURCES = [
    "Coal", "Biomass", "Natural gas", "Nuclear fuel", "Wind availability", "Solar"
]
for s in SOURCES + ["Electricity demand"]:
    INDEX_NAMES[s] = "Round"
    
    
    
def filter_empty(strings):
    return [s for s in strings if s]


def read_header_row(row):
    headers = row.find_elements(By.TAG_NAME, 'th')
    out = []
    for h in headers:
        span = h.get_attribute('colspan')
        num_elem = 1 if span is None else int(span)
        out.extend(
            [h.text] * num_elem
        )
    return out

def join_headers(header_elem):
    # Handle row joining more generally
    rows = header_elem.find_elements(By.TAG_NAME, "tr")
    assert len(rows) == 2

    row1 = read_header_row(rows[0])
    row2 = read_header_row(rows[1])
    return [' -- '.join(filter_empty([h1, h2])) for h1, h2 in zip(row1, row2)]

    
def join_2_rows(header_elem, key):
    rows = header_elem.find_elements(By.TAG_NAME, "tr")
    assert len(rows) == 2
    row1 = [h.text for h in rows[0].find_elements(By.TAG_NAME, 'th')]
    row2 = [h.text for h in rows[1].find_elements(By.TAG_NAME, 'th')]
    if key == "last_generation":
        # Extend the final column of the first row, since it pertains to each
        # of the last three columns of row2...
        
        row1 += [row1[-1], row1[-1]]
    return [' -- '.join(filter_empty([h1, h2])) for h1, h2 in zip(row1, row2)]
    
def extract_column_names(table, key):

    header_elem = table.find_element(By.TAG_NAME, "thead")
    # Add special logic for each table...
    if key in ['last_generation', 'availability', "Fuel characteristics"]:
        return join_2_rows(header_elem, key)
    if key in ["clearing_prices"]:
        return join_headers(header_elem)

    column_names = [header.text for header in header_elem.find_elements(By.TAG_NAME, "th")]

    if key == "overview":
        column_names.append("status")
    
    
    return column_names

def extract_rows(table, key):
    body = table.find_element(By.TAG_NAME, "tbody")
    rows = body.find_elements(By.TAG_NAME, "tr")
    if key == "overview":
        return extract_rows_overview(rows)
        
    data = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        row_data = [cell.text for cell in cells]
        data.append(row_data)
    return data


HEADER_TO_KEY = {
    "Operational power plants": "operational",
    "Power plants under construction": "under construction",
    "Dismantled power plants": "dismantled",
}

def extract_rows_overview(rows):
    data = []
    current_status = None
    for row in rows:
        headers = row.find_elements(By.TAG_NAME, "th")
        if headers:
            assert len(headers) == 1
            current_status = HEADER_TO_KEY[headers[0].text]
            continue
        row_data = [cell.text for cell in row.find_elements(By.TAG_NAME, "td")]
        if current_status == "under construction":
            # For some reason data in the section is missing a cell for "round dismantled".
            row_data.append('')
        row_data.append(current_status)
        data.append(row_data)
    return data
        
    
def extract_table(table, key):
    
    # Extract table headers and rows
    headers = extract_column_names(table, key)
    
    # Prepare data for DataFrame (skip the header row)
    rows = extract_rows(table, key)

    # print("Column names:", headers)
    
    # Create a DataFrame
    df = pd.DataFrame(rows, columns=headers)

    # Set index...
    index_name = INDEX_NAMES.get(key)
    if index_name is not None:
        df = df.set_index(index_name)
    return df


def navigate(driver, title):
    link = driver.find_element(By.XPATH, f"//a[@title='{title}']")
    link.find_element(By.TAG_NAME, 'img').click()

def read_current_page(driver, include_keys=None):
    tables = {}

    table_containers = driver.find_elements(By.XPATH, "//div[@class='component table left white']")

    for div in table_containers:
        name = div.find_element(By.TAG_NAME, 'h4').text
        print(name)
        if name in ["Electricity production per plant", 'Power plant availability', 'Sold plants']:
            continue


        key = TABLE_NAME_TO_KEY.get(name, name)
        if include_keys is not None and key not in include_keys:
            continue

        # print(key)
        tables_found = div.find_elements(By.TAG_NAME, "table")
        if len(tables_found) > 1:
            raise ValueError("Found multiple tables within single div!!!")
        elif len(tables_found) == 1:
            df = extract_table(tables_found[0], key)
            tables[key] = df
    return tables

def read_tables(driver, include_keys=None):


    tables = {}

    page_titles = [
        "Power plants", 
        "Stocks & trends",
        "Build, decommision or trade plant",
        "Electricity market"
    ]
    for page in page_titles:
        navigate(driver, page)
        tables.update(read_current_page(driver, include_keys=include_keys))

    # # Navigate to power plants page
    # navigate(driver, "Power plants")
    # tables.update(read_current_page(driver))

    # navigate(driver, "Stocks & trends")
    # tables.update(read_current_page(driver))
    # navigate(driver, )

    # tables.update(read_current_page(driver))

    return process_tables(tables)


##############################################################################
# Simplifying Column Names and Numeric Conversions
##############################################################################

def rename(d, mapping):
    """Return new dictionary with keys updated based on mapping dictionary."""
    return {mapping.get(k, k): v for k, v in d.items()}


SIMPLE_TABLE_NAMES = {
    # This is a map from original table name to a
    # more concise (and lowercase) one.
    # The original table names come directly from their
    # heading on the webpage (i.e. the <h4/> tag).
    "Coal": 'coal',
    'Biomass': 'biomass',
    'Natural gas': 'naturalgas',
    'Nuclear fuel': 'nuclear',
    'Wind availability': 'wind',
    'Solar': 'solar',
    'Electricity demand': 'demand',
    'Fuel characteristics': 'fuels',
    'Invest in a new power plant': 'invest',

}


SIMPLE_NAME_MAP = {
    # Mapping from table name -> "column mapper"
    # Column mapper is a dictionary with original column
    # names as key and renamed column name as values
    "dispatch": {
        "Type": 'type',
        "Capacity (MW)": 'cap',
        'Reliability (%)': 'rel',
        'Efficiency (%)': 'eff',
        'Loan payment (M€/year)': 'loan',
        'Remaining payments (years)': 'payments',
        'Fixed O&M costs (M€/year)': 'fixed',
        'Status': 'status',
        'First round active': 'first_round',
        'Priority': 'priority'
    },
    'fuels': {
        'Energy value -- (MJ/fuel unit)': 'energy',
        'Emission factor -- (ton CO2/fuel unit)': 'emmisions'
    },
    'coal': {'Price (€/ton)': 'price'},
    'biomass': {'Price (€/ton)': 'price'},
    'naturalgas': {'Price (€/m3)': 'price'},
    'nuclear': {'Price (€/kg)': 'price'},
    'wind': {'Wind availability (%)': 'avail'},
    'solar': {'Solar availability (%)': 'avail'},
    'invest': {
        "Reliability (%)": "rel",
        "Efficiency (%)": "eff",
        "Construction time (years)": "construct",
        "Permit time (years)": "permit",
        "Life expectancy (years)": "life_exp",
        "Down payment (M€/MW)": "down",
        "Loan payment per year (M€/(MW*year))": 'loan',
        'Number of loan payments': 'num_loan',
        'O&M cost (M€/(MW*year))': 'maint',
        'Capacity (MW)': 'cap_range'
    }, 
    "overview": {
        'Capacity (MW)': 'cap'
    },
    "clearing_prices": {
        "Period -- Round": "round",
        "Off-peak hours -- Demand (MW)": "offpeak_demand",
        "Off-peak hours -- Price (€/MWh)": "offpeak_price",
        "Shoulder hours -- Demand (MW)": "shoulder_demand",
        "Shoulder hours -- Price (€/MWh)": "shoulder_price",
        "Peak hours -- Demand (MW)": "peak_demand",
        "Peak hours -- Price (€/MWh)": "peak_price",
    }

}
        
TO_COMPLEX = {
    name: {v: k for k, v in dict_.items()}
    for name, dict_ in SIMPLE_NAME_MAP.items()
}

def to_simple(tables):
    """Apply SIMPLE_NAME_MAP to simplify the column names across tables."""
    simple_tables = tables.copy()
    for name, map_ in SIMPLE_NAME_MAP.items():
        if name not in tables:
            continue
        simple_tables[name] = tables[name].rename(columns=map_)
    return simple_tables



NUMERICAL_TYPES = {
    # Dictionary mapping table name -> a list of column names
    'dispatch': ['cap', 'rel', 'eff', 'loan', 'payments', 'fixed', 'first_round', 'priority'],
    'fuels': ['energy', 'emmisions'],
    'invest': ['rel', 'eff', 'construct', 'permit', 'life_exp', 'down', 'loan', 'num_loan', 'maint'],
    'overview': ['cap', 'Round active'],
    # 'clearing_prices': ['Period -- Round', 'offpeak_demand', 	'offpeak_demand', 	'shoulder_demand', 	'shoulder_demand',
    #                  	'peak_demand', 	'peak_demand'],
    'clearing_prices': ['round', 'offpeak_demand', 	'offpeak_price', 	'shoulder_demand', 	'shoulder_price',
                     	'peak_demand', 	'peak_price'],
}

FUEL_NAMES = ['biomass', 'naturalgas', 'nuclear', 'coal']
for name in FUEL_NAMES:
    NUMERICAL_TYPES[name] = ['index', 'price']

RENEWABLES = ['solar', 'wind']
for name in RENEWABLES:
    NUMERICAL_TYPES[name] = ['index', 'avail']

def to_numeric(tables):
    """
    Apply pd.to_numeric to columns given in NUMERICAL TYPES.

    Errors are parsed into NaN (i.e. setting errors=coerce in pd.to_numeric).
    """
    new_tables = tables.copy()
    for name, columns in NUMERICAL_TYPES.items():
        if name not in tables:
            continue
        table = tables[name].copy()
        for column in columns:
            if column == 'index':
                table.index = pd.to_numeric(table.index)
            else:
                table[column] = pd.to_numeric(table[column], errors='coerce')
        new_tables[name] = table
    return new_tables


def process_tables(tables):
    # Rename keys of fuel prices so that they correspond to the fuel types in the fuel characteristics chart
    tables = rename(tables, SIMPLE_TABLE_NAMES)
    simple_tables = to_simple(tables)
    return to_numeric(simple_tables)
