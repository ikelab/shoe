"""
n: number of orders
m: number of machines
L: number of lines

pi[t][i]: standard processing time of type t at machine i
alpha: setup time required to change material
beta: setup time required to change color
F[l][t]: additional processing time in line l for handling type t

T[j]: type of order j
Z[j]: additional processing time by size, of order j
R[j][i]: material at machine i, of order j
  -1 means that material is not used
gamma: additional processing time by leather (R[j][i] == 2)
  -1 means that color is not used
C[j][i]: color at machine i, of order j
"""

from collections.abc import Sequence

import openpyxl


LEATHER = 2


def makespan(n, m, L, pi, F, alpha, beta, T, Z, R, gamma, C, X, verbose=True):
    """
    lY[i]: last completion time of machine i
    lR[i]: last material used by machine i
    lC[i]: last color used by machine i
    """
    
    # Iterate each line (flow shop) and get its makespan
    ms = 0
    for l, Xl in enumerate(X):
        if verbose:
            print(f'[{l}]')
        
        # None means setup was not at all.
        lY, lR, lC = [0] * (m + 1), [None] * m, [None] * m
        
        Fl = F[l]
        
        for j in Xl:
            if verbose:
                print(f'{j}: ', end='')
            
            Tj, Rj, Cj = T[j], R[j], C[j]
            piTj, FlTj, Zj = pi[Tj], Fl[Tj], Z[j]
            
            for i in range(m):
                # Check end of step.
                if piTj[i] == -1:
                    break
                
                # Get processing and setup time.
                p, s = processing_and_setup_time(i, piTj, FlTj, alpha, beta, Zj,
                                                 Rj, gamma, Cj, lR, lC)
                
                lY[i] = max(lY[i - 1], lY[i] + s) + p
            
                if verbose:
                    print(f'm{i}({lY[i] - s - p}-{lY[i] - p}-{lY[i]}) ', end='')
            
            if verbose:
                print()
        
        ms = max(ms, max(lY))
    
    return ms


def processing_and_setup_time(i, piTj, FlTj, alpha, beta, Zj, Rj, gamma, Cj, lR, lC):
    # Processing time
    p = piTj[i] + FlTj + Zj
    if Rj[i] == LEATHER:
        p += gamma
    
    s = 0
    # Setup time by material
    if lR[i] is not None and Rj[i] != -1 and lR[i] != Rj[i]:
        s += alpha
    if Rj[i] != -1:
        lR[i] = Rj[i]
    # Setup time by color
    if lC[i] is not None and Cj[i] != -1 and lC[i] != Cj[i]:
        s += beta
    if Cj[i] != -1:
        lC[i] = Cj[i]
    
    return p, s


def xlread_by_name(wb, name):
    C = [wb[title][coord] for title, coord in wb.defined_names[name].destinations][0]
    
    # Handle one cell.
    if not isinstance(C, Sequence):
        return C.value
    
    # Handle 1 column.
    if len(C) == 1:
        V = []
        r0, c0 = C[0][0].row, C[0][0].col_idx
        for j, Cj in enumerate(C[0]):
            assert Cj.row == r0 and Cj.col_idx == c0 + j
            V.append(Cj.value)
        return V
    
    # Handle 1 row.
    if all(len(Ci) == 1 for Ci in C):
        V = []
        r0, c0 = C[0][0].row, C[0][0].col_idx
        for i, Ci in enumerate(C):
            assert Ci[0].row == r0 + i and Ci[0].col_idx == c0
            V.append(Ci[0].value)
        return V
    
    # Handle n by m matrix (n, m > 1)
    m = len(C[0])
    if all(len(Ci) == m for Ci in C):
        V = []
        r0, c0 = C[0][0].row, C[0][0].col_idx
        for i, Ci in enumerate(C):
            V.append([])
            for j, Cij in enumerate(Ci):
                assert Cij.row == r0 + i and Cij.col_idx == c0 + j
                V[-1].append(Cij.value)
        return V
    
    return C


def read_problem_from_xlsx(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    
    pi    = xlread_by_name(wb, 'pi')
    F     = xlread_by_name(wb, 'F')
    alpha = xlread_by_name(wb, 'alpha')
    beta  = xlread_by_name(wb, 'beta')  
    T     = xlread_by_name(wb, 'T')
    Z     = xlread_by_name(wb, 'Z')
    R     = xlread_by_name(wb, '_R')
    gamma = xlread_by_name(wb, 'gamma')  
    C     = xlread_by_name(wb, '_C')
    
    n, m, L = len(T), len(pi[0]), len(F)
    
    return n, m, L, pi, F, alpha, beta, T, Z, R, gamma, C


def ex1():
    # Process-related
    pi = [
        [3, 6, 4, 1, 2, 4, 5, 6, 4,  5,  6,  5,  2],
        [5, 4, 5, 3, 6, 6, 5, 4, 3,  2, -1, -1, -1],
        [4, 5, 6, 5, 6, 4, 5, 6, 4, -1, -1, -1, -1],
        [2, 4, 5, 3, 4, 3, 3, 4, 4, -1, -1, -1, -1],
        [4, 3, 3, 2, 4, 3, 5, 2, 3,  2,  3, -1, -1]
    ]
    F = [
        [0, 0, 1, 1, 1],
        [1, 1, 0, 0, 1],
        [1, 1, 1, 0, 0]
    ]
    alpha, beta = 2, 3
    
    # Order-related
    T = [0, 1, 0, 2, 3, 2, 4]
    Z = [0, 1, 0, 1, 0, 0, 1]
    R = [
        [0, 0, 1, 0, 0, 0, 0, 0, 1,  0,  0,  0,  0],
        [0, 0, 0, 1, 0, 0, 0, 2, 2,  0, -1, -1, -1],
        [0, 0, 0, 0, 0, 1, 1, 1, 0,  0,  0,  0,  1],
        [2, 2, 2, 2, 2, 2, 2, 1, 0, -1, -1, -1, -1],
        [0, 1, 1, 0, 1, 0, 2, 0, 1, -1, -1, -1, -1],
        [1, 2, 1, 1, 0, 1, 1, 1, 1, -1, -1, -1, -1],
        [1, 1, 1, 0, 0, 2, 0, 0, 0,  0,  2, -1, -1]
    ]
    gamma = 1
    C = [
        [3, 0, 1, 1, 5, 5, 3, 0, 0,  9,  3,  2,  1],
        [4, 2, 7, 5, 4, 2, 4, 4, 8,  6, -1, -1, -1],
        [2, 9, 7, 5, 4, 6, 7, 5, 6,  6,  3,  2,  1],
        [3, 5, 8, 2, 8, 1, 2, 6, 6, -1, -1, -1, -1],
        [5, 6, 5, 7, 6, 8, 3, 6, 3, -1, -1, -1, -1],
        [4, 1, 2, 3, 0, 3, 4, 7, 3, -1, -1, -1, -1],
        [5, 6, 4, 9, 1, 3, 8, 4, 3,  3,  5, -1, -1]
    ]
    
    n, m, L = len(T), len(pi[0]), len(F)
    
    return n, m, L, pi, F, alpha, beta, T, Z, R, gamma, C


def test_ex1():
    pb = ex1()
    X = [[0, 2, 1], [3, 4], [5, 6]]
    print(makespan(*pb, X))


def test_ex1_xls():
    pb = read_problem_from_xlsx('data/ex1.xlsx')
    X = [[0, 2, 1], [3, 4], [5, 6]]
    print(makespan(*pb, X))


def test_big4():
    pb = read_problem_from_xlsx('data/big4.xlsx')
    X = [
        [362, 321, 259, 62, 33, 27, 415, 106, 269, 426, 371, 128, 146, 351, 158, 76, 117, 361, 80, 264, 200, 388, 375, 424, 143, 166, 112, 132, 281, 421, 440, 67, 360, 116, 19, 271, 233, 410, 352, 333, 109, 144, 318, 69, 226, 10, 157, 68, 18, 260, 252, 436, 336, 449, 52, 193, 119, 448, 347, 422, 349, 278, 330, 443, 301, 6, 64, 247, 234, 327, 254, 174, 55, 251, 335, 188, 391, 194, 232, 334, 123, 414, 93, 237, 204, 368, 176, 384, 56, 104, 43, 295, 355, 148, 374, 340, 405, 114, 312, 51, 253, 370, 53, 127, 366, 373, 186, 133, 205, 150, 419, 31, 28, 407, 44, 342, 282, 418, 378, 37, 339, 218, 300, 15, 215, 113, 197, 220, 357, 323, 35, 403, 249, 383, 291, 231, 164, 284, 228, 294, 124, 91, 32, 367, 38, 324],
        [135, 298, 272, 287, 395, 433, 103, 285, 139, 236, 322, 326, 83, 192, 92, 212, 88, 57, 100, 239, 288, 161, 160, 170, 86, 225, 304, 171, 423, 317, 60, 54, 248, 411, 397, 437, 22, 289, 36, 34, 280, 209, 392, 122, 382, 343, 105, 61, 245, 111, 201, 216, 377, 241, 400, 130, 444, 311, 120, 242, 108, 13, 21, 344, 138, 257, 320, 20, 126, 26, 48, 442, 416, 425, 217, 17, 137, 332, 417, 431, 89, 189, 427, 187, 134, 65, 195, 3, 348, 42, 162, 434, 4, 404, 445, 115, 211, 409, 299, 315, 307, 159, 99, 206, 199, 380, 372, 151, 261, 319, 435, 0, 213, 47, 277, 387, 359, 316, 439, 136, 412, 147, 438, 11, 30, 125, 353, 356, 5, 262, 408, 183, 268, 155, 79, 376, 256, 258, 420, 227, 184, 364, 396, 314, 9, 337, 428, 191, 102, 90, 306, 142, 345, 156, 238, 432, 190, 293, 309, 70, 175, 118, 224, 221, 331],
        [14, 286, 308, 85, 180, 275, 87, 398, 273, 131, 202, 95, 210, 346, 229, 74, 177, 63, 296, 244, 50, 290, 389, 178, 297, 107, 98, 325, 292, 2, 196, 73, 243, 182, 39, 94, 279, 265, 140, 59, 167, 303, 350, 413, 222, 240, 24, 386, 274, 402, 29, 394, 401, 406, 141, 354, 219, 230, 173, 328, 7, 341, 1, 358, 181, 78, 169, 267, 235, 302, 41, 363, 145, 168, 214, 84, 263, 207, 399, 179, 185, 71, 8, 77, 283, 441, 40, 12, 23, 276, 266, 149, 172, 121, 305, 270, 110, 46, 430, 447, 250, 208, 429, 385, 165, 49, 66, 163, 329, 223, 381, 72, 154, 203, 390, 82, 310, 58, 81, 255, 338, 129, 96, 97, 101, 313, 379, 365, 446, 45, 369, 198, 393, 16, 152, 153, 25, 75, 246]
    ]
    print(makespan(*pb, X))


if __name__ == '__main__':
    #test_ex1()
    test_ex1_xls()
    #test_big4()
