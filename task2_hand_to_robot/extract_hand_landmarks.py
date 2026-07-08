import argparse
import json
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"


def parse_args():
    parser = argparse.ArgumentParser(description="Extract hand landmarks from a video using MediaPipe Hands.")
    parser.add_argument("--input", required=True, help="Path to the input video.")
    parser.add_argument("--output-dir", required=True, help="Directory where outputs will be written.")
    parser.add_argument("--max-frames", type=int, default=None, help="Optional limit on processed frames.")
    parser.add_argument("--min-detection-confidence", type=float, default=0.5)
    parser.add_argument("--min-tracking-confidence", type=float, default=0.5)
    return parser.parse_args()


def landmark_to_dict(landmark):
    return {"x": landmark.x, "y": landmark.y, "z": landmark.z}


def ensure_model(output_dir: Path) -> Path:
    model_path = output_dir / "hand_landmarker.task"
    if model_path.exists():
        return model_path
    urllib.request.urlretrieve(MODEL_URL, model_path)
    return model_path


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    capture = cv2.VideoCapture(str(input_path))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open input video: {input_path}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    annotated_video_path = output_dir / "annotated_hands.mp4"
    writer = cv2.VideoWriter(
        str(annotated_video_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    model_path = ensure_model(output_dir)

    base_options = python.BaseOptions(model_asset_path=str(model_path))
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=args.min_detection_confidence,
        min_tracking_confidence=args.min_tracking_confidence,
        min_hand_presence_confidence=args.min_tracking_confidence,
    )

    frame_results = []
    frame_index = 0

    with vision.HandLandmarker.create_from_options(options) as hands:
        while True:
            ok, frame = capture.read()
            if not ok:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp_ms = int((frame_index / fps) * 1000)
            result = hands.detect_for_video(mp_image, timestamp_ms)

            frame_record = {"frame_index": frame_index, "hands": []}

            if result.hand_landmarks:
                for hand_landmarks in result.hand_landmarks:
                    frame_record["hands"].append(
                        {
                            "landmarks": [landmark_to_dict(lm) for lm in hand_landmarks]
                        }
                    )
                    for landmark in hand_landmarks:
                        x = int(landmark.x * width)
                        y = int(landmark.y * height)
                        cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

            frame_results.append(frame_record)
            writer.write(frame)

            frame_index += 1
            if args.max_frames is not None and frame_index >= args.max_frames:
                break

    capture.release()
    writer.release()

    metadata = {
        "input_video": str(input_path),
        "annotated_video": str(annotated_video_path),
        "model_path": str(model_path),
        "fps": fps,
        "frame_width": width,
        "frame_height": height,
        "num_frames": frame_index,
    }

    with open(output_dir / "landmarks.json", "w", encoding="utf-8") as f:
        json.dump({"metadata": metadata, "frames": frame_results}, f, indent=2)

    print(f"Processed frames: {frame_index}")
    print(f"Annotated video: {annotated_video_path}")
    print(f"Landmarks JSON: {output_dir / 'landmarks.json'}")


if __name__ == "__main__":
    main()