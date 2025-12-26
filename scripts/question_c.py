import math
import csv

# Data loading functions

def read_csv_manual(filename):
    # Read Natixis prices from CSV
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
    # Log returns calculation
    returns = []
    for i in range(1, len(prices)):
        r = math.log(prices[i] / prices[i-1])
        returns.append(r)
    return returns


# Question C: Extreme Value Theory with Pickands estimator

def extract_block_maxima(data, block_size):
    # Extract maximum from each block for GEV fitting
    # Used for right tail (extreme gains)
    maxima = []
    num_blocks = len(data) // block_size

    for i in range(num_blocks):
        start_idx = i * block_size
        end_idx = start_idx + block_size
        block = data[start_idx:end_idx]
        if len(block) > 0:
            maxima.append(max(block))

    return maxima


def extract_block_minima(data, block_size):
    # Extract minimum from each block for GEV fitting
    # Used for left tail (extreme losses)
    minima = []
    num_blocks = len(data) // block_size

    for i in range(num_blocks):
        start_idx = i * block_size
        end_idx = start_idx + block_size
        block = data[start_idx:end_idx]
        if len(block) > 0:
            minima.append(min(block))

    return minima


def pickands_estimator(extremes):
    # Pickands estimator for GEV shape parameter xi
    # Based on quantiles of extreme values

    n = len(extremes)
    extremes_sorted = sorted(extremes)

    # Calculate quantiles for Pickands estimator
    # Using k = n/4 as recommended
    k = n // 4

    if k < 1:
        k = 1

    # Get empirical quantiles
    # X_{n-k}, X_{n-2k}, X_{n-4k}
    idx_1 = n - k - 1
    idx_2 = n - 2*k - 1
    idx_3 = n - 4*k - 1

    # Make sure indices are valid
    if idx_3 < 0:
        idx_3 = 0
    if idx_2 < 0:
        idx_2 = 0

    x1 = extremes_sorted[idx_1]
    x2 = extremes_sorted[idx_2]
    x3 = extremes_sorted[idx_3]

    # Pickands formula for xi
    numerator = x1 - x2
    denominator = x2 - x3

    if denominator != 0 and numerator > 0:
        ratio = numerator / denominator
        if ratio > 0:
            xi_estimate = (1.0 / math.log(2.0)) * math.log(ratio)
        else:
            xi_estimate = 0.0
    else:
        xi_estimate = 0.0

    return xi_estimate


def estimate_gev_parameters(extremes):
    # Estimate GEV parameters: xi (shape), mu (location), sigma (scale)

    xi = pickands_estimator(extremes)

    # Estimate mu and sigma using simple method of moments
    n = len(extremes)
    mean_extremes = sum(extremes) / n

    # Calculate variance
    variance = sum((x - mean_extremes)**2 for x in extremes) / (n - 1)
    std_extremes = math.sqrt(variance)

    # Simple approximation for sigma
    # Using empirical relationship
    sigma = std_extremes * 0.78

    # Estimate mu from mean and shape
    mu = mean_extremes - 0.577 * sigma

    return xi, mu, sigma


def var_evt(xi, mu, sigma, alpha):
    # Calculate VaR using GEV quantile formula
    # VaR_alpha = mu - (sigma/xi) * (1 - (-log(1-alpha))^(-xi))

    if abs(xi) > 0.01:
        # General case
        log_term = -math.log(1 - alpha)
        var_value = mu - (sigma / xi) * (1 - log_term**(-xi))
    else:
        # Gumbel case (xi ~= 0)
        var_value = mu - sigma * math.log(-math.log(1 - alpha))

    return var_value


# Main program

if __name__ == "__main__":

    print("="*50)
    print("Question C - Extreme Value Theory")
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
        # Calculate returns
        returns = get_returns(prices_all)
        print(f"Total returns: {len(returns)}")
        print()

        # Part a: GEV parameter estimation
        print("Part a: GEV Parameters (Pickands)")
        print("-"*50)

        block_size = 20

        # Right tail (gains)
        print("Right Tail:")
        maxima = extract_block_maxima(returns, block_size)
        print(f"Block maxima: {len(maxima)}")

        xi_right, mu_right, sigma_right = estimate_gev_parameters(maxima)
        print(f"xi: {xi_right:.4f}")
        print(f"mu: {mu_right:.6f}")
        print(f"sigma: {sigma_right:.6f}")

        if xi_right < 0:
            print("Bounded distribution")
        elif xi_right > 0:
            print("Heavy tail")
        else:
            print("Gumbel type")
        print()

        # Left tail (losses)
        print("Left Tail:")
        minima = extract_block_minima(returns, block_size)
        print(f"Block minima: {len(minima)}")

        losses = [-x for x in minima]
        xi_left, mu_left, sigma_left = estimate_gev_parameters(losses)
        print(f"xi: {xi_left:.4f}")
        print(f"mu: {-mu_left:.6f}")
        print(f"sigma: {sigma_left:.6f}")

        if xi_left < 0:
            print("Bounded distribution")
        elif xi_left > 0:
            print("Heavy tail")
        else:
            print("Gumbel type")
        print()

        # Part b: VaR using EVT
        print("Part b: VaR (EVT)")
        print("-"*50)

        confidence_levels = [0.90, 0.95, 0.99, 0.995]

        print("VaR (Left Tail):")
        for conf in confidence_levels:
            alpha = 1 - conf
            var_loss = var_evt(xi_left, -mu_left, sigma_left, conf)
            print(f"{conf*100:.1f}%: {var_loss:.6f} ({var_loss*100:.4f}%)")

        print()
        print("="*50)
