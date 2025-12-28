import math

def read_csv(filename):
    prices = []
    f = open(filename, 'r')
    for line in f:
        parts = line.strip().split(';')
        if len(parts) >= 2:
            prices.append(float(parts[1]))
    f.close()
    return prices

def get_returns(prices):
    returns = []
    for i in range(1, len(prices)):
        r = math.log(prices[i] / prices[i-1])
        returns.append(r)
    return returns

def get_blocks(data, bs, use_max=True):
    blocks = []
    nb = len(data) // bs
    for i in range(nb):
        block = data[i*bs:(i+1)*bs]
        blocks.append(max(block) if use_max else min(block))
    return blocks

def pickands(extremes):
    n = len(extremes)
    extremes_sorted = sorted(extremes)

    k = max(1, n // 4)

    x1 = extremes_sorted[n - k - 1]
    x2 = extremes_sorted[n - 2*k - 1]
    x3 = extremes_sorted[max(0, n - 4*k - 1)]

    if x2 - x3 > 0 and x1 - x2 > 0:
        xi = math.log((x1 - x2) / (x2 - x3)) / math.log(2)
    else:
        xi = 0.0

    return xi

def get_gev_params(extremes):
    xi = pickands(extremes)

    n = len(extremes)
    mean_ext = sum(extremes) / n
    var_ext = sum((x - mean_ext)**2 for x in extremes) / (n - 1)

    if xi == 0:
        sigma = math.sqrt(6 * var_ext) / math.pi
        mu = mean_ext - 0.5772 * sigma
    else:
        g1 = math.gamma(1 - xi)
        g2 = math.gamma(1 - 2*xi)
        sigma = abs(xi) * math.sqrt(var_ext) / math.sqrt(g2 - g1**2)
        mu = mean_ext - (g1 - 1) * sigma / xi

    return xi, mu, sigma

def var_evt(xi, mu, sigma, p):
    log_term = -math.log(1 - p)
    var_val = mu - (sigma / xi) * (1 - log_term**(-xi))
    return var_val

print("\nQuestion C Extreme Value Theory\n")

all_prices = read_csv("../data/Natixis.csv")
rets = get_returns(all_prices)
print(f"Total returns: {len(rets)}\n")

print("a) GEV parameters with Pickands\n")
bs = 20

print("Right tail (gains):")
max_vals = get_blocks(rets, bs, use_max=True)
xi_r, mu_r, sig_r = get_gev_params(max_vals)
print(f"Blocks: {len(max_vals)}")
print(f"xi={xi_r:.3f}, mu={mu_r:.4f}, sigma={sig_r:.4f}")

if xi_r < 0:
    print("Bounded distribution")
elif xi_r > 0:
    print("Heavy tail")
else:
    print("Gumbel type")

print("\nLeft tail (losses):")
min_vals = get_blocks(rets, bs, use_max=False)
losses = [-x for x in min_vals]
xi_l, mu_l, sig_l = get_gev_params(losses)
print(f"Blocks: {len(min_vals)}")
print(f"xi={xi_l:.3f}, mu={-mu_l:.4f}, sigma={sig_l:.4f}")

if xi_l < 0:
    print("Bounded distribution")
elif xi_l > 0:
    print("Heavy tail")
else:
    print("Gumbel type")

print("\n\nb) VaR with EVT\n")
levels = [0.90, 0.95, 0.99, 0.995]

print("VaR losses:")
for lv in levels:
    var_loss = var_evt(xi_l, -mu_l, sig_l, lv)
    print(f"  {lv*100:.1f}%: {var_loss:.6f} ({var_loss*100:.4f}%)")
