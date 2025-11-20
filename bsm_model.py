import numpy as np
from scipy.stats import norm

class BlackScholes:
    """
    Model class for Black-Scholes-Merton Option Pricing.
    """
    def __init__(self, S, K, T_days, r_pct, sigma_pct, q_pct=0.0):
        """
        Initialize with raw inputs.
        
        :param S: Spot Price
        :param K: Strike Price
        :param T_days: Time to expiration in Days
        :param r_pct: Risk-free rate in Percentage (e.g., 5.0 for 5%)
        :param sigma_pct: Volatility in Percentage (e.g., 20.0 for 20%)
        :param q_pct: Dividend Yield / Foreign Rate in Percentage
        """
        self.S = float(S)
        self.K = float(K)
        self.T = float(T_days) / 365.0
        self.r = float(r_pct) / 100.0
        self.sigma = float(sigma_pct) / 100.0
        self.q = float(q_pct) / 100.0

    def _d1_d2(self):
        """
        Calculate d1 and d2 parameters.
        Handles edge cases where T or sigma is close to zero.
        """
        if self.T <= 1e-9 or self.sigma <= 1e-9:
            return None, None
        
        d1 = (np.log(self.S / self.K) + (self.r - self.q + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))
        d2 = d1 - self.sigma * np.sqrt(self.T)
        return d1, d2

    def calculate_all(self):
        """
        Compute all option metrics (Price + Greeks).
        Returns a dictionary.
        """
        results = {
            'call_price': 0.0, 'put_price': 0.0,
            'call_delta': 0.0, 'put_delta': 0.0,
            'gamma': 0.0, 'vega': 0.0,
            'call_theta': 0.0, 'put_theta': 0.0,
            'call_rho': 0.0, 'put_rho': 0.0
        }

        # Edge case: Expiration or Zero Volatility
        if self.T <= 1e-9:
            # Intrinsic value
            results['call_price'] = max(0.0, self.S - self.K)
            results['put_price'] = max(0.0, self.K - self.S)
            # Deltas at expiration
            if self.S > self.K:
                results['call_delta'] = 1.0
                results['put_delta'] = 0.0
            elif self.S < self.K:
                results['call_delta'] = 0.0
                results['put_delta'] = -1.0
            return results

        d1, d2 = self._d1_d2()
        if d1 is None: # Should be covered by T check, but safety for sigma=0
             results['call_price'] = max(0.0, self.S - self.K)
             results['put_price'] = max(0.0, self.K - self.S)
             return results

        # Pre-compute common terms
        sqrt_T = np.sqrt(self.T)
        exp_mqT = np.exp(-self.q * self.T) # e^(-qT)
        exp_mrT = np.exp(-self.r * self.T) # e^(-rT)
        
        N_d1 = norm.cdf(d1)
        N_d2 = norm.cdf(d2)
        N_neg_d1 = norm.cdf(-d1)
        N_neg_d2 = norm.cdf(-d2)
        n_d1 = norm.pdf(d1) # Standard Normal PDF

        # Prices
        results['call_price'] = self.S * exp_mqT * N_d1 - self.K * exp_mrT * N_d2
        results['put_price'] = self.K * exp_mrT * N_neg_d2 - self.S * exp_mqT * N_neg_d1

        # Delta
        results['call_delta'] = exp_mqT * N_d1
        results['put_delta'] = exp_mqT * (N_d1 - 1)

        # Gamma (Same for Call & Put)
        results['gamma'] = (exp_mqT * n_d1) / (self.S * self.sigma * sqrt_T)

        # Vega (Same for Call & Put) - Display as change per 1% vol
        raw_vega = self.S * exp_mqT * sqrt_T * n_d1
        results['vega'] = raw_vega / 100.0

        # Theta (Annual)
        term1 = -(self.S * exp_mqT * n_d1 * self.sigma) / (2 * sqrt_T)
        
        call_theta_yr = term1 - self.r * self.K * exp_mrT * N_d2 + self.q * self.S * exp_mqT * N_d1
        put_theta_yr = term1 + self.r * self.K * exp_mrT * N_neg_d2 - self.q * self.S * exp_mqT * N_neg_d1
        
        # Convert to Daily Theta
        results['call_theta'] = call_theta_yr / 365.0
        results['put_theta'] = put_theta_yr / 365.0

        # Rho - Display as change per 1% rate
        raw_call_rho = self.K * self.T * exp_mrT * N_d2
        raw_put_rho = -self.K * self.T * exp_mrT * N_neg_d2
        
        results['call_rho'] = raw_call_rho / 100.0
        results['put_rho'] = raw_put_rho / 100.0

        return results

if __name__ == "__main__":
    # Quick verification
    # S=100, K=100, T=365 days (1yr), r=5%, sigma=20%, q=0%
    bs = BlackScholes(100, 100, 365, 5, 20, 0)
    res = bs.calculate_all()
    print("Verification (S=100, K=100, T=1yr, r=5%, v=20%):")
    print(f"Call Price: {res['call_price']:.4f} (Expected ~10.45)")
    print(f"Put Price:  {res['put_price']:.4f} (Expected ~5.57)")
    print(f"Call Delta: {res['call_delta']:.4f} (Expected ~0.63)")
