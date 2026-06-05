# SkiCheck Pose Lab

Independent high-precision pose validation project for SkiCheck skiing videos.

This lab does not modify the SkiCheck main page, demo mode, feedback prompt, or deployment code. Put real videos under `data/videos/`; that directory is ignored by Git.

## Models

The default config validates:

- MediaPipe Full
- MediaPipe Heavy
- YOLO Pose medium
- RTMPose-l Halpe26 256x192
- RTMPose-m Halpe26 384x288
- RTMPose-l Halpe26 384x288

## Install

Create an environment:

```powershell
cd C:\Users\21407\Desktop\ski\pose-lab
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

RTMPose needs the OpenMMLab stack. Install it only when you want to run RTMPose:

```powershell
pip install -U openmim
mim install mmengine
mim install "mmcv>=2.0.0"
mim install "mmdet>=3.0.0"
pip install -r requirements-rtmpose.txt
```

The RTMPose Body8-Halpe26 config names follow the MMPose model zoo and inferencer alias documentation.

## Test Set

Copy `configs/test_set.example.yaml` to `configs/test_set.yaml`, then fill in at least 12 real skiing videos:

- single close low-speed x 3
- single medium shot x 3
- strong leaning skier x 2
- vertical video x 2
- long shot x 2

Do not commit test videos.

## Run

Run all configured models:

```powershell
$env:PYTHONPATH="src"
python -m pose_lab run --config configs/models.yaml --manifest configs/test_set.yaml --out runs/exp01
```

Run only selected models:

```powershell
$env:PYTHONPATH="src"
python -m pose_lab run --config configs/models.yaml --manifest configs/test_set.yaml --out runs/exp01 --models mediapipe_full,yolo_pose_medium
```

Generate the summary report:

```powershell
$env:PYTHONPATH="src"
python -m pose_lab report --run runs/exp01
```

## Output

Each model/video pair writes:

```text
runs/exp01/<model>/<video_name>/
  debug_pose_overlay.mp4
  metrics.json
  anomaly_frames.json
  sample_frames/
```

The debug video draws only trusted keypoints, shows model name, cumulative valid pose ratio, current core-joint confidence, and highlights abnormal frames in red.
