import math

def read_fx_data(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    data = []
    for i in range(2, len(lines)):
        parts = lines[i].strip().split(';')
        if len(parts) >= 11:
            data.append([float(parts[1]), float(parts[2]), float(parts[5]), float(parts[6]), float(parts[9]), float(parts[10])])
    return data

def get_returns(data, col1, col2):
    returns = []
    for i in range(1, len(data)):
        avg_prev = (data[i-1][col1] + data[i-1][col2]) / 2.0
        avg_curr = (data[i][col1] + data[i][col2]) / 2.0
        returns.append(math.log(avg_curr / avg_prev))
    return returns

def hurst(returns):
    n = len(returns)

    sum_r2 = 0.0
    for r in returns:
        sum_r2 += r ** 2
    M2 = sum_r2 / n

    sum_r2_scale2 = 0.0
    count = 0
    for i in range(0, n-1, 2):
        r_aggregated = returns[i] + returns[i+1]
        sum_r2_scale2 += r_aggregated ** 2
        count += 1
    M2_prime = sum_r2_scale2 / count

    ratio = M2_prime / M2
    H = 0.5 * math.log(ratio) / math.log(2)

    return H

def volatility(returns):
    n = len(returns)

    mean = sum(returns) / n

    sum_squared_deviations = 0.0
    for r in returns:
        deviation = r - mean
        sum_squared_deviations += deviation ** 2

    variance = sum_squared_deviations / (n - 1)
    vol = math.sqrt(variance)

    return vol


print("QUESTION E\n")

data = read_fx_data("../data/Dataset TD5.csv")
gbp = get_returns(data, 0, 1)
sek = get_returns(data, 2, 3)
cad = get_returns(data, 4, 5)

currencies = [("GBPEUR", gbp), ("SEKEUR", sek), ("CADEUR", cad)]
H = [hurst(r) for _, r in currencies]
vol_d = [volatility(r) for _, r in currencies]

print("Hurst exponents:")
for i, (name, _) in enumerate(currencies):
    print(f"  {name}: H = {H[i]:.4f}")
print()

print("Daily volatility:")
for i, (name, _) in enumerate(currencies):
    print(f"  {name}: {vol_d[i]:.6f}")
print()

print("Annualized volatility (using Hurst exponent):")
for i, (name, _) in enumerate(currencies):
    print(f"  {name}: {vol_d[i] * (252 ** H[i]):.6f}")
print()
