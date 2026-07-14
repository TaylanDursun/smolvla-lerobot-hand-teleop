# Task 3 Part C - Talk Track

## Recommended Duration
- Total: 8 to 10 minutes
- Q and A: 2 to 3 minutes

## Timing by Slide
1. Title: 30 sec
2. Problem Statement: 45 sec
3. System Overview: 60 sec
4. Task 1 Setup: 75 sec
5. Task 1 Results: 75 sec
6. Task 2 Pipeline: 75 sec
7. Task 2 Results: 90 sec
8. Challenges and Fixes: 75 sec
9. Task 3 Roadmap: 60 sec
10. Conclusion: 30 sec

## Key Message per Slide
- Slide 1: Scope and goal of the presentation
- Slide 2: Why this problem is relevant in embodied AI
- Slide 3: End-to-end architecture view
- Slide 4: Why model and embodiment alignment mattered
- Slide 5: What worked and what was limited in Task 1
- Slide 6: How human hand motion was converted into robot motion
- Slide 7: Qualitative success criteria and final outputs
- Slide 8: Engineering issues and concrete fixes
- Slide 9: What Part C communicates and what comes next
- Slide 10: Final takeaway and confidence statement

## Demo Insert Points
- After Slide 5:
  - Show rollout snapshots from report figures
- After Slide 7:
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
