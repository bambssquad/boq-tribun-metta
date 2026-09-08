from pathlib import Path
import shutil
root=Path(__file__).resolve().parent
for name in ['index.html','tools.html','lookback.css','lookback.js','panzoom.js']:
 shutil.copy2(root/'dist'/name,root/name)
shutil.copytree(root/'dist/assets',root/'assets',dirs_exist_ok=True)
(root/'.nojekyll').touch()
