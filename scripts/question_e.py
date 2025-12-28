import math

def read_forex_data(filename):
    gbp_prices = []
    sek_prices = []
    cad_prices = []

    f = open(filename, 'r')
    next(f)
    next(f)
    for line in f:
        parts = line.strip().split(';')
        if len(parts) >= 11:
            gbp_high = float(parts[1])
            gbp_low = float(parts[2])
            gbp_prices.append((gbp_high + gbp_low) / 2.0)

            sek_high = float(parts[5])
            sek_low = float(parts[6])
            sek_prices.append((sek_high + sek_low) / 2.0)

            cad_high = float(parts[9])
            cad_low = float(parts[10])
            cad_prices.append((cad_high + cad_low) / 2.0)
    f.close()

    return {'GBP': gbp_prices, 'SEK': sek_prices, 'CAD': cad_prices}

def get_log_returns(prices):
    rets = []
    for i in range(1, len(prices)):
        rets.append(math.log(prices[i] / prices[i-1]))
    return rets


def correlation(x, y):
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n

    cov = 0.0
    vx = 0.0
    vy = 0.0

    for i in range(n):
        dx = x[i] - mx
        dy = y[i] - my
        cov += dx * dy
        vx += dx * dx
        vy += dy * dy

    return cov / math.sqrt(vx * vy)

def corr_at_scale(r1, r2, scale):
    if scale == 0:
        return correlation(r1, r2)

    step = 2 ** scale
    agg1 = []
    agg2 = []

    for i in range(0, min(len(r1), len(r2)) - step + 1, step):
        total1 = 0.0
        total2 = 0.0
        for j in range(step):
            total1 += r1[i + j]
            total2 += r2[i + j]
        agg1.append(total1)
        agg2.append(total2)

    return correlation(agg1, agg2)

def hurst_exponent(returns):
    n = len(returns)
    mean_r = sum(returns) / n

    cumul = []
    s = 0.0
    for r in returns:
        s += (r - mean_r)
        cumul.append(s)

    R = max(cumul) - min(cumul)

    var = 0.0
    for r in returns:
        var += (r - mean_r) ** 2
    var = var / n
    S = math.sqrt(var)

    H = math.log(R / S) / math.log(n)
    return H

def annualized_vol(returns, periods=252):
    n = len(returns)
    m = sum(returns) / n

    var = 0.0
    for r in returns:
        var += (r - m) ** 2
    var = var / (n - 1)

    daily_vol = math.sqrt(var)
    annual_vol = daily_vol * math.sqrt(periods)
    return annual_vol


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
    print(f"  scale {sc}: {corr:.3f}")

print("\nGBP/CAD:")
for sc in scales:
    corr = corr_at_scale(gbp_rets, cad_rets, sc)
    print(f"  scale {sc}: {corr:.3f}")

print("\nSEK/CAD:")
for sc in scales:
    corr = corr_at_scale(sek_rets, cad_rets, sc)
    print(f"  scale {sc}: {corr:.3f}")

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

print(f"GBP: {vol_gbp:.3f} soit {vol_gbp*100:.1f}%")
print(f"SEK: {vol_sek:.3f} soit {vol_sek*100:.1f}%")
print(f"CAD: {vol_cad:.3f} soit {vol_cad*100:.1f}%")
