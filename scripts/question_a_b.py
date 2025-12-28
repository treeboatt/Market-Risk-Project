import math

def read_csv(filename):
    prices = []
    dates = []
    f = open(filename, 'r')
    for line in f:
        parts = line.strip().split(';')
        if len(parts) >= 2:
            dates.append(parts[0])
            prices.append(float(parts[1]))
    f.close()
    return prices, dates

def get_returns(prices):
    returns = []
    for i in range(1, len(prices)):
        r = math.log(prices[i] / prices[i-1])
        returns.append(r)
    return returns

def filter_by_year(prices, dates, start_year, end_year):
    filtered = []
    for i in range(len(prices)):
        date_str = dates[i]
        year = int(date_str.split('/')[2])
        if start_year <= year <= end_year:
            filtered.append(prices[i])
    return filtered

def biweight_kernel(u):
    if abs(u) <= 1:
        return (15/16) * ((1 - u*u) ** 2)
    return 0.0

def bandwidth(data):
    n = len(data)
    m = sum(data) / n
    var = sum((x - m)**2 for x in data) / (n - 1)
    sd = math.sqrt(var)
    h = 1.06 * sd * (n ** (-1.0/5.0))
    return h

def kernel_density(x, data, h):
    n = len(data)
    total = 0.0
    for xi in data:
        u = (x - xi) / h
        total += biweight_kernel(u)
    return total / (n * h)

def var_kernel(returns, alpha=0.05):
    h = bandwidth(returns)
    lower = min(returns)
    upper = max(returns)

    steps = 1000
    dx = (upper - lower) / steps
    x = lower
    cumul = 0.0
    while cumul < alpha and x < upper:
        cumul += kernel_density(x, returns, h) * dx
        x += dx

    return x

def count_violations(returns, threshold):
    return sum(1 for r in returns if r < threshold)

def expected_shortfall(returns, alpha=0.05):
    var_val = var_kernel(returns, alpha)
    tail_losses = []
    for r in returns:
        if r < var_val:
            tail_losses.append(r)

    es = sum(tail_losses) / len(tail_losses)
    return es


print("="*50)
print("QUESTION A")
print("="*50)

all_prices, all_dates = read_csv("../data/Natixis.csv")

train_prices = filter_by_year(all_prices, all_dates, 2015, 2016)
train_returns = get_returns(train_prices)

alpha = 0.05
var_val = var_kernel(train_returns, alpha)
print(f"\nPart a) VaR (2015-2016, alpha={alpha}):")
print(f"VaR = {var_val:.4f}")

test_prices = filter_by_year(all_prices, all_dates, 2017, 2018)
test_returns = get_returns(test_prices)
viols = count_violations(test_returns, var_val)
real_rate = viols / len(test_returns)

print(f"\nPart b) Backtesting (2017-2018):")
print(f"Violations: {viols}/{len(test_returns)} ({real_rate*100:.2f}%)")
print(f"Expected: {alpha*100:.0f}%")
print()


print("="*50)
print("QUESTION B")
print("="*50)

es_val = expected_shortfall(train_returns, alpha)
print(f"\nExpected Shortfall (alpha={alpha}):")
print(f"VaR = {var_val:.4f}")
print(f"ES  = {es_val:.4f}")
print(f"ES/VaR ratio = {abs(es_val/var_val):.2f}")
print()
