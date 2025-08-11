import numpy as np

def make_linear_interp_with_extrapolation(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.ndim != 1 or y.ndim != 1 or x.size != y.size:
        raise ValueError("x and y must be 1D arrays of the same length")

    if not np.all(np.diff(x) > 0):
        idx = np.argsort(x)
        x, y = x[idx], y[idx]

    m_lo = (y[1] - y[0]) / (x[1] - x[0])
    b_lo = y[0] - m_lo * x[0]
    m_hi = (y[-1] - y[-2]) / (x[-1] - x[-2])
    b_hi = y[-1] - m_hi * x[-1]

    def f(xq):
        xq = np.asarray(xq, dtype=float)
        yq = np.empty_like(xq, dtype=float)

        lo = xq < x[0]
        hi = xq > x[-1]
        mid = ~(lo | hi)

        if np.any(mid):
            yq[mid] = np.interp(xq[mid], x, y)
        if np.any(lo):
            yq[lo] = m_lo * xq[lo] + b_lo
        if np.any(hi):
            yq[hi] = m_hi * xq[hi] + b_hi
        return yq

    return f
