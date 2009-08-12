"""
Minres demo.
"""

from nlpy.krylov import Minres
from nlpy.precon import DiagonalPreconditioner
from pysparse import spmatrix
import numpy

def diagA(n):
    "Creates A = diag(1,2,...,n) and b = [1, 1, ..., 1]"
    A = spmatrix.ll_mat_sym(n, n)
    for i in range(n): A[i,i] = i+1
    b = numpy.ones(n)
    return (A,b)

def test1(A, b, s=0.0, M=None):
    "Perform Minres solve with specified arguments"
    K = Minres(A, shift=s, precon=M)
    K.solve(b)
    print 'Solution: ', K.x
    return

if __name__ == '__main__':
    n = 10
    (A,b) = diagA(n)
    
    #test1(A, b)               # Solves Ax = b
    #test1(A, b, s=2.0)        # Solves (A-2I)x = b

    goodM = DiagonalPreconditioner( 1+numpy.arange(n) )
    for i in range(1,4): goodM[i] = 1.0

    test1(A, b, M=goodM.precon)      # Solves Ax = b with good preconditioner M
    #test1(A, b, s=2.0, M=goodM.precon)  # Solves (A-2I)x = b with good precon M
