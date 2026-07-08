import argparse
import csv
import json
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Map wrist trajectory to VX300s end-effector targets.")
    parser.add_argument("--input", required=True, help="Path to wrist_trajectory.json")
    parser.add_argument("--output-dir", required=True, help="Directory where mapped targets will be written")
    parser.add_argument("--x-center", type=float, default=0.24, help="Robot workspace center x in meters")
    parser.add_argument("--y-center", type=float, default=0.0, help="Robot workspace center y in meters")
    parser.add_argument("--z-center", type=float, default=0.22, help="Robot workspace center z in meters")
    parser.add_argument("--x-range", type=float, default=0.12, help="Robot workspace range in x")
    parser.add_argument("--y-range", type=float, default=0.20, help="Robot workspace range in y")
    parser.add_argument("--z-range", type=float, default=0.16, help="Robot workspace range in z")
    parser.add_argument("--pour-scale", type=float, default=0.8, help="Scale factor for mapping hand pour angle to robot wrist rotation")
    parser.add_argument("--yaw-scale", type=float, default=0.7, help="Scale factor for mapping palm axis yaw to robot wrist rotation")
    return parser.parse_args()


def min_max_scale(value, lower, upper, out_min, out_max):
    if upper - lower == 0:
        return (out_min + out_max) / 2.0
    alpha = (value - lower) / (upper - lower)
    return out_min + alpha * (out_max - out_min)


def clamp(value, low, high):
    return max(low, min(high, value))


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    trajectory = payload["trajectory"]
    detected = [row for row in trajectory if row["detected"] and row["wrist_x_smooth"] is not None]
    if not detected:
        raise RuntimeError("No detected wrist frames found in the trajectory input")

    x_values = [row["wrist_x_smooth"] for row in detected]
    y_values = [row["wrist_y_smooth"] for row in detected]
    z_values = [row["wrist_z_smooth"] for row in detected]
    pour_values = [row["pour_angle_rad_smooth"] for row in detected]
    palm_yaw_values = [row["palm_axis_angle_rad_smooth"] for row in detected]

    wrist_x_min, wrist_x_max = min(x_values), max(x_values)
    wrist_y_min, wrist_y_max = min(y_values), max(y_values)
    wrist_z_min, wrist_z_max = min(z_values), max(z_values)
    x_span = max(wrist_x_max - wrist_x_min, 1e-6)
    y_span = max(wrist_y_max - wrist_y_min, 1e-6)
    z_span = max(wrist_z_max - wrist_z_min, 1e-6)

    pour_ref = pour_values[0]
    palm_yaw_ref = palm_yaw_values[0]
    ref = detected[0]

    mapped = []
    for row in trajectory:
        mapped_row = {
            "frame_index": row["frame_index"],
            "time_s": row["time_s"],
            "detected": row["detected"],
            "target_x_m": None,
            "target_y_m": None,
            "target_z_m": None,
            "target_wrist_rotate_rad": None,
            "target_gripper": 0.024,
        }

        if row["detected"] and row["wrist_x_smooth"] is not None:
            dx_img = row["wrist_x_smooth"] - ref["wrist_x_smooth"]
            dy_img = row["wrist_y_smooth"] - ref["wrist_y_smooth"]
            dz_img = row["wrist_z_smooth"] - ref["wrist_z_smooth"]

            # Relative mapping behaves more like motion transfer than absolute min/max anchoring.
            target_y = args.y_center + (dx_img / x_span) * args.y_range
            target_z = args.z_center - (dy_img / y_span) * args.z_range
            target_x = args.x_center + (dz_img / z_span) * args.x_range

            pour_component = (row["pour_angle_rad_smooth"] - pour_ref) * args.pour_scale
            yaw_component = (row["palm_axis_angle_rad_smooth"] - palm_yaw_ref) * args.yaw_scale
            wrist_rotate = pour_component + 0.5 * yaw_component

            mapped_row.update(
                {
                    "target_x_m": round(clamp(target_x, args.x_center - args.x_range / 2, args.x_center + args.x_range / 2), 6),
                    "target_y_m": round(clamp(target_y, args.y_center - args.y_range / 2, args.y_center + args.y_range / 2), 6),
                    "target_z_m": round(clamp(target_z, 0.08, 0.38), 6),
                    "target_wrist_rotate_rad": round(clamp(wrist_rotate, -1.5, 1.5), 6),
                }
            )

        mapped.append(mapped_row)

    metadata = {
        "source_metadata": payload.get("metadata", {}),
        "mapping": {
            "x_center": args.x_center,
            "y_center": args.y_center,
            "z_center": args.z_center,
            "x_range": args.x_range,
            "y_range": args.y_range,
            "z_range": args.z_range,
            "pour_scale": args.pour_scale,
            "yaw_scale": args.yaw_scale,
        },
    }

    json_output = output_dir / "vx300s_targets.json"
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump({"metadata": metadata, "targets": mapped}, f, indent=2)

    csv_output = output_dir / "vx300s_targets.csv"
    fieldnames = list(mapped[0].keys()) if mapped else []
    with open(csv_output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(mapped)

    print(f"Frames mapped: {len(mapped)}")
    print(f"Detected mapped frames: {sum(1 for row in mapped if row['detected'])}")
    print(f"Targets JSON: {json_output}")
    print(f"Targets CSV: {csv_output}")


if __name__ == "__main__":
    main()