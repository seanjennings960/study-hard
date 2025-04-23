FUEL_TYPE_MAP = {
    "powderCoal": 'coal',
    'naturalgasCCGT': 'naturalgas',
    'naturalgasOCGT': 'naturalgas',
}

def infer_fuel_type(t):
    return FUEL_TYPE_MAP.get(t, t)


def get_fuel_price(tables, t, round):
    table = tables[t]
    if 'price' not in table.columns:
        # Renewable sources have 0 fuel cost...
        return 0
    # Otherwise, return the price from the most recent round.
    if round is None:
        round = table.index.max()
    print(round)
    return table.loc[round]['price']

def get_fuel_energy(tables, t):
    return tables['fuels'].loc[t]['energy']


def compute_fuel_costs(tables, efficiency, type_, round=None):
    fuel_type = type_.map(infer_fuel_type)
    fuel_price = fuel_type.map(lambda typ: get_fuel_price(tables, typ, round))
    fuel_energy = fuel_type.map(lambda typ: get_fuel_energy(tables, typ))
    print(fuel_price)
    # cost (Euros / MWh)
    # fuel_price (Euros / fuel unit)
    # fuel_energy (MJ / fuel unit)
    # (3600 MJ / MWh)
    efficiency = efficiency/100
    generator_cost = fuel_price * 3600 / (efficiency * fuel_energy)
    return generator_cost.fillna(0)
