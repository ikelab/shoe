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
dvar boolean w[1..n][1..n][1..n];
dvar float+ s_r[1..m][1..n];
dvar float+ s_c[1..m][1..n];
dvar float+ ms;

float M = 100;

minimize ms;

subject to {

	forall(l in 1..L, j in 1..n) 
	    ms >= x[m][j] + pi1[l][m][j];
	
	forall(j in 1..n)
	    sum(l in 1..L) z[l][j] == 1;
	    
	forall(l in 1..L, i in 1..m, j in 1..n, k in 1..n: j < k) {
	     x[i][j] + pi1[l][i][j] + s_r[i][k] + s_c[i][k] <= x[i][k] +  M * (3 - y[j][k] - z[l][j]- z[l][k]);
	     x[i][k] + pi1[l][i][k] + s_r[i][j] + s_c[i][j] <= x[i][j] +  M * (2 + y[j][k] - z[l][j]- z[l][k]);
    }
    
    forall(l in 1..L, j in 1..n, i in 1..(m-1))
        x[i][j] + pi1[l][i][j] <= x[i + 1][j] + M * (1 - z[l][j]); 	
    
    forall(l in 1..L, i in 1..m, j in 1..n, q in 1..n, k in 1..n: j != k && k != q && q != j) {
        w[j][q][k] <= (j < q ? y[j][q] : 1 - y[q][j]);
        w[j][q][k] <= (q < k ? y[q][k] : 1 - y[k][q]);
        w[j][q][k] <= z[l][j];
        w[j][q][k] <= z[l][q];
        w[j][q][k] <= z[l][k];
        
        // Above means below.
        //(j < q ? y[j][q] : 1 - y[q][j]) + (q < k ? y[q][k] : (1 - y[k][q])) + z[l][j] + z[l][q] + z[l][k] <= 4 => w[j][q][k] == 0;
    }
    
	forall(l in 1..L, i in 1..m, j in 1..n, k in 1..n: r[i][j] != -1 && r[i][k] != -1 && r[i][j] != r[i][k]) {		
		s_r[i][k] >= alpha * ((j < k ? y[j][k] : 1 - y[k][j]) + z[l][j] + z[l][k] - 2
							 - sum(q in 1..n : q != j && q != k && r[i][q] != -1) w[j][q][k]);
	}
	
	forall(l in 1..L, i in 1..m, j in 1..n, k in 1..n: c[i][j] != -1 && c[i][k] != -1 && c[i][j] != c[i][k]) {		
		s_c[i][k] >= beta * ((j < k ? y[j][k] : 1 - y[k][j]) + z[l][j] + z[l][k] - 2
							 - sum(q in 1..n : q != j && q != k && c[i][q] != -1) w[j][q][k]);
	}
	
	// For removing warnings for unused
	forall(j in 1..n, k in 1..n: j >= k) {
		y[j][k] == 0;
	}
	forall(j in 1..n, q in 1..n, k in 1..n: j == k || k == q || q == j) {
		w[j][q][k] == 0;
	}
}
