# Task 3 Part C - Talk Track

## Recommended Duration
- Total: 6 to 8 minutes
- Q and A: 2 to 3 minutes

## Timing by Slide
1. Title: 30 sec
2. Problem and System Overview: 75 sec
3. Task 1 Setup and Results: 90 sec
4. Task 2 Pipeline and Results: 105 sec
5. Challenges and Fixes: 75 sec
6. Conclusion and Next Steps: 45 sec

## Key Message per Slide
- Slide 1: Scope and goal of the presentation
- Slide 2: Why the problem matters and how the overall system is structured
- Slide 3: Why model and embodiment alignment mattered, and what Task 1 showed
- Slide 4: How hand motion was converted into robot motion and what Task 2 achieved
- Slide 5: Engineering issues and concrete fixes
- Slide 6: Final takeaway and future direction

## Demo Insert Points
- After Slide 3:
  - Show rollout snapshots from report figures
- After Slide 4:
  - Show side-by-side video from task2 outputs

## Q and A Preparation
- Why CPU for evaluation instead of GPU?
  - Because 4 GB VRAM caused OOM for stable policy loading.
- Why not include external dependencies directly in repo?
  - To keep clone size small and avoid third-party code duplication.
- Is the motion transfer exact?
  - No, current scope is coherent prototype-level transfer, not exact imitation.
- What is next for better imitation quality?
  - Better orientation modeling, constrained IK, and quantitative metrics.
