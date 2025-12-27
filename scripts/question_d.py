import math

def read_transaction_data(filename):
    transactions = []
    f = open(filename, 'r')
    lines = f.readlines()[1:]
    for line in lines:
        parts = line.strip().split(';')
        if len(parts) >= 5:
            t = float(parts[0].replace(',', '.'))
            spread = float(parts[1].replace(',', '.'))
            vol = float(parts[2].replace(',', '.')) if parts[2].strip() else None
            sign = int(parts[3])
            price = float(parts[4].replace(',', '.'))
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
    price_chg = []
    vols = []

    for i in range(1, len(transactions)):
        p0 = transactions[i-1]['price']
        p1 = transactions[i]['price']
        chg = p1 - p0
        vol = transactions[i]['volume']

        if vol is not None and vol > 0:
            price_chg.append(chg)
            vols.append(vol)

    n = len(price_chg)
    sum_lv = 0.0
    sum_li = 0.0
    cnt = 0

    for i in range(n):
        imp = abs(price_chg[i])
        v = vols[i]
        if imp > 0 and v > 0:
            sum_lv += math.log(v)
            sum_li += math.log(imp)
            cnt += 1

    if cnt > 0:
        mean_lv = sum_lv / cnt
        mean_li = sum_li / cnt

        num = 0.0
        denom = 0.0
        for i in range(n):
            imp = abs(price_chg[i])
            v = vols[i]
            if imp > 0 and v > 0:
                lv = math.log(v)
                li = math.log(imp)
                num += (lv - mean_lv) * (li - mean_li)
                denom += (lv - mean_lv) ** 2

        if denom > 0:
            delta = num / denom
            log_lam = mean_li - delta * mean_lv
            lam = math.exp(log_lam)
        else:
            delta = 0.5
            lam = 0.01
    else:
        delta = 0.5
        lam = 0.01

    return lam, delta

def get_tau(transactions):
    rets = calc_returns(transactions)
    n = len(rets)

    mean_r = sum(rets) / n
    var = sum((r - mean_r)**2 for r in rets) / (n - 1)

    # compute autocorrelation
    autocorr = 0.0
    for i in range(n - 1):
        autocorr += (rets[i] - mean_r) * (rets[i+1] - mean_r)
    autocorr = autocorr / ((n - 1) * var)

    time_diffs = []
    for i in range(1, len(transactions)):
        dt = transactions[i]['time'] - transactions[i-1]['time']
        time_diffs.append(dt)

    avg_dt = sum(time_diffs) / len(time_diffs)

    if autocorr > 0 and autocorr < 1:
        tau = -avg_dt / math.log(autocorr)
    else:
        tau = avg_dt

    return tau, autocorr

def get_sigma(transactions):
    rets = calc_returns(transactions)
    n = len(rets)
    mean_r = sum(rets) / n
    var = sum((r - mean_r)**2 for r in rets) / (n - 1)
    return math.sqrt(var)

print("\nQuestion D Bouchaud Model\n")


trans = read_transaction_data("../data/Dataset TD4.csv")
print(f"Transactions: {len(trans)}\n")

lam, delta = get_bouchaud_params(trans)
tau, ac = get_tau(trans)
sig = get_sigma(trans)

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
