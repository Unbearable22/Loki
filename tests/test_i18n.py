import json
from pathlib import Path
def test_locale_key_parity():
    files=list(Path("locales").glob("*.json"))
    base=json.loads(files[0].read_text(encoding="utf-8"))
    def keys(x,p=""):
        out=set()
        if isinstance(x,dict):
            for k,v in x.items(): out |= keys(v,f"{p}.{k}" if p else k)
        else: out.add(p)
        return out
    base_keys=keys(base)
    for f in files[1:]:
        assert keys(json.loads(f.read_text(encoding="utf-8")))==base_keys, f"Key mismatch: {f}"
