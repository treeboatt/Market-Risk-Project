import math

def read_transaction_data(filename):
    transactions = []
    f = open(filename, 'r')
    next(f)
    for line in f:
        parts = line.strip().split(';')
        if len(parts) >= 5:
            t = float(parts[0])
            spread = float(parts[1])
            vol = float(parts[2]) if parts[2].strip() else None
            sign = int(parts[3])
            price = float(parts[4])
            transactions.append({'time': t, 'spread': spread, 'volume': vol, 'sign': sign, 'price': price})
    f.close()
    return transactions


def calc_returns(transactions):
    rets = []
    for i in range(1, len(transactions)):
        p0 = transactions[i-1]['price']
        p1 = transactions[i]['price']
        rets.append((p1 - p0) / p0)
    return rets

def get_impact_params(transactions):
    log_vols = []
    log_impacts = []

    for i in range(1, len(transactions)):
        p0 = transactions[i-1]['price']
        p1 = transactions[i]['price']
        spread = transactions[i]['spread']
        vol = transactions[i]['volume']

        impact = abs(p1 - p0)

        if vol is not None and vol > 0 and impact > 0 and spread > 0:
            log_vols.append(math.log(vol))
            log_impacts.append(math.log(impact / spread))

    n = len(log_vols)
    if n == 0:
        return 0.01, 0.5

    mean_X = sum(log_vols) / n
    mean_Y = sum(log_impacts) / n

    cov_XY = sum((log_vols[i] - mean_X) * (log_impacts[i] - mean_Y) for i in range(n)) / n
    var_X = sum((x - mean_X)**2 for x in log_vols) / n

    r = cov_XY / var_X
    V = math.exp(mean_Y - r * mean_X)

    return V, r

def get_gamma(transactions):
    rets = calc_returns(transactions)
    n = len(rets)

    mean_r = sum(rets) / n
    var = sum((r - mean_r)**2 for r in rets) / (n - 1)

    rho_1 = sum((rets[i] - mean_r) * (rets[i+1] - mean_r) for i in range(n - 1)) / ((n - 1) * var)
    rho_2 = sum((rets[i] - mean_r) * (rets[i+2] - mean_r) for i in range(n - 2)) / ((n - 2) * var)

    if rho_1 > 0 and rho_2 > 0:
        gamma = math.log(rho_1 / rho_2) / math.log(2)
    else:
        gamma = 1.0

    return gamma

print("\n" + "="*60)
print("QUESTION D: Bouchaud Market Impact Model")
print("="*60)

trans = read_transaction_data("../data/Dataset TD4.csv")
print(f"\nDataset: {len(trans)} transactions")

V, r = get_impact_params(trans)
gamma = get_gamma(trans)

print("\n--- Impact Model: dp = V x S x Vol^r ---")
print(f"  V (scaling factor) = {V:.4f}")
print(f"  r (volume exponent) = {r:.3f}")

print(f"\n--- Relaxation: G(t) ~ 1/t^gamma ---")
print(f"  gamma = {gamma:.3f}")
