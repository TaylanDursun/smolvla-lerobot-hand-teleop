# hand_to_robot

This repository transfers hand motion from video to robot end-effector targets and replays the motion in MuJoCo.

## Project Structure

- `task2_hand_to_robot/`: Task 2 pipeline scripts
- `task1_smolvla_lerobot/`: Task 1 outputs and related files
- `report/`: LaTeX report sources
- `environment.yml`, `environment_full.yml`: environment definitions
- `requirements_lock.txt`: pinned pip package list

## Quick Start

Run all commands from the repository root.

### 1) Clone the repository

```bash
git clone <REPO_URL>
cd hand_to_robot
```

### 2) Create and activate the conda environment

Preferred:

```bash
conda env create -f environment_full.yml -n hand2robot
conda activate hand2robot
```

Alternative:

```bash
conda create -n hand2robot python=3.10 -y
conda activate hand2robot
pip install -r requirements_lock.txt
```

### 3) Download external dependencies

If `external/` is not included in your clone, fetch only what is needed:

```bash
mkdir -p external
git clone --depth 1 https://github.com/google-deepmind/mujoco_menagerie.git external/mujoco_menagerie
git clone --depth 1 https://github.com/Lifelong-Robot-Learning/LIBERO.git external/LIBERO
```

## Task 2: End-to-End Run

Example input video: `task2_hand_to_robot/pouring.mp4`

### 1) Extract hand landmarks

```bash
python task2_hand_to_robot/extract_hand_landmarks.py \
  --input task2_hand_to_robot/pouring.mp4 \
  --output-dir task2_hand_to_robot/outputs/pouring_run_01_full
```

### 2) Extract wrist trajectory

```bash
python task2_hand_to_robot/extract_wrist_trajectory.py \
  --input task2_hand_to_robot/outputs/pouring_run_01_full/landmarks.json \
  --output-dir task2_hand_to_robot/outputs/pouring_run_01_full_wrist_v2
```

### 3) Map trajectory to VX300s targets

```bash
python task2_hand_to_robot/map_wrist_to_vx300s_targets.py \
  --input task2_hand_to_robot/outputs/pouring_run_01_full_wrist_v2/wrist_trajectory.json \
  --output-dir task2_hand_to_robot/outputs/pouring_run_01_full_targets_v2
```

### 4) Replay in MuJoCo and record video

```bash
python task2_hand_to_robot/replay_vx300s_targets.py \
  --input task2_hand_to_robot/outputs/pouring_run_01_full_targets_v2/vx300s_targets.json \
  --scene external/mujoco_menagerie/trossen_vx300s/scene.xml \
  --headless \
  --playback-speed 0.85 \
  --record-video task2_hand_to_robot/outputs/pouring_run_01_full_targets_v2/vx300s_replay.mp4
```

### 5) Combine reference and replay videos side by side

```bash
python task2_hand_to_robot/combine_side_by_side.py \
  --left task2_hand_to_robot/pouring.mp4 \
  --right task2_hand_to_robot/outputs/pouring_run_01_full_targets_v2/vx300s_replay.mp4 \
  --output task2_hand_to_robot/outputs/pouring_run_01_full_targets_v2/pouring_side_by_side.mp4
```

## Expected Outputs

After a successful run, these files are generated:

- `task2_hand_to_robot/outputs/pouring_run_01_full/landmarks.json`
- `task2_hand_to_robot/outputs/pouring_run_01_full_wrist_v2/wrist_trajectory.json`
- `task2_hand_to_robot/outputs/pouring_run_01_full_targets_v2/vx300s_targets.json`
- `task2_hand_to_robot/outputs/pouring_run_01_full_targets_v2/vx300s_replay.mp4`
- `task2_hand_to_robot/outputs/pouring_run_01_full_targets_v2/pouring_side_by_side.mp4`

## Versioning Policy

- `report/`: recommended to keep tracked (source of final deliverable).
- `external/`: recommended to keep ignored (large third-party dependencies, slower clones, noisy diffs).

## Notes

- GPU is not required; the pipeline can run on CPU.
- If your MuJoCo scene path differs, pass the correct XML path with `--scene`.

## Task 3 Part C Presentation Assets

- Slide deck outline: `report/task3_part_c_presentation.md`
- Speaker notes and timing plan: `report/task3_part_c_talk_track.md`
