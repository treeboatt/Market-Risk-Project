import math
import csv

def read_csv(filename):
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
        return (15.0/16.0) * ((1 - u*u) ** 2)
    return 0.0

def compute_bandwidth(data):
    n = len(data)
    mean_val = sum(data) / n
    variance = sum((x - mean_val)**2 for x in data) / (n - 1)
    std_dev = math.sqrt(variance)
    h = 1.06 * std_dev * (n ** (-0.2))
    return h

def kernel_density(x, data, h):
    n = len(data)
    total = 0.0
    for xi in data:
        u = (x - xi) / h
        total += biweight_kernel(u)
    return total / (n * h)

def var_kernel(returns, alpha=0.05):
    h = compute_bandwidth(returns)
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

def expected_shortfall(returns, alpha=0.05):
    var_val = var_kernel(returns, alpha)
    tail_losses = []
    for r in returns:
        if r < var_val:
            tail_losses.append(r)

    if len(tail_losses) > 0:
        es = sum(tail_losses) / len(tail_losses)
    else:
        es = var_val
    return es

print("\nQuestion B Expected Shortfall\n")

import os
if os.path.exists("../data/Natixis.csv"):
    filename = "../data/Natixis.csv"
else:
    filename = "data/Natixis.csv"

all_prices, all_dates = read_csv(filename)
train_prices = filter_by_year(all_prices, all_dates, 2015, 2016)
train_rets = get_returns(train_prices)

alpha = 0.05
var_val = var_kernel(train_rets, alpha)
es_val = expected_shortfall(train_rets, alpha)

print(f"Period 2015-2016: {len(train_rets)} returns")
print(f"Alpha = {alpha}\n")
print(f"VaR = {var_val:.6f} ({var_val*100:.4f}%)")
print(f"ES  = {es_val:.6f} ({es_val*100:.4f}%)")
print(f"\nDifference: {abs(es_val - var_val):.6f}")
print(f"Ratio ES/VaR: {abs(es_val/var_val):.4f}")

if abs(es_val) > abs(var_val):
    print("=> ES is higher than VaR")
else:
    print("=> ES close to VaR")
