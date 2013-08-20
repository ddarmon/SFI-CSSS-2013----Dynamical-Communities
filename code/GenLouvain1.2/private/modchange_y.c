#include "mex.h"
#include "matrix.h"
#include "math.h"


/*fixed problem with all-zero sparse matrices*/

/*dH = modchange_y(Mi,y,u)*/
void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]){
	
	/*variables*/
	int i,j, n, nnz;
	mwIndex *Mr,*Mc;
	double *Mv, *u, *dH, *y;

/*test for all-zero Mi*/
    
   
        
        /*sparse case*/
        if(mxIsSparse(prhs[0])){
            /*get modularity matrix*/
            Mr=mxGetIr(prhs[0]);
            Mc=mxGetJc(prhs[0]);
            Mv=mxGetPr(prhs[0]);
            
            /*check for all-zero matrix*/
            if(Mc[1]==0){
                n=mxGetM(prhs[2]);
                plhs[0]=mxCreateDoubleMatrix(1,n,0);
                return;
            } 	
          
            
            /*number of non-zero elements*/
            nnz=Mc[1];
            
            y=mxGetPr(prhs[1]);	/*get community assignments*/
            
            u=mxGetPr(prhs[2]);	/*get potential reassignments*/
            
            n=mxGetM(prhs[2]);	/*get length of u*/
            
            
            
            
            plhs[0]=mxCreateDoubleMatrix(1,n,0);	/*create output matrix*/
            dH=mxGetPr(plhs[0]);
            
           
            
            /*calculate change in modularity*/
            for(i=0;i<n;i++){
                for(j=0;j<nnz;j++){	/*loop over non-zero elements of Mi*/
                    if(y[Mr[j]]==(u[i])){
                        dH[i]+=Mv[j];
                    }
                }
            }
        }
        /*full case*/
        else{
            Mv=mxGetPr(prhs[0]);
            nnz=mxGetM(prhs[0]);
            
            y=mxGetPr(prhs[1]);	/*get community assignments*/
            
            u=mxGetPr(prhs[2]);	/*get potential reassignments*/
            
            n=mxGetM(prhs[2]);	/*get length of u*/
            
            
            
            
            plhs[0]=mxCreateDoubleMatrix(1,n,0);	/*create output matrix*/
            dH=mxGetPr(plhs[0]);
            
            
            /*calculate change in modularity*/
            for(i=0;i<n;i++){
                for(j=0;j<nnz;j++){	/*loop over elements of Mi*/
                    if(y[j]==(u[i])){
                        dH[i]+=Mv[j];
                    }
                }
            }
        }
         		
	
}	
				 
