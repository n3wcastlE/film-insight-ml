"""Fetch original archives. Cornell texts are not redistributed in the source package."""
from pathlib import Path
import hashlib, json, urllib.request
ROOT=Path(__file__).resolve().parents[1]
raw=ROOT/'data/raw'; raw.mkdir(parents=True,exist_ok=True)
urls={'review_polarity.tar.gz':'https://www.cs.cornell.edu/people/pabo/movie-review-data/review_polarity.tar.gz','ml-latest-small.zip':'https://files.grouplens.org/datasets/movielens/ml-latest-small.zip'}
manifest=ROOT/'results/summary.json'
expected=json.loads(manifest.read_text(encoding='utf-8'))['provenance'] if manifest.exists() else {}
for name,url in urls.items():
    path=raw/name
    if not path.exists():
        temp=path.with_suffix('.download')
        with urllib.request.urlopen(url,timeout=120) as response, temp.open('wb') as stream:
            import shutil
            shutil.copyfileobj(response,stream)
        temp.replace(path)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if name in expected and digest!=expected[name]['sha256']:
        raise RuntimeError(f'Archive differs from recorded version: {name}. Keep the original archive for exact reproduction.')
    print(name,digest)
