import math
import csv

# Data loading and processing functions

def read_csv_manual(filename):
    # Read CSV file with Natixis prices
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
    # Filter prices by year range
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


# Question A: Non-parametric VaR with biweight kernel

def biweight_kernel(u):
    # Biweight kernel function from TD1
    abs_u = abs(u)
    if abs_u <= 1:
        factor = 1 - u*u
        kernel_val = (15.0/16.0) * (factor * factor)
        return kernel_val
    else:
        return 0.0


def compute_bandwidth(data):
    # Silverman's rule: h = 1.06 * std * n^(-1/5)
    n = len(data)

    mean_val = sum(data) / n

    # Compute standard deviation manually
    squared_diffs = 0.0
    for x in data:
        diff = x - mean_val
        squared_diffs += diff * diff

    variance = squared_diffs / (n - 1)
    std_dev = math.sqrt(variance)

    # Apply Silverman formula
    bandwidth = 1.06 * std_dev * math.pow(n, -0.2)
    return bandwidth


def kernel_density(x, data, h):
    # Density estimation at point x
    n = len(data)
    total = 0.0
    for xi in data:
        u = (x - xi) / h
        total += biweight_kernel(u)
    density = total / (n * h)
    return density


def var_kernel(returns, alpha=0.05):
    # Calculate VaR at given alpha level using KDE
    h = compute_bandwidth(returns)

    # Integration bounds - use 3*bandwidth on each side
    lower_bound = min(returns) - 3*h
    upper_bound = max(returns) + 3*h

    # Numerical integration parameters
    num_steps = 1000
    step_size = (upper_bound - lower_bound) / num_steps

    # Search for quantile by accumulating probability
    current_x = lower_bound
    cumulative_prob = 0.0

    while cumulative_prob < alpha and current_x < upper_bound:
        density_at_x = kernel_density(current_x, returns, h)
        cumulative_prob += density_at_x * step_size
        current_x += step_size

    var_threshold = current_x
    return var_threshold


def count_violations(returns, threshold):
    # Count returns below VaR threshold
    count = 0
    for r in returns:
        if r < threshold:
            count += 1
    return count


# Main program

if __name__ == "__main__":

    print("="*50)
    print("Question A - Non-parametric VaR")
    print("="*50)

    # Load Natixis data
    # Try relative path from scripts folder first, then from root
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

        # Part a: VaR estimation on 2015-2016
        print("Part a: VaR Estimation (2015-2016)")
        print("-"*50)

        prices_train = filter_by_year(prices_all, dates_all, 2015, 2016)
        returns_train = get_returns(prices_train)
        print(f"Training data: {len(returns_train)} returns")

        # Risk level
        alpha = 0.05
        confidence = (1-alpha)*100
        print(f"Alpha: {alpha} ({confidence}% confidence)")

        # Calculate VaR
        var_value = var_kernel(returns_train, alpha)
        var_percent = var_value * 100
        print(f"VaR: {var_value:.6f} ({var_percent:.4f}%)")
        print()

        # Part b: Backtesting on 2017-2018
        print("Part b: Backtesting (2017-2018)")
        print("-"*50)

        prices_test = filter_by_year(prices_all, dates_all, 2017, 2018)
        returns_test = get_returns(prices_test)
        print(f"Test data: {len(returns_test)} returns")

        # Count violations
        violations = count_violations(returns_test, var_value)
        n_test = len(returns_test)
        actual_violation_rate = violations / n_test
        theoretical_rate = alpha

        print(f"Violations: {violations}")
        print(f"Actual rate: {actual_violation_rate*100:.2f}%")
        print(f"Expected rate: {theoretical_rate*100}%")

        rate_difference = abs(actual_violation_rate - theoretical_rate)
        if rate_difference < 0.02:
            print("Model validated")
        elif actual_violation_rate > theoretical_rate:
            print("Underestimates risk")
        else:
            print("Overestimates risk")

        print()
        print("="*50)
