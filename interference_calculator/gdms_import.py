# -*- coding: utf-8 -*-
"""Import helpers for GDMS isotope profile exports."""
from __future__ import annotations

from dataclasses import dataclass
import math
import re
import struct
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


_GDMS_LABEL_RE = re.compile(r'^\s*([A-Z][a-z]?)\{(\d{1,3})\}\s*$')


class GDMSImportDependencyError(RuntimeError):
    """Raised when an optional importer dependency is missing."""


class GDMSImportFormatError(ValueError):
    """Raised when a GDMS profile file cannot be parsed."""


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
    """One isotope profile parsed from a GDMS profile export."""

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
    natural_abundance: Optional[float] = None


@dataclass(frozen=True)
class GDMSRun:
    """One run parsed from a GD90Trace TRR file."""

    index: int
    name: str
    sample_id: str
    sample_for: str
    profiles: Tuple[GDMSProfile, ...]


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


def parse_gdms_profile_file(path: str) -> List[GDMSProfile]:
    """Parse a supported GDMS profile file by extension."""
    suffix = str(path).lower().rsplit('.', 1)[-1] if '.' in str(path) else ''
    if suffix == 'trr':
        return parse_gdms_profile_trr(path)
    if suffix == 'gdr':
        return parse_gdms_profile_gdr(path)
    return parse_gdms_profile_xlsx(path)


def parse_gdms_profile_xlsx(path: str, worksheet: Optional[str] = None) -> List[GDMSProfile]:
    """Parse GDMS Excel profile exports.

    The supported export shape is the profile sheet where row 1 contains isotope
    labels such as ``Fe{56}`` and row 2 contains repeating ``Mass``, ``Values``,
    ``Peaks`` groups.
    """
    try:
        import openpyxl
    except ImportError as exc:
        raise GDMSImportDependencyError(
            'openpyxl is required to import GDMS Excel profiles'
        ) from exc

    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        sheets = [workbook[worksheet]] if worksheet else list(workbook.worksheets)
        profiles = []
        for sheet in sheets:
            profiles.extend(_parse_profile_sheet(sheet))
        return profiles
    finally:
        workbook.close()


def parse_gdms_profile_trr(path: str, run_index: int = 0) -> List[GDMSProfile]:
    """Parse a GD90Trace ``.TRR`` raw run file.

    TRR files are .NET BinaryFormatter payloads containing
    ``GD90Trace.GDExperimentRunsV2``. This reader implements only the NRBF
    records needed for read-only GDMS import and never executes .NET code.
    """
    runs = parse_gdms_raw_runs(path)
    if not runs:
        return []
    if run_index < 0 or run_index >= len(runs):
        raise GDMSImportFormatError('TRR run index is out of range.')
    return list(runs[run_index].profiles)


def parse_gdms_profile_gdr(path: str, run_index: int = 0) -> List[GDMSProfile]:
    """Parse an Elsima ``.GDR`` raw run file."""
    runs = parse_gdms_raw_runs(path)
    if not runs:
        return []
    if run_index < 0 or run_index >= len(runs):
        raise GDMSImportFormatError('GDR run index is out of range.')
    return list(runs[run_index].profiles)


def parse_gdms_trr_runs(path: str) -> List[GDMSRun]:
    """Parse all runs from a GD90Trace ``.TRR`` raw run file."""
    return parse_gdms_raw_runs(path)


def parse_gdms_gdr_runs(path: str) -> List[GDMSRun]:
    """Parse all runs from an Elsima ``.GDR`` raw run file."""
    return parse_gdms_raw_runs(path)


def parse_gdms_raw_runs(path: str) -> List[GDMSRun]:
    """Parse all runs from a supported GDMS raw run file."""
    with open(path, 'rb') as handle:
        data = handle.read()
    if b'GD90Trace' not in data[:4096] and b'Elsima' not in data[:4096]:
        raise GDMSImportFormatError('This file does not look like a supported GDMS raw file.')

    reader = _NRBFReader(data)
    root_id = reader.read_stream()
    root = _nrbf_deref(reader.objects.get(root_id), reader.objects)
    root_class = root.get('class_name') if isinstance(root, dict) else ''
    if root_class not in ('GD90Trace.GDExperimentRunsV2', 'Elsima.GDExperimentRuns'):
        raise GDMSImportFormatError('Unsupported GDMS raw root object.')

    run_objects = _nrbf_list_items(root.get('values', {}).get('m_ExperimentRuns'), reader.objects)
    runs = []
    for index, run in enumerate(run_objects):
        if not isinstance(run, dict):
            continue
        values = run.get('values', {})
        components = _nrbf_list_items(values.get('m_GDAnalysisComponents'), reader.objects)
        profiles = _profiles_from_trr_components(components, reader.objects)
        name = _string_or_empty(_nrbf_scalar(values.get('m_ExperimentName'), reader.objects))
        sample_id = _string_or_empty(_nrbf_scalar(values.get('m_SampleID'), reader.objects))
        sample_for = _string_or_empty(_nrbf_scalar(values.get('m_SampleFor'), reader.objects))
        runs.append(
            GDMSRun(
                index=index,
                name=name,
                sample_id=sample_id,
                sample_for=sample_for,
                profiles=tuple(profiles),
            )
        )
    return runs


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


def _profiles_from_trr_components(
    components: Sequence[Dict[str, Any]],
    objects: Dict[int, Any],
) -> List[GDMSProfile]:
    profiles = []
    for index, component in enumerate(components):
        values = component.get('values', {}) if isinstance(component, dict) else {}
        label = _nrbf_scalar(values.get('m_ComponentName'), objects)
        parsed = label_to_isotope(str(label or ''))
        if parsed is None:
            continue

        masses = _nrbf_array_values(values.get('m_Mass'), objects)
        current_values = _nrbf_array_values(values.get('m_Current'), objects)
        ic_values = _nrbf_array_values(values.get('m_ICValues'), objects)
        intensities = current_values
        if _max_finite(current_values) <= 0 and _max_finite(ic_values) > 0:
            intensities = ic_values

        points = []
        clean_masses = []
        clean_intensities = []
        for mass, intensity in zip(masses, intensities):
            mass = _coerce_float(mass)
            intensity = _coerce_float(intensity)
            if mass is None or intensity is None:
                continue
            points.append((mass, intensity))
            clean_masses.append(mass)
            clean_intensities.append(intensity)

        element, mass_number, isotope = parsed
        summary = summarize_profile(clean_masses, clean_intensities)
        observed_mz = _coerce_float(_nrbf_scalar(values.get('m_CentroidMassValue'), objects))
        stored_peak = _coerce_float(_nrbf_scalar(values.get('m_PeakValue'), objects))
        natural_abundance = _trr_percent_abundance(
            _coerce_float(_nrbf_scalar(values.get('m_Abundancy'), objects))
        )

        centroid_mz = observed_mz if observed_mz is not None else summary.centroid_mz
        apex_mz = summary.apex_mz
        apex_intensity = summary.apex_intensity
        if apex_mz is None and observed_mz is not None:
            apex_mz = observed_mz
        if apex_intensity is None and stored_peak is not None:
            apex_intensity = stored_peak

        profiles.append(
            GDMSProfile(
                label='{}{{{}}}'.format(element, mass_number),
                element=element,
                mass_number=mass_number,
                isotope=isotope,
                column=index + 1,
                point_count=summary.point_count,
                apex_mz=apex_mz,
                apex_intensity=apex_intensity,
                centroid_mz=centroid_mz,
                fwhm=summary.fwhm,
                profile_points=tuple(points),
                natural_abundance=natural_abundance,
            )
        )
    return profiles


def _trr_percent_abundance(value: Optional[float]) -> Optional[float]:
    if value is None or value < 0:
        return None
    return value / 100.0


def _string_or_empty(value: Any) -> str:
    if value is None:
        return ''
    return str(value)


def _max_finite(values: Sequence[Any]) -> float:
    maximum = 0.0
    for value in values:
        value = _coerce_float(value)
        if value is not None and value > maximum:
            maximum = value
    return maximum


def _nrbf_is_class(value: Any, class_name: str) -> bool:
    return isinstance(value, dict) and value.get('class_name') == class_name


def _nrbf_scalar(value: Any, objects: Dict[int, Any]) -> Any:
    value = _nrbf_deref(value, objects)
    if isinstance(value, dict) and value.get('kind') == 'primitive':
        return value.get('value')
    return value


def _nrbf_array_values(value: Any, objects: Dict[int, Any]) -> List[Any]:
    value = _nrbf_deref(value, objects)
    if isinstance(value, dict) and value.get('kind') == 'array':
        return [_nrbf_scalar(item, objects) for item in value.get('values', [])]
    return []


def _nrbf_list_items(value: Any, objects: Dict[int, Any]) -> List[Any]:
    value = _nrbf_deref(value, objects)
    if not isinstance(value, dict):
        return []
    values = value.get('values', {})
    items = _nrbf_deref(values.get('_items'), objects)
    size = _nrbf_scalar(values.get('_size'), objects)
    if not isinstance(items, dict) or items.get('kind') != 'array':
        return []
    try:
        size = int(size)
    except (TypeError, ValueError):
        size = len(items.get('values', []))
    return [_nrbf_deref(item, objects) for item in items.get('values', [])[:size]]


def _nrbf_deref(value: Any, objects: Dict[int, Any]) -> Any:
    seen = set()
    while isinstance(value, dict) and value.get('kind') == 'reference':
        object_id = value.get('id')
        if object_id in seen:
            return value
        seen.add(object_id)
        value = objects.get(object_id, value)
    if isinstance(value, dict) and value.get('kind') == 'string':
        return value.get('value')
    if isinstance(value, dict) and value.get('kind') == 'primitive':
        return value.get('value')
    return value


class _NRBFReader:
    """Minimal reader for the NRBF records emitted by GD90Trace TRR files."""

    def __init__(self, data: bytes):
        self._data = data
        self._offset = 0
        self.objects: Dict[int, Any] = {}
        self._class_defs: Dict[int, Tuple[str, List[str], List[int], List[Any]]] = {}
        self.root_id: Optional[int] = None

    def read_stream(self) -> int:
        while self._offset < len(self._data):
            record = self._read_record()
            if isinstance(record, dict) and record.get('kind') == 'header':
                self.root_id = record['root_id']
            if isinstance(record, dict) and record.get('kind') == 'end':
                break
        if self.root_id is None:
            raise GDMSImportFormatError('TRR stream header was not found.')
        return self.root_id

    def _read_record(self) -> Any:
        pos = self._offset
        record_type = self._u8()
        if record_type == 0:  # SerializedStreamHeader
            root_id = self._i32()
            header_id = self._i32()
            major = self._i32()
            minor = self._i32()
            return {
                'kind': 'header',
                'root_id': root_id,
                'header_id': header_id,
                'major': major,
                'minor': minor,
            }
        if record_type == 1:  # ClassWithId
            object_id = self._i32()
            metadata_id = self._i32()
            try:
                class_name, members, binary_types, additional = self._class_defs[metadata_id]
            except KeyError as exc:
                raise GDMSImportFormatError('TRR class metadata reference is invalid.') from exc
            obj = {
                'kind': 'object',
                'id': object_id,
                'class_name': class_name,
                'values': {},
            }
            self.objects[object_id] = obj
            for name, binary_type, extra in zip(members, binary_types, additional):
                obj['values'][name] = self._read_member_value(binary_type, extra)
            return obj
        if record_type == 2:  # SystemClassWithMembers
            object_id, class_name, members = self._read_class_info()
            binary_types = [2] * len(members)
            additional = [None] * len(members)
            self._class_defs[object_id] = (class_name, members, binary_types, additional)
            obj = {
                'kind': 'object',
                'id': object_id,
                'class_name': class_name,
                'values': {},
            }
            self.objects[object_id] = obj
            for name, binary_type, extra in zip(members, binary_types, additional):
                obj['values'][name] = self._read_member_value(binary_type, extra)
            return obj
        if record_type in (3, 4, 5):  # ClassWithMembers[AndTypes]
            object_id, class_name, members = self._read_class_info()
            if record_type in (4, 5):
                binary_types, additional = self._read_member_type_info(len(members))
            else:
                binary_types = [2] * len(members)
                additional = [None] * len(members)
            if record_type == 5:
                self._i32()  # library id
            self._class_defs[object_id] = (class_name, members, binary_types, additional)
            obj = {
                'kind': 'object',
                'id': object_id,
                'class_name': class_name,
                'values': {},
            }
            self.objects[object_id] = obj
            for name, binary_type, extra in zip(members, binary_types, additional):
                obj['values'][name] = self._read_member_value(binary_type, extra)
            return obj
        if record_type == 6:  # BinaryObjectString
            object_id = self._i32()
            value = self._string()
            obj = {'kind': 'string', 'id': object_id, 'value': value}
            self.objects[object_id] = obj
            return obj
        if record_type == 7:  # BinaryArray
            return self._read_binary_array()
        if record_type == 8:  # MemberPrimitiveTyped
            primitive_type = self._u8()
            return {'kind': 'primitive', 'value': self._primitive(primitive_type)}
        if record_type == 9:  # MemberReference
            return {'kind': 'reference', 'id': self._i32()}
        if record_type == 10:  # ObjectNull
            return None
        if record_type == 11:  # MessageEnd
            return {'kind': 'end'}
        if record_type == 12:  # BinaryLibrary
            self._i32()
            self._string()
            return {'kind': 'library'}
        if record_type == 13:  # ObjectNullMultiple256
            return {'kind': 'nulls', 'count': self._u8()}
        if record_type == 14:  # ObjectNullMultiple
            return {'kind': 'nulls', 'count': self._i32()}
        if record_type == 15:  # ArraySinglePrimitive
            object_id = self._i32()
            length = self._i32()
            primitive_type = self._u8()
            values = [self._primitive(primitive_type) for _ in range(length)]
            obj = {'kind': 'array', 'id': object_id, 'values': values}
            self.objects[object_id] = obj
            return obj
        if record_type in (16, 17):  # ArraySingleObject / ArraySingleString
            object_id = self._i32()
            length = self._i32()
            values = self._read_record_array_items(length)
            obj = {'kind': 'array', 'id': object_id, 'values': values}
            self.objects[object_id] = obj
            return obj
        raise GDMSImportFormatError(
            'Unsupported TRR record type {} at offset {}.'.format(record_type, pos)
        )

    def _read_binary_array(self) -> Dict[str, Any]:
        object_id = self._i32()
        array_type = self._u8()
        rank = self._i32()
        lengths = [self._i32() for _ in range(rank)]
        if array_type in (3, 4, 5):  # offset variants include lower bounds
            for _ in range(rank):
                self._i32()
        binary_type = self._u8()
        extra = self._read_additional_type_info(binary_type)
        total = 1
        for length in lengths:
            total *= length
        if binary_type == 0:
            values = [self._primitive(extra) for _ in range(total)]
        else:
            values = self._read_record_array_items(total)
        obj = {'kind': 'array', 'id': object_id, 'values': values}
        self.objects[object_id] = obj
        return obj

    def _read_record_array_items(self, length: int) -> List[Any]:
        values: List[Any] = []
        while len(values) < length:
            item = self._read_record()
            if isinstance(item, dict) and item.get('kind') == 'nulls':
                values.extend([None] * item['count'])
            else:
                values.append(item)
        return values[:length]

    def _read_member_value(self, binary_type: int, extra: Any) -> Any:
        if binary_type == 0:  # Primitive
            return {'kind': 'primitive', 'value': self._primitive(extra)}
        return self._read_record()

    def _read_class_info(self) -> Tuple[int, str, List[str]]:
        object_id = self._i32()
        class_name = self._string()
        member_count = self._i32()
        members = [self._string() for _ in range(member_count)]
        return object_id, class_name, members

    def _read_member_type_info(self, count: int) -> Tuple[List[int], List[Any]]:
        binary_types = [self._u8() for _ in range(count)]
        additional = [self._read_additional_type_info(binary_type) for binary_type in binary_types]
        return binary_types, additional

    def _read_additional_type_info(self, binary_type: int) -> Any:
        if binary_type == 0:  # Primitive
            return self._u8()
        if binary_type in (1, 2, 5, 6):  # String/Object/ObjectArray/StringArray
            return None
        if binary_type == 3:  # SystemClass
            return self._string()
        if binary_type == 4:  # Class
            return self._string(), self._i32()
        if binary_type == 7:  # PrimitiveArray
            return self._u8()
        raise GDMSImportFormatError('Unsupported TRR binary type {}.'.format(binary_type))

    def _primitive(self, primitive_type: int) -> Any:
        if primitive_type == 1:  # Boolean
            return bool(self._u8())
        if primitive_type == 2:  # Byte
            return self._u8()
        if primitive_type == 3:  # Char
            return self._read(2).decode('utf-16le', errors='replace')
        if primitive_type == 5:  # Decimal
            return self._string()
        if primitive_type == 6:  # Double
            return struct.unpack('<d', self._read(8))[0]
        if primitive_type == 7:  # Int16
            return struct.unpack('<h', self._read(2))[0]
        if primitive_type == 8:  # Int32
            return self._i32()
        if primitive_type == 9:  # Int64
            return struct.unpack('<q', self._read(8))[0]
        if primitive_type == 10:  # SByte
            return struct.unpack('<b', self._read(1))[0]
        if primitive_type == 11:  # Single
            return struct.unpack('<f', self._read(4))[0]
        if primitive_type == 12:  # TimeSpan
            return struct.unpack('<q', self._read(8))[0]
        if primitive_type == 13:  # DateTime raw ticks/kind
            return struct.unpack('<q', self._read(8))[0]
        if primitive_type == 14:  # UInt16
            return struct.unpack('<H', self._read(2))[0]
        if primitive_type == 15:  # UInt32
            return struct.unpack('<I', self._read(4))[0]
        if primitive_type == 16:  # UInt64
            return struct.unpack('<Q', self._read(8))[0]
        if primitive_type == 18:  # String
            return self._string()
        raise GDMSImportFormatError(
            'Unsupported TRR primitive type {} at offset {}.'.format(
                primitive_type, self._offset
            )
        )

    def _string(self) -> str:
        length = self._read_7bit_int()
        return self._read(length).decode('utf-8', errors='replace')

    def _read_7bit_int(self) -> int:
        value = 0
        shift = 0
        while True:
            byte = self._u8()
            value |= (byte & 0x7f) << shift
            if not byte & 0x80:
                return value
            shift += 7
            if shift > 35:
                raise GDMSImportFormatError('Invalid TRR string length encoding.')

    def _u8(self) -> int:
        return self._read(1)[0]

    def _i32(self) -> int:
        return struct.unpack('<i', self._read(4))[0]

    def _read(self, length: int) -> bytes:
        end = self._offset + length
        if end > len(self._data):
            raise GDMSImportFormatError('Unexpected end of TRR file.')
        chunk = self._data[self._offset:end]
        self._offset = end
        return chunk
