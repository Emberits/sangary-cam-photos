"""Frozen 09:01/10:01 attachment replay, not a production tracker.
Usage: python temporal_replay.py SOURCE_DIR NEW_REPORT.json
Tests: python temporal_replay.py --self-test
Dependencies: requirements-control.txt. No OpenCV, network or mm conversion.
The uploaded 10:01 JPEG is required, not the unverified repository namesake.
Axes below are frozen from the earlier manual diagnostic and approved control.
Golden values verify replay only; no general acceptance criterion is provided.
"""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates, gaussian_filter, gaussian_filter1d, shift
from scipy.signal import correlate

FILES = {
    "2026-11-23_09-01-27.jpg": "3ddb069f5825cdc30a504eabb1d7f2723ddb312d7f71fc73a914290a049ee688",
    "2026-11-23_10-01-55.jpg": "074e36e86224ccd20890ff3c4166cbf48d757abb2a45c38be8a9ddf74d044fa1",
}
AXES = [
    (975.2525022704792,511.8218616354675,0.7057717567567573),
    (1016.3946399537015,538.9179844912609,0.6733647500000046),
    (1055.4727168942306,563.975328909881,0.6743991304347837),
]


def sample(image,center,slope,t,n):
    norm = np.sqrt(1+slope*slope)
    tx,ty = 1/norm,slope/norm
    xx = center[0]+t[None,:]*tx-n[:,None]*ty
    yy = center[1]+t[None,:]*ty+n[:,None]*tx
    if xx.min()<0 or yy.min()<0 or xx.max()>image.shape[1]-1 or yy.max()>image.shape[0]-1:
        raise ValueError("sampling_outside_image")
    return map_coordinates(image,[yy,xx],order=1)


def match(first,second,center,slope,half):
    def highpass(a):
        return a-gaussian_filter(a,2)
    template = highpass(sample(first,center,slope,np.arange(-12,12.001,.5),np.arange(-half,half+.001,.5)))
    search = highpass(sample(second,center,slope,np.arange(-20,20.001,.5),np.arange(-half-8,half+8.001,.5)))
    template -= template.mean()
    energy = np.sum(template**2)
    if energy<=1e-12:
        raise ValueError("flat_template")
    ones = np.ones_like(template)
    numerator = correlate(search,template,mode="valid",method="fft")
    sums = correlate(search,ones,mode="valid",method="fft")
    squares = correlate(search**2,ones,mode="valid",method="fft")
    scores = numerator/np.sqrt(np.maximum(squares-sums*sums/template.size,1e-12)*energy)
    row,col = np.unravel_index(np.argmax(scores),scores.shape)
    dt,dn = (col-16)*.5,(row-16)*.5
    yy,xx = np.indices(scores.shape)
    alternative = scores.copy()
    alternative[(xx-col)**2+(yy-row)**2<16] = -2
    norm = np.sqrt(1+slope*slope)
    delta = np.array([(dt-dn*slope)/norm,(dt*slope+dn)/norm])
    return delta,dict(along_shift_px=float(dt),normal_shift_px=float(dn),
                      ncc=float(scores[row,col]),peak_gap=float(scores[row,col]-alternative.max()))


def edges(image,center,slope):
    t,n = np.arange(-8,8.001,.25),np.arange(-14,14.001,.125)
    strip = sample(image,center,slope,t,n)
    profile = gaussian_filter1d(np.median(strip[:,abs(t)<=3],axis=1),.3/.125)
    grad = np.gradient(profile,n)
    ui = np.flatnonzero((n>=-9)&(n<=-.25))
    li = np.flatnonzero((n>=.25)&(n<=9))
    upper,lower = float(n[ui[np.argmax(grad[ui])]]),float(n[li[np.argmin(grad[li])]])
    return dict(upper_normal_px=upper,lower_normal_px=lower,width_px=lower-upper)


def run(root):
    images = []
    for name,expected in FILES.items():
        path = Path(root)/name
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError("source_hash_mismatch: "+name)
        image = Image.open(path)
        if image.size!=(1280,720):
            raise ValueError("unexpected_image_size")
        images.append(np.asarray(image.convert("L"),float))
    matches,widths = [],[]
    for wi,(x,y,slope) in enumerate(AXES,1):
        center = np.array([x,y])
        for half in (4,6,10):
            delta,forward = match(images[0],images[1],center,slope,half)
            backward,reverse = match(images[1],images[0],center+delta,slope,half)
            cycle = float(np.linalg.norm(delta+backward))
            if np.linalg.norm(delta)>1e-9 or cycle>1e-9:
                raise ValueError("frozen_transfer_regression_failed")
            matches.append(dict(window=wi,half_normal_px=half,forward=forward,reverse=reverse,cycle_error_px=cycle))
            if half==6:
                target = center+delta
        for fi,c in enumerate((center,target)):
            result = edges(images[fi],c,slope)
            expected = ((3.625,4.5,4.5),(3.75,4.375,4.5))[fi][wi-1]
            if abs(result["width_px"]-expected)>1e-6:
                raise ValueError("frozen_width_regression_failed")
            widths.append(dict(image=list(FILES)[fi],window=wi,**result))
    return dict(status="frozen_replay_passed_not_general_validation",source_sha256=FILES,matches=matches,widths=widths)


def self_test():
    rng = np.random.default_rng(813)
    first = gaussian_filter(rng.normal(size=(128,128)),.7)
    second = shift(first,(-1,2),order=1,mode="nearest")
    center = np.array([64.,64.])
    delta,_ = match(first,second,center,0,6)
    assert np.allclose(delta,[2,-1])
    back,_ = match(second,first,center+delta,0,6)
    assert np.allclose(delta+back,[0,0])
    try:
        match(np.ones((128,128)),np.ones((128,128)),center,0,6)
    except ValueError as error:
        assert str(error)=="flat_template"
    else:
        raise AssertionError("flat template accepted")
    return 3


if __name__ == "__main__":
    if sys.argv[1:]==["--self-test"]:
        print(f"PASS: {self_test()} synthetic checks")
    else:
        report = run(sys.argv[1])
        with open(sys.argv[2],"x",encoding="utf-8") as output:
            json.dump(report,output,indent=2)
        print("PASS: nine transfers and six widths replayed; physical accuracy not validated")
