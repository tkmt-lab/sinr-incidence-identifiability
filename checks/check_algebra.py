"""Finite controls for the all-n proof. No new large-n Wronskian samples."""
from fractions import Fraction as Q
from math import factorial, comb
from pathlib import Path
import json, hashlib, time, resource
P=Path(__file__).resolve().parents[1]

def det(a):
 a=[[Q(v) for v in row] for row in a];out=Q(1)
 for c in range(len(a)):
  j=next((j for j in range(c,len(a)) if a[j][c]),None)
  if j is None:return Q(0)
  if j!=c:a[c],a[j]=a[j],a[c];out=-out
  d=a[c][c];out*=d
  for i in range(c+1,len(a)):
   f=a[i][c]/d
   for k in range(c+1,len(a)):a[i][k]-=f*a[c][k]
 return out

def convolution(a,b,L):
 out=[Q(0)]*L
 for i,x in enumerate(a):
  for j,y in enumerate(b):
   if i+j<L:out[i+j]+=x*y
 return out

def power(a,k,L):
 out=[Q(1)]+[Q(0)]*(L-1)
 for _ in range(k):out=convolution(out,a,L)
 return out

def puiseux(n):
 L=2*n+1;w=[Q(0)]*L;coeff=[]
 for m in range(1,n):
  c=Q(1,m)
  for j in range(m-1):c*=Q(m,n)+j
  c/=factorial(m-1);w[m]=c;coeff.append(str(c));assert c>0
 if n==1:w[1]=Q(1)
 left=power(w,n,L);right=[Q(0)]*L
 for j in range(n):
  t=power(w,j,L)
  for i in range(L-n):right[i+n]+=t[i]
 upto=1 if n==1 else 2*n-2
 assert left[:upto+1]==right[:upto+1]
 return {'n':n,'coefficients_c1_to_c_n_minus_1':coeff,'root_identity_through_degree':upto}

def center(n):
 L=6;u=Q(7);r=Q(3,2);d=[Q(0)]*L;h=Q(n)-r/u
 def equation(d):
  out=[n*v for v in d];out[1]+=1
  for j in range(1,L):
   term=power(d,j,L);c=-r*Q((-1)**(j+1),j)/u**j
   out=[a+c*b for a,b in zip(out,term)]
  return out
 for j in range(1,L):d[j]=-equation(d)[j]/h
 assert not any(equation(d))
 return {'n':n,'u':str(u),'r':str(r),'S_minus_u_coefficients':[str(v) for v in d],'formal_identity_through_degree':L-1}

def main():
 start=time.perf_counter();out={'scope':'finite algebra controls only; general proof is PROOF.md','rows':[]};inputs=[]
 for n in range(1,7):
  # Verify the original committed polynomial at C=s, not the producer's q recurrence.
  path=f'baseline/polynomial-n{n}.json'
  raw=(P/path).read_bytes();data=json.loads(raw)
  inputs.append({'source':'packet baseline','path':path,'sha256':hashlib.sha256(raw).hexdigest()})
  val={}
  for term in data['terms']:
   ex=list(term['powers']);ex[3]+=ex[4];ex[4]=0;ex=tuple(ex)
   val[ex]=val.get(ex,0)+term['coefficient']
  val={m:c for m,c in val.items() if c}
  expected=[0]*(n+6);expected[5]=n+1
  assert val=={tuple(expected):factorial(n)}
  obs={tuple(m) for m in data['observable_monomials']}
  lead=[0]*(n+2);lead[0]=n;lead[-1]=1;obs.remove(tuple(lead))
  for m in obs:
   for j in range(m[0]+1):assert (j,*m[1:]) in obs
  # Translation +2 then -2 gives identity, independently of ordering of the columns.
  for m in obs:
   transformed={}
   for j in range(m[0]+1):
    for k in range(j+1):transformed[k]=transformed.get(k,0)+comb(m[0],j)*2**(m[0]-j)*comb(j,k)*(-2)**(j-k)
   assert {k:v for k,v in transformed.items() if v}=={m[0]:1}
  # Literal characteristic determinant versus chain formula, at n+1 lambda values.
  for lam in range(n+1):
   A=[[Q((lam+3 if i==j else -3 if i==j+1 else 0)-(10 if i==0 else 0)) for j in range(n)] for i in range(n)]
   q=sum(comb(n,j+1)*3**(n-1-j)*lam**j for j in range(n))
   assert det(A)==(lam+3)**n-10*q
  weights=list(range(n,0,-1))
  assert weights[0]==n
  assert [(-weights[j]+(weights[j+1] if j+1<n else 0)) for j in range(n)]==[-1]*n
  out['rows'].append({'n':n,'at_C_equals_s':f'{factorial(n)}*y0^{n+1}','translation_basis_size':len(obs),
                      'characteristic_points':n+1,'weighted_chain_telescope':True,'puiseux':puiseux(n),'center':center(n)})
 # A deliberately wrong c2 for n=3 violates the required cubic coefficient.
 w=[Q(0),Q(1),Q(4,3),Q(0),Q(0)];lhs=power(w,3,5);rhs=[Q(0)]*5
 for j in range(3):
  term=power(w,j,5)
  for i in range(2):rhs[i+3]+=term[i]
 assert lhs!=rhs
 out.update(status='PASS',negative_control_rejected=True,seconds=time.perf_counter()-start,
            maxrss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            no_new_n_ge_7_wronskians=True,all_n_proof_checked_by_program=False)
 assert out['seconds']<600 and out['maxrss']<2*1024**3
 (P/'results'/'algebra-check.json').write_text(json.dumps(out,indent=2)+'\n')
 (P/'results'/'polynomial-hashes.json').write_text(json.dumps(inputs,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
