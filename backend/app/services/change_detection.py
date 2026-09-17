"""Explainable classical image differencing for synthetic Phase 3 imagery."""
from pathlib import Path

import cv2
import numpy as np


class ChangeDetectionError(ValueError):
    pass


def _region_label(x: float, y: float, width: int, height: int) -> str:
    vertical = "north" if y < height / 2 else "south"
    horizontal = "west" if x < width / 2 else "east"
    return f"{vertical}-{horizontal} section"


def analyze_change(before_path: Path, after_path: Path, output_dir: Path, parcel_area_hectares: float) -> dict:
    before, after = cv2.imread(str(before_path)), cv2.imread(str(after_path))
    if before is None or after is None:
        raise ChangeDetectionError("One or both imagery files are missing or malformed.")
    if before.shape != after.shape:
        after = cv2.resize(after, (before.shape[1], before.shape[0]), interpolation=cv2.INTER_AREA)

    before_lab = cv2.cvtColor(before, cv2.COLOR_BGR2LAB)
    after_lab = cv2.cvtColor(after, cv2.COLOR_BGR2LAB)
    difference = cv2.absdiff(before_lab, after_lab)
    magnitude = np.max(difference, axis=2)
    magnitude = cv2.GaussianBlur(magnitude, (5, 5), 0)
    _, mask = cv2.threshold(magnitude, 22, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    components, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    clean_mask = np.zeros_like(mask)
    kept = []
    for index in range(1, components):
        if stats[index, cv2.CC_STAT_AREA] >= 60:
            clean_mask[labels == index] = 255
            kept.append(index)

    changed_pixels = int(cv2.countNonZero(clean_mask))
    total_pixels = int(clean_mask.size)
    percentage = round(changed_pixels / total_pixels * 100, 2)
    changed_area = round(parcel_area_hectares * 10000 * percentage / 100, 1)
    if percentage < 1.5:
        status, requires_verification, strength = "No significant change detected", False, "Low"
    elif percentage <= 8:
        status, requires_verification, strength = "Potential change", True, "Moderate"
    else:
        status, requires_verification, strength = "Requires verification", True, "High"

    if kept:
        largest = max(kept, key=lambda i: stats[i, cv2.CC_STAT_AREA])
        main_region = _region_label(*centroids[largest], before.shape[1], before.shape[0])
    else:
        main_region = "No concentrated changed region"

    output_dir.mkdir(parents=True, exist_ok=True)
    mask_path, overlay_path = output_dir / "change-mask.png", output_dir / "change-overlay.png"
    overlay = after.copy()
    tint = np.zeros_like(overlay)
    tint[:, :] = (40, 40, 230)
    changed_overlay = cv2.addWeighted(overlay, 0.5, tint, 0.5, 0)
    overlay[clean_mask > 0] = changed_overlay[clean_mask > 0]
    contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours, -1, (20, 20, 255), 2)
    if not cv2.imwrite(str(mask_path), clean_mask) or not cv2.imwrite(str(overlay_path), overlay):
        raise ChangeDetectionError("Analysis outputs could not be written.")

    observation = "No material visual difference exceeded the demo threshold." if not kept else "Visual structure or land-cover differences exceeded the demo threshold."
    recommendation = "No immediate follow-up indicated by this demo analysis." if not requires_verification else "Human review and field verification are recommended."
    return {
        "changed_area_sqm": changed_area,
        "change_percentage": percentage,
        "change_status": status,
        "change_strength": strength,
        "requires_verification": requires_verification,
        "analysis_method": "Classical image difference (LAB threshold and morphological cleanup)",
        "analysis_explanation": observation,
        "main_changed_region": main_region,
        "recommendation": recommendation,
        "changed_pixels": changed_pixels,
        "total_pixels": total_pixels,
        "mask_path": mask_path,
        "overlay_path": overlay_path,
    }
