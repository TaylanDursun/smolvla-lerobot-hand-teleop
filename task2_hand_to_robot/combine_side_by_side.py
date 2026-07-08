import argparse
from pathlib import Path

import cv2
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description="Combine reference and robot replay videos side by side.")
    parser.add_argument("--left", required=True, help="Path to the reference video")
    parser.add_argument("--right", required=True, help="Path to the robot replay video")
    parser.add_argument("--output", required=True, help="Path to the combined output video")
    parser.add_argument("--label-left", default="Reference Hand Motion")
    parser.add_argument("--label-right", default="VX300s Replay")
    return parser.parse_args()


def add_label(frame, text):
    labeled = frame.copy()
    cv2.rectangle(labeled, (10, 10), (320, 46), (20, 20, 20), -1)
    cv2.putText(labeled, text, (18, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (240, 240, 240), 2, cv2.LINE_AA)
    return labeled


def resize_to_height(frame, height):
    h, w = frame.shape[:2]
    if h == height:
        return frame
    scale = height / h
    new_w = int(round(w * scale))
    return cv2.resize(frame, (new_w, height), interpolation=cv2.INTER_LINEAR)


def main():
    args = parse_args()
    left_cap = cv2.VideoCapture(args.left)
    right_cap = cv2.VideoCapture(args.right)

    if not left_cap.isOpened():
        raise RuntimeError(f"Could not open left video: {args.left}")
    if not right_cap.isOpened():
        raise RuntimeError(f"Could not open right video: {args.right}")

    left_fps = left_cap.get(cv2.CAP_PROP_FPS) or 30.0
    right_fps = right_cap.get(cv2.CAP_PROP_FPS) or left_fps
    out_fps = min(left_fps, right_fps)

    ok_left, left_frame = left_cap.read()
    ok_right, right_frame = right_cap.read()
    if not ok_left or not ok_right:
        raise RuntimeError("Could not read initial frames from both videos")

    target_height = min(left_frame.shape[0], right_frame.shape[0])
    left_frame = resize_to_height(left_frame, target_height)
    right_frame = resize_to_height(right_frame, target_height)
    left_frame = add_label(left_frame, args.label_left)
    right_frame = add_label(right_frame, args.label_right)
    combined = np.hstack([left_frame, right_frame])

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        out_fps,
        (combined.shape[1], combined.shape[0]),
    )
    writer.write(combined)

    while True:
        ok_left, left_frame = left_cap.read()
        ok_right, right_frame = right_cap.read()
        if not ok_left or not ok_right:
            break
        left_frame = add_label(resize_to_height(left_frame, target_height), args.label_left)
        right_frame = add_label(resize_to_height(right_frame, target_height), args.label_right)
        writer.write(np.hstack([left_frame, right_frame]))

    left_cap.release()
    right_cap.release()
    writer.release()
    print(f"Combined video: {output_path}")


if __name__ == "__main__":
    main()