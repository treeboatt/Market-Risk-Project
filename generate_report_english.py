import zipfile
import os

def create_market_risk_report():
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    zip_filename = os.path.join(downloads_path, "Market_Risk_ESILV_2025.zip")

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
\usepackage{booktabs}
\usepackage{fancyhdr}

\geometry{margin=2.5cm}

\lstset{
    language=Python,
    basicstyle=\ttfamily\footnotesize,
    keywordstyle=\color{blue}\bfseries,
    commentstyle=\color{gray}\itshape,
    stringstyle=\color{red},
    numbers=left,
    numberstyle=\tiny\color{gray},
    frame=single,
    breaklines=true,
    breakatwhitespace=true,
    tabsize=4,
    showstringspaces=false
}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small Market Risk Analysis}
\fancyhead[R]{\small ESILV 2025-2026}
\fancyfoot[C]{\thepage}

\title{
    \includegraphics[width=0.3\textwidth]{esilv_logo.png}\\[1cm]
    \textbf{Advanced Market Risk Measurement:\\
    A Non-Parametric and Microstructural Approach}\\
    \vspace{0.5cm}
    \large Market Risk Project
}

\author{
    \textbf{Lucas Soares} \and \textbf{Maxime Gruez}\\
    \small ESILV - École Supérieure d'Ingénieurs Léonard de Vinci\\
    \small Master in Financial Engineering\\
    \small Academic Year 2025-2026
}

\date{\today}

\begin{document}

\maketitle
\thispagestyle{empty}
\newpage

\tableofcontents
\newpage

\begin{abstract}
This paper presents a comprehensive quantitative analysis of market risk for Natixis stock using five complementary methodologies: non-parametric Value-at-Risk estimation via kernel density, Expected Shortfall computation, Extreme Value Theory with Pickands estimator, Bouchaud's microstructural price impact model, and wavelet-based multiresolution analysis of FX correlations. All implementations are coded from scratch in pure Python without external libraries (numpy, pandas), demonstrating deep algorithmic understanding. The study reveals significant asymmetry in Natixis returns ($\xi_{left} = -0.29$ vs $\xi_{right} = -0.70$), fat-tailed distributions (ES/VaR ratio of 1.43), and bounded extremal behavior under the Weibull domain of attraction. Forex analysis confirms the Epps effect and near-efficient market dynamics (Hurst $\approx 0.5$).
\end{abstract}

\section{Introduction}

Market risk quantification remains a cornerstone of modern financial engineering. This project implements cutting-edge statistical and microstructural techniques to measure tail risk, extreme events, and price dynamics. The methodological contributions include:

\begin{itemize}
    \item \textbf{Non-parametric VaR}: Biweight kernel density estimation without distributional assumptions
    \item \textbf{Coherent risk measure}: Expected Shortfall as a tail-sensitive alternative to VaR
    \item \textbf{Extreme Value Theory}: Pickands estimator for Generalized Extreme Value (GEV) parameters
    \item \textbf{Market microstructure}: Bouchaud's power-law price impact model
    \item \textbf{Multiscale analysis}: Haar wavelets and Hurst exponent for FX correlation structure
\end{itemize}

The dataset comprises 1023 daily Natixis prices (2015-2018) and high-frequency FX tick data (GBPEUR, SEKEUR, CADEUR). All computations are performed in pure Python to ensure full transparency and pedagogical depth.

\section{Data and Methodology}

\subsection{Dataset Description}

\begin{table}[H]
\centering
\begin{tabular}{@{}lll@{}}
\toprule
\textbf{Asset} & \textbf{Period} & \textbf{Observations} \\ \midrule
Natixis Stock & 2015-2018 & 1023 daily prices \\
FX Rates (GBP/SEK/CAD vs EUR) & Intraday & 12929 ticks \\ \bottomrule
\end{tabular}
\caption{Data summary}
\end{table}

Returns are computed as logarithmic differences:
\begin{equation}
r_t = \log\left(\frac{P_t}{P_{t-1}}\right)
\end{equation}

\subsection{Implementation Philosophy}

All statistical methods are implemented without third-party numerical libraries. This constraint enforces:
\begin{itemize}
    \item Explicit understanding of kernel convolution
    \item Manual implementation of quantile search algorithms
    \item Custom CSV parsing and numerical integration
    \item Direct computation of statistical estimators (variance, correlation, Hurst R/S)
\end{itemize}

This "from-scratch" approach transforms a technical assignment into a fundamental learning exercise in computational finance.

\section{Question A: Non-Parametric Value-at-Risk}

\subsection{Theory}

The Value-at-Risk at confidence level $\alpha$ is defined as:
\begin{equation}
\text{VaR}_\alpha = \inf\{x \in \mathbb{R} : F(x) \geq \alpha\}
\end{equation}

We employ the Parzen-Rosenblatt kernel density estimator with the biweight kernel:
\begin{equation}
K(u) = \frac{15}{16}(1-u^2)^2 \mathbb{1}_{|u| \leq 1}
\end{equation}

The estimated density is:
\begin{equation}
\hat{f}(x) = \frac{1}{nh} \sum_{i=1}^{n} K\left(\frac{x - X_i}{h}\right)
\end{equation}

Bandwidth selection follows Silverman's rule:
\begin{equation}
h = 1.06 \times \hat{\sigma} \times n^{-1/5}
\end{equation}

\subsection{Implementation}

\begin{lstlisting}
def biweight_kernel(u):
    if abs(u) <= 1:
        return 0.9375 * ((1 - u*u) ** 2)
    return 0.0

def bandwidth(data):
    n = len(data)
    m = sum(data) / n
    var = sum((x - m)**2 for x in data) / (n - 1)
    sd = math.sqrt(var)
    h = 1.1 * sd * (n ** -0.2)
    return h

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
\end{lstlisting}

\subsection{Results}

\textbf{Training Period (2015-2016):}
\begin{itemize}
    \item Sample size: 512 returns
    \item VaR$_{95\%}$ = -3.86\%
\end{itemize}

\textbf{Backtesting (2017-2018):}
\begin{itemize}
    \item Test sample: 509 returns
    \item Violations: 8 (1.57\%)
    \item Expected violations: 25 (5.0\%)
\end{itemize}

\subsection{Analysis}

The kernel estimator exhibits \textbf{overly conservative behavior}. With only 1.57\% violations versus the expected 5\%, the model overestimates risk. This discrepancy stems from two factors:

\begin{enumerate}
    \item \textbf{Regime shift}: 2017-2018 exhibited lower volatility than 2015-2016 (post-crisis stabilization)
    \item \textbf{Kernel smoothing bias}: The biweight kernel tends to "flatten" tail probabilities, yielding a more negative VaR than empirical quantiles
\end{enumerate}

The backtesting failure rate of 1.57\% suggests the true 95\% VaR for the test period was closer to -2.5\%, not -3.86\%. This validates the importance of conditional volatility models (GARCH) for time-varying risk.

\section{Question B: Expected Shortfall}

\subsection{Theory}

Expected Shortfall (ES), also known as Conditional Value-at-Risk (CVaR), measures the average loss beyond VaR:
\begin{equation}
\text{ES}_\alpha = \mathbb{E}[X \mid X \leq \text{VaR}_\alpha] = \frac{1}{\alpha} \int_0^\alpha \text{VaR}_u \, du
\end{equation}

Unlike VaR, ES satisfies the coherence axioms (monotonicity, sub-additivity, positive homogeneity, translation invariance), making it theoretically superior for portfolio optimization.

\subsection{Implementation}

\begin{lstlisting}
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
\end{lstlisting}

\subsection{Results}

\begin{table}[H]
\centering
\begin{tabular}{@{}lcc@{}}
\toprule
\textbf{Metric} & \textbf{Value} & \textbf{Interpretation} \\ \midrule
VaR$_{95\%}$ & -3.86\% & 5\% quantile \\
ES$_{95\%}$ & -5.52\% & Average tail loss \\
ES/VaR Ratio & 1.43 & Tail risk multiplier \\ \bottomrule
\end{tabular}
\caption{VaR vs Expected Shortfall}
\end{table}

\subsection{Analysis}

The ES/VaR ratio of 1.43 significantly exceeds the Gaussian benchmark of 1.25. This 14\% excess directly quantifies the presence of \textbf{fat tails} and \textbf{negative skewness} in Natixis returns.

Mathematical interpretation:
\begin{itemize}
    \item \textbf{Fat tails}: Extreme losses occur with higher probability than under normality
    \item \textbf{Skewness}: The left tail (losses) is thicker than the right tail (gains)
    \item \textbf{Risk underestimation}: Relying solely on VaR would ignore 43\% of tail risk
\end{itemize}

For a 1M€ position:
\begin{itemize}
    \item VaR prediction: 38,600€ loss (5\% of days)
    \item ES reality: 55,200€ average loss when VaR is breached
    \item Hidden risk: 16,600€ underestimated
\end{itemize}

This validates ES as the Basel III preferred risk measure for capital requirements.

\section{Question C: Extreme Value Theory}

\subsection{Theory}

The Generalized Extreme Value (GEV) distribution models block maxima:
\begin{equation}
G_{\xi,\mu,\sigma}(x) = \exp\left\{-\left[1 + \xi\left(\frac{x-\mu}{\sigma}\right)\right]^{-1/\xi}\right\}
\end{equation}

where:
\begin{itemize}
    \item $\xi$: shape parameter (tail index)
    \item $\mu$: location parameter
    \item $\sigma > 0$: scale parameter
\end{itemize}

The Pickands estimator for $\xi$ is:
\begin{equation}
\hat{\xi} = \frac{1}{\log 2} \log\left(\frac{X_{(n-k)} - X_{(n-2k)}}{X_{(n-2k)} - X_{(n-4k)}}\right)
\end{equation}

Classification by $\xi$:
\begin{equation}
\begin{cases}
\xi > 0 & \text{Fréchet (fat tails, power-law decay)} \\
\xi = 0 & \text{Gumbel (exponential tails)} \\
\xi < 0 & \text{Weibull (bounded support)}
\end{cases}
\end{equation}

\subsection{Implementation}

\begin{lstlisting}
def pickands(extremes):
    n = len(extremes)
    extremes_sorted = sorted(extremes)
    k = n // 4

    x1 = extremes_sorted[n - k - 1]
    x2 = extremes_sorted[n - 2*k - 1]
    x3 = extremes_sorted[n - 4*k - 1]

    num = x1 - x2
    denom = x2 - x3

    if denom != 0 and num > 0:
        ratio = num / denom
        if ratio > 0:
            xi = math.log(ratio) / math.log(2)
        else:
            xi = 0.0
    else:
        xi = 0.0

    return xi
\end{lstlisting}

\subsection{Results}

\begin{table}[H]
\centering
\begin{tabular}{@{}lccc@{}}
\toprule
\textbf{Tail} & $\boldsymbol{\xi}$ & $\boldsymbol{\mu}$ & $\boldsymbol{\sigma}$ \\ \midrule
Right (Gains) & -0.70 & 0.0294 & 0.0127 \\
Left (Losses) & -0.29 & -0.0257 & 0.0211 \\ \bottomrule
\end{tabular}
\caption{GEV parameters via Pickands estimator}
\end{table}

\textbf{VaR under EVT:}
\begin{itemize}
    \item VaR$_{90\%}$ = -4.57\%
    \item VaR$_{95\%}$ = -5.31\%
    \item VaR$_{99\%}$ = -6.64\%
    \item VaR$_{99.5\%}$ = -7.11\%
\end{itemize}

\subsection{Analysis}

\subsubsection{Weibull Domain of Attraction}

Both $\xi$ values are negative, placing Natixis returns in the \textbf{Weibull class}. This implies:
\begin{itemize}
    \item \textbf{Bounded extremes}: Returns have a theoretical upper/lower limit on this sample
    \item \textbf{Light tails}: Exponential-like decay (contrary to power-law Fréchet distributions)
    \item \textbf{No "black swans"}: Infinite losses are theoretically impossible under this model
\end{itemize}

\subsubsection{Asymmetry Analysis}

The ratio $|\xi_{right}| / |\xi_{left}| = 0.70 / 0.29 \approx 2.4$ quantifies tail asymmetry:
\begin{itemize}
    \item Right tail is 2.4× more constrained than left tail
    \item Extreme losses decay slower than extreme gains
    \item Financial interpretation: "Stocks take the stairs up, the elevator down"
\end{itemize}

\subsubsection{Cross-Validation with Kernel ES}

Comparing methodologies:
\begin{equation}
\text{VaR}^{\text{EVT}}_{95\%} = -5.31\% \quad \text{vs} \quad \text{ES}^{\text{Kernel}}_{95\%} = -5.52\%
\end{equation}

The 4\% discrepancy validates both approaches. EVT focuses exclusively on extremes (block maxima), while ES averages all tail observations. Their convergence confirms the robustness of our tail risk estimate around -5.3\%.

\subsubsection{Practical Implications}

For a \$10M Natixis position:
\begin{itemize}
    \item 1-day VaR$_{99\%}$: \$664,000 loss
    \item 10-day VaR$_{99\%}$ (scaling): $\$664k \times \sqrt{10} = \$2.1M$
    \item Regulatory capital (Basel III, 99\% over 10 days): \$2.1M minimum
\end{itemize}

\section{Question D: Bouchaud's Price Impact Model}

\subsection{Theory}

Bouchaud's model describes transient price impact from order flow:
\begin{equation}
\frac{dP}{P} = \lambda \cdot \text{sign}(Q) \cdot |Q|^\delta \cdot dt - \frac{1}{\tau}(P - P^*) dt + \sigma dW_t
\end{equation}

where:
\begin{itemize}
    \item $\lambda$: impact coefficient (price per unit volume)
    \item $\delta$: power-law exponent (Kyle's model predicts $\delta = 0.5$)
    \item $\tau$: relaxation time (mean-reversion speed)
    \item $\sigma$: diffusive volatility
\end{itemize}

Kyle's square-root law states:
\begin{equation}
\Delta P \propto \sqrt{Q}
\end{equation}

\subsection{Implementation}

\begin{lstlisting}
def get_bouchaud_params(transactions):
    price_chg = []
    vols = []

    for i in range(1, len(transactions)):
        p0 = transactions[i-1]['price']
        p1 = transactions[i]['price']
        chg = p1 - p0
        vol = transactions[i]['volume']

        if vol is not None and vol > 0:
            price_chg.append(chg)
            vols.append(vol)

    n = len(price_chg)
    sum_lv = sum(math.log(v) for v in vols)
    sum_li = sum(math.log(abs(p)) for p in price_chg if abs(p) > 0)
    cnt = sum(1 for p in price_chg if abs(p) > 0)

    mean_lv = sum_lv / cnt
    mean_li = sum_li / cnt

    cov = sum((math.log(vols[i]) - mean_lv) *
              (math.log(abs(price_chg[i])) - mean_li)
              for i in range(n) if abs(price_chg[i]) > 0) / cnt
    var_lv = sum((math.log(v) - mean_lv)**2
                 for v in vols) / cnt

    delta = cov / var_lv
    lam = math.exp(mean_li - delta * mean_lv)

    return lam, delta
\end{lstlisting}

\subsection{Results}

\begin{table}[H]
\centering
\begin{tabular}{@{}lll@{}}
\toprule
\textbf{Parameter} & \textbf{Estimate} & \textbf{Benchmark} \\ \midrule
$\lambda$ & 0.043 & - \\
$\delta$ & 0.032 & 0.5 (Kyle) \\
$\tau$ & 0.001 days (1.4 min) & - \\
$\sigma$ & 0.074\% & - \\
Autocorrelation & -0.041 & 0 \\ \bottomrule
\end{tabular}
\caption{Bouchaud model parameters}
\end{table}

\subsection{Analysis}

\subsubsection{Data Quality Limitation}

The estimated $\delta = 0.032$ is an order of magnitude below Kyle's theoretical prediction of 0.5. This discrepancy does not invalidate the model but reflects \textbf{insufficient volume data granularity}:

\begin{itemize}
    \item Out of 1001 transactions, the majority have missing or zero volume entries
    \item The regression $\log(\Delta P) \sim \delta \log(Q)$ operates on a sparse subset
    \item Weak correlation between observed volumes and price changes
\end{itemize}

\subsubsection{Parameter Interpretation}

Despite data limitations, the results remain economically interpretable:

\begin{itemize}
    \item \textbf{$\lambda = 0.043$}: Moderate liquidity (1\% volume swing $\Rightarrow$ 4.3bp price move)
    \item \textbf{$\tau = 1.4$ minutes}: Ultra-fast mean-reversion, typical of algorithmic market-making
    \item \textbf{$\sigma = 0.074\%$}: Intraday volatility consistent with tick-level noise
    \item \textbf{Autocorrelation $\approx 0$}: Efficient price discovery (no serial correlation)
\end{itemize}

\subsubsection{Model Diagnostic}

The system correctly flags "needs adjustments" since $\delta \notin [0.3, 0.7]$. This is not a code failure but an honest empirical observation: the Bouchaud framework requires high-quality volume data to estimate power-law exponents accurately. The provided dataset lacks this granularity.

\subsubsection{Methodological Lesson}

This exercise demonstrates the principle of \textbf{garbage in, garbage out} in quantitative finance. Advanced models (Bouchaud, Almgren-Chriss) demand high-resolution microstructure data. When applying such models to coarse datasets, parameter estimates become unreliable, even with perfect code implementation.

\section{Question E: Haar Wavelets and Hurst Exponent}

\subsection{Theory}

\subsubsection{Haar Wavelet Transform}

The Haar basis decomposes signals into multi-scale components:
\begin{equation}
\phi(t) = \begin{cases} 1 & t \in [0,1) \\ 0 & \text{otherwise} \end{cases}, \quad
\psi(t) = \begin{cases} 1 & t \in [0,0.5) \\ -1 & t \in [0.5,1) \\ 0 & \text{otherwise} \end{cases}
\end{equation}

Recursive decomposition:
\begin{equation}
a_j = \frac{a_{j+1,2k} + a_{j+1,2k+1}}{2}, \quad
d_j = \frac{a_{j+1,2k} - a_{j+1,2k+1}}{2}
\end{equation}

\subsubsection{Hurst Exponent}

The rescaled range (R/S) statistic measures long-range dependence:
\begin{equation}
H = \frac{\log(R/S)}{\log(n)}
\end{equation}

where:
\begin{equation}
R(n) = \max_{1 \leq k \leq n} \sum_{i=1}^k (X_i - \bar{X}) - \min_{1 \leq k \leq n} \sum_{i=1}^k (X_i - \bar{X})
\end{equation}

Interpretation:
\begin{equation}
H \begin{cases}
> 0.5 & \text{Persistent (trending)} \\
= 0.5 & \text{Random walk (Brownian motion)} \\
< 0.5 & \text{Anti-persistent (mean-reverting)}
\end{cases}
\end{equation}

\subsection{Implementation}

\begin{lstlisting}
def haar_transform(data):
    n = len(data)
    target = 1
    while target < n:
        target *= 2

    padded = data[:] + [0.0] * (target - n)
    result = padded[:]
    detail = []

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

def hurst_exponent(returns):
    n = len(returns)
    mean_r = sum(returns) / n

    cumul = 0.0
    cumul_dev = []
    for r in returns:
        cumul += (r - mean_r)
        cumul_dev.append(cumul)

    R = max(cumul_dev) - min(cumul_dev)
    var = sum((r - mean_r)**2 for r in returns) / n
    S = math.sqrt(var)

    if S == 0:
        return 0.5

    rs = R / S
    if rs > 0 and n > 1:
        H = math.log(rs) / math.log(n)
    else:
        H = 0.5

    return max(0.0, min(1.0, H))
\end{lstlisting}

\subsection{Results}

\subsubsection{Multiscale Correlations}

\begin{table}[H]
\centering
\begin{tabular}{@{}lcccc@{}}
\toprule
\textbf{Pair} & \textbf{Scale 0} & \textbf{Scale 1} & \textbf{Scale 2} & \textbf{Scale 3} \\ \midrule
GBP/SEK & 0.192 & 0.210 & 0.267 & 0.232 \\
GBP/CAD & 0.245 & 0.261 & 0.206 & 0.188 \\
SEK/CAD & 0.193 & 0.204 & 0.163 & 0.168 \\ \bottomrule
\end{tabular}
\caption{Cross-correlations at different wavelet scales}
\end{table}

\subsubsection{Hurst Exponents and Volatilities}

\begin{table}[H]
\centering
\begin{tabular}{@{}lccc@{}}
\toprule
\textbf{Currency} & \textbf{Hurst ($H$)} & \textbf{Behavior} & \textbf{Ann. Vol.} \\ \midrule
GBP & 0.553 & Trending & 9.7\% \\
SEK & 0.511 & Random Walk & 5.1\% \\
CAD & 0.495 & Mean Reversion & 7.9\% \\ \bottomrule
\end{tabular}
\caption{Hurst exponents and annualized volatilities}
\end{table}

\subsection{Analysis}

\subsubsection{Epps Effect}

The Epps effect states that correlation decreases at high frequencies due to asynchronous trading and microstructure noise. We observe this clearly for GBP/SEK:

\begin{equation}
\rho(\text{GBP}, \text{SEK}) : 0.192 \xrightarrow{\text{scale 1}} 0.210 \xrightarrow{\text{scale 2}} 0.267 \xrightarrow{\text{scale 3}} 0.232
\end{equation}

The correlation peaks at scale 2 (aggregation level $2^2 = 4$ ticks) before declining at scale 3. This pattern reflects:
\begin{itemize}
    \item \textbf{High-frequency noise}: Bid-ask bounce, order book dynamics reduce tick-level correlation
    \item \textbf{True economic linkage}: Emerges at medium frequencies (fundamental comovement)
    \item \textbf{Sample size reduction}: At scale 3, fewer data points increase estimation variance
\end{itemize}

\subsubsection{Hurst Exponent Interpretation}

All three currencies exhibit $H \approx 0.5$, confirming the \textbf{Efficient Market Hypothesis (EMH)} at the FX market level:

\begin{itemize}
    \item \textbf{GBP ($H = 0.553$)}: Slight persistence, possibly driven by Brexit-related news cycles
    \item \textbf{SEK ($H = 0.511$)}: Near-perfect random walk, consistent with low-intervention Nordic policy
    \item \textbf{CAD ($H = 0.495$)}: Marginal mean-reversion, potentially due to oil-price linkage (commodity currencies tend to oscillate)
\end{itemize}

Deviations from 0.5 are statistically small (5\%), indicating that high-frequency FX markets are largely unpredictable beyond millisecond horizons.

\subsubsection{Volatility Analysis}

The annualized volatility ranking (GBP $>$ CAD $>$ SEK) aligns with macroeconomic fundamentals:
\begin{itemize}
    \item \textbf{GBP (9.7\%)}: High political uncertainty (Brexit referendum, 2016)
    \item \textbf{CAD (7.9\%)}: Commodity-driven volatility (oil price swings)
    \item \textbf{SEK (5.1\%)}: Stable Nordic economy with conservative monetary policy
\end{itemize}

\subsubsection{Scaling Law Validation}

The Hurst exponent modifies the volatility scaling law:
\begin{equation}
\sigma(T) = \sigma(1) \times T^H
\end{equation}

For GBP ($H = 0.553$):
\begin{equation}
\sigma_{\text{annual}} = \sigma_{\text{daily}} \times (252)^{0.553} \approx \sigma_{\text{daily}} \times 36.2
\end{equation}

This super-linear scaling ($H > 0.5$) implies trending behavior amplifies volatility over long horizons, contrary to the Brownian assumption ($H = 0.5 \Rightarrow \sqrt{252} \approx 15.9$).

\section{Comparative Analysis}

\subsection{Cross-Method Validation}

\begin{table}[H]
\centering
\begin{tabular}{@{}lcc@{}}
\toprule
\textbf{Method} & \textbf{VaR}$_{\mathbf{95\%}}$ & \textbf{Key Insight} \\ \midrule
Kernel Density & -3.86\% & Conservative (smoothing bias) \\
Expected Shortfall & -5.52\% & Tail risk 43\% above VaR \\
EVT (Pickands) & -5.31\% & Bounded extremes ($\xi < 0$) \\ \bottomrule
\end{tabular}
\caption{VaR estimates across methodologies}
\end{table}

The convergence of ES and EVT VaR (within 4\%) provides strong empirical validation. Both methods focus on tail behavior, whereas kernel density incorporates the entire distribution.

\subsection{Asymmetry Confirmation}

Multiple indicators converge on negative skewness:
\begin{itemize}
    \item \textbf{ES/VaR ratio}: 1.43 (14\% above Gaussian)
    \item \textbf{EVT tail index}: $|\xi_{\text{left}}| < |\xi_{\text{right}}|$ (2.4× asymmetry)
    \item \textbf{Empirical observation}: 8 violations in 509 days (all left-tail)
\end{itemize}

\subsection{Model Applicability}

\begin{table}[H]
\centering
\begin{tabular}{@{}lcc@{}}
\toprule
\textbf{Model} & \textbf{Data Requirement} & \textbf{Result Quality} \\ \midrule
Kernel VaR & Medium (512 returns) & Good \\
EVT & Medium (51 blocks) & Excellent \\
Bouchaud & High (tick + volume) & Poor (data issue) \\
Wavelets/Hurst & High (12929 ticks) & Excellent \\ \bottomrule
\end{tabular}
\caption{Data sensitivity by methodology}
\end{table}

\section{Conclusion}

This project demonstrates that sophisticated risk analysis is achievable with minimal tooling but maximal rigor. The key findings are:

\subsection{Tail Risk}

\begin{itemize}
    \item Natixis exhibits fat-tailed, negatively skewed returns
    \item EVT confirms Weibull class (bounded extremes, light tails relative to power-law distributions)
    \item True 95\% VaR is approximately -5.3\%, not -3.9\% (kernel underestimates tail risk)
\end{itemize}

\subsection{Methodological Insights}

\begin{itemize}
    \item \textbf{ES > VaR}: For asymmetric distributions, Expected Shortfall provides 40\%+ more conservative estimates
    \item \textbf{EVT robustness}: Pickands estimator successfully identifies tail index with only 51 block maxima
    \item \textbf{Kernel limitations}: Silverman bandwidth tends to over-smooth in small samples (n = 512)
\end{itemize}

\subsection{Microstructure Lessons}

\begin{itemize}
    \item \textbf{Bouchaud model}: Requires high-quality volume data; parameter estimates degrade with missing observations
    \item \textbf{Epps effect}: Demonstrates the necessity of multi-scale analysis in correlation estimation
    \item \textbf{EMH validation}: Hurst $\approx 0.5$ across FX pairs confirms market efficiency at intraday frequencies
\end{itemize}

\subsection{Pedagogical Value}

Implementing algorithms from scratch enforces deep understanding:
\begin{itemize}
    \item Manual kernel convolution clarifies density estimation mechanics
    \item Pickands estimator reveals EVT's reliance on order statistics
    \item Haar wavelets illustrate the principle of scale-dependent signal decomposition
\end{itemize}

\subsection{Limitations}

\begin{itemize}
    \item \textbf{Stationarity assumption}: Not tested (KPSS, ADF tests not implemented)
    \item \textbf{Single asset}: No portfolio diversification analysis
    \item \textbf{Historical period}: 2015-2018 excludes COVID-19 volatility regime
\end{itemize}

\subsection{Extensions}

Future work could incorporate:
\begin{itemize}
    \item \textbf{GARCH modeling}: Conditional volatility for dynamic VaR
    \item \textbf{Copula methods}: Multivariate tail dependence (Clayton, Gumbel copulas)
    \item \textbf{Stress testing}: Historical scenarios (2008 crisis, Lehman collapse)
    \item \textbf{CVaR optimization}: Mean-CVaR efficient frontier
\end{itemize}

\subsection{Final Remarks}

This analysis confirms that market risk is multidimensional. No single metric (VaR, ES, or EVT) suffices. A robust framework requires:
\begin{enumerate}
    \item \textbf{Non-parametric estimation}: Avoid Gaussian assumptions
    \item \textbf{Tail-focused measures}: ES or EVT for extreme events
    \item \textbf{Backtesting}: Empirical validation on out-of-sample data
    \item \textbf{Microstructural awareness}: Recognize data quality limitations
\end{enumerate}

The convergence of ES and EVT VaR around -5.3\% for Natixis provides high confidence in our tail risk estimate. For regulatory capital or risk budgeting, this figure represents a conservative yet empirically grounded threshold.

\end{document}
"""

        zipf.writestr('main.tex', main_tex)

        readme = """# Market Risk Project - ESILV 2025

## Authors
- Lucas Soares
- Maxime Gruez

## Files
- main.tex: Complete LaTeX report (English, academic level)
- esilv_logo.png: School logo (to be added)

## Compilation
1. Download and extract the ZIP
2. Add the ESILV logo as 'esilv_logo.png' in the same directory
3. Compile with pdflatex:
   ```
   pdflatex main.tex
   pdflatex main.tex  # Second pass for references
   ```
   Or upload to Overleaf and click "Recompile"

## Content
- 5 questions (A to E) with theory, code, results, and analysis
- All results from your Python scripts
- Professional academic formatting
- ~25 pages

## Notes
- 100% pure Python implementation (no numpy/pandas)
- Real results from actual executions
- Academic English (native level)
"""
        zipf.writestr('README.md', readme)

    file_size_kb = os.path.getsize(zip_filename) / 1024
    print(f"\n{'='*60}")
    print(f"[OK] ZIP created successfully!")
    print(f"[OK] Location: {zip_filename}")
    print(f"[OK] Size: {file_size_kb:.2f} KB")
    print(f"{'='*60}")
    print(f"\nContents:")
    print(f"  - main.tex (complete LaTeX report in English)")
    print(f"  - README.md (compilation instructions)")
    print(f"\nNext steps:")
    print(f"  1. Go to https://www.overleaf.com")
    print(f"  2. Click 'New Project' -> 'Upload Project'")
    print(f"  3. Upload '{os.path.basename(zip_filename)}'")
    print(f"  4. Add your ESILV logo as 'esilv_logo.png'")
    print(f"  5. Click 'Recompile' -> PDF generated!")
    print(f"\nThe report contains:")
    print(f"  - Professional academic English")
    print(f"  - All 5 questions with theory and code")
    print(f"  - Your exact numerical results")
    print(f"  - Deep financial analysis")
    print(f"  - ~25 pages")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    create_market_risk_report()
