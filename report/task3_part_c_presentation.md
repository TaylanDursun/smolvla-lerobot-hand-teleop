# Task 3 Part C - Presentation Deck

## Slide 1 - Title
- Monitize Case Study
- Embodied AI with LeRobot, SmolVLA, and Vision-Based Teleoperation
- Presenter: Taylan Dursun
- Date

Speaker note:
- This presentation summarizes the implementation and outcomes of Task 1 and Task 2, and proposes clear next steps for Task 3.

---

## Slide 2 - Problem Statement
- Goal: Transfer human intent into robot behavior through learning and perception
- Task 1 focus: Run and evaluate a pretrained Vision-Language-Action policy
- Task 2 focus: Map hand motion from video to robot motion in simulation
- Why it matters: Fast prototyping pipeline for embodied AI workflows

Speaker note:
- Emphasize that both tasks were approached as end-to-end engineering pipelines, not isolated scripts.

---

## Slide 3 - System Overview
- Input sources:
  - Task 1: LIBERO observations plus robot state
  - Task 2: First-person hand video
- Core modules:
  - Policy inference with LeRobot and SmolVLA
  - Landmark extraction and trajectory processing
  - Motion mapping and inverse kinematics replay
- Output artifacts:
  - Evaluation videos
  - Robot replay videos
  - Side-by-side comparison video

Speaker note:
- Mention reproducibility: environment files and script-based pipeline are available.

---

## Slide 4 - Task 1 Setup and Model Choice
- Selected checkpoint: lerobot/smolvla_libero
- Dataset alignment: trained on lerobot/libero
- Robot embodiment alignment: Panda
- Evaluation environment: LIBERO (libero_10 suite)
- Key constraint: 4 GB VRAM caused OOM on GPU, stable evaluation done on CPU

Speaker note:
- Highlight why embodiment matching was critical for coherent behavior.

---

## Slide 5 - Task 1 Results
- Pipeline successfully executed end-to-end
- Rollouts generated and recorded
- Longer horizons showed clearer, task-related behavior
- Qualitative observation:
  - Not perfect success in all episodes
  - Motion is coherent and non-random
- Evidence:
  - report/figures/task1_rollout_frame_1.png
  - report/figures/task1_rollout_frame_2.png

Speaker note:
- Explain that short rollouts can mislead interpretation of policy quality.

---

## Slide 6 - Task 2 Pipeline
- Step 1: Hand landmarks from video (MediaPipe Tasks)
- Step 2: Wrist trajectory and orientation cue extraction
- Step 3: Relative-motion mapping to VX300s workspace
- Step 4: Jacobian-based damped IK replay in MuJoCo
- Step 5: Side-by-side comparison video generation

Speaker note:
- Stress that relative mapping improved transfer quality versus direct normalization.

---

## Slide 7 - Task 2 Results
- Target behavior: lifting plus pouring-like wrist rotation
- Improvements achieved:
  - Orientation-aware mapping
  - Better replay timing with playback-speed 0.85
  - Better camera framing for evaluation
- Final outputs:
  - vx300s_targets.json and csv
  - vx300s_replay.mp4
  - pouring_side_by_side.mp4

Speaker note:
- Clarify that this is a coherent prototype, not exact kinematic imitation.

---

## Slide 8 - Technical Challenges and Fixes
- Dependency compatibility issues across MuJoCo, LIBERO, and robosuite stack
- MediaPipe API change handled by migrating to Tasks API
- GPU memory limitation mitigated by CPU fallback for stable evaluation
- Repository cleanup for clarity and onboarding:
  - unnecessary artifacts removed
  - outputs reorganized under task folders

Speaker note:
- This slide demonstrates engineering rigor and troubleshooting depth.

---

## Slide 9 - Task 3 Plan and Part C Positioning
- Part C objective: clear communication of technical work and outcomes
- Presentation deliverables prepared:
  - concise technical narrative
  - evidence-driven visuals
  - reproducibility and roadmap
- Next development priorities:
  - stronger orientation control
  - improved IK constraints
  - quantitative metrics for imitation quality

Speaker note:
- Present this as a bridge from prototype success to robust system design.

---

## Slide 10 - Conclusion
- Task 1 and Task 2 objectives are completed at prototype level
- End-to-end embodied AI pipeline is operational
- Results are coherent, reproducible, and presentation-ready
- Open to questions

Speaker note:
- Close with confidence and invite discussion around scaling and evaluation metrics.
