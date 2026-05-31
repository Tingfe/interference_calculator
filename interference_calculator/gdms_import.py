# -*- coding: utf-8 -*-
"""Import helpers for GDMS isotope profile exports."""
from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Iterable, List, Optional, Sequence, Tuple


_GDMS_LABEL_RE = re.compile(r'^\s*([A-Z][a-z]?)\{(\d{1,3})\}\s*$')


@dataclass(frozen=True)
class PeakSummary:
    """Summary statistics for one exported isotope profile."""

    point_count: int
    apex_mz: Optional[float]
    apex_intensity: Optional[float]
    centroid_mz: Optional[float]
    fwhm: Optional[float]


@dataclass(frozen=True)
class GDMSProfile:
    """One isotope profile parsed from a GDMS Excel export."""

    label: str
    element: str
    mass_number: int
    isotope: str
    column: int
    point_count: int
    apex_mz: Optional[float]
    apex_intensity: Optional[float]
    centroid_mz: Optional[float]
    fwhm: Optional[float]
    profile_points: Tuple[Tuple[float, float], ...] = ()


def label_to_isotope(label: str) -> Optional[Tuple[str, int, str]]:
    """Convert a GDMS label such as ``Fe{56}`` to ``('Fe', 56, '56Fe')``."""
    match = _GDMS_LABEL_RE.match(str(label or ''))
    if not match:
        return None
    element = match.group(1)
    mass_number = int(match.group(2))
    return element, mass_number, '{}{}'.format(mass_number, element)


def extract_profile_elements(profiles: Sequence[GDMSProfile]) -> List[str]:
    """Return unique elements from parsed profiles, preserving file order."""
    elements = []
    seen = set()
    for profile in profiles:
        if profile.element not in seen:
            seen.add(profile.element)
            elements.append(profile.element)
    return elements


def summarize_profile(masses: Iterable[float], intensities: Iterable[float]) -> PeakSummary:
    """Summarize one isotope scan profile.

    The centroid is calculated from the top 10% intensity region to reduce the
    influence of baseline points in broad GDMS profile exports.
    """
    points = []
    for mass, intensity in zip(masses, intensities):
        mass = _coerce_float(mass)
        intensity = _coerce_float(intensity)
        if mass is None or intensity is None:
            continue
        points.append((mass, intensity))

    if not points:
        return PeakSummary(0, None, None, None, None)

    apex_index, (apex_mz, apex_intensity) = max(
        enumerate(points), key=lambda item: item[1][1]
    )
    if apex_intensity <= 0:
        return PeakSummary(len(points), apex_mz, apex_intensity, None, None)

    threshold = apex_intensity * 0.10
    centroid_points = [(m, y) for m, y in points if y >= threshold and y > 0]
    if not centroid_points:
        centroid_points = [(m, y) for m, y in points if y > 0]
    total_intensity = sum(y for _, y in centroid_points)
    centroid_mz = None
    if total_intensity > 0:
        centroid_mz = sum(m * y for m, y in centroid_points) / total_intensity

    fwhm = _fwhm(points, apex_index, apex_intensity)
    return PeakSummary(len(points), apex_mz, apex_intensity, centroid_mz, fwhm)


def parse_gdms_profile_xlsx(path: str, worksheet: Optional[str] = None) -> List[GDMSProfile]:
    """Parse GDMS Excel profile exports.

    The supported export shape is the profile sheet where row 1 contains isotope
    labels such as ``Fe{56}`` and row 2 contains repeating ``Mass``, ``Values``,
    ``Peaks`` groups.
    """
    try:
        import openpyxl
    except ImportError as exc:
        raise RuntimeError('openpyxl is required to import GDMS Excel profiles') from exc

    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        sheets = [workbook[worksheet]] if worksheet else list(workbook.worksheets)
        profiles = []
        for sheet in sheets:
            profiles.extend(_parse_profile_sheet(sheet))
        return profiles
    finally:
        workbook.close()


def _parse_profile_sheet(sheet) -> List[GDMSProfile]:
    rows = list(sheet.iter_rows(values_only=True))
    if len(rows) < 2:
        return []
    labels = rows[0]
    headers = rows[1]
    profiles = []
    for col in range(len(labels)):
        parsed = label_to_isotope(labels[col])
        if parsed is None:
            continue
        header_mass = str(_row_value(headers, col) or '').strip().lower()
        header_value = str(_row_value(headers, col + 1) or '').strip().lower()
        if header_mass and header_mass != 'mass':
            continue
        if header_value and not header_value.startswith('value'):
            continue

        masses = []
        intensities = []
        for row in rows[2:]:
            mass = _row_value(row, col)
            intensity = _row_value(row, col + 1)
            mass = _coerce_float(mass)
            intensity = _coerce_float(intensity)
            if mass is None or intensity is None:
                continue
            masses.append(mass)
            intensities.append(intensity)

        element, mass_number, isotope = parsed
        summary = summarize_profile(masses, intensities)
        profile_points = tuple(zip(masses, intensities))
        profiles.append(
            GDMSProfile(
                label='{}{{{}}}'.format(element, mass_number),
                element=element,
                mass_number=mass_number,
                isotope=isotope,
                column=col + 1,
                point_count=summary.point_count,
                apex_mz=summary.apex_mz,
                apex_intensity=summary.apex_intensity,
                centroid_mz=summary.centroid_mz,
                fwhm=summary.fwhm,
                profile_points=profile_points,
            )
        )
    return profiles


def _row_value(row, index):
    if index < 0 or index >= len(row):
        return None
    return row[index]


def _coerce_float(value) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        number = float(value)
    else:
        try:
            number = float(str(value).strip().replace(',', ''))
        except ValueError:
            return None
    if not math.isfinite(number):
        return None
    return number


def _fwhm(points: Sequence[Tuple[float, float]], apex_index: int,
          apex_intensity: float) -> Optional[float]:
    if len(points) < 3 or apex_intensity <= 0:
        return None
    half = apex_intensity / 2.0
    left = _crossing(points, apex_index, -1, half)
    right = _crossing(points, apex_index, 1, half)
    if left is None or right is None or right <= left:
        return None
    return right - left


def _crossing(points: Sequence[Tuple[float, float]], start: int,
              step: int, level: float) -> Optional[float]:
    previous_mass, previous_y = points[start]
    index = start + step
    while 0 <= index < len(points):
        mass, y = points[index]
        if y <= level:
            if previous_y == y:
                return mass
            fraction = (level - y) / (previous_y - y)
            return mass + (previous_mass - mass) * fraction
        previous_mass, previous_y = mass, y
        index += step
    return None
