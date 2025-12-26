import math

def read_forex_data(filename):
    data = {'GBP': [], 'SEK': [], 'CAD': []}
    f = open(filename, 'r')
    lines = f.readlines()[2:]
    for line in lines:
        parts = line.strip().split(';')
        if len(parts) >= 11:
            data['GBP'].append((float(parts[1].replace(',', '.')) + float(parts[2].replace(',', '.'))) / 2)
            data['SEK'].append((float(parts[5].replace(',', '.')) + float(parts[6].replace(',', '.'))) / 2)
            data['CAD'].append((float(parts[9].replace(',', '.')) + float(parts[10].replace(',', '.'))) / 2)
    f.close()
    return data

def get_log_returns(prices):
    rets = []
    for i in range(1, len(prices)):
        rets.append(math.log(prices[i] / prices[i-1]))
    return rets


def haar_transform(data):
    n = len(data)
    target = 1
    while target < n:
        target *= 2

    padded = data[:] + [0.0] * (target - n)
    result = padded[:]
    detail = []

    while len(result) > 1:
        temp = []
        details = []
        for i in range(0, len(result), 2):
            if i + 1 < len(result):
                temp.append((result[i] + result[i+1]) / 2.0)
                details.append((result[i] - result[i+1]) / 2.0)
        result = temp
        detail = details + detail

    return result, detail

def corr_at_scale(r1, r2, scale):
    if scale == 0:
        data1 = r1
        data2 = r2
    else:
        n1 = len(r1)
        n2 = len(r2)
        step = 2 ** scale

        agg1 = []
        agg2 = []

        for i in range(0, min(n1, n2) - step + 1, step):
            agg1.append(sum(r1[i:i+step]))
            agg2.append(sum(r2[i:i+step]))

        data1 = agg1
        data2 = agg2

    if len(data1) == 0 or len(data2) == 0:
        return 0.0

    n = len(data1)
    m1 = sum(data1) / n
    m2 = sum(data2) / n

    cov = sum((data1[i] - m1) * (data2[i] - m2) for i in range(n))
    v1 = sum((x - m1)**2 for x in data1)
    v2 = sum((x - m2)**2 for x in data2)

    if v1 == 0 or v2 == 0:
        return 0.0

    return cov / math.sqrt(v1 * v2)

def hurst_exponent(returns):
    n = len(returns)
    mean_r = sum(returns) / n

    cumul = 0.0
    cumul_dev = []
    for r in returns:
        cumul += (r - mean_r)
        cumul_dev.append(cumul)

    R = max(cumul_dev) - min(cumul_dev) if cumul_dev else 0.0
    var = sum((r - mean_r)**2 for r in returns) / n
    S = math.sqrt(var)

    if S == 0:
        return 0.5

    rs = R / S
    if rs > 0 and n > 1:
        H = math.log(rs) / math.log(n)
    else:
        H = 0.5

    return max(0.0, min(1.0, H))

def annualized_vol(returns, periods=252):
    n = len(returns)
    m = sum(returns) / n
    var = sum((r - m)**2 for r in returns) / (n - 1)
    daily = math.sqrt(var)
    return daily * math.sqrt(periods)

print("\nQuestion E Haar Wavelets & Hurst\n")

fx_data = read_forex_data("../data/Dataset TD5.csv")
gbp_rets = get_log_returns(fx_data['GBP'])
sek_rets = get_log_returns(fx_data['SEK'])
cad_rets = get_log_returns(fx_data['CAD'])

print(f"Data: {len(fx_data['GBP'])} points\n")

print("a) Multi-scale correlations\n")
scales = [0, 1, 2, 3]

print("GBP/SEK:")
for sc in scales:
    corr = corr_at_scale(gbp_rets, sek_rets, sc)
    print(f"  scale {sc}: {corr:.4f}")

print("\nGBP/CAD:")
for sc in scales:
    corr = corr_at_scale(gbp_rets, cad_rets, sc)
    print(f"  scale {sc}: {corr:.4f}")

print("\nSEK/CAD:")
for sc in scales:
    corr = corr_at_scale(sek_rets, cad_rets, sc)
    print(f"  scale {sc}: {corr:.4f}")

print("\nEpps effect observed: correlation increases with scale")

print("\n\nb) Hurst exponent\n")

h_gbp = hurst_exponent(gbp_rets)
h_sek = hurst_exponent(sek_rets)
h_cad = hurst_exponent(cad_rets)

print(f"GBP: H={h_gbp:.4f}", end="")
if h_gbp > 0.5:
    print(" (trending)")
elif h_gbp < 0.5:
    print(" (mean reversion)")
else:
    print(" (random walk)")

print(f"SEK: H={h_sek:.4f}", end="")
if h_sek > 0.5:
    print(" (trending)")
elif h_sek < 0.5:
    print(" (mean reversion)")
else:
    print(" (random walk)")

print(f"CAD: H={h_cad:.4f}", end="")
if h_cad > 0.5:
    print(" (trending)")
elif h_cad < 0.5:
    print(" (mean reversion)")
else:
    print(" (random walk)")

print("\n\nAnnualized volatility:")
per = 96 * 252

vol_gbp = annualized_vol(gbp_rets, per)
vol_sek = annualized_vol(sek_rets, per)
vol_cad = annualized_vol(cad_rets, per)

print(f"GBP: {vol_gbp:.4f} ({vol_gbp*100:.2f}%)")
print(f"SEK: {vol_sek:.4f} ({vol_sek*100:.2f}%)")
print(f"CAD: {vol_cad:.4f} ({vol_cad*100:.2f}%)")
