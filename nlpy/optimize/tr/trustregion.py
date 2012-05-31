"""
Class definition for Trust-Region Algorithm
"""

from nlpy.krylov.pcg  import TruncatedCG
from nlpy.krylov.ppcg import ProjectedCG
import numpy as np
from math import sqrt

__docformat__ = 'restructuredtext'

class TrustRegionFramework(object):
    """
    Initializes an object allowing management of a trust region.

    :keywords:

        :Delta:         Initial trust-region radius (default: 1.0)
        :eta1:          Step acceptance threshold   (default: 0.01)
        :eta2:          Radius increase threshold   (default: 0.99)
        :gamma1:        Radius decrease factor      (default: 1/3)
        :gamma2:        Radius increase factor      (default: 2.5)

    Subclass and override :meth:`UpdateRadius` to implement custom trust-region
    management rules.

    See, e.g.,

    A. R. Conn, N. I. M. Gould and Ph. L. Toint, Trust-Region Methods,
    MP01 MPS-SIAM Series on Optimization, 2000.
    """

    def __init__(self, **kwargs):

        self.Delta0 = kwargs.get('Delta', 1.0) # Initial trust-region radius
        self.Delta  = self.Delta0 # Current trust-region radius
        self.DeltaMax = 1.0e+10 # Largest trust-region radius
        self.eta1   = kwargs.get('eta1', 0.01)     # Step acceptance threshold
        self.eta2   = kwargs.get('eta2', 0.99)     # Radius increase threshold
        self.gamma1 = kwargs.get('gamma1', 1.0/3)  # Radius decrease factor
        self.gamma2 = kwargs.get('gamma2', 2.5)    # Radius increase factor
        self.eps    = self._Epsilon() # Machine epsilon

    def _Epsilon(self):
        """
        Return approximate value of machine epsilon
        """
        one = 1.0
        eps = 1.0
        while (one + eps) > one:
            eps = eps / 2.0
        return eps*2.0

    def Rho(self, f, f_trial, m, check_positive=True):
        """
        Compute the ratio of actual versus predicted reduction
        rho = (f - f_trial)/(-m)
        """
        pred = -m + max(1.0, abs(f)) * 10.0 * self.eps
        ared = f - f_trial + max(1.0, abs(f)) * 10.0 * self.eps
        if pred > 0 or not check_positive:
            return ared/pred
        else:
            # Error: Negative predicted reduction
            msg = 'TrustRegion:: Nonpositive predicted reduction: %8.1e' % pred
            raise ValueError, msg
            return None

    def UpdateRadius(self, rho, stepNorm):
        """
        Update the trust-region radius. The rule implemented by this method is:

        Delta = gamma1 * stepNorm       if ared/pred <  eta1
        Delta = gamma2 * Delta          if ared/pred >= eta2
        Delta unchanged otherwise,

        where ared/pred is the quotient computed by self.Rho().
        """
        if rho < self.eta1:
            self.Delta = self.gamma1 * stepNorm
        elif rho >= self.eta2:
            self.Delta = min(max(self.Delta, self.gamma2 * stepNorm),
                              self.DeltaMax)

    def ResetRadius(self):
        """
        Reset radius to original value
        """
        self.Delta = self.Delta0



class TrustRegionSolver(object):
    """
    A generic template class for implementing solvers for the trust-region
    subproblem

    minimize    q(d)
    subject to  ||d|| <= radius,

    where q(d) is a quadratic function of the n-vector d, i.e., q has the
    general form q(d) = g' d + 1/2 d' H d,

    where `g` is a n-vector typically interpreted as the gradient of some
    merit function and `H` is a real symmetric n-by-n matrix. Note that `H`
    need not be positive semi-definite.

    The trust-region constraint `||d|| <= radius` can be defined in any
    norm although most derived classes currently implement the Euclidian
    norm only. Note however that any elliptical norm may be used via a
    preconditioner.

    For more information on trust-region methods, see

    A. R. Conn, N. I. M. Gould and Ph. L. Toint, Trust-Region Methods,
    MP01 MPS-SIAM Series on Optimization, 2000.
    """

    def __init__(self, qp, **kwargs):

        self.qp = qp

    def Solve(self):
        """
        Solve the trust-region subproblem. This method must be overridden.
        """
        return None


class TrustRegionCG(TrustRegionSolver):
    """
    Instantiate a trust-region subproblem solver based on the truncated
    conjugate gradient method of Steihaug and Toint. See the :mod:`pcg` module
    for more information.

    The main difference between this class and the :class:`TrustRegionPCG`
    class is that :class:`TrustRegionPCG` only accepts explicit
    preconditioners (i.e. in matrix form). This class accepts an implicit
    preconditioner, i.e., any callable object.
    """

    def __init__(self, qp, **kwargs):

        TrustRegionSolver.__init__(self, qp, **kwargs)
        self.cgSolver = TruncatedCG(qp, **kwargs)
        self.niter = 0
        self.stepNorm = 0.0
        self.step = None
        self.m = None # Model value at candidate solution

    def Solve(self, **kwargs):
        """
        Solve trust-region subproblem using the truncated conjugate-gradient
        algorithm.
        """
        self.cgSolver.Solve(**kwargs)
        self.niter = self.cgSolver.niter
        self.stepNorm = self.cgSolver.stepNorm
        self.step= self.cgSolver.step
        self.m = self.qp.obj(self.step)        # Compute model reduction.
        #self.m = np.dot(self.g, self.step)
        #self.m += 0.5 * np.dot(self.step, self.cgSolver.H * self.step)
        return


class TrustRegionPCG(TrustRegionSolver):
    """
    Instantiate a trust-region subproblem solver based on the projected
    truncated conjugate gradient of Gould, Hribar and Nocedal.
    See the :mod:`ppcg` module for more information.

    The trust-region subproblem has the form

    minimize q(d)  subject to  Ad = 0  and  ||d|| <= radius,

    where q(d) is a quadratic function of the n-vector d, i.e., q has the
    general form q(d) = g' d + 1/2 d' H d,

    where `g` is a n-vector typically interpreted as the gradient of some
    merit function and `H` is a real symmetric n-by-n matrix. Note that `H`
    need not be positive semi-definite.

    The trust-region constraint `||d|| <= radius` can be defined in any
    norm although most derived classes currently implement the Euclidian
    norm only. Note however that any elliptical norm may be used via a
    preconditioner.

    For more information on trust-region methods, see

    A. R. Conn, N. I. M. Gould and Ph. L. Toint, Trust-Region Methods,
    MP01 MPS-SIAM Series on Optimization, 2000.
    """

    def __init__(self, qp, **kwargs):

        TrustRegionSolver.__init__(self, qp, **kwargs)
        self.cgSolver = ProjectedCG(qp, **kwargs)
        self.niter = 0
        self.stepNorm = 0.0
        self.step = None
        self.hprod = kwargs.get('matvec', None)
        self.m = None # Model value at candidate solution

    def Solve(self, **kwargs):
        """
        Solve trust-region subproblem using the projected truncated conjugate
        gradient algorithm.
        """
        self.cgSolver.Solve(**kwargs)
        self.niter = self.cgSolver.iter
        self.stepNorm = self.cgSolver.stepNorm
        self.step= self.cgSolver.x
        self.m = self.qp.obj(self.step)        # Compute model reduction.
        #self.m = np.dot(self.g, self.step)
        #self.m += 0.5 * np.dot(self.step, self.cgSolver.H * self.step)
        return


# Define GLTR solver only if available

try:
    from nlpy.krylov import pygltr

    class TrustRegionGLTR(TrustRegionSolver):
        """
        Instantiate a trust-region subproblem solver based on the Generalized
        Lanczos iterative method of Gould, Lucidi, Roma and Toint.
        See :mod:`pygltr` for more information.
        """

        def __init__(self, qp, **kwargs):

            TrustRegionSolver.__init__(self, qp, **kwargs)
            self.gltrSolver = pygltr.PyGltrContext(qp, **kwargs)
            self.niter = 0
            self.stepNorm = 0.0
            self.step = None
            self.hprod = kwargs.get('matvec', None)
            self.H = kwargs.get('H', None)
            self.m = None

        def Solve(self):
            """
            Solve the trust-region subproblem using the generalized Lanczos
            method.
            """
            self.gltrSolver.implicit_solve(self.qp)
            self.niter = self.gltrSolver.niter
            self.stepNorm = self.gltrSolver.snorm
            self.step = self.gltrSolver.step
            self.m = self.gltrSolver.m
            return
except:
    pass

