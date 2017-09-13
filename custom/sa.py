from random import random, sample, seed
from math import exp, inf
from itertools import permutations

import numpy as np

from custom import prob
from custom.prob import processing_and_setup_time


LEATHER = prob.LEATHER


def solve(n, m, L, pi, F, alpha, beta, T, Z, R, gamma, C, t0=1000, t1=0.00001, td=0.999):
    """
    LX, LX0: current and best solution (list schedule)
    ms, ms0: makespan of current and best solution
    """
    LX0 = LX = sample(range(n), n)  # initial solution
    ms0, _ = ms, _ = evaluate(n, m, L, pi, F, alpha, beta, T, Z, R, gamma, C, LX)
    print(f'0: {ms}')
    
    t, num_iter = t0, 0
    while t > t1:
        num_iter += 1
        
        # Tweak (move to a neighborhood).
        k, l = sample(range(n), 2)
        LX[k], LX[l] = LX[l], LX[k]
        
        ms1, _ = evaluate(n, m, L, pi, F, alpha, beta, T, Z, R, gamma, C, LX)
        
        # Determine acceptance of candidate solution.
        if ms1 <= ms or random() < exp((ms - ms1) / t):
            ms = ms1
            if ms < ms0:
                LX0, ms0 = LX[:], ms
                print(f'{num_iter}: {ms}')
        
        else:
            # Move back to the previous solution.
            LX[k], LX[l] = LX[l], LX[k]
        
        # Cooling
        t *= td
    
    print(f'Total number of iters: {num_iter}')
    
    return LX0


def evaluate(n, m, L, pi, F, alpha, beta, T, Z, R, gamma, C, LX):
    """
    Evaluate list schedule X
    
    MS[l]: last makespan of line l
    
    lY[l][i]: last completion time of machine i of line l
    lR[l][i]: last material used by machine i of line l
    lC[l][i]: last color used by machine i of line l
    """
    MS = [0] * L
    lY = [[0] * (m + 1) for _ in range(L)]
    lR = [[None] * m for _ in range(L)]
    lC = [[None] * m for _ in range(L)]
    
    X = [[] for _ in range(L)]
    
    # Iterate each line (flow shop) and get its makespan
    for j in LX:
        l = np.argmin(MS)  # line where j is handled
        #print(f'Makespan is {MS}, so order {j} is assigned to line {l}')
        X[l].append(j)
        
        Tj, Rj, Cj = T[j], R[j], C[j]
        piTj, FlTj, Zj = pi[Tj], F[l][Tj], Z[j]
        
        for i in range(m):
            # Check end of step.
            if piTj[i] == -1:
                break
            
            # Get processing and setup time.
            p, s = processing_and_setup_time(i, piTj, FlTj, alpha, beta, Zj,
                                             Rj, gamma, Cj, lR[l], lC[l])
            
            lY[l][i] = max(lY[l][i - 1], lY[l][i] + s) + p
        
        MS[l] = max(lY[l])
    
    return max(MS), X


def test_makespan():
    pb = prob.ex1()
    LX = [0, 3, 5, 2, 6, 4, 1]
    ms, X = evaluate(*pb, LX)
    assert ms == prob.makespan(*pb, X)
    print(ms, X)


def test():
    #seed(0)
    
    #pb = prob.ex1()
    pb = prob.read_problem_from_xlsx('data/rand.xlsx')
    #pb = prob.read_problem_from_xlsx('data/big4.xlsx')
    
    LX = solve(*pb)
    ms, X = evaluate(*pb, LX)
    
    print(ms)
    print(LX)
    print(X)


if __name__ == '__main__':
    #test_makespan()
    test()
