import argparse
import json
import time
from pathlib import Path

import cv2
import mujoco
import mujoco.viewer
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description="Replay mapped VX300s end-effector targets in MuJoCo using a simple numerical IK solver.")
    parser.add_argument("--input", required=True, help="Path to vx300s_targets.json")
    parser.add_argument(
        "--scene",
        default="/home/taylan/hand_to_robot/external/mujoco_menagerie/trossen_vx300s/scene.xml",
        help="Path to the VX300s MuJoCo scene XML",
    )
    parser.add_argument("--max-frames", type=int, default=None, help="Optional cap on number of replayed frames")
    parser.add_argument("--ik-iters", type=int, default=25, help="Maximum IK iterations per frame")
    parser.add_argument("--ik-step-scale", type=float, default=0.6, help="Scale factor for IK updates")
    parser.add_argument("--ik-damping", type=float, default=1e-3, help="Damping factor for pseudoinverse IK")
    parser.add_argument("--sleep", type=float, default=None, help="Optional fixed sleep time between rendered frames; overrides timestamp-based timing")
    parser.add_argument("--playback-speed", type=float, default=1.0, help="Playback speed multiplier. Values < 1.0 slow the motion down, values > 1.0 speed it up")
    parser.add_argument("--record-video", type=str, default=None, help="Optional output path for saving the robot replay as an mp4 video")
    parser.add_argument("--video-width", type=int, default=848, help="Recorded video width")
    parser.add_argument("--video-height", type=int, default=478, help="Recorded video height")
    parser.add_argument("--camera", type=str, default="closeup", help="Named MuJoCo camera to use for rendering and viewer framing")
    parser.add_argument("--headless", action="store_true", help="Run without opening the interactive viewer")
    return parser.parse_args()


def load_targets(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload


def solve_position_ik(model, data, site_id, target_pos, joint_slice, max_iters=25, step_scale=0.6, damping=1e-3):
    jacp = np.zeros((3, model.nv))
    jacr = np.zeros((3, model.nv))

    for _ in range(max_iters):
        mujoco.mj_forward(model, data)
        current_pos = data.site_xpos[site_id].copy()
        error = target_pos - current_pos
        if np.linalg.norm(error) < 1e-3:
            break

        mujoco.mj_jacSite(model, data, jacp, jacr, site_id)
        jac = jacp[:, joint_slice]
        jjt = jac @ jac.T
        dq = jac.T @ np.linalg.solve(jjt + damping * np.eye(3), error)
        data.qpos[joint_slice] += step_scale * dq


def apply_controls_from_qpos(data):
    # Actuator order in the Menagerie XML:
    # waist, shoulder, elbow, forearm_roll, wrist_angle, wrist_rotate, gripper
    data.ctrl[0] = data.qpos[0]
    data.ctrl[1] = data.qpos[1]
    data.ctrl[2] = data.qpos[2]
    data.ctrl[3] = data.qpos[3]
    data.ctrl[4] = data.qpos[4]
    data.ctrl[5] = data.qpos[5]
    data.ctrl[6] = data.qpos[6]


def replay_targets(model, data, targets, args, viewer=None, renderer=None, writer=None, output_fps=None, camera_name=None):
    site_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "pinch")
    joint_slice = slice(0, 5)

    processed = 0
    previous_time_s = None
    for row in targets:
        if args.max_frames is not None and processed >= args.max_frames:
            break

        if not row["detected"] or row["target_x_m"] is None:
            continue

        target_pos = np.array([row["target_x_m"], row["target_y_m"], row["target_z_m"]], dtype=np.float64)

        solve_position_ik(
            model,
            data,
            site_id,
            target_pos,
            joint_slice,
            max_iters=args.ik_iters,
            step_scale=args.ik_step_scale,
            damping=args.ik_damping,
        )

        # Apply wrist rotate and keep the gripper slightly open.
        if row["target_wrist_rotate_rad"] is not None:
            data.qpos[5] = row["target_wrist_rotate_rad"]
        data.qpos[6] = row.get("target_gripper", 0.024)
        data.qpos[7] = -data.qpos[6]

        apply_controls_from_qpos(data)
        mujoco.mj_step(model, data)

        current_time_s = row.get("time_s")

        if renderer is not None and writer is not None and output_fps is not None:
            if camera_name:
                renderer.update_scene(data, camera=camera_name)
            else:
                renderer.update_scene(data)
            frame = renderer.render()
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            if previous_time_s is None or current_time_s is None:
                repeat_count = 1
            else:
                dt = max(0.0, current_time_s - previous_time_s)
                speed = max(args.playback_speed, 1e-6)
                repeat_count = max(1, int(round((dt / speed) * output_fps)))
            for _ in range(repeat_count):
                writer.write(frame_bgr)

        if viewer is not None:
            viewer.sync()
            if args.sleep is not None:
                time.sleep(args.sleep)
            else:
                if previous_time_s is not None and current_time_s is not None:
                    dt = max(0.0, current_time_s - previous_time_s)
                    speed = max(args.playback_speed, 1e-6)
                    time.sleep(dt / speed)

        previous_time_s = current_time_s

        processed += 1

    return processed


def main():
    args = parse_args()
    payload = load_targets(Path(args.input))
    targets = payload["targets"]
    source_fps = payload.get("metadata", {}).get("source_metadata", {}).get("fps", 30.0)

    model = mujoco.MjModel.from_xml_path(args.scene)
    data = mujoco.MjData(model)
    camera_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_CAMERA, args.camera) if args.camera else -1
    camera_name = args.camera if camera_id != -1 else None

    # Start from the home keyframe when available.
    if model.nkey > 0:
        mujoco.mj_resetDataKeyframe(model, data, 0)
    else:
        mujoco.mj_resetData(model, data)

    renderer = None
    writer = None
    if args.record_video:
        record_path = Path(args.record_video)
        record_path.parent.mkdir(parents=True, exist_ok=True)
        renderer = mujoco.Renderer(model, height=args.video_height, width=args.video_width)
        writer = cv2.VideoWriter(
            str(record_path),
            cv2.VideoWriter_fourcc(*"mp4v"),
            float(source_fps),
            (args.video_width, args.video_height),
        )

    if args.headless:
        processed = replay_targets(model, data, targets, args, viewer=None, renderer=renderer, writer=writer, output_fps=float(source_fps), camera_name=camera_name)
    else:
        with mujoco.viewer.launch_passive(model, data) as viewer:
            if camera_id != -1:
                viewer.cam.type = mujoco.mjtCamera.mjCAMERA_FIXED
                viewer.cam.fixedcamid = camera_id
            processed = replay_targets(model, data, targets, args, viewer=viewer, renderer=renderer, writer=writer, output_fps=float(source_fps), camera_name=camera_name)

    if writer is not None:
        writer.release()
    if renderer is not None and hasattr(renderer, "close"):
        renderer.close()

    pinch_site = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "pinch")
    print(f"Processed target frames: {processed}")
    print("Final pinch position:", data.site_xpos[pinch_site])
    print("Final joint qpos:", data.qpos[:8])
    if args.record_video:
        print(f"Recorded video: {args.record_video}")


if __name__ == "__main__":
    main()