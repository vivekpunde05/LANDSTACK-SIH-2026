"""Generate small deterministic synthetic aerial-style PNGs for the Phase 3 demo."""
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "datasets" / "satellite"
CASES = {
    "RTN-RAT-0001": "no_change",
    "RTN-RAT-0002": "small_structure",
    "RTN-CHI-0013": "land_cover",
    "RTN-SAN-0019": "vegetation",
}


def base_image(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    height, width = 260, 360
    noise = rng.normal(0, 12, (height, width, 1)).astype(np.float32)
    field = np.zeros((height, width, 3), dtype=np.float32)
    field[:] = (95, 132, 95)  # BGR muted vegetation
    field += noise
    field = cv2.GaussianBlur(field, (0, 0), 4)
    image = np.clip(field, 0, 255).astype(np.uint8)
    # Stable field strips, drainage line, and access track give an aerial texture.
    cv2.rectangle(image, (25, 22), (170, 118), (82, 143, 92), -1)
    cv2.rectangle(image, (178, 24), (334, 112), (105, 151, 91), -1)
    cv2.rectangle(image, (28, 128), (330, 232), (111, 145, 98), -1)
    cv2.line(image, (0, 205), (360, 157), (142, 165, 168), 12)
    cv2.line(image, (0, 205), (360, 157), (190, 198, 190), 4)
    for x, y in rng.integers([35, 35], [330, 220], size=(75, 2)):
        cv2.circle(image, (int(x), int(y)), 2, (58, 112, 62), -1)
    cv2.rectangle(image, (15, 15), (344, 244), (225, 239, 205), 2)
    return image


def changed_image(before: np.ndarray, case: str) -> np.ndarray:
    after = before.copy()
    if case == "small_structure":
        cv2.rectangle(after, (250, 52), (304, 91), (160, 171, 179), -1)
        cv2.rectangle(after, (250, 52), (304, 91), (215, 220, 218), 3)
    elif case == "land_cover":
        polygon = np.array([[205, 125], [326, 122], [320, 199], [216, 210]], dtype=np.int32)
        cv2.fillPoly(after, [polygon], (81, 106, 138))
        for offset in range(0, 100, 18):
            cv2.line(after, (215 + offset, 132), (225 + offset, 201), (100, 125, 151), 3)
    elif case == "vegetation":
        cv2.ellipse(after, (105, 72), (65, 42), -12, 0, 360, (55, 104, 56), -1)
        cv2.ellipse(after, (210, 172), (60, 38), 8, 0, 360, (63, 117, 62), -1)
    return after


def main() -> None:
    for index, (parcel_id, case) in enumerate(CASES.items(), start=1):
        directory = OUTPUT / parcel_id
        directory.mkdir(parents=True, exist_ok=True)
        before = base_image(4100 + index)
        after = changed_image(before, case)
        cv2.imwrite(str(directory / "before.png"), before)
        cv2.imwrite(str(directory / "after.png"), after)
        print(f"generated {parcel_id}: {case}")


if __name__ == "__main__":
    main()
