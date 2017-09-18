int n = ...; // number of orders
int m = ...; // number of machines
int L = ...; // number of lines
int h = ...;

float pi[1..h][1..m] = ...;

float alpha = ...;
float beta = ...;
float gamma = ...;

int T[1..n] = ...;  // type of order

execute {
  for (var j = 1; j <= n; j++) {
      T[j] = T[j] + 1;
  }
}

int Z[1..n] = ...;

float c[1..m][1..n] = ...;
float r[1..m][1..n] = ...;
float F[1..L][1..h] = ...;

float pi1[l in 1..L][i in 1..m][j in 1..n] = pi[T[j]][i]== -1 ? 0 : pi[T[j]][i] + F[l][T[j]] + ((r[i][j] == 2 ? gamma : 0)) + Z[j];

dvar float+ x[1..m][1..n];
dvar boolean y[1..n][1..n];
dvar boolean z[1..L][1..n];
dvar boolean w[1..L][1..n][1..n][1..n];
dvar float+ s_r[1..m][1..n];
dvar float+ s_c[1..m][1..n];
dvar float+ ms;

float M = ceil(n / L + m) * (max(i in 1..m, j in 1..n) pi[i][j] + max(j in 1..n) Z[j] + alpha + beta + gamma) * 1.2;


constraint C1[1..L][1..n];
constraint C2[1..n];
constraint C3_1[1..L][1..m][1..n][1..n];
constraint C3_2[1..L][1..m][1..n][1..n];
constraint C4[1..L][1..(m-1)][1..n];
constraint C5_1[1..L][1..n][1..n][1..n];
constraint C5_2[1..L][1..n][1..n][1..n];
constraint C5_3[1..L][1..n][1..n][1..n];
constraint C5_4[1..L][1..n][1..n][1..n];
constraint C5_5[1..L][1..n][1..n][1..n];
constraint C6[1..L][1..m][1..n][1..n];
constraint C7[1..L][1..m][1..n][1..n];


//minimize ms;
minimize ms + 0.0001 * sum(i in 1..m, j in 1..n) x[i][j];

subject to {

	forall(l in 1..L, j in 1..n)
	    C1[l][j]:
	    ms >= x[m][j] + pi1[l][m][j] * z[l][j];
	
	forall(j in 1..n)
	    C2[j]:
	    sum(l in 1..L) z[l][j] == 1;
	    
	forall(l in 1..L, i in 1..m, j in 1..n, k in 1..n: j < k) {
	    C3_1[l][i][j][k]:
	    x[i][j] + pi1[l][i][j] + s_r[i][k] + s_c[i][k] <= x[i][k] +  M * (3 - y[j][k] - z[l][j]- z[l][k]);
	    C3_2[l][i][j][k]:
	    x[i][k] + pi1[l][i][k] + s_r[i][j] + s_c[i][j] <= x[i][j] +  M * (2 + y[j][k] - z[l][j]- z[l][k]);
    }
    
    forall(l in 1..L, i in 1..(m-1), j in 1..n)
      	C4[l][i][j]:
        x[i][j] + pi1[l][i][j] <= x[i + 1][j] + M * (1 - z[l][j]); 	
    
    forall(l in 1..L, j in 1..n, q in 1..n, k in 1..n: j != k && k != q && q != j) {
    	C5_1[l][j][q][k]:
    	w[l][j][q][k] <= (j < q ? y[j][q] : 1 - y[q][j]);
    	C5_2[l][j][q][k]:
        w[l][j][q][k] <= (q < k ? y[q][k] : 1 - y[k][q]);
        C5_3[l][j][q][k]:
        w[l][j][q][k] <= z[l][j];
        C5_4[l][j][q][k]:
        w[l][j][q][k] <= z[l][q];
        C5_5[l][j][q][k]:
        w[l][j][q][k] <= z[l][k];
    }
    
	forall(l in 1..L, i in 1..m, j in 1..n, k in 1..n: r[i][j] != -1 && r[i][k] != -1 && r[i][j] != r[i][k]) {
		C6[l][i][j][k]:	
		s_r[i][k] >= alpha * ((j < k ? y[j][k] : 1 - y[k][j]) + z[l][j] + z[l][k] - 2
							  - sum(q in 1..n : q != j && q != k && r[i][q] != -1) w[l][j][q][k]);
	}
	
	forall(l in 1..L, i in 1..m, j in 1..n, k in 1..n: c[i][j] != -1 && c[i][k] != -1 && c[i][j] != c[i][k]) {
		C7[l][i][j][k]:	
		s_c[i][k] >= beta * ((j < k ? y[j][k] : 1 - y[k][j]) + z[l][j] + z[l][k] - 2
							 - sum(q in 1..n : q != j && q != k && c[i][q] != -1) w[l][j][q][k]);
	}
	
	// For removing warnings for unused
	forall(j in 1..n, k in 1..n: j >= k) {
		y[j][k] == 0;
	}
	forall(l in 1..L, j in 1..n, q in 1..n, k in 1..n: j == k || k == q || q == j) {
		w[l][j][q][k] == 0;
	}
}
