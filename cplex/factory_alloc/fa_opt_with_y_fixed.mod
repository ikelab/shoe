int m = ...;        // number of factories
int L[1..m] = ...;  // number of lines in factory
int n = ...;        // number of products

tuple KI_tuple {
	int k;
	int i;
};


{KI_tuple} KI = {<k, i> | k in 1..m, i in 1..L[k]};

float W[KI][1..n] = ...;    // labor cost per shoes
float D[1..n] = ...;        // demand of product
float C[KI] = ...;          // capacity of line i of factory k
float E[KI][1..n] = ...;    // efficiency
float R[KI] = ...;          // yield rate
float H[1..n] = ...;        // difficulty (hardness)
float T[1..m] = ...;        // transportation cost 
float S[1..m][1..n] = ...;  // setup cost
float O[KI] = ...;          // overtime cost

float y[1..m][1..n] = ...;    // assignment


dvar float+ x[KI][1..n];    // production quantity
dvar float+ z[KI];          // over-production quantity
dvar float+ v[KI];          // over-over-production quantity (checking violation of over-production quantity)


minimize sum(<k, i> in KI) sum(j in 1..n) W[<k, i>][j] * H[j] / (R[<k, i>] * E[<k, i>][j]) * x[<k, i>][j] +
         sum(<k, i> in KI) sum(j in 1..n) T[k] * x[<k,i>][j] +
         sum(k in 1..m) sum(j in 1..n) S[k][j] * y[k][j] +
         sum(<k, i> in KI) O[<k,i>] * z[<k,i>] +
         sum(<k, i> in KI) 300000 * O[<k,i>] * v[<k,i>];


subject to {
   
	forall(j in 1..n) {
    	Demand:
    	sum(<k, i> in KI) x[<k,i>][j] >= D[j];
	}
     
	forall(<k,i> in KI) {
		Capacity:
		sum(j in 1..n) H[j] / (R[<k,i>] * E[<k,i>][j]) * x[<k,i>][j] <= C[<k,i>] + z[<k,i>];
		
		Capacity_overtime:
		z[<k, i>] <= 0.5 * C[<k, i>];
	}
   	
	forall(<k,i> in KI, j in 1..n) {
	    Production_feasibility_by_assignment:
		x[<k, i>][j] <= 10000000 * y[k][j];
	}
}
