"""Exact sparse-polynomial diagnostics n=1..6; not an identifiability solver."""
from math import comb
from fractions import Fraction as Q
from pathlib import Path
import json,time,resource
P=Path(__file__).resolve().parents[1]

def add(a,b):
 c=a.copy()
 for m,v in b.items():c[m]=c.get(m,0)+v
 return {m:v for m,v in c.items() if v}
def scale(a,k):return {m:v*k for m,v in a.items() if v*k}
def mul(a,b):
 c={}
 for m,u in a.items():
  for n,v in b.items():
   k=tuple(x+y for x,y in zip(m,n));c[k]=c.get(k,0)+u*v
 return {m:v for m,v in c.items() if v}
def det(a):
 a=[[Q(x) for x in r] for r in a];v=Q(1)
 for i in range(len(a)):
  j=next((j for j in range(i,len(a)) if a[j][i]),None)
  if j is None:return Q(0)
  if i!=j:a[i],a[j]=a[j],a[i];v=-v
  d=a[i][i];v*=d
  for j in range(i+1,len(a)):
   f=a[j][i]/d
   for k in range(i+1,len(a)):a[j][k]-=f*a[i][k]
 return v

def run(n):
 # Variables: q,b,z,s,C,y0,...,yn. Dq=-y0, Dyj=y(j+1).
 size=n+6; one={(0,)*size:1}
 def var(i):m=[0]*size;m[i]=1;return {tuple(m):1}
 def power(i,k):m=[0]*size;m[i]=k;return {tuple(m):1}
 def D(poly):
  out={}
  for m,c in poly.items():
   for i in [0,*range(5,size-1)]:
    if not m[i]:continue
    mm=list(m);mm[i]-=1;mm[5 if i==0 else i+1]+=1
    out=add(out,{tuple(mm):c*m[i]*(-1 if i==0 else 1)})
  return out
 Ps=[var(5)]
 for k in range(n):Ps.append(add(mul(var(0),D(Ps[-1])),scale(mul(var(5),Ps[-1]),k+1)))
 F={}
 for k in range(n+1):F=add(F,scale(mul(mul(power(2,n-k),power(0,n-k)),Ps[k]),comb(n,k)))
 for j in range(n):F=add(F,scale(mul(mul(mul(var(1),power(0,n+1)),power(2,n-1-j)),var(5+j)),-comb(n,j+1)))
 expanded={}
 for m,c in F.items():
  h=m[0]
  for j in range(h+1):
   mm=list(m);mm[0]=0;mm[3]+=h-j;mm[4]+=j
   expanded=add(expanded,{tuple(mm):c*comb(h,j)*(-1)**j})
 def coeff(cpow,yindex):
  obs=[0]*(size-4);obs[0]=cpow;obs[1+yindex]=1
  return {m[:4]:v for m,v in expanded.items() if list(m[4:])==obs}
 def par(b=0,z=0,s=0):return (0,b,z,s)
 assert coeff(n,n)=={par():(-1)**n}
 assert coeff(n-1,n)=={par(s=1):(-1)**(n-1)*n}
 assert coeff(n+1,n-1)=={par(b=1):(-1)**n}
 assert coeff(n,n-1)=={par(z=1):(-1)**n*n,par(b=1,s=1):(-1)**(n+1)*(n+1)}
 # Exact observability determinant at z=2; general determinant proved by triangularity.
 z=Q(2);A=[[(-z if i==j else z if i==j+1 else Q(0)) for j in range(n)] for i in range(n)]
 O=[];row=[Q(1)]*n
 for _ in range(n):O.append(row);row=[sum(row[k]*A[k][j] for k in range(n)) for j in range(n)]
 value=det(O);assert value==(-1)**(n*(n-1)//2)*z**(n*(n-1)//2)
 obs=sorted({m[4:] for m in expanded})
 data={'n':n,'variables':['q','beta','zeta','s','C']+[f'y{j}' for j in range(n+1)],
       'terms':[{'powers':m,'coefficient':v} for m,v in sorted(expanded.items())],
       'observable_monomials':obs,'observable_dimension':len(obs),'normalization':(-1)**n,
       'O_det_at_zeta_2':str(value),'coefficient_inverse_checked':True}
 (P/'results'/f'polynomial-n{n}.json').write_text(json.dumps(data,indent=2)+'\n')
 return {k:data[k] for k in ['n','observable_dimension','O_det_at_zeta_2','coefficient_inverse_checked']}
if __name__=='__main__':
 start=time.perf_counter();out={'diagnostics':[run(n) for n in range(1,7)],'status':'PASS','all_n_identifiability':'UNPROVED'}
 out.update(seconds=time.perf_counter()-start,maxrss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
 assert out['seconds']<600 and out['maxrss']<2*1024**3
 (P/'results'/'diagnostics.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
