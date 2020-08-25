---
# About
---

Due to the nature of collecting and testing samples and reporting cases the data is very noisy. We can use a filter to smooth this.

The filter used here was introduced by Savitzky and  Golay in 1964 in their paper published in Analytical chemistry (1).  This filter fits low order polynomials over sliding windows of the time series data using least squares regression.  Apart from its application to extract signal from noise it also offers easy access to the derivatives.  The Savitzky-Golay (savgol) filter is implemented in [SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html) which makes it easy to use.



* The first graph shows the daily new cases as dots and the fitted savgol data as lines.
* The graphs adjacent shows the first derivatives of the above mentioned.
  * The sign (+/-) indicates increased/decreased cases.
  * The magnitude indicates how much change.
* The third graphs simply plots the cumulative cases .



**Data source:** https://github.com/CSSEGISandData/COVID-19.git

**Source:** https://github.com/ArmandBester/sars-cov19-dashboard







---
### References

1. A Savitzky and M. J. E. Golay.  **Smoothing and Differentiation of Data by Simplified Least Squares Procedures.**  1964.  *Anal. Chem. 1964, 36, 8, 1627–1639*
