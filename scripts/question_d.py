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

def get_bouchaud_params(transactions):
    log_vols = []
    log_impacts = []

    for i in range(1, len(transactions)):
        p0 = transactions[i-1]['price']
        p1 = transactions[i]['price']
        impact = abs(p1 - p0)
        vol = transactions[i]['volume']

        if vol is not None and vol > 0 and impact > 0:
            log_vols.append(math.log(vol))
            log_impacts.append(math.log(impact))

    n = len(log_vols)
    if n == 0:
        return 0.01, 0.5

    mean_v = sum(log_vols) / n
    mean_i = sum(log_impacts) / n

    cov = sum((log_vols[i] - mean_v) * (log_impacts[i] - mean_i) for i in range(n)) / n
    var_v = sum((lv - mean_v)**2 for lv in log_vols) / n

    if var_v > 0:
        delta = cov / var_v
        lam = math.exp(mean_i - delta * mean_v)
    else:
        delta = 0.5
        lam = 0.01

    return lam, delta

def get_tau_sigma(transactions):
    rets = calc_returns(transactions)
    n = len(rets)

    mean_r = sum(rets) / n
    var = sum((r - mean_r)**2 for r in rets) / (n - 1)

    autocorr = sum((rets[i] - mean_r) * (rets[i+1] - mean_r) for i in range(n - 1)) / ((n - 1) * var)

    avg_dt = sum(transactions[i]['time'] - transactions[i-1]['time'] for i in range(1, len(transactions))) / (len(transactions) - 1)

    if 0 < autocorr < 1:
        tau = -avg_dt / math.log(autocorr)
    else:
        tau = avg_dt

    sigma = math.sqrt(var)

    return tau, autocorr, sigma

print("\nQuestion D Bouchaud Model\n")


trans = read_transaction_data("../data/Dataset TD4.csv")
print(f"Transactions: {len(trans)}\n")

lam, delta = get_bouchaud_params(trans)
tau, ac, sig = get_tau_sigma(trans)

print("Results:")
print(f"lambda = {lam:.4f}")
print(f"delta = {delta:.3f}", end="")
if delta > 0.5:
    print(" (strong volume effect)")
else:
    print(" (weak volume effect)")

print(f"tau = {tau:.4f} days")
print(f"sigma = {sig:.4f} soit {sig*100:.2f}%")
print(f"\nAutocorrelation: {ac:.3f}")

print("\nModel", end=" ")
if 0.3 < delta < 0.7 and tau > 0:
    print("ok")
else:
    print("needs adjustments")
