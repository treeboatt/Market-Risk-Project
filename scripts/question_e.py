import math

def read_fx_data(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()

    gbp_high = []
    gbp_low = []
    sek_high = []
    sek_low = []
    cad_high = []
    cad_low = []

    for i in range(2, len(lines)):
        parts = lines[i].strip().split(';')
        if len(parts) >= 11:
            gbp_high.append(float(parts[1]))
            gbp_low.append(float(parts[2]))
            sek_high.append(float(parts[5]))
            sek_low.append(float(parts[6]))
            cad_high.append(float(parts[9]))
            cad_low.append(float(parts[10]))

    return gbp_high, gbp_low, sek_high, sek_low, cad_high, cad_low

def get_average_price(high, low):
    avg = []
    for i in range(len(high)):
        avg.append((high[i] + low[i]) / 2.0)
    return avg

def get_returns(prices):
    returns = []
    for i in range(1, len(prices)):
        r = math.log(prices[i] / prices[i-1])
        returns.append(r)
    return returns

def haar_wavelet(data, j_max):
    approximation = list(data)
    details = {}

    for j in range(j_max):
        new_approx = []
        detail = []

        for k in range(0, len(approximation) - 1, 2):
            a_k = (approximation[k] + approximation[k+1]) / math.sqrt(2)
            d_k = (approximation[k] - approximation[k+1]) / math.sqrt(2)
            new_approx.append(a_k)
            detail.append(d_k)

        details[j+1] = detail
        approximation = new_approx

    return details

def multiresolution_correlation(details_x, details_y, j):
    dx = details_x[j]
    dy = details_y[j]

    sum_xy = 0.0
    sum_xx = 0.0
    sum_yy = 0.0

    for k in range(len(dx)):
        sum_xy += dx[k] * dy[k]
        sum_xx += dx[k] * dx[k]
        sum_yy += dy[k] * dy[k]

    rho = sum_xy / math.sqrt(sum_xx * sum_yy)
    return rho

def hurst_exponent(returns):
    n = len(returns)

    sum_r2 = 0.0
    for i in range(n):
        sum_r2 += returns[i] ** 2
    M2 = sum_r2 / n

    sum_r2_prime = 0.0
    count = 0
    for i in range(0, n-1, 2):
        diff = returns[i] + returns[i+1]
        sum_r2_prime += diff ** 2
        count += 1
    M2_prime = sum_r2_prime / count

    H = 0.5 * math.log(M2_prime / M2) / math.log(2)
    return H



print("QUESTION E")
print()

gbp_h, gbp_l, sek_h, sek_l, cad_h, cad_l = read_fx_data("../data/Dataset TD5.csv")

gbp_avg = get_average_price(gbp_h, gbp_l)
sek_avg = get_average_price(sek_h, sek_l)
cad_avg = get_average_price(cad_h, cad_l)

gbp_ret = get_returns(gbp_avg)
sek_ret = get_returns(sek_avg)
cad_ret = get_returns(cad_avg)

print("Part a) Multiresolution correlation with Haar wavelets")
print()

j_max = 4

gbp_details = haar_wavelet(gbp_ret, j_max)
sek_details = haar_wavelet(sek_ret, j_max)
cad_details = haar_wavelet(cad_ret, j_max)

print("GBPEUR vs SEKEUR:")
for j in range(1, j_max+1):
    rho = multiresolution_correlation(gbp_details, sek_details, j)
    print(f"  j={j} ({2**j} days): rho = {rho:.4f}")
print()

print("GBPEUR vs CADEUR:")
for j in range(1, j_max+1):
    rho = multiresolution_correlation(gbp_details, cad_details, j)
    print(f"  j={j} ({2**j} days): rho = {rho:.4f}")
print()

print("SEKEUR vs CADEUR:")
for j in range(1, j_max+1):
    rho = multiresolution_correlation(sek_details, cad_details, j)
    print(f"  j={j} ({2**j} days): rho = {rho:.4f}")
print()

print("Part b) Hurst exponent and annualized volatility")
print()

H_gbp = hurst_exponent(gbp_ret)
H_sek = hurst_exponent(sek_ret)
H_cad = hurst_exponent(cad_ret)

print(f"Hurst exponents:")
print(f"  GBPEUR: H = {H_gbp:.4f}")
print(f"  SEKEUR: H = {H_sek:.4f}")
print(f"  CADEUR: H = {H_cad:.4f}")
print()

mean_gbp = sum(gbp_ret) / len(gbp_ret)
var_gbp = sum((r - mean_gbp)**2 for r in gbp_ret) / (len(gbp_ret) - 1)
vol_daily_gbp = math.sqrt(var_gbp)

mean_sek = sum(sek_ret) / len(sek_ret)
var_sek = sum((r - mean_sek)**2 for r in sek_ret) / (len(sek_ret) - 1)
vol_daily_sek = math.sqrt(var_sek)

mean_cad = sum(cad_ret) / len(cad_ret)
var_cad = sum((r - mean_cad)**2 for r in cad_ret) / (len(cad_ret) - 1)
vol_daily_cad = math.sqrt(var_cad)

vol_annual_gbp = vol_daily_gbp * (252 ** H_gbp)
vol_annual_sek = vol_daily_sek * (252 ** H_sek)
vol_annual_cad = vol_daily_cad * (252 ** H_cad)

print(f"Daily volatility:")
print(f"  GBPEUR: {vol_daily_gbp:.6f}")
print(f"  SEKEUR: {vol_daily_sek:.6f}")
print(f"  CADEUR: {vol_daily_cad:.6f}")
print()

print(f"Annualized volatility (using Hurst exponent):")
print(f"  GBPEUR: {vol_annual_gbp:.6f}")
print(f"  SEKEUR: {vol_annual_sek:.6f}")
print(f"  CADEUR: {vol_annual_cad:.6f}")
print()
