# Task 3 Part C - Presentation Deck

## Slide 1 - Title
- Monitize Case Study
- Embodied AI with LeRobot, SmolVLA, and Vision-Based Teleoperation
- Presenter: Taylan Dursun
- Date

Speaker note:
- This presentation summarizes the implementation and outcomes of Task 1 and Task 2, and proposes clear next steps for Task 3.

---

## Slide 2 - Problem and System Overview
- Goal: Transfer human intent into robot behavior through learning and perception
- Task 1 focus: Run and evaluate a pretrained Vision-Language-Action policy
- Task 2 focus: Map hand motion from video to robot motion in simulation
- Why it matters: Fast prototyping pipeline for embodied AI workflows
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
- Emphasize that both tasks were approached as end-to-end engineering pipelines, not isolated scripts.

---

## Slide 3 - Task 1: Setup and Results
- Selected checkpoint: lerobot/smolvla_libero
- Dataset alignment: trained on lerobot/libero
- Robot embodiment alignment: Panda
- Evaluation environment: LIBERO (libero_10 suite)
- Key constraint: 4 GB VRAM caused OOM on GPU, stable evaluation done on CPU
- Pipeline successfully executed end-to-end
- Rollouts generated and recorded
- Longer horizons showed clearer, task-related behavior
- Qualitative observation: motion is coherent and non-random, but not perfect in every episode
- Evidence:
  - report/figures/task1_rollout_frame_1.png
  - report/figures/task1_rollout_frame_2.png

Speaker note:
- Highlight why embodiment matching mattered, and explain that short rollouts initially hid the actual behavior quality.

---

## Slide 4 - Task 2: Pipeline and Results
- Step 1: Hand landmarks from video (MediaPipe Tasks)
- Step 2: Wrist trajectory and orientation cue extraction
- Step 3: Relative-motion mapping to VX300s workspace
- Step 4: Jacobian-based damped IK replay in MuJoCo
- Step 5: Side-by-side comparison video generation
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
- Stress that relative mapping improved transfer quality versus direct normalization, and clarify that this is coherent prototype-level transfer rather than exact imitation.

---

## Slide 5 - Technical Challenges and Fixes
- Dependency compatibility issues across MuJoCo, LIBERO, and robosuite stack
- MediaPipe API change handled by migrating to Tasks API
- GPU memory limitation mitigated by CPU fallback for stable evaluation
- Repository cleanup for clarity and onboarding:
  - unnecessary artifacts removed
  - outputs reorganized under task folders

Speaker note:
- This slide demonstrates engineering rigor and troubleshooting depth.

---

## Slide 6 - Conclusion and Next Steps
- Part C objective: clear communication of technical work and outcomes
- Task 1 and Task 2 objectives are completed at prototype level
- End-to-end embodied AI pipeline is operational
- Results are coherent, reproducible, and presentation-ready
- Next development priorities:
  - stronger orientation control
  - improved IK constraints
  - quantitative metrics for imitation quality
- Open to questions

Speaker note:
- Present this as a bridge from prototype success to a more robust future system, then close with questions.
