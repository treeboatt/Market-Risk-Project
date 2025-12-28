import math

def read_transaction_data(filename):
    transactions = []
    f = open(filename, 'r', encoding='utf-8')
    next(f)
    for line in f:
        parts = line.strip().split(';')
        if len(parts) >= 5:
            spread = float(parts[1])
            vol = float(parts[2]) if parts[2].strip() else None
            price = float(parts[4])
            transactions.append({'spread': spread, 'volume': vol, 'price': price})
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

        impact = abs((p1 - p0) / spread)

        if vol is not None:
            log_vols.append(math.log(vol))
            log_impacts.append(math.log(impact))

    n = len(log_vols)
    mean_vols = sum(log_vols) / n
    mean_impacts = sum(log_impacts) / n

    cov = sum((log_vols[i] - mean_vols) * (log_impacts[i] - mean_impacts) for i in range(n)) / n
    var_vols = sum((x - mean_vols)**2 for x in log_vols) / n

    r = cov / var_vols
    V = math.exp(mean_impacts - r * mean_vols)

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

print("QUESTION D: Bouchaud Market Impact Model")

trans = read_transaction_data("../data/Dataset TD4.csv")
print(f"\nDataset: {len(trans)} transactions")

V, r = get_impact_params(trans)
gamma = get_gamma(trans)

print(f"  V = {V:.4f}")
print(f"  r = {r:.3f}")
print(f"  gamma = {gamma:.3f}")
