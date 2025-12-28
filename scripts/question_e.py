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

def haar_wavelet(data, j_max):
    approx = list(data)
    details = {}
    for j in range(j_max):
        new_approx = []
        detail = []
        for k in range(0, len(approx) - 1, 2):
            new_approx.append((approx[k] + approx[k+1]) / math.sqrt(2))
            detail.append((approx[k] - approx[k+1]) / math.sqrt(2))
        details[j+1] = detail
        approx = new_approx
    return details

def correlation(dx, dy):
    sum_xy = sum_xx = sum_yy = 0.0
    for k in range(len(dx)):
        sum_xy += dx[k] * dy[k]
        sum_xx += dx[k] * dx[k]
        sum_yy += dy[k] * dy[k]
    return sum_xy / math.sqrt(sum_xx * sum_yy)

def hurst(returns):
    n = len(returns)
    M2 = sum(r**2 for r in returns) / n
    M2_prime = sum((returns[i] + returns[i+1])**2 for i in range(0, n-1, 2)) / ((n-1) // 2)
    return 0.5 * math.log(M2_prime / M2) / math.log(2)

def volatility(returns):
    n = len(returns)
    mean = sum(returns) / n
    return math.sqrt(sum((r - mean)**2 for r in returns) / (n - 1))


print("QUESTION E\n")

data = read_fx_data("../data/Dataset TD5.csv")
gbp = get_returns(data, 0, 1)
sek = get_returns(data, 2, 3)
cad = get_returns(data, 4, 5)

print("Part a) Multiresolution correlation with Haar wavelets\n")

gbp_d = haar_wavelet(gbp, 4)
sek_d = haar_wavelet(sek, 4)
cad_d = haar_wavelet(cad, 4)

pairs = [("GBPEUR vs SEKEUR", gbp_d, sek_d), ("GBPEUR vs CADEUR", gbp_d, cad_d), ("SEKEUR vs CADEUR", sek_d, cad_d)]
for name, d1, d2 in pairs:
    print(f"{name}:")
    for j in range(1, 5):
        print(f"  j={j} ({2**j} days): rho = {correlation(d1[j], d2[j]):.4f}")
    print()

print("Part b) Hurst exponent and annualized volatility\n")

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
