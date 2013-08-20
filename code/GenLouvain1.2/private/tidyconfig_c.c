/* [S,y]=tidyconfig(S,y)
   tidy up S i.e.  S = [2 4 2 6] -> S = [1 2 1 3]*/
   
   
#include "mex.h"
#include "matrix.h"
#include "math.h"


void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]){
	/*variables*/
	double *S, *y, *T, *yy;
	int i, j, n, N, groupnumber;
	
	/*get input*/
	S=mxGetPr(prhs[0]);
	N=mxGetM(prhs[0]);
	
	y=mxGetPr(prhs[1]);
	n=mxGetM(prhs[1]);
	
	/*create output*/
	plhs[1]=mxCreateDoubleMatrix(n,1,0);
	yy=mxGetPr(plhs[1]);
	
	plhs[0]=mxDuplicateArray(prhs[0]);
	T=mxGetPr(plhs[0]);
	
	/*run tidyconfig*/
	groupnumber=1;
	
	for(i=0;i<n;i++){
		if(yy[i]==0){
			for(j=0;j<n;j++){
				if(y[j]==y[i]){
					yy[j]=groupnumber;
				}
			}
			groupnumber++;
		}
	}
	
	/*change S*/
	for(i=0;i<n;i++){
		for(j=0;j<N;j++){
			if(S[j]==i+1){
				T[j]=yy[i];
			}
		}
	}
	
}
