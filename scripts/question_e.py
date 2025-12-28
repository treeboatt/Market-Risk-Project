import math

def read_fx_data(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    data = []
    for i in range(2, len(lines)):
        parts = lines[i].strip().split(';')
        gbp_high = float(parts[1])
        gbp_low = float(parts[2])
        sek_high = float(parts[5])
        sek_low = float(parts[6])
        cad_high = float(parts[9])
        cad_low = float(parts[10])
        data.append([gbp_high, gbp_low, sek_high, sek_low, cad_high, cad_low])
    return data

def get_returns(data, col1, col2):
    returns = []
    for i in range(1, len(data)):
        avg_prev = (data[i-1][col1] + data[i-1][col2]) / 2.0 #moyenne entre high et low
        avg_curr = (data[i][col1] + data[i][col2]) / 2.0 
        returns.append(math.log(avg_curr / avg_prev))
    return returns

def hurst(returns):
    n = len(returns)
    M2 = sum(r**2 for r in returns) / n

    sum_agg = 0.0
    for i in range(0, n-1, 2):
        sum_agg += (returns[i] + returns[i+1])**2
    M2_prime = sum_agg / ((n-1) // 2)

    return 0.5 * math.log(M2_prime / M2) / math.log(2)

def volatility(returns):
    n = len(returns)
    mean = sum(returns) / n

    sum_sq_dev = 0.0
    for r in returns:
        sum_sq_dev += (r - mean) ** 2

    variance = sum_sq_dev / (n - 1)
    return math.sqrt(variance)

print("QUESTION E")
print()

data = read_fx_data("../data/Dataset TD5.csv")
gbp = get_returns(data, 0, 1)
sek = get_returns(data, 2, 3)
cad = get_returns(data, 4, 5)

H_gbp = hurst(gbp)
H_sek = hurst(sek)
H_cad = hurst(cad)

vol_gbp = volatility(gbp)
vol_sek = volatility(sek)
vol_cad = volatility(cad)

print("Hurst exponents:")
print(f"GBPEUR: {H_gbp:.4f}")
print(f"SEKEUR: {H_sek:.4f}")
print(f"CADEUR: {H_cad:.4f}")
print()

print("Daily volatility:")
print(f"GBPEUR: {vol_gbp:.6f}")
print(f"SEKEUR: {vol_sek:.6f}")
print(f"CADEUR: {vol_cad:.6f}")
print()

print("Annualized volatility:")
print(f"GBPEUR: {vol_gbp * (252 ** H_gbp):.6f}")
print(f"SEKEUR: {vol_sek * (252 ** H_sek):.6f}")
print(f"CADEUR: {vol_cad * (252 ** H_cad):.6f}")
print()
