"""Frozen six-section regression, NOT a detector for new frames.
Usage: python replay_control.py SOURCE_DIR APPROVED.csv NEW_OUTPUT.csv
Requires numpy, scipy and Pillow. Sources include the separately supplied
wire_alignment_diagnostic.jpg; axes for each date are reconstructed from it.
The baseline is read-only. Width tolerance is 1e-6 original pixels, a numerical
replay tolerance, NOT physical measurement accuracy. No millimetres are tested.
Anchor constants preserve the reviewed control calculation, including its
rounded centre coordinates. Do not silently replace them with refitted axes.
"""
import csv
import hashlib
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates, gaussian_filter1d

HASHES = {
    "wire_alignment_diagnostic.jpg": "7cd60de77d75e94acf40162c4bc2b80597af6193e43334ccaceebe4eda59e2c8",
    "2026-11-23_09-01-27.jpg": "3ddb069f5825cdc30a504eabb1d7f2723ddb312d7f71fc73a914290a049ee688",
    "2026-11-20_15-01-35.jpg": "ec4abdb1628178c62dfdfa5805aac0fa0c0c1a3630e88452059b5d99a12e28a5",
}
ANCHORS = [
    (973.7, (513.097000+514.946169)/2, (515.708356-510.485645)/7.4),
    (1014.6, (540.459125+542.707209)/2, (543.152584-537.765666)/8),
    (1053.4, (565.656571+568.440942)/2, (568.758807-562.554335)/9.2),
]


def extract(source_dir):
    root = Path(source_dir)
    for name, expected in HASHES.items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest() != expected:
            raise ValueError("source_hash_mismatch: " + name)
    diag = np.asarray(Image.open(root/"wire_alignment_diagnostic.jpg").convert("RGB"), float)
    offsets = []
    for top, bottom in [(58,317),(411,670),(763,1022)]:
        r,g,b = diag[top:bottom+1,1212:2116].transpose(2,0,1)
        mask = (g-r>22)&(g-b>8)&(g>70)
        uv = [(u,np.median(np.flatnonzero(mask[:,u])))
              for u in range(5,898) if mask[:,u].any()]
        if len(uv)<10:
            raise ValueError("diagnostic_axis_missing")
        coef = np.polyfit(*np.array(uv).T,1)
        offsets.append([-16+32*np.polyval(coef,(x-950)/150*903)/259
                        for x,y,slope in ANCHORS])
    t = np.arange(-8,8.001,.25)
    n = np.arange(-14,14.001,.125)
    rows = []
    for ri,name in enumerate(list(HASHES)[1:],1):
        image = np.asarray(Image.open(root/name).convert("L"), float)
        for ci,(x,y,slope) in enumerate(ANCHORS):
            norm = np.sqrt(1+slope*slope)
            tx,ty = 1/norm,slope/norm
            shift = offsets[ri][ci]-offsets[0][ci]
            xx = x+t[None,:]*tx-(n[:,None]+shift)*ty
            yy = y+t[None,:]*ty+(n[:,None]+shift)*tx
            strip = map_coordinates(image,[yy,xx],order=1)
            profile = gaussian_filter1d(np.median(strip[:,abs(t)<=3],axis=1),.3/.125)
            gradient = np.gradient(profile,n)
            ui = np.flatnonzero((n>=-9)&(n<=-.25))
            li = np.flatnonzero((n>=.25)&(n<=9))
            upper = float(n[ui[np.argmax(gradient[ui])]])
            lower = float(n[li[np.argmin(gradient[li])]])
            rows.append(dict(image=name,position="upper",window=ci+1,
                             axis_shift_px=shift,upper_normal_px=upper,
                             lower_normal_px=lower,outer_width_px=lower-upper))
    return rows


def verify(rows, baseline):
    with open(baseline,newline="",encoding="utf-8") as stream:
        expected = list(csv.DictReader(stream))
    def key(row):
        return row["image"],row["position"],int(row["window"])
    targets = {key(row):float(row["outer_width_px"]) for row in expected}
    if len(expected)!=6 or len(targets)!=6 or {key(row) for row in rows}!=set(targets):
        raise ValueError("baseline_section_mismatch")
    errors = [abs(row["outer_width_px"]-targets[key(row)]) for row in rows]
    if not all(np.isfinite(e) and e<=1e-6 for e in errors):
        raise ValueError("width_regression_failed")
    return max(errors)


if __name__ == "__main__":
    rows = extract(sys.argv[1])
    maximum = verify(rows,sys.argv[2])
    with open(sys.argv[3],"x",newline="",encoding="utf-8") as stream:
        writer = csv.DictWriter(stream,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"PASS: {len(rows)} sections, maximum width error {maximum:.9g} px")
