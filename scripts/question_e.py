import math
import csv

# Data loading functions

def read_forex_data(filename):
    # Read TD5 dataset with forex pairs
    data = {'GBP': [], 'SEK': [], 'CAD': []}

    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')

            # Skip first two rows (header)
            next(reader)
            next(reader)

            for row in reader:
                if len(row) >= 11:
                    try:
                        # GBP HIGH and LOW
                        gbp_high = float(row[1].replace(',', '.'))
                        gbp_low = float(row[2].replace(',', '.'))
                        gbp_mid = (gbp_high + gbp_low) / 2
                        data['GBP'].append(gbp_mid)

                        # SEK HIGH and LOW
                        sek_high = float(row[5].replace(',', '.'))
                        sek_low = float(row[6].replace(',', '.'))
                        sek_mid = (sek_high + sek_low) / 2
                        data['SEK'].append(sek_mid)

                        # CAD HIGH and LOW
                        cad_high = float(row[9].replace(',', '.'))
                        cad_low = float(row[10].replace(',', '.'))
                        cad_mid = (cad_high + cad_low) / 2
                        data['CAD'].append(cad_mid)
                    except (ValueError, IndexError):
                        continue
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        return data

    return data


def get_log_returns(prices):
    # Calculate log returns
    returns = []
    for i in range(1, len(prices)):
        r = math.log(prices[i] / prices[i-1])
        returns.append(r)
    return returns


# Question E: Haar wavelets and Hurst exponent

def haar_transform(data):
    # Haar wavelet transform

    n = len(data)

    # Pad to power of 2
    target = 1
    while target < n:
        target *= 2

    padded = data[:] + [0.0] * (target - n)

    result = padded[:]
    detail = []

    # Haar decomposition
    while len(result) > 1:
        temp = []
        details = []

        for i in range(0, len(result), 2):
            if i + 1 < len(result):
                temp.append((result[i] + result[i+1]) / 2.0)
                details.append((result[i] - result[i+1]) / 2.0)

        result = temp
        detail = details + detail

    return result, detail


def correlation_at_scale(returns1, returns2, scale):
    # Calculate correlation at given scale using Haar wavelets

    # Apply Haar transform
    approx1, detail1 = haar_transform(returns1)
    approx2, detail2 = haar_transform(returns2)

    # Extract coefficients at given scale
    # Scale 0 = finest details, higher scale = coarser details
    n = len(detail1)

    # Determine range for this scale
    block_size = 2 ** scale
    start_idx = max(0, n - block_size)

    coef1 = detail1[start_idx:n]
    coef2 = detail2[start_idx:n]

    # Calculate correlation
    if len(coef1) == 0 or len(coef2) == 0:
        return 0.0

    n_coef = len(coef1)
    mean1 = sum(coef1) / n_coef
    mean2 = sum(coef2) / n_coef

    # Covariance
    cov = sum((coef1[i] - mean1) * (coef2[i] - mean2) for i in range(n_coef))

    # Standard deviations
    var1 = sum((x - mean1)**2 for x in coef1)
    var2 = sum((x - mean2)**2 for x in coef2)

    if var1 == 0 or var2 == 0:
        return 0.0

    correlation = cov / math.sqrt(var1 * var2)

    return correlation


def estimate_hurst_exponent(returns):
    # Hurst exponent using R/S analysis

    n = len(returns)
    mean_ret = sum(returns) / n

    # Cumulative deviation
    cum_sum = 0.0
    cumulative_dev = []
    for r in returns:
        cum_sum += (r - mean_ret)
        cumulative_dev.append(cum_sum)

    # Range
    R = max(cumulative_dev) - min(cumulative_dev) if cumulative_dev else 0.0

    # Std dev
    variance = sum((r - mean_ret)**2 for r in returns) / n
    S = math.sqrt(variance)

    if S == 0:
        return 0.5

    # Hurst: H = log(R/S) / log(n)
    rs_ratio = R / S
    if rs_ratio > 0 and n > 1:
        hurst = math.log(rs_ratio) / math.log(n)
    else:
        hurst = 0.5

    return max(0.0, min(1.0, hurst))


def annualized_volatility(returns, periods_per_year=252):
    # Calculate annualized volatility

    n = len(returns)
    mean_ret = sum(returns) / n

    variance = sum((r - mean_ret)**2 for r in returns) / (n - 1)
    daily_vol = math.sqrt(variance)

    annual_vol = daily_vol * math.sqrt(periods_per_year)

    return annual_vol


# Main program

if __name__ == "__main__":

    print("="*50)
    print("Question E - Wavelets & Hurst")
    print("="*50)

    # Load forex data
    import os
    if os.path.exists("../data/Dataset TD5.csv"):
        filename = "../data/Dataset TD5.csv"
    elif os.path.exists("data/Dataset TD5.csv"):
        filename = "data/Dataset TD5.csv"
    else:
        filename = "../data/Dataset TD5.csv"

    forex_data = read_forex_data(filename)

    if len(forex_data['GBP']) == 0:
        print("Error: no data loaded")
    else:
        print(f"Data points: {len(forex_data['GBP'])}")
        print()

        # Calculate returns for each pair
        gbp_returns = get_log_returns(forex_data['GBP'])
        sek_returns = get_log_returns(forex_data['SEK'])
        cad_returns = get_log_returns(forex_data['CAD'])

        # Part a: Multi-resolution correlation
        print("Part a: Multi-Resolution Correlation")
        print("-"*50)

        scales = [0, 1, 2, 3]

        print("GBP vs SEK:")
        for scale in scales:
            corr = correlation_at_scale(gbp_returns, sek_returns, scale)
            print(f"Scale {scale}: {corr:.4f}")
        print()

        print("GBP vs CAD:")
        for scale in scales:
            corr = correlation_at_scale(gbp_returns, cad_returns, scale)
            print(f"Scale {scale}: {corr:.4f}")
        print()

        print("SEK vs CAD:")
        for scale in scales:
            corr = correlation_at_scale(sek_returns, cad_returns, scale)
            print(f"Scale {scale}: {corr:.4f}")
        print()

        # Part b: Hurst exponent
        print("Part b: Hurst Exponent")
        print("-"*50)

        hurst_gbp = estimate_hurst_exponent(gbp_returns)
        hurst_sek = estimate_hurst_exponent(sek_returns)
        hurst_cad = estimate_hurst_exponent(cad_returns)

        print(f"GBP: H = {hurst_gbp:.4f}")
        print(f"SEK: H = {hurst_sek:.4f}")
        print(f"CAD: H = {hurst_cad:.4f}")
        print()

        # Interpretation
        for name, h in [('GBP', hurst_gbp), ('SEK', hurst_sek), ('CAD', hurst_cad)]:
            if h > 0.5:
                print(f"{name}: trending")
            elif h < 0.5:
                print(f"{name}: mean-reverting")
            else:
                print(f"{name}: random walk")
        print()

        # Part c: Annualized volatility
        print("Part c: Annualized Volatility")
        print("-"*50)

        # Assuming 15-min intervals, ~96 per day, ~24000 per year
        periods = 96 * 252

        vol_gbp = annualized_volatility(gbp_returns, periods)
        vol_sek = annualized_volatility(sek_returns, periods)
        vol_cad = annualized_volatility(cad_returns, periods)

        print(f"GBP: {vol_gbp:.4f} ({vol_gbp*100:.2f}%)")
        print(f"SEK: {vol_sek:.4f} ({vol_sek*100:.2f}%)")
        print(f"CAD: {vol_cad:.4f} ({vol_cad*100:.2f}%)")
        print()

        print("="*50)
