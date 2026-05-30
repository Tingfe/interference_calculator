#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Rebuild the isotope database from CIAAW 2024 and AME2020 data."""

import argparse
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd


PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT = PACKAGE_DIR / 'periodic_table.csv'
DEFAULT_EXISTING = PACKAGE_DIR / 'periodic_table.csv'

MASS_URL = 'https://ciaaw.org/data/IUPAC-atomic-masses.csv'
ABUNDANCE_URL = 'https://ciaaw.org/isotopic-abundances.htm'
ABUNDANCE_SOURCE = 'CIAAW 2024'
MASS_SOURCE = 'AME2020'


class _CIAAWTableParser(HTMLParser):
    """Small HTML table parser that tolerates CIAAW's rowspans."""

    def __init__(self):
        HTMLParser.__init__(self)
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.rows = []
        self.row = []
        self.cell = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'table' and attrs.get('id') == 'mytable':
            self.in_table = True
        elif self.in_table and tag == 'tr':
            self.in_row = True
            self.row = []
        elif self.in_row and tag in ('td', 'th'):
            self.in_cell = True
            self.cell = []

    def handle_endtag(self, tag):
        if self.in_cell and tag in ('td', 'th'):
            text = unescape(''.join(self.cell)).replace('\xa0', ' ').strip()
            text = re.sub(r'\s+', ' ', text)
            self.row.append(text)
            self.in_cell = False
        elif self.in_table and tag == 'tr':
            if self.row:
                self.rows.append(self.row)
            self.in_row = False
        elif self.in_table and tag == 'table':
            self.in_table = False

    def handle_data(self, data):
        if self.in_cell:
            self.cell.append(data)


def _read_text(url=None, filename=None):
    if filename:
        return Path(filename).read_text(encoding='utf-8')
    import requests

    response = requests.get(url, timeout=60)
    response.raise_for_status()
    response.encoding = response.encoding or 'utf-8'
    return response.text


def _load_existing_abundances(filename):
    if not filename or not Path(filename).exists():
        return {}
    data = pd.read_csv(filename, comment='#')
    return data.set_index('isotope')['abundance'].to_dict()


def _parse_abundance_table(html, existing_abundances=None):
    # A few CIAAW rows begin with <td rowspan=...> without an opening <tr>.
    html = re.sub(r'\n<td rowspan=', '\n<tr><td rowspan=', html)
    parser = _CIAAWTableParser()
    parser.feed(html)

    rows = []
    last_z = last_symbol = last_name = ''
    for row in parser.rows:
        if row and row[0] == 'Z':
            continue
        if len(row) >= 5:
            if len(row) == 5:
                z, symbol, name, mass_number, composition = row
                notes = ''
            else:
                z, symbol, name, mass_number, composition, notes = row[:6]
            if not composition:
                composition = '1'
            if not z.isdigit():
                continue
            last_z, last_symbol, last_name = z, symbol, name
        elif len(row) >= 2:
            z, symbol, name = last_z, last_symbol, last_name
            mass_number, composition = row[:2]
            notes = row[2] if len(row) > 2 else ''
            if not z or not z.isdigit():
                continue
        else:
            continue

        digits = re.sub(r'[^0-9]', '', mass_number)
        if not digits:
            continue
        atomic_mass = int(digits)
        isotope = '{}{}'.format(atomic_mass, symbol)
        info = _parse_composition(composition)
        abundance = _representative_abundance(
            isotope, info, existing_abundances or {}
        )
        rows.append({
            'atomic number': int(z),
            'element': symbol,
            'element name': name,
            'isotope': isotope,
            'atomic mass': atomic_mass,
            'abundance': abundance,
            'abundance low': info['low'],
            'abundance high': info['high'],
            'abundance uncertainty': info['uncertainty'],
            'abundance kind': info['kind'],
            'abundance source': ABUNDANCE_SOURCE,
            'standard': ABUNDANCE_SOURCE,
            'notes': notes,
        })

    data = pd.DataFrame(rows)
    data = data.drop_duplicates('isotope', keep='last')
    data = data.sort_values(['atomic number', 'atomic mass']).reset_index(drop=True)
    data = _normalise_element_abundances(data)
    return data


def _parse_composition(composition):
    raw = composition.strip()
    compact = raw.replace(' ', '')
    if compact == '-':
        return {
            'value': 1.0,
            'low': pd.NA,
            'high': pd.NA,
            'uncertainty': pd.NA,
            'kind': 'radioactive',
        }
    if compact == '1':
        return {
            'value': 1.0,
            'low': 1.0,
            'high': 1.0,
            'uncertainty': 0.0,
            'kind': 'exact',
        }

    interval = re.match(r'^\[(.*?),(.*?)\]$', compact)
    if interval:
        low = float(interval.group(1))
        high = float(interval.group(2))
        return {
            'value': (low + high) / 2.0,
            'low': low,
            'high': high,
            'uncertainty': pd.NA,
            'kind': 'interval',
        }

    value = re.match(r'^([0-9.]+)(?:\(([0-9]+)\))?$', compact)
    if value:
        nominal = float(value.group(1))
        uncertainty = _expanded_uncertainty(value.group(1), value.group(2))
        return {
            'value': nominal,
            'low': pd.NA,
            'high': pd.NA,
            'uncertainty': uncertainty,
            'kind': 'value',
        }

    raise ValueError('Could not parse isotopic composition: {}'.format(raw))


def _expanded_uncertainty(value_text, digits):
    if not digits:
        return pd.NA
    if '.' in value_text:
        places = len(value_text.split('.', 1)[1])
    else:
        places = 0
    return int(digits) * 10 ** (-places)


def _representative_abundance(isotope, info, existing_abundances):
    if info['kind'] == 'interval':
        old_value = existing_abundances.get(isotope)
        if old_value is not None and info['low'] <= old_value <= info['high']:
            return old_value
    return info['value']


def _normalise_element_abundances(data):
    data = data.copy()
    for element, idx in data.groupby('element').groups.items():
        total = data.loc[idx, 'abundance'].sum()
        if total > 0:
            data.loc[idx, 'abundance'] = data.loc[idx, 'abundance'] / total
    return data


def _parse_mass_table(text):
    from io import StringIO

    data = pd.read_csv(StringIO(text), skiprows=2)
    data = data.rename(columns={'nuclide': 'isotope'})
    data['mass'] = pd.to_numeric(data['mass'], errors='raise')
    data['mass uncertainty'] = pd.to_numeric(data['uncertainty'], errors='coerce')
    data['mass source year'] = (
        data['Year/link'].astype(str)
        .str.extract(r'>(\d{4})</a>$')
        .astype(int)
    )
    data = data.sort_values(['isotope', 'mass source year'])
    data = data.drop_duplicates('isotope', keep='last')
    data['mass source'] = MASS_SOURCE
    return data[['isotope', 'mass', 'mass uncertainty',
                 'mass source year', 'mass source']]


def build_periodic_table(mass_text, abundance_html, existing=None):
    existing_abundances = _load_existing_abundances(existing)
    abundance = _parse_abundance_table(abundance_html, existing_abundances)
    mass = _parse_mass_table(mass_text)
    data = abundance.merge(mass, on='isotope', how='left')

    missing = data[data['mass'].isna()]['isotope'].tolist()
    if missing:
        raise ValueError('Missing AME masses for: {}'.format(', '.join(missing)))

    data = _add_major_isotope(data)
    data = data[[
        'atomic number', 'element', 'element name', 'major isotope',
        'isotope', 'atomic mass', 'mass', 'mass uncertainty',
        'mass source year', 'mass source', 'abundance', 'abundance low',
        'abundance high', 'abundance uncertainty', 'abundance kind',
        'abundance source', 'standard', 'notes',
    ]]
    return data.sort_values(['atomic number', 'atomic mass']).reset_index(drop=True)


def _add_major_isotope(data):
    data = data.copy()
    major = {}
    for element, element_data in data.groupby('element'):
        row = element_data.sort_values(
            ['abundance', 'atomic mass'], ascending=[False, True]
        ).iloc[0]
        major[element] = row['isotope']
    data['major isotope'] = data['element'].map(major)
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mass-file', help='Local CIAAW/AME mass CSV.')
    parser.add_argument('--abundance-file', help='Local CIAAW abundance HTML.')
    parser.add_argument('--existing-file', default=str(DEFAULT_EXISTING),
                        help='Existing table used for interval representatives.')
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT),
                        help='Output periodic_table.csv path.')
    args = parser.parse_args(argv)

    mass_text = _read_text(MASS_URL, args.mass_file)
    abundance_html = _read_text(ABUNDANCE_URL, args.abundance_file)
    table = build_periodic_table(
        mass_text, abundance_html, existing=args.existing_file
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output, index=False)
    print('Wrote {} rows to {}'.format(table.shape[0], output))


if __name__ == '__main__':
    main()
