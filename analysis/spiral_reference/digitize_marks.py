"""Digitize this specific manual annotation, not image contours.
Requires numpy and Pillow. Run: python digitize_marks.py ANNOTATION.jpg OUTPUT.csv
The source JPEG is supplied separately; its hash is checked. Existing files are
not changed. Fitted endpoints are estimates of stroke centrelines, not clicks.
"""
import csv
import hashlib
import sys
from pathlib import Path
import numpy as np
from PIL import Image

SOURCE_SHA256 = "f5bdb767251ad9f6dc5d338d9c39df2600d4141f13ad98cf19327fe8fce99e68"
ROIS = [
    ("red", "upper", 1, (148,285,196,327)),
    ("red", "lower", 1, (135,409,184,452)),
    ("red", "upper", 2, (350,423,402,466)),
    ("red", "lower", 2, (345,563,405,612)),
    ("red", "upper", 3, (540,549,598,596)),
    ("red", "lower", 3, (540,704,592,747)),
    ("green", "upper", 1, (186,303,236,350)),
    ("green", "upper", 2, (387,426,433,487)),
    ("green", "upper", 3, (586,554,644,621)),
]


def digitize(path):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("unexpected_source_hash")
    with Image.open(path) as image:
        if image.size != (850,1035):
            raise ValueError("unexpected_image_size")
        pixels = np.asarray(image.convert("RGB"), dtype=float)
    rows = []
    for color, position, window, (x0,y0,x1,y1) in ROIS:
        r,g,b = pixels[y0:y1,x0:x1].transpose(2,0,1)
        mask = ((r-g>35)&(r-b>30)) if color == "red" else ((g-r>20)&(g-b>12))
        yy,xx = np.where(mask)
        if len(xx) < 20:
            raise ValueError("insufficient_mark_pixels")
        x,y = xx+x0,yy+y0
        xc,slope = x.mean(),0.68
        for _ in range(30):
            residual = y-slope*(x-xc)
            centers = np.percentile(residual,[20,80])
            for _ in range(15):
                groups = np.argmin(abs(residual[:,None]-centers),axis=1)
                if any(not np.any(groups==k) for k in (0,1)):
                    raise ValueError("unresolved_pair")
                centers = np.array([residual[groups==k].mean() for k in (0,1)])
            design = np.column_stack([x-xc,groups==0,groups==1])
            beta = np.linalg.lstsq(design,y,rcond=None)[0]
            if abs(beta[0]-slope)<1e-7:
                break
            slope = beta[0]
        slope = float(beta[0])
        top,bottom = sorted(beta[1:])
        row = dict(color=color,position=position,window=window,
                   width_px=(bottom-top)/np.sqrt(1+slope*slope)/5,
                   fit_rms_annotation_px=np.sqrt(np.mean((y-design@beta)**2)))
        # Pillow pixel-centre mapping: crop (940,475), scale 5, header 110.
        for side,intercept in (("top",top),("bottom",bottom)):
            for end,xa in (("start",float(x.min())),("end",float(x.max()))):
                ya = float(intercept+slope*(xa-xc))
                row[f"{side}_{end}_x"] = 940+(xa+0.5)/5-0.5
                row[f"{side}_{end}_y"] = 475+(ya-110+0.5)/5-0.5
        rows.append(row)
    return rows


if __name__ == "__main__":
    rows = digitize(sys.argv[1])
    with open(sys.argv[2],"x",newline="",encoding="utf-8") as output:
        writer = csv.DictWriter(output,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
