import math

def read_csv(filename):
    prices = []
    dates = []
    f = open(filename, 'r')
    for line in f:
        parts = line.strip().split(';')
        if len(parts) >= 2:
            dates.append(parts[0])
            prices.append(float(parts[1].replace(',', '.')))
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
        if '/' in date_str:
            year = int(date_str.split('/')[2])
        elif '-' in date_str:
            year = int(date_str.split('-')[0])
        else:
            continue
        if start_year <= year <= end_year:
            filtered.append(prices[i])
    return filtered

def biweight_kernel(u):
    if abs(u) <= 1:
        return 0.9375 * ((1 - u*u) ** 2)
    return 0.0

def bandwidth(data):
    n = len(data)
    m = sum(data) / n
    # variance calculcation
    var = sum((x - m)**2 for x in data) / (n - 1)
    sd = math.sqrt(var)
    h = 1.1 * sd * (n ** -0.2)
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
    lower = min(returns) - 3*h
    upper = max(returns) + 3*h

    steps = 1000
    dx = (upper - lower) / steps
    x = lower
    cumul = 0.0
    while cumul < alpha and x < upper:
        cumul += kernel_density(x, returns, h) * dx
        x += dx

    return x

def count_violations(returns, threshold):
    count = 0
    for r in returns:
        if r < threshold:
            count += 1
    return count


print("\nQuestion A Non parametric VaR\n")
# temp_var = 0

all_prices, all_dates = read_csv("../data/Natixis.csv")
print(f"Loaded data: {len(all_prices)} prices\n")

print("a) VaR estimation (2015-2016)")
train_prices = filter_by_year(all_prices, all_dates, 2015, 2016)
train_returns = get_returns(train_prices)

alpha = 0.05
var_val = var_kernel(train_returns, alpha)
print(f"Number of returns: {len(train_returns)}")
print(f"Alpha = {alpha}")
print(f"VaR = {var_val:.4f} soit {var_val*100:.2f}%\n")

print("b) Backtesting (2017-2018)")
test_prices = filter_by_year(all_prices, all_dates, 2017, 2018)
test_returns = get_returns(test_prices)

viols = count_violations(test_returns, var_val)
n_test = len(test_returns)
real_rate = viols / n_test

print(f"Test returns: {n_test}")
print(f"Violations: {viols}")
print(f"Actual rate: {real_rate*100:.2f}%")
print(f"Expected rate: {alpha*100}%")

diff = abs(real_rate - alpha)
if diff < 0.02:
    print("Model ok")
elif real_rate < alpha:
    print("Underestimates risk")
else:
    print("Overestimates risk")
