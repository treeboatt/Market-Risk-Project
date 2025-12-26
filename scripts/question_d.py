import math
import csv

# Data loading for Bouchaud model

def read_transaction_data(filename):
    # Read transaction data from TD4 dataset
    transactions = []
    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')

            # Skip header
            next(reader)

            for row in reader:
                if len(row) >= 5:
                    try:
                        time_val = float(row[0].replace(',', '.'))
                        spread = float(row[1].replace(',', '.'))

                        # Volume might be missing
                        if row[2].strip() != '':
                            volume = float(row[2].replace(',', '.'))
                        else:
                            volume = None

                        sign = int(row[3].replace(',', '.'))
                        price = float(row[4].replace(',', '.'))

                        transactions.append({
                            'time': time_val,
                            'spread': spread,
                            'volume': volume,
                            'sign': sign,
                            'price': price
                        })
                    except ValueError:
                        continue
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        return []

    return transactions


# Question D: Bouchaud price impact model

def calculate_returns(transactions):
    # Calculate price returns between transactions
    returns = []
    for i in range(1, len(transactions)):
        price_prev = transactions[i-1]['price']
        price_curr = transactions[i]['price']
        ret = (price_curr - price_prev) / price_prev
        returns.append(ret)
    return returns


def estimate_bouchaud_parameters(transactions):
    # Estimate parameters for Bouchaud model
    # Model: price impact = lambda * sign * volume^delta

    # Calculate price changes
    price_changes = []
    signs = []
    volumes = []

    for i in range(1, len(transactions)):
        price_prev = transactions[i-1]['price']
        price_curr = transactions[i]['price']

        change = price_curr - price_prev
        sign = transactions[i]['sign']
        volume = transactions[i]['volume']

        # Only keep transactions with known volume
        if volume is not None and volume > 0:
            price_changes.append(change)
            signs.append(sign)
            volumes.append(volume)

    # Estimate delta using log-log regression
    # log(|price_change|) = log(lambda) + delta * log(volume)

    n = len(price_changes)

    # Calculate averages for regression
    sum_log_volume = 0.0
    sum_log_impact = 0.0
    count = 0

    for i in range(n):
        impact = abs(price_changes[i])
        vol = volumes[i]

        if impact > 0 and vol > 0:
            sum_log_volume += math.log(vol)
            sum_log_impact += math.log(impact)
            count += 1

    if count > 0:
        mean_log_volume = sum_log_volume / count
        mean_log_impact = sum_log_impact / count

        # Calculate delta (slope)
        numerator = 0.0
        denominator = 0.0

        for i in range(n):
            impact = abs(price_changes[i])
            vol = volumes[i]

            if impact > 0 and vol > 0:
                log_vol = math.log(vol)
                log_imp = math.log(impact)

                numerator += (log_vol - mean_log_volume) * (log_imp - mean_log_impact)
                denominator += (log_vol - mean_log_volume) ** 2

        if denominator > 0:
            delta = numerator / denominator

            # Calculate lambda (intercept)
            log_lambda = mean_log_impact - delta * mean_log_volume
            lambda_param = math.exp(log_lambda)
        else:
            delta = 0.5
            lambda_param = 0.01
    else:
        delta = 0.5
        lambda_param = 0.01

    return lambda_param, delta


def estimate_relaxation_time(transactions):
    # Estimate relaxation time tau
    # Measure how fast price impact decays

    returns = calculate_returns(transactions)

    # Calculate autocorrelation of returns
    n = len(returns)

    # Mean of returns
    mean_ret = sum(returns) / n

    # Variance
    variance = sum((r - mean_ret)**2 for r in returns) / (n - 1)

    # Autocorrelation at lag 1
    autocorr = 0.0
    for i in range(n - 1):
        autocorr += (returns[i] - mean_ret) * (returns[i+1] - mean_ret)

    autocorr = autocorr / ((n - 1) * variance)

    # Estimate tau from autocorrelation
    # autocorr ≈ exp(-dt/tau)
    # Average time between transactions
    time_diffs = []
    for i in range(1, len(transactions)):
        dt = transactions[i]['time'] - transactions[i-1]['time']
        time_diffs.append(dt)

    avg_dt = sum(time_diffs) / len(time_diffs)

    # Calculate tau
    if autocorr > 0 and autocorr < 1:
        tau = -avg_dt / math.log(autocorr)
    else:
        tau = avg_dt

    return tau, autocorr


def estimate_volatility(transactions):
    # Estimate market volatility sigma

    returns = calculate_returns(transactions)
    n = len(returns)

    # Mean return
    mean_ret = sum(returns) / n

    # Variance
    variance = sum((r - mean_ret)**2 for r in returns) / (n - 1)
    volatility = math.sqrt(variance)

    return volatility


# Main program

if __name__ == "__main__":

    print("="*50)
    print("Question D - Bouchaud Model")
    print("="*50)

    # Load transaction data
    import os
    if os.path.exists("../data/Dataset TD4.csv"):
        filename = "../data/Dataset TD4.csv"
    elif os.path.exists("data/Dataset TD4.csv"):
        filename = "data/Dataset TD4.csv"
    else:
        filename = "../data/Dataset TD4.csv"

    transactions = read_transaction_data(filename)

    if len(transactions) == 0:
        print("Error: no transaction data loaded")
    else:
        print(f"Transactions: {len(transactions)}")
        print()

        # Parameter estimation
        print("Parameter Estimation")
        print("-"*50)

        # Lambda and delta
        lambda_param, delta = estimate_bouchaud_parameters(transactions)
        print(f"Lambda: {lambda_param:.6f}")
        print(f"Delta: {delta:.4f}")

        if delta > 0.5:
            print("(strong volume effect)")
        else:
            print("(weak volume effect)")
        print()

        # Tau
        tau, autocorr = estimate_relaxation_time(transactions)
        print(f"Tau: {tau:.6f} days")
        print(f"Autocorr: {autocorr:.4f}")
        print()

        # Volatility
        volatility = estimate_volatility(transactions)
        print(f"Sigma: {volatility:.6f} ({volatility*100:.4f}%)")
        print()

        # Results
        print("Results:")
        print("-"*50)
        print(f"lambda = {lambda_param:.6f}")
        print(f"delta = {delta:.4f}")
        print(f"tau = {tau:.6f} days")
        print(f"sigma = {volatility:.6f}")
        print()

        print("="*50)
