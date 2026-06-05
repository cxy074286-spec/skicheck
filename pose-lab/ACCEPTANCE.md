# SkiCheck Pose Lab Acceptance Notes

## Project Directory

```text
pose-lab/
  configs/
    models.yaml
    test_set.example.yaml
  src/pose_lab/
    models/
    bbox.py
    cli.py
    config.py
    core_joints.py
    detectors.py
    drawing.py
    metrics.py
    report.py
    runner.py
    video_io.py
  .gitignore
  README.md
  requirements.txt
  requirements-rtmpose.txt
  pyproject.toml
```

## Install Command

```powershell
cd C:\Users\21407\Desktop\ski\pose-lab
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -U openmim
mim install mmengine
mim install "mmcv>=2.0.0"
mim install "mmdet>=3.0.0"
pip install -r requirements-rtmpose.txt
```

## Execute Command

```powershell
Copy-Item configs\test_set.example.yaml configs\test_set.yaml
# Fill configs\test_set.yaml with local, non-Git skiing videos.
$env:PYTHONPATH="src"
python -m pose_lab run --config configs/models.yaml --manifest configs/test_set.yaml --out runs/exp01
python -m pose_lab report --run runs/exp01
```

## Result Table

After running real videos, use:

```text
runs/exp01/summary.md
runs/exp01/model_summary.csv
runs/exp01/metrics.csv
```

These files contain:

- every model's test result table
- every model's valid pose frame ratio
- every model's processing time
- per-video valid/invalid frame counts

## Screenshots

Use images from:

```text
runs/exp01/<model>/<video_name>/sample_frames/
```

Select:

- typical success: `*_ok_*`
- typical failure: `*_bad_*`

## Recommendation Rules

Frontend model:

- Prefer the fastest model whose valid pose ratio is acceptable on close and medium shots.
- If YOLO Pose Medium is stable enough, prefer it for frontend preview because it keeps detector and pose in one family.
- Avoid RTMPose-l in frontend unless the device budget and latency are acceptable.

Backend full-video analysis model:

- Prefer the model with the highest valid pose ratio, low core-joint invalid count, and low large-jump count.
- If RTMPose-l Halpe26 384x288 beats other models on long shot, leaning, feet, and ankle stability, use it for backend full-video analysis.
- The configured RTMPose Body8-Halpe26 variants use MMPose config names such as `rtmpose-l_8xb512-700e_body8-halpe26-384x288`.

Fine-tuning:

- Enter ski-specific fine-tuning if the best model still has low ankle/foot confidence, frequent lower-body jumps, or long-shot failures.
- Do not fine-tune before collecting the 12-video baseline and at least 100 manually reviewed bad frames.
