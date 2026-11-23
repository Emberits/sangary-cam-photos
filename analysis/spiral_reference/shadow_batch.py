"""Read-only shadow batch for the known upper-wire seed on 2026-11-23.
No millimetres, no visibility approval, no photo/CSV-baseline modification.
Uses temporal_replay helpers, NOT its frozen hash-checking run(). All outputs
require human review, including a track passing the unvalidated heuristics.
"""
import argparse
import csv
import hashlib
import json
import os
import platform
from datetime import datetime
from pathlib import Path
import numpy as np
from PIL import Image, __version__ as pillow_version
import scipy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from temporal_replay import AXES, match, edges, sample

SEED = "2026-11-23_09-01-27.jpg"
FIELDS = ["image","window","reference_image","status","candidate_width_px",
          "upper_normal_px","lower_normal_px","ncc_min","peak_gap_min",
          "cycle_error_max_px","template_disagreement_px","reason","sha256"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transfer(first,second,center,slope):
    variants = []
    for half in (4,6,10):
        delta,forward = match(first,second,center,slope,half)
        back,reverse = match(second,first,center+delta,slope,half)
        variants.append((delta,forward,float(np.linalg.norm(delta+back))))
    main = variants[1][0]
    metrics = dict(ncc_min=min(v[1]["ncc"] for v in variants),
                   peak_gap_min=min(v[1]["peak_gap"] for v in variants),
                   cycle_error_max_px=max(v[2] for v in variants),
                   template_disagreement_px=max(float(np.linalg.norm(v[0]-main)) for v in variants))
    reasons = []
    if metrics["ncc_min"]<.75: reasons.append("weak_match")
    if metrics["peak_gap_min"]<.03: reasons.append("competing_match")
    if metrics["cycle_error_max_px"]>.5: reasons.append("reverse_inconsistent")
    if metrics["template_disagreement_px"]>1: reasons.append("template_disagreement")
    if any(max(abs(v[1]["along_shift_px"]),abs(v[1]["normal_shift_px"]))>=8 for v in variants):
        reasons.append("search_limit")
    return center+main,metrics,reasons


def batch(photos,out,limit,archive_sha):
    if not 1<=limit<=24: raise ValueError("max_frames_must_be_1_to_24")
    files = sorted(p for p in photos.glob("2026-11-23_*.jpg") if p.name>=SEED)[:limit]
    if not files or files[0].name!=SEED: raise ValueError("required_seed_missing")
    for path in files: datetime.strptime(path.stem,"%Y-%m-%d_%H-%M-%S")
    out.mkdir(parents=True,exist_ok=False)
    rows,inputs = [],[]
    centers = [np.array([x,y]) for x,y,slope in AXES]
    active = [True]*3
    previous,previous_path,previous_time = None,None,None
    for path in files:
        when = datetime.strptime(path.stem,"%Y-%m-%d_%H-%M-%S")
        checksum = digest(path)
        image,error = None,""
        try:
            with Image.open(path) as source:
                if source.size!=(1280,720): raise ValueError("unexpected_image_size")
                image = np.asarray(source.convert("L"),float)
        except (OSError,ValueError) as exc: error=type(exc).__name__+": "+str(exc)
        inputs.append(dict(file=path.name,bytes=path.stat().st_size,sha256=checksum,decode_error=error))
        fig,axes = plt.subplots(1,3,figsize=(11,4))
        for wi,((x,y,slope),ax) in enumerate(zip(AXES,axes)):
            row = dict.fromkeys(FIELDS,"")
            row.update(image=path.name,window=wi+1,reference_image=previous_path or "fixed_09_01_axis",
                       status="candidate_review_required",reason="visibility_not_validated",sha256=checksum)
            result = None
            try:
                if error: raise ValueError("decode_failed")
                if not active[wi]: raise ValueError("track_lost_no_auto_reseed")
                if previous is not None:
                    if (when-previous_time).total_seconds()>5400: raise ValueError("time_gap_over_90_minutes")
                    target,metrics,reasons = transfer(previous,image,centers[wi],slope)
                    row.update(metrics)
                    if reasons: raise ValueError(";".join(reasons))
                    centers[wi] = target
                else:
                    row["status"] = "seed_candidate_review_required"
                    row["reason"] = "attachment_derived_axis_on_archive_seed_unverified"
                result = edges(image,centers[wi],slope)
                row.update(candidate_width_px=result["width_px"],upper_normal_px=result["upper_normal_px"],
                           lower_normal_px=result["lower_normal_px"])
            except (ValueError,IndexError,FloatingPointError) as exc:
                row.update(status="no_measurement",reason=str(exc),candidate_width_px="",upper_normal_px="",lower_normal_px="")
                active[wi] = False
            if image is not None:
                try:
                    t,n = np.arange(-8,8.001,.25),np.arange(-14,14.001,.125)
                    strip = sample(image,centers[wi],slope,t,n)
                    ax.imshow(strip,cmap="gray",extent=[-8,8,14,-14],aspect="auto",vmin=0,vmax=255)
                    if row["candidate_width_px"]!="":
                        for key,color in (("upper_normal_px","cyan"),("lower_normal_px","orange")):
                            ax.plot([-5,5],[row[key]]*2,color=color,lw=1)
                except ValueError: pass
            ax.set_title(f"W{wi+1}: {row['status']}",fontsize=8)
            ax.set_xlabel("Along wire, original px")
            ax.set_ylabel("Normal offset, original px")
            rows.append(row)
        fig.suptitle(path.name+" | SHADOW: no automatic contour approval",fontsize=10)
        fig.tight_layout()
        fig.savefig(out/(path.stem+".png"),dpi=130)
        plt.close(fig)
        previous,previous_path,previous_time = image,path.name,when
    with (out/"candidates.csv").open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)
    manifest = dict(mode="shadow_no_mm_no_publication",review_required_for_every_candidate=True,
                    archive_commit=archive_sha,code_commit=os.environ.get("GITHUB_SHA","local-test"),
                    seed=SEED,input_files=inputs,python=platform.python_version(),
                    versions=dict(numpy=np.__version__,scipy=scipy.__version__,Pillow=pillow_version,matplotlib=matplotlib.__version__),
                    heuristic_thresholds=dict(ncc_min=.75,peak_gap_min=.03,cycle_max_px=.5,template_disagreement_max_px=1),
                    limitations=["Heuristics reject matching failures, not low visibility reliably",
                                 "Seed axes derived from reviewed attachment, not reapproved on archive",
                                 "Upper conductor only; frozen 23 November seed; no reseeding",
                                 "Uses temporal local gradient rule; conditional-gap experiment not integrated"])
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps(dict(frames=len(files),candidates=sum(r["candidate_width_px"]!="" for r in rows),
                          no_measurement=sum(r["status"]=="no_measurement" for r in rows))))
    return rows


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--photos",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--max-frames",type=int,default=8)
    parser.add_argument("--archive-sha",required=True)
    args=parser.parse_args()
    batch(args.photos,args.out,args.max_frames,args.archive_sha)
