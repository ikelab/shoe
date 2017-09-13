from itertools import permutations
from math import inf

from custom.prob import makespan
from custom.sa import evaluate as ls_evaluate


def enum_all_schedules(n, m, L, pi, F, alpha, beta, T, Z, R, gamma, C):
    ms0, count = inf, 0
    
    for k in range(L**n):
        # Get an assignment
        A = [[] for _ in range(L)]
        for j in range(n):
            A[k % 3].append(j)
            k //= 3
        
        if any(len(Ai) == 0 for Ai in A):
            continue
        
        # Iterate all sequences
        PI = [permutations(Ai) for Ai in A]
        X = [next(PIi) for PIi in PI]
        while True:
            count += 1
            
            # Check makespan.
            ms = makespan(n, m, L, pi, F, alpha, beta, T, Z, R, gamma, C, X, False)
            if ms <= ms0:
                print(ms, X)
                ms0 = ms
            
            try:
                X[0] = next(PI[0])
            except StopIteration:
                for ci in range(L - 1):
                    PI[ci] = permutations(A[ci])
                    X[ci] = next(PI[ci])
                    
                    try:
                        X[ci + 1] = next(PI[ci + 1])
                        break
                    except StopIteration:
                        pass
                else:
                    break
    
    print(f'Total: {count}')
    
    return ms0


def enum_all_list_schedules(n, m, L, pi, F, alpha, beta, T, Z, R, gamma, C):
    ms0, count = inf, 0
    
    for LX in permutations(range(n)):
        count += 1
        
        ms, X = ls_evaluate(n, m, L, pi, F, alpha, beta, T, Z, R, gamma, C, LX)
        if ms <= ms0:
            print(ms, X)
            ms0 = ms
    
    print(f'Total: {count}')
    
    return ms0


if __name__ == '__main__':
    from custom import prob
     
    #pb = prob.read_problem_from_xlsx('data/ex1.xlsx')
    pb = prob.read_problem_from_xlsx('data/rand.xlsx')
    
    print(enum_all_schedules(*pb))
    #print(enum_all_list_schedules(*pb))
