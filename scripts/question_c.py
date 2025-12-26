import math
import csv

def read_csv_manual(filename):
    prices = []
    dates = []
    with open(filename, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if len(row) >= 2:
                try:
                    date = row[0]
                    price_str = row[1].replace(',', '.')
                    prices.append(float(price_str))
                    dates.append(date)
                except ValueError:
                    continue
    return prices, dates

def get_returns(prices):
    returns = []
    for i in range(1, len(prices)):
        r = math.log(prices[i] / prices[i-1])
        returns.append(r)
    return returns

def extract_block_maxima(data, bs):
    maxima = []
    nb = len(data) // bs
    for i in range(nb):
        block = data[i*bs:(i+1)*bs]
        if len(block) > 0:
            maxima.append(max(block))
    return maxima

def extract_block_minima(data, bs):
    minima = []
    nb = len(data) // bs
    for i in range(nb):
        block = data[i*bs:(i+1)*bs]
        if len(block) > 0:
            minima.append(min(block))
    return minima

def pickands_estimator(extremes):
    n = len(extremes)
    extremes_sorted = sorted(extremes)

    k = n // 4
    if k < 1:
        k = 1

    idx1 = n - k - 1
    idx2 = n - 2*k - 1
    idx3 = n - 4*k - 1

    if idx3 < 0:
        idx3 = 0
    if idx2 < 0:
        idx2 = 0

    x1 = extremes_sorted[idx1]
    x2 = extremes_sorted[idx2]
    x3 = extremes_sorted[idx3]

    num = x1 - x2
    denom = x2 - x3

    if denom != 0 and num > 0:
        ratio = num / denom
        if ratio > 0:
            xi = math.log(ratio) / math.log(2.0)
        else:
            xi = 0.0
    else:
        xi = 0.0

    return xi

def estimate_gev_params(extremes):
    xi = pickands_estimator(extremes)

    n = len(extremes)
    mean_ext = sum(extremes) / n
    var = sum((x - mean_ext)**2 for x in extremes) / (n - 1)
    std_ext = math.sqrt(var)

    sigma = std_ext * 0.78
    mu = mean_ext - 0.577 * sigma

    return xi, mu, sigma

def var_evt(xi, mu, sigma, alpha):
    if abs(xi) > 0.01:
        log_term = -math.log(1 - alpha)
        var_val = mu - (sigma / xi) * (1 - log_term**(-xi))
    else:
        var_val = mu - sigma * math.log(-math.log(1 - alpha))
    return var_val

if __name__ == "__main__":
    print("\nQuestion C - Extreme Value Theory\n")

    import os
    if os.path.exists("../data/Natixis.csv"):
        filename = "../data/Natixis.csv"
    else:
        filename = "data/Natixis.csv"

    all_prices, all_dates = read_csv_manual(filename)
    rets = get_returns(all_prices)
    print(f"Total returns: {len(rets)}\n")

    # part a
    print("a) GEV parameters with Pickands\n")
    bs = 20

    print("Right tail (gains):")
    max_vals = extract_block_maxima(rets, bs)
    xi_r, mu_r, sig_r = estimate_gev_params(max_vals)
    print(f"Blocks: {len(max_vals)}")
    print(f"xi={xi_r:.4f}, mu={mu_r:.6f}, sigma={sig_r:.6f}")

    if xi_r < 0:
        print("Bounded distribution")
    elif xi_r > 0:
        print("Heavy tail")
    else:
        print("Gumbel type")

    print("\nLeft tail (losses):")
    min_vals = extract_block_minima(rets, bs)
    losses = [-x for x in min_vals]
    xi_l, mu_l, sig_l = estimate_gev_params(losses)
    print(f"Blocks: {len(min_vals)}")
    print(f"xi={xi_l:.4f}, mu={-mu_l:.6f}, sigma={sig_l:.6f}")

    if xi_l < 0:
        print("Bounded distribution")
    elif xi_l > 0:
        print("Heavy tail")
    else:
        print("Gumbel type")

    # part b
    print("\n\nb) VaR with EVT\n")
    levels = [0.90, 0.95, 0.99, 0.995]

    print("VaR losses:")
    for lv in levels:
        alpha = 1 - lv
        var_loss = var_evt(xi_l, -mu_l, sig_l, lv)
        print(f"  {lv*100:.1f}%: {var_loss:.6f} ({var_loss*100:.4f}%)")
