---
# About
---

Due to the nature of collecting and testing samples and reporting cases the data is very noisy. We can use a filter to smooth this.

The filter used here was introduced by Savitzky and  Golay in 1964 in there paper published in Analytical chemistry (1).  This filter fits low order polynomials over as sliding windows of the time series data using least squares regression.  Apart from it's application to extract signal from noise it also offers easy access to the derivatives.



---
### References

1. A Savitzky and M. J. E. Golay.  **Smoothing and Differentiation of Data by Simplified Least Squares Procedures.**  1964.  *Anal. Chem. 1964, 36, 8, 1627–1639*