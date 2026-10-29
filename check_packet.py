"""Offline publication integrity and scope checks; not an all-n proof checker."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
from publication_privacy import scan_tree
ROOT=Path(__file__).resolve().parent
SKIP={'.git','.work','results','build','__pycache__'}
def require(condition,message):
 if not condition:raise ValueError(message)
def files():
 result=set()
 for p in ROOT.rglob('*'):
  rel=p.relative_to(ROOT)
  if any(x in SKIP for x in rel.parts):continue
  require(not p.is_symlink(),'Symbolic link in packet')
  if p.is_file():result.add(rel.as_posix())
 return result
def manifest_check():
 want={}
 for line in (ROOT/'MANIFEST.sha256').read_text().splitlines():
  d,n=line.split('  ',1);p=Path(n)
  require(bool(re.fullmatch('[0-9a-f]{64}',d)) and not p.is_absolute() and '..' not in p.parts,'Unsafe manifest row')
  require(n not in want,'Duplicate manifest file');want[n]=d
 require(set(want)==files()-{'MANIFEST.sha256'},'Manifest file inventory mismatch')
 for n,d in want.items():require(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==d,'Hash mismatch: '+n)
 return len(want)
def main():
 require(__debug__,'Run without -O')
 count=manifest_check();c=json.loads((ROOT/'claims.json').read_text());z=json.loads((ROOT/'.zenodo.json').read_text());citation=json.loads((ROOT/'CITATION.cff').read_text());p=json.loads((ROOT/'PROVENANCE.json').read_text())
 require(c['version']==z['version']==citation['version']=='1.0.0','Version mismatch')
 require(c['title']==z['title']==citation['title'],'Title mismatch')
 require(c['manuscript_status']=='THEOREM' and c['formal_proof_certificate'] is False and c['human_peer_review'] is False,'Evidence scope mismatch')
 require(c['review_independence']['fully_independent_all_n_proof'] is False,'Review independence inflated')
 require(c['fresh_editorial_reader']['major_count']==0 and c['fresh_editorial_reader']['minor_count']==2,'Editorial verdict mismatch')
 require(c['model']['competitors']=='all real points with the same n and N0; no positivity, genericity or nonzero-zeta restriction','Competitor scope mismatch')
 require(c['claims'][1]['all_n_proof_checked'] is False,'Finite checks promoted to all-n certificate')
 require(set(['unknown n','unknown N0','noise','finite sampled data']).issubset(c['excluded']),'Missing exclusions')
 for row in p['unchanged_scientific_files']:
  b=(ROOT/row['path']).read_bytes();require(len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],'Scientific source differs: '+row['path'])
 for row in p['review_record_derivatives']:
  b=(ROOT/row['public_path']).read_bytes();require(len(b)==row['public_bytes'] and hashlib.sha256(b).hexdigest()==row['public_sha256'],'Public record digest mismatch')
 require(citation['authors'][0]['family-names']=='Takimoto' and citation['authors'][0]['given-names']=='Tatsuhiko','Author mismatch')
 text=subprocess.check_output(['pdftotext',str(ROOT/'paper.pdf'),'-'],text=True)
 info=subprocess.check_output(['pdfinfo',str(ROOT/'paper.pdf')],text=True)
 require(bool(re.search(r'^Pages:\s+6\s*$',info,re.M)),'Unexpected PDF page count')
 require(c['title'] in re.sub(r'\s+',' ',text),'PDF title mismatch')
 require('Tatsuhiko Takimoto' in text and 'Conjecture' in text and 'Theorem 1' in text,'PDF text incomplete')
 privacy=scan_tree(ROOT);require(privacy['status']=='PASS','Privacy-pattern hits: '+json.dumps(privacy['hits']))
 # Check repository-relative document links, including fragment-bearing links.
 for doc in ROOT.rglob('*.md'):
  if any(x in SKIP for x in doc.relative_to(ROOT).parts):continue
  for link in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
   if re.match(r'[a-z]+:',link) or link.startswith('#'):continue
   target=(doc.parent/link.split('#')[0]).resolve();require(target.is_relative_to(ROOT) and target.exists(),'Broken local link in '+doc.name)
 print(json.dumps(dict(status='PASS',manifest_files=count,scientific_files_unchanged=len(p['unchanged_scientific_files']),privacy=privacy,pdf_pages=6,scope='file integrity, metadata and claim boundaries only; no proof verification'),indent=2))
if __name__=='__main__':
 try:main()
 except (ValueError,KeyError,OSError,subprocess.CalledProcessError) as exc:
  print('FAIL '+str(exc),file=sys.stderr);raise SystemExit(1)
