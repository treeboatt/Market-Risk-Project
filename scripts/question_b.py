import math
import csv

# Data loading functions reused from Question A

def read_csv_manual(filename):
    # Read CSV with Natixis prices
    prices = []
    dates = []
    try:
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
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        return [], []

    return prices, dates


def get_returns(prices):
    # Calculate log returns
    returns = []
    for i in range(1, len(prices)):
        r = math.log(prices[i] / prices[i-1])
        returns.append(r)
    return returns


def filter_by_year(prices, dates, start_year, end_year):
    # Filter data by year range
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


# Question B: Expected Shortfall calculation

def biweight_kernel(u):
    # Biweight kernel from Question A
    abs_u = abs(u)
    if abs_u <= 1:
        factor = 1 - u*u
        kernel_val = (15.0/16.0) * (factor * factor)
        return kernel_val
    else:
        return 0.0


def compute_bandwidth(data):
    # Silverman's rule for bandwidth selection
    n = len(data)

    mean_val = sum(data) / n

    # Manual standard deviation calculation
    squared_diffs = 0.0
    for x in data:
        diff = x - mean_val
        squared_diffs += diff * diff

    variance = squared_diffs / (n - 1)
    std_dev = math.sqrt(variance)

    # Bandwidth formula
    bandwidth = 1.06 * std_dev * math.pow(n, -0.2)
    return bandwidth


def kernel_density(x, data, h):
    # Estimate density at point x
    n = len(data)
    total = 0.0
    for xi in data:
        u = (x - xi) / h
        total += biweight_kernel(u)
    density = total / (n * h)
    return density


def var_kernel(returns, alpha=0.05):
    # VaR using kernel density estimation
    h = compute_bandwidth(returns)

    lower_bound = min(returns) - 3*h
    upper_bound = max(returns) + 3*h

    num_steps = 1000
    step_size = (upper_bound - lower_bound) / num_steps

    current_x = lower_bound
    cumulative_prob = 0.0

    while cumulative_prob < alpha and current_x < upper_bound:
        density_at_x = kernel_density(current_x, returns, h)
        cumulative_prob += density_at_x * step_size
        current_x += step_size

    var_threshold = current_x
    return var_threshold


def expected_shortfall_historical(returns, alpha=0.05):
    # ES = average of losses worse than VaR
    # Simpler approach: use empirical returns below VaR

    var_level = var_kernel(returns, alpha)

    # Collect all returns below VaR threshold
    tail_losses = []
    for r in returns:
        if r < var_level:
            tail_losses.append(r)

    # Average of tail losses
    if len(tail_losses) > 0:
        es_value = sum(tail_losses) / len(tail_losses)
    else:
        es_value = var_level

    return es_value


# Main program

if __name__ == "__main__":

    print("="*50)
    print("Question B - Expected Shortfall")
    print("="*50)

    # Load Natixis data
    import os
    if os.path.exists("../data/Natixis.csv"):
        filename = "../data/Natixis.csv"
    elif os.path.exists("data/Natixis.csv"):
        filename = "data/Natixis.csv"
    else:
        filename = "../data/Natixis.csv"

    prices_all, dates_all = read_csv_manual(filename)

    if len(prices_all) == 0:
        print("Error: no data loaded")
    else:
        print(f"Total prices loaded: {len(prices_all)}")
        print()

        # Use 2015-2016 data
        print("Expected Shortfall Calculation (2015-2016)")
        print("-"*50)

        prices_train = filter_by_year(prices_all, dates_all, 2015, 2016)
        returns_train = get_returns(prices_train)
        print(f"Data: {len(returns_train)} returns")

        # Risk level
        alpha = 0.05
        confidence = (1-alpha)*100
        print(f"Alpha: {alpha} ({confidence}% confidence)")
        print()

        # Calculate VaR and ES
        var_value = var_kernel(returns_train, alpha)
        var_percent = var_value * 100

        es_value = expected_shortfall_historical(returns_train, alpha)
        es_percent = es_value * 100

        print(f"VaR: {var_value:.6f} ({var_percent:.4f}%)")
        print(f"ES: {es_value:.6f} ({es_percent:.4f}%)")
        print()

        # Comparison
        print("Comparison:")
        print("-"*50)

        es_var_ratio = abs(es_value / var_value)
        difference = abs(es_value - var_value)
        diff_percent = difference * 100

        print(f"Difference: {difference:.6f} ({diff_percent:.4f}%)")
        print(f"ES/VaR ratio: {es_var_ratio:.4f}")

        if abs(es_value) > abs(var_value):
            print("ES > VaR (tail losses are worse on average)")
        else:
            print("ES close to VaR")

        print()
        print("="*50)
