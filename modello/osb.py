"""Schema di taglio del pannello OSB/3 2500×1250×18 (dal modello)."""
import json
_d = json.load(open("parts_kvh.json")); _p = {p["name"]: p for p in _d["parts"]}
def _wd(n):
    b = _p[n]["box"]; return round(b[3] - b[0]), round(b[4] - b[1])
K = 4
cw, cd = _wd("Ripiano basso cassetti"); rw, rd = _wd("Ripiano basso ricarica")
fw, fd = _wd("Rinforzo piano ricarica"); sw, sd = _wd("Ripiano basso post. seduta")
OSB_CUTS = [((0, 0), cw, cd, f"Ripiano cassetti\n{cw}×{cd}"),
            ((cw + K, 0), rw, rd, f"Ripiano ricarica\n{rw}×{rd}"),
            ((cw + rw + 2 * K, 0), fw, fd, f"Rinforzo A\n{fw}×{fd}"),
            ((cw + rw + fw + 3 * K, 0), fw, fd, f"Rinforzo B\n{fw}×{fd}"),
            ((0, max(cd, rd, fd) + K), sw, sd, f"Ripiano seduta {sw}×{sd}")]
assert cw + rw + 2 * fw + 3 * K <= 2500 and max(cd, rd, fd) + K + sd <= 1250
STRIP = max(cd, rd, fd)
