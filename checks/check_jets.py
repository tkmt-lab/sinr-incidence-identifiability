"""Independent ODE Taylor jet + finite-field Wronskian diagnostic, no producer imports."""
from pathlib import Path
from math import comb
import json,time,resource
P=Path(__file__).resolve().parents[1]
PRIME=1000003

def diagnostic(n):
 t=time.perf_counter();data=json.loads((P/'results'/f'polynomial-n{n}.json').read_text())
 obs=[tuple(m) for m in data['observable_monomials']];M=len(obs);K=M-1;L=K+n+2;p=PRIME
 b,z,s=2,3,11
 S=[s]+[0]*L;Is=[[i+2]+[0]*L for i in range(n)];Y=[0]*L
 inv=[0]+[pow(i,p-2,p) for i in range(1,L+2)]
 for r in range(L):
  Y[r]=b*sum(S[k]*sum(I[r-k] for I in Is) for k in range(r+1))%p
  S[r+1]=-Y[r]*inv[r+1]%p
  for i in range(n):Is[i][r+1]=((Y[r] if i==0 else z*Is[i-1][r])-z*Is[i][r])*inv[r+1]%p
 fac=[1]
 for i in range(1,L+2):fac.append(fac[-1]*i%p)
 ifac=[pow(v,p-2,p) for v in fac]
 C=[0]+[-S[r]%p for r in range(1,K)]
 ys=[[Y[r+j]*fac[r+j]*ifac[r]%p for r in range(K)] for j in range(n+1)]
 vars=[C,*ys]
 def conv(a,b):
  out=[0]*K
  for i,x in enumerate(a):
   if not x:continue
   for j in range(K-i):out[i+j]+=x*b[j]
  return [v%p for v in out]
 one=[1]+[0]*(K-1); powers={(i,0):one for i in range(len(vars))}
 for i,v in enumerate(vars):powers[i,1]=v
 def power(i,k):
  if (i,k) not in powers:powers[i,k]=conv(power(i,k-1),vars[i])
  return powers[i,k]
 columns={}
 for mon in obs:
  a=one
  for i,e in enumerate(mon):
   if e:a=conv(a,power(i,e))
  columns[mon]=a
 lead=[0]*(n+2);lead[0]=n;lead[-1]=1;lead=tuple(lead)
 assert lead in columns
 keep=[m for m in obs if m!=lead]
 A=[[columns[m][r] for m in keep] for r in range(K)]
 determinant=1;rank=0
 for col in range(K):
  pivot=next((r for r in range(rank,K) if A[r][col]),None)
  if pivot is None:continue
  if pivot!=rank:A[pivot],A[rank]=A[rank],A[pivot];determinant=-determinant
  d=A[rank][col];determinant=determinant*d%p;di=pow(d,p-2,p)
  row=A[rank]
  for r in range(rank+1,K):
   f=A[r][col]*di%p
   if f:
    for j in range(col+1,K):A[r][j]=(A[r][j]-f*row[j])%p
   A[r][col]=0
  rank+=1
 if rank<K:determinant=0
 # Polynomial relation checked on independently generated ODE jets.
 residual=[0]*K
 for term in data['terms']:
  e=term['powers'];assert e[0]==0
  c=term['coefficient']*pow(b,e[1],p)*pow(z,e[2],p)*pow(s,e[3],p)%p
  for r,v in enumerate(columns[tuple(e[4:])]):residual[r]=(residual[r]+c*v)%p
 assert not any(residual)
 # Recover all stage initials from derivatives of J=sum I, independently of polynomial recurrence.
 J=[sum(I[r] for I in Is)%p for r in range(L)]
 recovered=[]
 for m in range(n):
  v=sum(comb(m,k)*pow(z,m-k,p)*(Y[k]*fac[k]-J[k+1]*fac[k+1]) for k in range(m+1))%p
  recovered.append(v*pow(pow(z,m+1,p),p-2,p)%p)
 assert recovered==[n-i+1 for i in range(n)]
 # Altering the leading coefficient destroys the jet identity at this point.
 assert any(columns[lead])
 delta=determinant
 for r in range(K):delta=delta*fac[r]%p
 return {'n':n,'M':M,'prime':p,'point':{'beta':b,'zeta':z,'S0':s,'I0':list(range(2,n+2))},
         'wronskian_size':K,'rank':rank,'taylor_matrix_det_mod_p':determinant,'derivative_wronskian_det_mod_p':delta,
         'identity_jet_orders_checked':K,'chain_initials_recovered':True,'coefficient_mutation_rejected':True,
         'seconds':time.perf_counter()-t}
if __name__=='__main__':
 start=time.perf_counter();rows=[]
 for n in range(1,7):
  r=diagnostic(n);rows.append(r);print(json.dumps(r),flush=True)
 out={'diagnostics':rows,'all_n_nonvanishing':'UNPROVED','seconds':time.perf_counter()-start,
      'maxrss':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      'scope':'one exact finite-field witness for each fixed n; not a uniform proof or a replication of author software'}
 assert out['seconds']<600 and out['maxrss']<2*1024**3
 (P/'results'/'jet-check.json').write_text(json.dumps(out,indent=2)+'\n')
