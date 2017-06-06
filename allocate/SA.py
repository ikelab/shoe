from random import random, sample, randrange
from math import exp

import numpy as np

import mpike

import prob


def solve(pb, t0=1000, t1=0.0001, pi=0.99):
    """
    t0: initial temperature
    pi: temperature cooling parameter
    
    y, val, x, z: current solution and its quality
    y0, val0, x0, z0: best solution and quality, so far
    y1, val1, x1, z1: next candidate solution and its quality
    t: current temperature
    t1: termination temperature
    """
    
    m, L, n = pb[:3]
    
    # Initial seed (TODO Better one?)
    y0 = y = [randrange(m) for _ in range(n)]
    
    TC0, _ = TC, _ = solve_relaxed_LP(pb, normalize_y(y, m, n))
    
    t, num_iter = t0, 0
    while t > t1:
        num_iter += 1
        
        # Tweak.
        y1 = y[:]
        j = randrange(n)
        while True:
            k = randrange(m)
            if k != y1[j]:
                break
        y1[j] = k
        ''' TODO
        for _ in range(m):
            k = sample(range(n),1)
            y1[k[0]] = randrange(m)
        '''
        
        TC1, _ = solve_relaxed_LP(pb, normalize_y(y1, m, n))
        assert TC1 is not None
        
        """
        if TC1 == None:
            x1 = [[[x1[(k, i, j)].sv for j in range(n)] for i in range(L[k])] for k in range(m)]
            z1 = [[z1[(k,i)].sv for i in range(L[k])] for k in range(m)]
            A  = [[A[(k,i)].sv for i in range(L[k])] for k in range(m)]
            print(y1)
            print(x1)
            print(z1)
            print(A)
        """
        
        # 
        if TC1 <= TC or random() < exp((TC - TC1) / t):
            y, TC = y1, TC1
            if TC < TC0:
                y0, TC0 = y, TC
                print(num_iter, TC0)
        
        # Cooling
        t *= pi
    
    print(num_iter)
    
    TC0, (x0, z0, v0)  = solve_relaxed_LP(pb, normalize_y(y0, m, n))
    x0, z0, v0 = extract_values(m, L, n, x0, z0, v0)
    
    return TC0, (x0, y0, z0, v0)


def normalize_y(y1, m, n):
    """
    Get y from y1; e.g. [0,2,1,0] --> [[1,0,0,1], [0,0,1,0], [0,1,0,0]]
    """
    y = [[0] * n for _ in range(m)]
    for j, k in enumerate(y1):
        y[k][j] = 1
    return y


def denormalize_y(y, m, n):
    """
    Get y1 from y; e.g. [[1,0,0,1], [0,0,1,0], [0,1,0,0]] --> [0,2,1,0]
    """
    y1 = []
    for j in range(n):
        for k in range(m):
            if y[k][j] == 1:
                y1.append(k)
                break
        else:
            assert False
    return y1


def extract_values(m, L, n, x0, z0, v0):
    x0 = [[[x0[k][i][j].sv for j in range(n)] for i in range(L[k])] for k in range(m)]
    z0 = [[z0[k][i].sv for i in range(L[k])] for k in range(m)]
    v0 = [[v0[k][i].sv for i in range(L[k])] for k in range(m)]
    return x0, z0, v0


def solve_relaxed_LP(pb, y):
    """
    k : factory index, k = 0...m-1 
    <k,i> : line index in factory k
    j : number of order, j = 0...n-1
    L[k] : number of line in factory k
    D[j] : Demand of order j
    C[<k,i>] : capacity of line i in factory k
    E[<k,i>][j] : probability of line i in factory k about order j
    R[<k,i>] : ???? of line i in factory k
    H[j] : hardness of order j
    T[k] : shipping expenses on factory k
    W[<k,i>][j] : labor cost per unit 
    s[k][j] : transport cost of mold
    
    x[<k,i>][j] : production amount
    y[k][j] : decision variable
    """
    
    m, L, n, D, C, E, R, H, T, W, S, O = pb
    
    M = mpike.lpm()
    
    # Decision variables
    x = [[[M.var(f'x{k},{i},{j}') for j in range(n)] for i in range(L[k])] for k in range(m)]
    z = [[M.var(f'x{k},{i}') for i in range(L[k])]for k in range(m)]
    v = [[M.var(f'x{k},{i}') for i in range(L[k])] for k in range(m)]
    
    # Objective function
    M.min(sum(W[k][i][j] * H[j] / (R[k][i] * E[k][i][j]) * x[k][i][j] for k in range(m) for i in range(L[k]) for j in range(n)) +
          sum(T[k] * x[k][i][j]                                       for k in range(m) for i in range(L[k]) for j in range(n)) +
          sum(S[k][j] * y[k][j]                                       for k in range(m) for j in range(n)) +
          sum(O[k][i] * z[k][i]                                       for k in range(m) for i in range(L[k])) +
          sum(v[k][i] * O[k][i] * 300000                              for k in range(m) for i in range(L[k])))
    
    for j in range(n):
        # Demand:    
        M.st(sum(x[k][i][j] for k in range(m) for i in range(L[k])) >= D[j])
    
    for k in range(m):
        for i in range(L[k]):
            # Capacity:
            M.st(sum(H[j] / (R[k][i] * E[k][i][j]) * x[k][i][j] for j in range(n)) <= C[k][i] + z[k][i] + v[k][i])
            
            # Capacity_overtime:
            M.st(z[k][i] <= 0.5 * C[k][i])
    
    for k in range(m):
        for i in range(L[k]):
            for j in range(n):
                # Production_feasibility_by_assignment:
                M.st(x[k][i][j] <= 10000000 * y[k][j])
    
    # Solve.  
    z0 = M.solve()
    #z0 = M.solve('scipy')
    
    return z0, (x, z, v)


def display_sol(m, n, x, y, z, v):
    print('---------- x')
    for xk in x:
        print(f'{np.around(xk, 1)}')
    print()
    print(f'---------- y\n{np.array(normalize_y(y, m, n))}\n')
    print('---------- z')
    for zk in z:
        print(f'{np.around(zk, 1)}')
    print()
    print('---------- v')
    for vk in v:
        print(f'{np.around(vk, 1)}')
    print()


def test_lp():
    #pb = prob.test_data1(); y = [[1, 0, 0, 1, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 0, 1, 1, 1, 1, 0]]
    
    pb = prob.read_problem_from_xlsx('data/base.xlsx'); #y1 = [0, 1, 2, 0, 1, 1, 2, 2, 0, 1, 1, 0, 2, 1, 1]
    y = [[0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]]
    
    #TC0, (x, z, v) = solve_relaxed_LP(pb, normalize_y(y1, pb[0], pb[2]))
    TC0, (x, z, v) = solve_relaxed_LP(pb, y)
    x, z, v = extract_values(*pb[:3], x, z, v)
    
    print(TC0, '\n')
    #display_sol(pb[0], pb[2], x, y1, z, v)
    display_sol(pb[0], pb[2], x, denormalize_y(y, pb[0], pb[2]), z, v)


def test():
    #pb = prob.test_data1()
    pb = prob.read_problem_from_xlsx('data/base.xlsx')
    
    TC, (x, y, z, v) = solve(pb)
    
    print(f'TC = {TC}\n')
    display_sol(pb[0], pb[2], x, y, z, v)


if __name__ == "__main__":
    np.set_printoptions(linewidth=200)
    #test_lp()
    test()
