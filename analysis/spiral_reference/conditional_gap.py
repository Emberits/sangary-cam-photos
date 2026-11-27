"""Frozen conditional-gap experiment, not production measurement.
Run from this directory: python conditional_gap.py SOURCE_DIR NEW_OUTPUT.csv
Or: python conditional_gap.py --self-test
Uses ANCHORS and HASHES from replay_control.py; target-date manual axes are
not used. Dependencies: requirements-control.txt. Widths are candidates only;
no mm conversion, visibility classifier or automatic acceptance is provided.
Golden widths below test replay, not accuracy. Source files are supplied
separately. An existing output is never overwritten.
"""
import csv
import hashlib
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates, gaussian_filter, grey_closing, label, find_objects
from scipy.signal import find_peaks
from replay_control import ANCHORS, HASHES

X = np.arange(955,1075.001,.5)
N = np.arange(-14,14.001,.25)
GOLDEN = ((3.750,4.250,4.375),(1.625,6.500,8.250))


def fill_gap(smooth):
    if smooth.ndim != 2 or not np.isfinite(smooth).all():
        raise ValueError("invalid_strip")
    closed = grey_closing(smooth,size=(9,1),mode="nearest")
    eligible = np.zeros_like(smooth,dtype=bool)
    for j in range(smooth.shape[1]):
        diff = closed[:,j]-smooth[:,j]
        runs,count = label(diff>3)
        background = np.percentile(smooth[:,j],50)
        for k in range(1,count+1):
            ids = np.flatnonzero(runs==k)
            a,b = ids[0],ids[-1]
            if a<2 or b>len(N)-3 or len(ids)>9 or diff[ids].max()<12:
                continue
            left = smooth[max(0,a-4):a,j].max()
            right = smooth[b+1:min(len(N),b+5),j].max()
            if min(left,right)<background+25 or abs(left-right)>60:
                continue
            eligible[ids,j] = True
    labs,count = label(eligible,structure=np.ones((3,3)))
    accepted = np.zeros_like(eligible)
    for k,sl in enumerate(find_objects(labs),1):
        if sl is None:
            continue
        component = labs[sl]==k
        cols = component.any(axis=0)
        if cols.sum()>=16 and cols.mean()>=.8:
            accepted[sl] |= component
    result = smooth.copy()
    result[accepted] = closed[accepted]
    return result,accepted


def paired_path(smooth):
    if smooth.shape != (len(N),len(X)) or not np.isfinite(smooth).all():
        raise ValueError("invalid_path_input")
    grad = np.gradient(smooth,N,axis=0)
    scale = max(np.percentile(abs(grad),80),1)
    states = []
    for j in range(len(X)):
        gu,pr = grad[:,j]/scale,smooth[:,j]
        ups,_ = find_peaks(gu)
        lows,_ = find_peaks(-gu)
        pairs = []
        for u in ups:
            for l in lows:
                width,center = N[l]-N[u],(N[u]+N[l])/2
                if not (1<=width<=14 and abs(center)<=7 and gu[u]>0 and gu[l]<0):
                    continue
                outside = np.mean([pr[max(0,u-8):max(1,u-4)].mean(),
                                   pr[min(len(N)-1,l+4):min(len(N),l+8)].mean()])
                score = np.sqrt(gu[u]*(-gu[l]))+.15*(pr[u:l+1].mean()-outside)/scale
                pairs.append((score,N[u],N[l]))
        if not pairs:
            return None
        states.append(np.array(sorted(pairs,reverse=True)[:36]))
    cost,backs = -states[0][:,0],[]
    for previous,current in zip(states[:-1],states[1:]):
        distance = ((previous[:,1,None]-current[None,:,1])**2+
                    (previous[:,2,None]-current[None,:,2])**2)
        matrix = cost[:,None]+2*distance
        ix = np.argmin(matrix,axis=0)
        cost = matrix[ix,np.arange(len(current))]-current[:,0]
        backs.append(ix)
    indices = [int(np.argmin(cost))]
    for back in backs[::-1]:
        indices.append(int(back[indices[-1]]))
    return np.array([states[j][k,1:] for j,k in enumerate(indices[::-1])]).T


def run(root):
    root = Path(root)
    anchors = np.array(ANCHORS)
    coef = np.polyfit(anchors[:,0],anchors[:,1],2)
    y = np.polyval(coef,X)
    slope = np.polyval(np.polyder(coef),X)
    norm = np.sqrt(1+slope*slope)
    rows = []
    for fi,name in enumerate(list(HASHES)[1:]):
        source = root/name
        if hashlib.sha256(source.read_bytes()).hexdigest()!=HASHES[name]:
            raise ValueError("source_hash_mismatch: "+name)
        image = np.asarray(Image.open(source).convert("L"),float)
        strip = map_coordinates(image,[y[None,:]+N[:,None]/norm,
                                X[None,:]-N[:,None]*slope/norm],order=1)
        smooth = gaussian_filter(strip,(.3/.25,1/.5))
        filled,mask = fill_gap(smooth)
        for method,processed in (("raw",smooth),("conditional",filled)):
            path = paired_path(processed)
            for wi,center in enumerate(anchors[:,0]):
                width = None if path is None else float(np.median((path[1]-path[0])[abs(X-center)<=3]))
                if method=="conditional" and (width is None or abs(width-GOLDEN[fi][wi])>1e-6):
                    raise ValueError("conditional_replay_failed")
                rows.append(dict(image=name,window=wi+1,method=method,
                                 candidate_width_px=width,
                                 status="no_candidates" if width is None else "candidate_only",
                                 filled_pixels=int(mask.sum()) if method=="conditional" else 0))
    return rows


def self_test():
    shape = (len(N),len(X))
    flat = np.full(shape,50.)
    assert not fill_gap(flat)[1].any()
    assert paired_path(flat) is None
    good = flat.copy()
    good[40:72] = 180
    good[54:58] = 50
    filled,mask = fill_gap(good)
    assert mask.any() and np.all(filled[54:58]==180)
    wide = flat.copy()
    wide[40:82] = 180
    wide[54:66] = 50
    assert not fill_gap(wide)[1].any()
    short = flat.copy()
    short[40:72,:8] = 180
    short[54:58,:8] = 50
    assert not fill_gap(short)[1].any()
    lone = flat.copy()
    lone[40:54] = 180
    assert not fill_gap(lone)[1].any()
    bad = flat.copy()
    bad[0,0] = np.nan
    try:
        fill_gap(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("nonfinite input accepted")
    return 7


if __name__ == "__main__":
    if sys.argv[1:]==["--self-test"]:
        print(f"PASS: {self_test()} synthetic checks")
    else:
        rows = run(sys.argv[1])
        with open(sys.argv[2],"x",newline="",encoding="utf-8") as stream:
            writer = csv.DictWriter(stream,fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print("PASS: six conditional widths replayed; candidates are not visibility-approved")
