import zipfile
import os
import shutil

def create_market_risk_report():
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    zip_filename = os.path.join(downloads_path, "Market_Risk_Report_Final.zip")

    # Image files from Downloads
    image_files = {
        'kernel': 'WhatsApp Image 2025-12-29 at 13.45.14.jpeg',
        'filter': 'WhatsApp Image 2025-12-29 at 13.49.33.jpeg',
        'expected_shortfall': 'WhatsApp Image 2025-12-29 at 13.50.05.jpeg',
        'pickands': 'WhatsApp Image 2025-12-29 at 13.58.24.jpeg',
        'blocks': 'WhatsApp Image 2025-12-29 at 13.58.36.jpeg',
        'bouchaud': 'WhatsApp Image 2025-12-29 at 14.20.51.jpeg',
        'gamma': 'WhatsApp Image 2025-12-29 at 14.21.19.jpeg',
        'course_var': 'WhatsApp Image 2025-12-29 at 15.12.59.jpeg',
        'course_kernel': 'WhatsApp Image 2025-12-29 at 15.13.08.jpeg',
        'course_gev_moments': 'WhatsApp Image 2025-12-29 at 15.13.20.jpeg',
        'course_gumbel': 'WhatsApp Image 2025-12-29 at 15.14.05.jpeg',
        'course_bouchaud': 'WhatsApp Image 2025-12-29 at 15.14.19.jpeg',
        'course_bouchaud2': 'WhatsApp Image 2025-12-29 at 15.14.43.jpeg',
        'course_hurst': 'WhatsApp Image 2025-12-29 at 15.14.59.jpeg',
        'course_moments': 'WhatsApp Image 2025-12-29 at 15.15.15.jpeg',
        'course_pickands': 'PickandsEstimator.jpeg',
        'output_menu': 'WhatsApp Image 2025-12-29 at 15.21.31.jpeg',
        'output_a': 'WhatsApp Image 2025-12-29 at 15.38.50.jpeg',
        'output_b': 'WhatsApp Image 2025-12-29 at 15.39.42.jpeg',
        'output_c': 'WhatsApp Image 2025-12-29 at 15.40.13.jpeg',
        'output_d': 'WhatsApp Image 2025-12-29 at 15.40.45.jpeg'
    }

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:

        main_tex = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[english]{babel}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{geometry}
\usepackage{hyperref}
\usepackage{float}
\usepackage{fancyvrb}

\geometry{margin=2.5cm}

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

        {\Large Quantitative Finance Project}\\[2cm]

        {\large Lucas Soares \hspace{3cm} Maxime Gruez}\\[0.5cm]
        {\large ESILV - Financial Engineering}\\[0.3cm]
        {\large Academic Year 2025-2026}\\[2cm]

        {\large December 30, 2025}\\[3cm]

        \vfill

        {\large ESILV}

    \end{center}
\end{titlepage}
\newpage

\tableofcontents
\newpage

\section{Introduction}

This project applies various market risk measurement techniques to different data. We implemented everything from scratch in pure Python - no numpy, no pandas, no scipy. Just Python's standard library and math module.

\subsection{Project Structure}

The project is organized around three main directories:

\begin{itemize}
\item \textbf{data/}: Contains our datasets - Natixis daily prices (2015-2018, 1023 observations) and intraday transaction data for Question D, plus high-frequency forex data for Question E
\item \textbf{scripts/}: All our Python implementations, one file per question
\end{itemize}

At the root, we have \texttt{main.py} which provides an interactive console menu. When you run it, you get:

\begin{figure}[H]
\centering
\includegraphics[width=0.5\textwidth]{output_menu.jpeg}
\end{figure}

The architecture is simple: each question script (\texttt{question\_a\_b.py}, \texttt{question\_c.py}, etc.) is self-contained and can be run independently. The main script just uses \texttt{exec()} to load and execute them based on user input.

\subsection{Methodology}

The main objective was to calculate Value-at-Risk through multiple approaches and compare their results. We used VaR methods, Expected Shortfall, Extreme Value Theory, the Bouchaud model, and Hurst exponent analysis. Each technique gives a different perspective on the risk.

We manually implemented kernel density estimation, the Pickands estimator with gamma functions, log-linear regression for the Bouchaud model, and the Hurst exponent.

\section{Question A: Non-Parametric VaR}

\subsection{Theory}

Value-at-Risk at confidence level $\alpha$ represents the maximum expected loss over a given time period at a specified confidence level. VaR is defined as the quantile:
\begin{equation}
\text{VaR}_\alpha = \inf\{x : F(x) \geq \alpha\}
\end{equation}

where $F$ is the cumulative distribution function of returns.

According to the assignment, we estimate the density function non-parametrically using the Parzen-Rosenblatt kernel density estimator with the biweight kernel:
\begin{equation}
K(u) = \frac{15}{16}(1-u^2)^2 \mathbb{1}_{|u| \leq 1}
\end{equation}

The kernel density estimate is given by:

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{course_kernel.jpeg}
\end{figure}
\begin{center}
\textit{Kernel density estimation}
\end{center}

where $h$ is the bandwidth parameter. We use the optimal choice for $h$ (\url{https://en.wikipedia.org/wiki/Kernel_density_estimation#A_rule-of-thumb_bandwidth_estimator}):

$h = 1.06 \times \hat{\sigma} \times n^{-1/5}$

\begin{figure}[H]
\centering
\includegraphics[width=0.9\textwidth]{course_var.jpeg}
\end{figure}
\begin{center}
\textit{VaR computation}
\end{center}

where $\hat{\sigma}$ is the sample standard deviation and $n$ is the sample size.

To compute VaR, we use the integral.

\subsection{Implementation}

Our implementation uses the biweight kernel with Silverman's bandwidth and numerical integration for VaR calculation:

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{code_kernel.jpeg}
\end{figure}
\begin{center}
\textit{Biweight kernel and VaR calculation}
\end{center}

We filter the data by year to separate training (2015-2016) and test (2017-2018) periods:

\begin{figure}[H]
\centering
\includegraphics[width=0.65\textwidth]{code_filter.jpeg}
\end{figure}
\begin{center}
\textit{Data filtering by year}
\end{center}

\subsection{Results}

We estimate VaR on the training period (2015-2016) and validate it through backtesting on the test period (2017-2018).

\begin{figure}[H]
\centering
\includegraphics[width=0.5\textwidth]{output_a.jpeg}
\end{figure}

\subsection{Analysis}

The VaR we got is $-3.86\%$ at 95\% confidence. Thus, 95\% of trading days, losses should stay above this level, and only 5\% of the time we would expect worst losses.

But when we backtest on 2017-2018 data, we only see 8 violations out of 509 days, which corresponds to 1.57\% of the cases. We can see that the model overestimates the risk, as 2015-2016 is very volatile compared to 2017-2018, we think this is one of the reasons. The model overestimates as it trained on more volatile data.

Secondly, the biweight kernel smooths everything out, including the tails. We notice that this makes the tails look fatter than they really are.

Finally, we only had 512 observations in the training set which is not a huge sample.

Conclusion: the model is overestimating the data but we validate the choice of the non parametric VaR as it's better to overestimate than underestimate data in finance.

\section{Question B: Expected Shortfall}

\subsection{Theory}

Expected Shortfall (ES) measures the expected loss given that the loss exceeds the VaR threshold. It is defined as:
\begin{equation}
\text{ES}_\alpha = \mathbb{E}[X \mid X \leq \text{VaR}_\alpha]
\end{equation}

VaR calculates the maximum loss whereas ES calculates the average loss beyond the VaR. We also know thanks to the course that ES is a coherent risk compared to VaR.

\subsection{Implementation}

We use the formula of ES to compute it on Python:

\begin{figure}[H]
\centering
\includegraphics[width=0.6\textwidth]{code_expected_shortfall.jpeg}
\end{figure}
\begin{center}
\textit{Expected Shortfall}
\end{center}

\subsection{Results}

We compute ES on the same training period (2015-2016) used for VaR estimation:

\begin{figure}[H]
\centering
\includegraphics[width=0.5\textwidth]{output_b.jpeg}
\end{figure}

\subsection{Analysis}

The ES is $-5.52\%$ versus VaR at $-3.86\%$ - that's a 1.66pp gap. This tells us that losses beyond the VaR threshold are pretty severe. The ES/VaR ratio we got is 1.43. This means Natixis stock has fat tails.

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

\begin{figure}[H]
\centering
\includegraphics[width=0.6\textwidth]{course_pickands.jpeg}
\end{figure}

where $X_{(i)}$ denotes the $i$-th order statistic and $k$ is chosen as $n/4$.

Once $\xi$ is estimated, we compute $\mu$ and $\sigma$ using the theoretical moments of the GEV distribution. Using the gamma function $\Gamma(\cdot)$, the mean and variance of a GEV distribution are:

\begin{equation}
\mathbb{E}[X] = \mu + \frac{\sigma}{\xi}(g_1 - 1) \quad \text{for } \xi < 1
\end{equation}

\begin{equation}
\text{Var}(X) = \frac{\sigma^2}{\xi^2}(g_2 - g_1^2) \quad \text{for } \xi < 1/2
\end{equation}

where $g_k = \Gamma(1 - k\xi)$.

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{course_gev_moments.jpeg}
\end{figure}
\begin{center}
\textit{GEV moments with gamma function}
\end{center}

For the Gumbel case ($\xi = 0$), we have:
\begin{equation}
\mathbb{E}[X] = \mu + \gamma \sigma, \quad \text{Var}(X) = \frac{\pi^2 \sigma^2}{6}
\end{equation}

where $\gamma \approx 0.5772$ is the Euler-Mascheroni constant.

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{course_gumbel.jpeg}
\end{figure}
\begin{center}
\textit{Gumbel distribution parameters}
\end{center}

The VaR at confidence level $p$ is obtained by inverting the GEV distribution:
\begin{equation}
\text{VaR}_p = \mu - \frac{\sigma}{\xi}\left(1 - \left[-\ln(1-p)\right]^{-\xi}\right)
\end{equation}

\subsection{Implementation}

Our implementation uses the Pickands estimator and the method of moments with the gamma function:

\begin{figure}[H]
\centering
\includegraphics[width=0.95\textwidth]{code_pickands.jpeg}
\end{figure}
\begin{center}
\textit{Pickands estimator and GEV parameters}
\end{center}

We apply block maxima method with block size 20 to extract extremes from the return series:

\begin{figure}[H]
\centering
\includegraphics[width=0.7\textwidth]{code_blocks.jpeg}
\end{figure}
\begin{center}
\textit{Block maxima extraction}
\end{center}

\subsection{Results}

We estimate GEV parameters for both tails using block size 20:

\begin{figure}[H]
\centering
\includegraphics[width=0.5\textwidth]{output_c.jpeg}
\end{figure}

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

\begin{figure}[H]
\centering
\includegraphics[width=0.9\textwidth]{course_bouchaud.jpeg}
\end{figure}
\begin{center}
\textit{Bouchaud transitory impact model}
\end{center}

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

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{course_bouchaud2.jpeg}
\end{figure}
\begin{center}
\textit{Backward price definition and impact decay}
\end{center}

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
\gamma = \frac{\ln(\rho(1)/\rho(2))}{\ln(2)}
\end{equation}

Empirical studies (Bouchaud et al., 2004) find $\gamma \approx 0.5$ for stocks, indicating that price impacts decay relatively slowly, with market memory extending over multiple transactions.

\subsection{Implementation}

We implement the Bouchaud model by computing impact as price change normalized by spread, then performing log-linear regression:

\begin{figure}[H]
\centering
\includegraphics[width=0.95\textwidth]{code_bouchaud.jpeg}
\end{figure}
\begin{center}
\textit{Bouchaud's price impact model}
\end{center}

For the temporal decay parameter $\gamma$, we compute autocorrelations at lags 1 and 2:

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{code_gamma.jpeg}
\end{figure}
\begin{center}
\textit{Temporal decay parameter estimation}
\end{center}

\subsection{Results}

We apply the model to intraday transaction data for Natixis:

\begin{figure}[H]
\centering
\includegraphics[width=0.5\textwidth]{output_d.jpeg}
\end{figure}

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

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{course_hurst.jpeg}
\end{figure}
\begin{center}
\textit{Hurst exponent estimation}
\end{center}

\subsubsection{Method of Absolute Moments}

We use the empirical absolute moments method. Define the $k$-th absolute moment at resolution $1/N$:

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{course_moments.jpeg}
\end{figure}
\begin{center}
\textit{Empirical absolute moments}
\end{center}

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

The key insight is in the aggregation: by summing consecutive pairs of returns and computing their squared moments, we effectively double the time scale. The ratio $M'_2 / M_2$ captures how variance scales with time, revealing the Hurst exponent.

Our implementation is straightforward - we calculate moments at two different resolutions and compute the Hurst exponent from their ratio.

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

Coding everything from scratch in pure Python was honestly painful at times. When you implement the Pickands estimator yourself with gamma functions, you can't just treat it as a black box anymore.

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

        # Add images to ZIP
        for img_key, img_filename in image_files.items():
            img_path = os.path.join(downloads_path, img_filename)
            if os.path.exists(img_path):
                # Rename to simpler names
                if img_key.startswith('course_') or img_key.startswith('output_'):
                    simple_name = f'{img_key}.jpeg'
                else:
                    simple_name = f'code_{img_key}.jpeg'
                zipf.write(img_path, simple_name)

        readme = """# Market Risk Measurement: Application to Natixis Stock

## Authors
Lucas Soares & Maxime Gruez
ESILV - Financial Engineering
Academic Year 2025-2026

## Project Description
This project implements various market risk measurement techniques applied to Natixis stock data. All implementations are done in pure Python without external packages (no numpy, pandas, scipy).

## Contents
- `main.tex`: Complete LaTeX report with theory, implementation, results and analysis
- `code_*.jpeg`: Screenshots of actual implementation code

## Report Compilation
To compile the LaTeX report:

1. Extract the ZIP file
2. Upload to Overleaf or compile locally:
   ```bash
   pdflatex main.tex
   pdflatex main.tex  # Run twice for TOC
   ```

## Running the Code
The complete project code is available at:
https://github.com/treeboatt/Market-Risk-Project

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
- Question E: Hurst exponent analysis

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
    print(f"[OK] Images: 7 code + 9 course + 5 outputs")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    create_market_risk_report()
