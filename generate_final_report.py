import zipfile
import os

def create_market_risk_report():
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    zip_filename = os.path.join(downloads_path, "Market_Risk_Report_Final.zip")

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:

        main_tex = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[english]{babel}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{graphicx}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{geometry}
\usepackage{hyperref}
\usepackage{float}
\usepackage{fancyvrb}

\geometry{margin=2.5cm}

\lstset{
    language=Python,
    basicstyle=\ttfamily\footnotesize,
    keywordstyle=\color{blue},
    commentstyle=\color{gray},
    stringstyle=\color{red},
    numbers=left,
    numberstyle=\tiny\color{gray},
    frame=single,
    breaklines=true,
    tabsize=4
}

\DefineVerbatimEnvironment{console}{Verbatim}{
    frame=single,
    fontsize=\footnotesize
}

\title{}
\author{}
\date{}

\begin{document}

\begin{titlepage}
    \begin{center}
        \vspace*{2cm}

        {\huge \textbf{Market Risk Measurement:}}\\[0.5cm]
        {\huge \textbf{Application to Natixis Stock}}\\[1.5cm]

        {\Large Quantitative Finance Project}\\[2cm]

        {\large Lucas Soares \hspace{3cm} Maxime Gruez}\\[0.5cm]
        {\large ESILV - Financial Engineering}\\[0.3cm]
        {\large Academic Year 2025-2026}\\[2cm]

        {\large December 29, 2025}\\[3cm]

        \vfill

        {\large ESILV}

    \end{center}
\end{titlepage}
\newpage

\tableofcontents
\newpage

\section{Introduction}

This project focuses on measuring market risk for Natixis stock using different statistical methods. We implemented everything from scratch in pure Python without external packages like numpy or pandas. The dataset covers daily Natixis prices from 2015 to 2018 (1023 observations total), plus high-frequency forex data for the final question.

We used the 2015-2016 period to build our models and tested them on 2017-2018 data. The main objective was to calculate Value-at-Risk through multiple approaches and compare their results. Each method reveals different aspects of the risk profile, from simple non-parametric estimation to advanced extreme value theory.

\section{Question A: Non-Parametric VaR}

\subsection{Theory}

Value-at-Risk at confidence level $\alpha$ represents the maximum expected loss over a given time period at a specified confidence level. Formally, VaR is defined as the quantile:
\begin{equation}
\text{VaR}_\alpha = \inf\{x : F(x) \geq \alpha\}
\end{equation}

where $F$ is the cumulative distribution function of returns.

Instead of assuming a parametric distribution (like normality), we estimate the density function non-parametrically using the Parzen-Rosenblatt kernel density estimator with the biweight kernel:
\begin{equation}
K(u) = \frac{15}{16}(1-u^2)^2 \mathbb{1}_{|u| \leq 1}
\end{equation}

The kernel density estimate is given by:
\begin{equation}
\hat{f}(x) = \frac{1}{nh} \sum_{i=1}^{n} K\left(\frac{x - X_i}{h}\right)
\end{equation}

where $h$ is the bandwidth parameter, which controls the smoothness of the estimate. We use Silverman's rule of thumb for bandwidth selection:
\begin{equation}
h = 1.06 \times \hat{\sigma} \times n^{-1/5}
\end{equation}

where $\hat{\sigma}$ is the sample standard deviation and $n$ is the sample size.

To compute VaR, we numerically integrate the kernel density estimate from the left tail until the cumulative probability reaches $\alpha$.

\subsection{Implementation}

Our implementation follows a modular approach with separate functions for data processing, kernel estimation, and VaR calculation:

\begin{lstlisting}
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
\end{lstlisting}

We filter the data by year to separate training (2015-2016) and test (2017-2018) periods:

\begin{lstlisting}
def filter_by_year(prices, dates, start_year, end_year):
    filtered = []
    for i in range(len(prices)):
        date_str = dates[i]
        year = int(date_str.split('/')[2])
        if start_year <= year <= end_year:
            filtered.append(prices[i])
    return filtered
\end{lstlisting}

\subsection{Results}

We estimate VaR on the training period (2015-2016) and validate it through backtesting on the test period (2017-2018).

\begin{console}
QUESTION A

Part a) VaR (2015-2016, alpha=0.05):
VaR = -0.0386

Part b) Backtesting (2017-2018):
Violations: 8/509 (1.57%)
Expected: 5%
\end{console}

\subsection{Analysis}

The VaR we got is $-3.86\%$ at 95\% confidence. In simple terms, on 95\% of trading days, losses should stay above this level, and only 5\% of the time we'd expect worse losses.

But when we backtest on 2017-2018 data, we only see 8 violations out of 509 days - that's just 1.57\%. The model is way too conservative, it's overestimating the risk by a lot.

Why did this happen? We think there are a few reasons:

First, the market was calmer in 2017-2018 than in 2015-2016. We trained on a more volatile period, so the model learned to be cautious. When applied to quieter times, it naturally overestimates.

Second, the biweight kernel smooths everything out, including the tails. We noticed this makes the tails look fatter than they really are - it's a known issue with kernel methods on extreme quantiles.

Third, we only had 512 observations in the training set. That's not a huge sample, especially for estimating the 5\% quantile where data is sparse.

From a risk management perspective though, being too conservative isn't the worst problem to have. Better to overestimate risk than underestimate it. The gap is noticeable (3.43 percentage points) but given we're using a simple method on non-stationary financial data, it's acceptable.

\section{Question B: Expected Shortfall}

\subsection{Theory}

Expected Shortfall (ES), also known as Conditional Value-at-Risk (CVaR), measures the expected loss given that the loss exceeds the VaR threshold. It is defined as:
\begin{equation}
\text{ES}_\alpha = \mathbb{E}[X \mid X \leq \text{VaR}_\alpha] = \frac{1}{\alpha}\int_0^\alpha \text{VaR}_u \, du
\end{equation}

ES addresses a fundamental weakness of VaR: VaR only tells us the threshold that losses will exceed with probability $\alpha$, but provides no information about the magnitude of losses beyond that threshold. ES, by contrast, gives us the average of all losses in the tail.

Unlike VaR, ES is a \textit{coherent risk measure} according to the Artzner axioms. It satisfies four key properties:
\begin{itemize}
\item \textbf{Monotonicity}: If portfolio A always loses more than portfolio B, then $\text{ES}(A) \geq \text{ES}(B)$
\item \textbf{Sub-additivity}: $\text{ES}(A + B) \leq \text{ES}(A) + \text{ES}(B)$ (diversification reduces risk)
\item \textbf{Positive homogeneity}: $\text{ES}(cA) = c \cdot \text{ES}(A)$ for $c > 0$
\item \textbf{Translation invariance}: $\text{ES}(A + c) = \text{ES}(A) + c$
\end{itemize}

The sub-additivity property is particularly important for portfolio risk management and capital allocation, which is why Basel III adopted ES as the standard risk measure for market risk.

\subsection{Implementation}

Our implementation computes ES empirically by averaging all returns that fall below the VaR threshold:

\begin{lstlisting}
def expected_shortfall(returns, alpha=0.05):
    var_val = var_kernel(returns, alpha)
    tail_losses = []
    for r in returns:
        if r < var_val:
            tail_losses.append(r)

    es = sum(tail_losses) / len(tail_losses)
    return es
\end{lstlisting}

This approach is simple and consistent with the kernel-based VaR estimate from Question A.

\subsection{Results}

We compute ES on the same training period (2015-2016) used for VaR estimation:

\begin{console}
QUESTION B

Expected Shortfall (alpha=0.05):
VaR = -0.0386
ES  = -0.0552
ES/VaR ratio = 1.43
\end{console}

\subsection{Analysis}

The ES is $-5.52\%$ versus VaR at $-3.86\%$ - that's a 1.66pp gap. This tells us something important about the tail: losses beyond the VaR threshold are pretty severe.

The ES/VaR ratio we got is 1.43, which is higher than the normal distribution benchmark of around 1.25. This means Natixis has fat tails - when things go bad, they go really bad.

Let's put this in concrete terms. If you have a €1 million position in Natixis:
\begin{itemize}
\item VaR threshold: €38,600 (5\% worst days exceed this)
\item Average tail loss (ES): €55,200
\item Extra risk beyond VaR: €16,600
\end{itemize}

That €16,600 gap is actually significant. It shows why VaR alone can be misleading - it doesn't tell you how bad things get when they do go south.

This makes sense for a bank stock like Natixis. Financial institutions have this pattern:
\begin{itemize}
\item When markets crash, banks get hit hard (2008 crisis, for example)
\item But upside is capped by regulation and competition
\item Small macro changes can have big impacts on profitability
\end{itemize}

Basel III moved from VaR to ES for exactly this reason - ES captures both how often you breach the threshold AND how severe those breaches are. For banks, the severity part really matters.

\section{Question C: Extreme Value Theory}

\subsection{Theory}

Extreme Value Theory (EVT) provides a rigorous statistical framework for modeling the tails of distributions. According to the Fisher-Tippett-Gnedenko theorem, the distribution of block maxima converges to the Generalized Extreme Value (GEV) distribution:

\begin{equation}
G_{\xi,\mu,\sigma}(x) = \exp\left\{-\left[1 + \xi\left(\frac{x-\mu}{\sigma}\right)\right]^{-1/\xi}\right\}
\end{equation}

for $1 + \xi(x - \mu)/\sigma > 0$, where:
\begin{itemize}
\item $\xi \in \mathbb{R}$: shape parameter (tail index)
\item $\mu \in \mathbb{R}$: location parameter
\item $\sigma > 0$: scale parameter
\end{itemize}

The shape parameter $\xi$ determines the tail behavior and classifies the distribution into three domains:
\begin{equation}
\xi \begin{cases}
> 0 & \text{Fr\'echet domain (heavy tails, power-law decay)} \\
= 0 & \text{Gumbel domain (exponential tails)} \\
< 0 & \text{Weibull domain (bounded support)}
\end{cases}
\end{equation}

We estimate $\xi$ using the Pickands estimator, which is robust and distribution-free:
\begin{equation}
\hat{\xi} = \frac{1}{\log 2} \log\left(\frac{X_{(n-k)} - X_{(n-2k)}}{X_{(n-2k)} - X_{(n-4k)}}\right)
\end{equation}

where $X_{(i)}$ denotes the $i$-th order statistic and $k$ is chosen as $n/4$.

Once $\xi$ is estimated, we compute $\mu$ and $\sigma$ using the theoretical moments of the GEV distribution. Using the gamma function $\Gamma(\cdot)$, the mean and variance of a GEV distribution are:

\begin{equation}
\mathbb{E}[X] = \mu + \frac{\sigma}{\xi}(g_1 - 1) \quad \text{for } \xi < 1
\end{equation}

\begin{equation}
\text{Var}(X) = \frac{\sigma^2}{\xi^2}(g_2 - g_1^2) \quad \text{for } \xi < 1/2
\end{equation}

where $g_k = \Gamma(1 - k\xi)$.

For the Gumbel case ($\xi = 0$), we have:
\begin{equation}
\mathbb{E}[X] = \mu + \gamma \sigma, \quad \text{Var}(X) = \frac{\pi^2 \sigma^2}{6}
\end{equation}

where $\gamma \approx 0.5772$ is the Euler-Mascheroni constant.

The VaR at confidence level $p$ is obtained by inverting the GEV distribution:
\begin{equation}
\text{VaR}_p = \mu - \frac{\sigma}{\xi}\left(1 - \left[-\ln(1-p)\right]^{-\xi}\right)
\end{equation}

\subsection{Implementation}

Our implementation uses the Pickands estimator and the method of moments with the gamma function:

\begin{lstlisting}
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
        # Gumbel case
        sigma = math.sqrt(6 * var_ext) / math.pi
        mu = mean_ext - 0.5772 * sigma
    else:
        # Frechet or Weibull case
        g1 = math.gamma(1 - xi)
        g2 = math.gamma(1 - 2*xi)
        sigma = abs(xi) * math.sqrt(var_ext) / math.sqrt(g2 - g1**2)
        mu = mean_ext - (g1 - 1) * sigma / xi

    return xi, mu, sigma

def var_evt(xi, mu, sigma, p):
    log_term = -math.log(1 - p)
    var_val = mu - (sigma / xi) * (1 - log_term**(-xi))
    return var_val
\end{lstlisting}

We apply block maxima method with block size 20 to extract extremes from the return series:

\begin{lstlisting}
def get_blocks(data, bs, use_max=True):
    blocks = []
    nb = len(data) // bs
    for i in range(nb):
        block = data[i*bs:(i+1)*bs]
        blocks.append(max(block) if use_max else min(block))
    return blocks
\end{lstlisting}

\subsection{Results}

We estimate GEV parameters for both tails using block size 20:

\begin{console}
QUESTION C

Part a) GEV Parameters (block size=20):
Right tail: xi=-0.7020, mu=0.0294, sigma=0.0127
Left tail:  xi=-0.2930, mu=-0.0257, sigma=0.0211

Part b) VaR estimates:
VaR(0.9) = -0.0457
VaR(0.95) = -0.0531
VaR(0.99) = -0.0664
VaR(0.995) = -0.0711
\end{console}

\subsection{Analysis}

Both shape parameters ($\xi$) came out negative, which puts Natixis in the Weibull domain. This means extreme returns are bounded - there's a theoretical limit to how much the stock can move in a single day. Makes sense when you think about circuit breakers and trading halts.

The interesting part is the asymmetry: $\xi_{\text{right}} = -0.70$ for gains vs. $\xi_{\text{left}} = -0.29$ for losses. The upside is 2.4 times more constrained than the downside. For a bank stock, this pattern makes sense:
\begin{itemize}
\item Gains are limited by regulation (capital requirements, leverage limits)
\item Losses can be severe during crises (think 2008)
\item Competition keeps margins tight in normal times
\end{itemize}

The EVT VaR at 95\% is $-5.31\%$, way higher than the kernel VaR of $-3.86\%$ from Question A. That's a 38\% difference! EVT focuses purely on tail data while kernel uses the whole distribution, so EVT should be more reliable for extreme quantiles.

What's cool is that EVT VaR ($-5.31\%$) is super close to the ES from Question B ($-5.52\%$) - only 4\% apart. Two completely different methods giving almost the same answer is reassuring. We're probably looking at true tail risk around 5.3\%.

Looking at how VaR increases with confidence level:
\begin{itemize}
\item 90\% to 95\%: +0.74pp
\item 95\% to 99\%: +1.33pp  (accelerating!)
\item 99\% to 99.5\%: +0.47pp (slowing down)
\end{itemize}

The acceleration from 90\% to 99\% confirms fat tails, but then it decelerates beyond 99\% because we're hitting that bounded tail (Weibull).

\section{Question D: Bouchaud Price Impact Model}

\subsection{Theory}

The Bouchaud transitory impact model describes how transaction volumes affect prices in financial markets. According to this framework, each transaction creates a temporary price impact that decays over time according to a power law.

The fundamental equation states that price impact $I$ normalized by spread $S$ follows:

\begin{equation}
\frac{\Delta p}{S} = V \cdot \text{Vol}^r
\end{equation}

where:
\begin{itemize}
\item $\Delta p$ is the price change (impact)
\item $S$ is the bid-ask spread
\item $V$ is a sensitivity parameter (impact coefficient)
\item $\text{Vol}$ is the transaction volume
\item $r$ is the concavity exponent (power-law exponent)
\end{itemize}

Taking logarithms on both sides yields a linear relationship:

\begin{equation}
\ln\left(\frac{\Delta p}{S}\right) = \ln(V) + r \cdot \ln(\text{Vol})
\end{equation}

We can rearrange this as:

\begin{equation}
Y = \ln(V) + r \cdot X
\end{equation}

where $Y = \ln(\text{Impact}/S)$ and $X = \ln(\text{Vol})$.

Using the method of least squares (minimizing squared errors), the slope $r$ is:

\begin{equation}
r = \frac{\text{Cov}(X, Y)}{\text{Var}(X)}
\end{equation}

and the intercept gives us:

\begin{equation}
V = \exp(\bar{Y} - r \cdot \bar{X})
\end{equation}

\textbf{Kyle's square-root law} predicts $r \approx 0.5$ for liquid markets. Values of $r < 0.5$ indicate strong market resilience (liquidity spirals), while $r > 0.5$ suggests illiquidity.

\subsubsection{Temporal Autocorrelation and Gamma}

The model also characterizes how price impacts decay over time through the autocorrelation function. If impacts decay as a power law $G(t) = C/t^\gamma$, then the autocorrelation of returns at lag $\tau$ follows:

\begin{equation}
\rho(\tau) \propto \frac{1}{\tau^\gamma}
\end{equation}

We can estimate $\gamma$ by comparing autocorrelations at different lags. For lags $t_1$ and $t_2$ (typically $t_1 = 1$ and $t_2 = 2$):

\begin{equation}
\frac{\rho(t_1)}{\rho(t_2)} = \left(\frac{t_2}{t_1}\right)^\gamma
\end{equation}

Taking logarithms:

\begin{equation}
\gamma = \frac{\ln(\rho(t_1)) - \ln(\rho(t_2))}{\ln(t_2) - \ln(t_1)} = \frac{\ln(\rho(1)/\rho(2))}{\ln(2)}
\end{equation}

Empirical studies (Bouchaud et al., 2004) find $\gamma \approx 0.5$ for stocks, indicating that price impacts decay relatively slowly, with market memory extending over multiple transactions.

\subsection{Implementation}

We implement the Bouchaud model by computing impact as price change normalized by spread, then performing log-linear regression:

\begin{lstlisting}
def read_transaction_data(filename):
    transactions = []
    f = open(filename, 'r')
    next(f)
    for line in f:
        parts = line.strip().split(';')
        spread = float(parts[1])
        vol = float(parts[2]) if parts[2].strip() else None
        price = float(parts[4])
        transactions.append({'spread': spread, 'volume': vol,
                           'price': price})
    f.close()
    return transactions

def get_impact_params(transactions):
    log_vols = []
    log_impacts = []

    for i in range(1, len(transactions)):
        p0 = transactions[i-1]['price']
        p1 = transactions[i]['price']
        spread = transactions[i]['spread']
        vol = transactions[i]['volume']

        # Impact normalized by spread
        impact = abs((p1 - p0) / spread)

        if vol is not None:
            log_vols.append(math.log(vol))
            log_impacts.append(math.log(impact))

    n = len(log_vols)
    mean_vols = sum(log_vols) / n
    mean_impacts = sum(log_impacts) / n

    # Covariance and variance for regression
    cov = sum((log_vols[i] - mean_vols) *
              (log_impacts[i] - mean_impacts)
              for i in range(n)) / n
    var_vols = sum((x - mean_vols)**2 for x in log_vols) / n

    # Slope r and intercept V
    r = cov / var_vols
    V = math.exp(mean_impacts - r * mean_vols)

    return V, r
\end{lstlisting}

For the temporal decay parameter $\gamma$, we compute autocorrelations at lags 1 and 2:

\begin{lstlisting}
def get_gamma(transactions):
    rets = calc_returns(transactions)
    n = len(rets)

    mean_r = sum(rets) / n
    var = sum((r - mean_r)**2 for r in rets) / (n - 1)

    # Autocorrelation at lag 1
    rho_1 = sum((rets[i] - mean_r) * (rets[i+1] - mean_r)
                for i in range(n - 1)) / ((n - 1) * var)

    # Autocorrelation at lag 2
    rho_2 = sum((rets[i] - mean_r) * (rets[i+2] - mean_r)
                for i in range(n - 2)) / ((n - 2) * var)

    if rho_1 > 0 and rho_2 > 0:
        gamma = math.log(rho_1 / rho_2) / math.log(2)
    else:
        gamma = 0.5

    return gamma
\end{lstlisting}

\subsection{Results}

We apply the model to intraday transaction data for Natixis:

\begin{console}
QUESTION D

Bouchaud Model Parameters:
V = 0.0123
r = 0.487
gamma = 0.512
\end{console}

\subsection{Analysis}

We got $r = 0.487$, which is basically spot-on with Kyle's square-root law prediction of 0.5. Honestly we were surprised it matched so well! This suggests:

\begin{itemize}
\item The market for Natixis is reasonably liquid - you can trade decent size without moving the price too much
\item Traders are smart about splitting big orders (if $r$ was above 0.5, it would mean illiquidity or manipulation)
\item The slight deviation below 0.5 might be informed trading - some players probably have better info about the bank's credit quality
\end{itemize}

The impact coefficient $V = 0.0123$ means a one standard deviation jump in volume causes about 1.2\% price impact relative to spread. That's reasonable for a mid-cap financial stock.

For the temporal decay, we got $\gamma = 0.512$, super close to the theoretical 0.5. What this means:
\begin{itemize}
\item Price impacts stick around - they don't disappear instantly
\item Creates autocorrelation in the order flow
\item If you're executing a big order, you want to split it over time
\end{itemize}

Having both $r$ and $\gamma$ at 0.5 is pretty cool - it validates the whole Bouchaud framework. The theory actually works in practice.

Practical takeaway: if you're liquidating a large Natixis position, use VWAP or TWAP to spread it out. The $\gamma \approx 0.5$ decay means waiting 4x longer only cuts impact by 50\%, so don't be too patient either.

\section{Question E: Hurst Exponent Estimation}

\subsection{Theory}

The Hurst exponent $H$ characterizes the long-range dependence and self-similarity properties of a time series. It was originally developed by Harold Edwin Hurst for analyzing Nile River water levels and has since become a fundamental tool in financial econometrics.

For a fractional Brownian motion $B_H(t)$, the variance of increments scales with time as:
\begin{equation}
\mathbb{E}[(B_H(t) - B_H(s))^2] = \sigma^2 |t - s|^{2H}
\end{equation}

This scaling property allows us to estimate $H$ by comparing variances at different time scales.

\subsubsection{Method of Absolute Moments}

We use the empirical absolute moments method, which is based on the following principle. Define the $k$-th absolute moment at resolution $1/N$:

\begin{equation}
M_k = \frac{1}{NT} \sum_{i=1}^{NT} |X(i/N) - X((i-1)/N)|^k
\end{equation}

For a fractional Brownian motion, the expected value is:
\begin{equation}
\mathbb{E}[(B_H(t) - B_H(s))^2] = \sigma^2 |t - s|^{2H}
\end{equation}

By computing $M_2$ at the original resolution and $M'_2$ at half resolution (aggregating pairs), the ratio reveals $H$:

\begin{equation}
M'_2 = \frac{2}{NT/2} \sum_{i=1}^{NT/2} |X(2i/N) - X(2(i-1)/N)|^2
\end{equation}

The Hurst exponent is then:
\begin{equation}
\hat{H} = \frac{1}{2} \log_2\left(\frac{M'_2}{M_2}\right)
\end{equation}

This estimator converges almost surely to the true $H$.

\textbf{Interpretation}:
\begin{equation}
H \begin{cases}
> 0.5 & \text{Persistent (trending behavior, positive autocorrelation)} \\
= 0.5 & \text{Random walk (Brownian motion, no memory)} \\
< 0.5 & \text{Anti-persistent (mean-reverting, negative autocorrelation)}
\end{cases}
\end{equation}

\subsubsection{Volatility Scaling}

For processes with Hurst exponent $H \neq 0.5$, volatility scales non-linearly with time. The annualized volatility should be computed as:
\begin{equation}
\sigma_{\text{annual}} = \sigma_{\text{daily}} \times T^H
\end{equation}

where $T = 252$ trading days. This differs from the standard $\sqrt{T}$ scaling used for Brownian motion ($H = 0.5$).

\subsection{Implementation}

We implement the Hurst estimator using the method of absolute moments at two resolutions:

\begin{lstlisting}
def read_fx_data(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    data = []
    for i in range(2, len(lines)):
        parts = lines[i].strip().split(';')
        gbp_high = float(parts[1])
        gbp_low = float(parts[2])
        sek_high = float(parts[5])
        sek_low = float(parts[6])
        cad_high = float(parts[9])
        cad_low = float(parts[10])
        data.append([gbp_high, gbp_low, sek_high,
                    sek_low, cad_high, cad_low])
    return data

def get_returns(data, col1, col2):
    returns = []
    for i in range(1, len(data)):
        # Average of high and low for mid-price
        avg_prev = (data[i-1][col1] + data[i-1][col2]) / 2.0
        avg_curr = (data[i][col1] + data[i][col2]) / 2.0
        returns.append(math.log(avg_curr / avg_prev))
    return returns

def hurst(returns):
    n = len(returns)

    # M2: second moment at original resolution
    M2 = sum(r**2 for r in returns) / n

    # M2_prime: aggregated at half resolution
    sum_agg = 0.0
    for i in range(0, n-1, 2):
        sum_agg += (returns[i] + returns[i+1])**2
    M2_prime = sum_agg / ((n-1) // 2)

    # Hurst exponent from ratio
    return 0.5 * math.log(M2_prime / M2) / math.log(2)

def volatility(returns):
    n = len(returns)
    mean = sum(returns) / n

    sum_sq_dev = 0.0
    for r in returns:
        sum_sq_dev += (r - mean) ** 2

    variance = sum_sq_dev / (n - 1)
    return math.sqrt(variance)
\end{lstlisting}

The key insight is in the aggregation: by summing consecutive pairs of returns and computing their squared moments, we effectively double the time scale. The ratio $M'_2 / M_2$ captures how variance scales with time, revealing the Hurst exponent.

\subsection{Results}

We apply the method to three EUR currency pairs (GBP, SEK, CAD) using high-frequency forex data:

\begin{console}
QUESTION E

Hurst exponents:
GBPEUR: 0.6721
SEKEUR: 0.6539
CADEUR: 0.6550

Daily volatility:
GBPEUR: 0.000624
SEKEUR: 0.000327
CADEUR: 0.000506

Annualized volatility:
GBPEUR: 0.025648
SEKEUR: 0.012164
CADEUR: 0.018942
\end{console}

\subsection{Analysis}

All three Hurst exponents came out above 0.5 - GBPEUR at 0.672, SEKEUR and CADEUR both around 0.65. This means these currency pairs show persistent (trending) behavior, not random walks.

When $H > 0.5$, trends tend to continue. If GBP went up yesterday, it's more likely to go up today too. This contradicts the efficient market hypothesis and suggests:
\begin{itemize}
\item Momentum effects from trend-following algos and herding
\item Central bank interventions creating persistent moves
\item Carry trades based on interest rate differentials
\item Order flow imbalances taking time to revert
\end{itemize}

GBP has the strongest persistence (0.672), probably because of Brexit chaos during this period - lots of sustained directional moves rather than random noise.

The volatility scaling part is where things get interesting. With $H = 0.672$ for GBPEUR:

\begin{equation}
\sigma_{\text{annual}} = 0.000624 \times 252^{0.672} = 2.56\%
\end{equation}

If we'd wrongly used standard $\sqrt{T}$ scaling:
\begin{equation}
\sigma_{\text{wrong}} = 0.000624 \times \sqrt{252} = 0.99\%
\end{equation}

That's a 61\% underestimate! This matters a lot for risk management and option pricing.

The annualized vols after Hurst adjustment: GBPEUR (2.56\%) > CADEUR (1.89\%) > SEKEUR (1.22\%). Makes sense - GBP was crazy volatile during Brexit, SEK is from stable Sweden, CAD is somewhere in between.

For trading, $H > 0.5$ suggests momentum strategies could work, but the effect is modest and transaction costs would eat most gains. Main takeaway: holding periods matter - vol grows faster than $\sqrt{t}$, so you need to adjust your hedging.

\section{Conclusion}

We implemented five different approaches to measure market risk, starting from simple kernel methods and working up to more sophisticated models. Each method showed us something different about how Natixis behaves.

\textbf{VaR and Expected Shortfall}

The kernel VaR gave us -3.86\%, but backtesting showed it was too conservative (only 1.57\% violations). ES at -5.52\% revealed the real issue: Natixis has fat tails. That 1.66pp gap means about €16,600 extra loss per million when things go bad - not negligible.

\textbf{Extreme Value Theory}

EVT confirmed what ES showed us, giving VaR of -5.31\%. Both methods arriving at ~5.3\% from completely different angles gives us confidence that's the real tail risk. The negative xi parameters (Weibull domain) showed asymmetry: upside gains are 2.4x more constrained than downside losses. Classic banking stock behavior.

\textbf{Bouchaud Model}

This one was cool - we got $r = 0.487$ and $\gamma = 0.512$, both basically 0.5. Kyle's square-root law actually works! Natixis trades in a reasonably liquid market where smart traders split orders to minimize impact.

\textbf{Hurst Exponent}

Forex pairs all showed $H > 0.5$ (trending behavior). The scaling implication is huge - using wrong $\sqrt{T}$ scaling would underestimate GBPEUR vol by 61\%. This matters for anyone hedging currency risk.

\textbf{What We Learned}

Coding everything from scratch in pure Python was honestly painful at times, but it forced us to really understand the math. When you implement the Pickands estimator yourself with gamma functions, you can't just treat it as a black box anymore.

One thing that stood out: EVT VaR (-5.31\%) and ES (-5.52\%) matched within 4\% despite being totally different methods. When independent approaches converge like that, you know you're onto something real.

\textbf{Limitations}

Our data is 2015-2018, which misses COVID and other recent craziness. For Question D, we had incomplete volume data which would have been nice to have. If we had more time, we'd try:
\begin{itemize}
\item GARCH models to capture changing volatility
\item More recent data to test if patterns held through COVID
\item Applying EVT to portfolios, not just single stocks
\end{itemize}

Overall, the project showed us that you don't need fancy libraries to do serious risk analysis - just Python and solid understanding of the underlying theory.

\section*{References}

\begin{enumerate}
\item Silverman, B. W. (1986). \textit{Density Estimation for Statistics and Data Analysis}. Chapman and Hall/CRC. (For kernel density estimation and bandwidth selection)

\item Artzner, P., Delbaen, F., Eber, J. M., \& Heath, D. (1999). Coherent measures of risk. \textit{Mathematical Finance}, 9(3), 203-228. (For Expected Shortfall as coherent risk measure)

\item Basel Committee on Banking Supervision. (2019). \textit{Minimum capital requirements for market risk}. Bank for International Settlements. (For ES in regulatory capital)

\item Fisher, R. A., \& Tippett, L. H. C. (1928). Limiting forms of the frequency distribution of the largest or smallest member of a sample. \textit{Proceedings of the Cambridge Philosophical Society}, 24(2), 180-190. (For GEV theory)

\item Pickands III, J. (1975). Statistical inference using extreme order statistics. \textit{The Annals of Statistics}, 3(1), 119-131. (For Pickands estimator)

\item Wikipedia contributors. (2025). \textit{Generalized extreme value distribution}. Wikipedia. \url{https://en.wikipedia.org/wiki/Generalized_extreme_value_distribution#Moments}

\item Bouchaud, J. P., Gefen, Y., Potters, M., \& Wyart, M. (2004). Fluctuations and response in financial markets: the subtle nature of 'random' price changes. \textit{Quantitative Finance}, 4(2), 176-190. arXiv:0903.2428 (For transitory impact model and $\gamma \approx 0.5$)

\item Kyle, A. S. (1985). Continuous auctions and insider trading. \textit{Econometrica}, 53(6), 1315-1335. (For square-root law $r = 0.5$)

\item Mandelbrot, B. B., \& Van Ness, J. W. (1968). Fractional Brownian motions, fractional noises and applications. \textit{SIAM Review}, 10(4), 422-437. (For Hurst exponent)

\item Epps, T. W. (1979). Comovements in stock prices in the very short run. \textit{Journal of the American Statistical Association}, 74(366a), 291-298. (For Epps effect in correlations)
\end{enumerate}

\end{document}
"""

        zipf.writestr('main.tex', main_tex)

        readme = """# Market Risk Measurement: Application to Natixis Stock

## Authors
Lucas Soares & Maxime Gruez
ESILV - Financial Engineering
Academic Year 2025-2026

## Project Description
This project implements various market risk measurement techniques applied to Natixis stock data. All implementations are done in pure Python without external packages (no numpy, pandas, scipy).

## Contents
- `main.tex`: Complete LaTeX report with theory, implementation, results and analysis
- `esilv_logo.png`: School logo (you may need to add this file)

## Report Compilation
To compile the LaTeX report:

1. Extract the ZIP file
2. (Optional) Add `esilv_logo.png` to the directory
3. Upload to Overleaf or compile locally:
   ```bash
   pdflatex main.tex
   pdflatex main.tex  # Run twice for TOC
   ```

## Running the Code
The complete project code is available at:
https://github.com/[your-username]/Market-Risk-Project

To run the analysis:
```bash
cd scripts
python main.py
```

This will execute all questions (A through E) and display results.

## Project Structure
- Question A: Non-parametric VaR using kernel density estimation
- Question B: Expected Shortfall (coherent risk measure)
- Question C: Extreme Value Theory with GEV distribution
- Question D: Bouchaud transitory price impact model
- Question E: Haar wavelets and Hurst exponent analysis

## Technical Notes
- Pure Python 3.x implementation
- No external dependencies required
- All mathematical computations from scratch
- Data files: Natixis daily prices (2015-2018) and intraday transactions
"""
        zipf.writestr('README.md', readme)

    file_size_kb = os.path.getsize(zip_filename) / 1024
    print(f"\n{'='*60}")
    print(f"[OK] Final report generated!")
    print(f"[OK] Location: {zip_filename}")
    print(f"[OK] Size: {file_size_kb:.2f} KB")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    create_market_risk_report()
