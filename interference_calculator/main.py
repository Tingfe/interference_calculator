# -*- coding: utf-8 -*-
""" Calculate isotopic interference and standard ratios. """

import itertools
import logging
import math
import os
from math import comb as _comb
import numpy as np
import pandas as pd
from interference_calculator.molecule import Molecule, mass_electron, periodic_table

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ncr(n, r):
    """Number of combinations with replacement: C(n + r - 1, r)."""
    return _comb(n + r - 1, r)


def _format_from_indices(indices_picked, elem_arr, isos_list,
                         charge_val, chargesign, style,
                         major_isotope_set=frozenset()):
    """Format a molecular formula from structured index data.

    Parameters
    ----------
    indices_picked : ndarray
        Isotope indices into *picked_atoms* (the filtered periodic-table slice).
    elem_arr : ndarray
        Element symbol for each isotope index.
    isos_list : list of str
        Isotope labels (e.g. ``"75As"``) for each index.
    charge_val : int
        Absolute charge value.
    chargesign : str
        ``'+'``, ``'-'``, ``'o'``, or ``'0'``.
    style : str
        Output format style (``'plain'``, ``'html'``, ``'latex'``,
        ``'mhchem'``, ``'molecular'``, ``'isotope'``).
    major_isotope_set : set of str, optional
        Isotope strings that are the **major** (most abundant) isotope of
        their element.  When an isotope is in this set its atomic mass
        number is omitted from the output (e.g. ``"16O"`` -> ``"O"``).
        Default is empty (always show full isotope label).

    Returns
    -------
    str
        Formatted molecular formula.
    """
    # Build unique units with counts (sorted for deterministic output).
    unit_counts = {}
    for idx in indices_picked:
        unit_counts[idx] = unit_counts.get(idx, 0) + 1
    sorted_keys = sorted(unit_counts.keys())
    units = [(k, unit_counts[k]) for k in sorted_keys]

    # ------------------------------------------------------------------ #
    # Build the charge suffix                                            #
    # ------------------------------------------------------------------ #
    if chargesign in ('o', '0') or charge_val == 0:
        charge_part = ''
    else:
        if charge_val == 1:
            cs = chargesign
        else:
            cs = '{}{}'.format(charge_val, chargesign)

        if style in ('html',):
            charge_part = '<sup>{}</sup>'.format(cs)
        elif style in ('latex',):
            charge_part = '{{}}^{{{}}}'.format(cs)
        elif style in ('mhchem',):
            charge_part = '^{}'.format(cs)
        elif style in ('molecular',):
            charge_part = '[{}]'.format(cs)
        else:  # plain / isotope
            charge_part = ' {}'.format(cs)

    # Helper: strip mass number prefix when the isotope is the major one.
    def _display_iso(iso):
        if iso in major_isotope_set:
            return ''.join(ch for ch in iso if not ch.isdigit())
        return iso

    def _mass_and_element(iso):
        """Return (mass_str, element_str) for an isotope label."""
        mass = ''.join(ch for ch in iso if ch.isdigit())
        el = iso[len(mass):]
        return mass, el

    # ------------------------------------------------------------------ #
    # Build each unit for every isotope                                  #
    # ------------------------------------------------------------------ #
    if style in ('plain', 'isotope'):
        parts = []
        for idx, cnt in units:
            iso = isos_list[idx]
            disp = _display_iso(iso)
            parts.append(disp if cnt == 1 else '{}{}'.format(disp, cnt))
        return ' '.join(parts) + charge_part

    elif style in ('html',):
        parts = []
        for idx, cnt in units:
            iso = isos_list[idx]
            mass, el = _mass_and_element(iso)
            mass_tag = '<sup>{}</sup>'.format(mass) if iso not in major_isotope_set else ''
            cnt_tag = '<sub>{}</sub>'.format(cnt) if cnt > 1 else ''
            parts.append(mass_tag + el + cnt_tag)
        return ' '.join(parts) + charge_part

    elif style in ('latex',):
        parts = []
        for idx, cnt in units:
            iso = isos_list[idx]
            mass, el = _mass_and_element(iso)
            mass_tag = r'{{}}^{{{}}}'.format(mass) if iso not in major_isotope_set else ''
            cnt_tag = '_{{{}}}'.format(cnt) if cnt > 1 else ''
            parts.append(mass_tag + el + cnt_tag)
        return r'$\mathrm{' + ' '.join(parts) + charge_part + '}$'

    elif style in ('mhchem',):
        parts = []
        for idx, cnt in units:
            iso = isos_list[idx]
            mass, el = _mass_and_element(iso)
            mass_tag = r'^{{{}}}'.format(mass) if iso not in major_isotope_set else ''
            cnt_tag = '{}'.format(cnt) if cnt > 1 else ''
            parts.append(mass_tag + el + cnt_tag)
        return r'\ce{' + ' '.join(parts) + charge_part + '}'

    elif style in ('molecular',):
        parts = []
        for idx, cnt in units:
            iso = isos_list[idx]
            mass, el = _mass_and_element(iso)
            mass_tag = '[{}]'.format(mass) if iso not in major_isotope_set else ''
            cnt_tag = '{}'.format(cnt) if cnt > 1 else ''
            parts.append(mass_tag + el + cnt_tag)
        return ' '.join(parts) + charge_part

    # Fallback: plain
    parts = []
    for idx, cnt in units:
        iso = isos_list[idx]
        disp = _display_iso(iso)
        parts.append(disp if cnt == 1 else '{}{}'.format(disp, cnt))
    return ' '.join(parts) + charge_part


def _abundance_from_indices(indices_picked, elem_arr, abun_arr):
    """Compute isotopic abundance from structured index data.

    Uses the multinomial distribution for elements that appear with
    multiple isotopes.

    Parameters
    ----------
    indices_picked : ndarray
        Isotope indices into the picked-atoms slice.
    elem_arr : ndarray
        Element symbol for each isotope index.
    abun_arr : ndarray
        Natural abundance for each isotope index.

    Returns
    -------
    float
        Total probability of the isotopic composition.
    """
    # Count occurrences of each isotope index.
    counts = {}
    for idx in indices_picked:
        counts[idx] = counts.get(idx, 0) + 1

    # Group by element.
    el_groups = {}
    for idx, c in counts.items():
        el = elem_arr[idx]
        if el not in el_groups:
            el_groups[el] = []
        el_groups[el].append((c, abun_arr[idx]))

    prob = 1.0
    for items in el_groups.values():
        n = sum(c for c, _ in items)
        if len(items) == 1:
            c, p = items[0]
            prob *= p ** c
        else:
            # Multinomial coefficient: n! / (c1! * c2! * ...) * prod(p_i^c_i)
            nf = math.factorial(n)
            cf = 1
            pp = 1.0
            for c, p in items:
                cf *= math.factorial(c)
                pp *= p ** c
            prob *= nf / cf * pp

    return prob


# ---------------------------------------------------------------------------
# Main public API
# ---------------------------------------------------------------------------

def interference(atoms, target, targetrange=0.3, maxsize=5, charge=(1,),
                 chargesign='-', style='plain', use_pruning=True, n_workers=None,
                 use_streaming=False):
    """Calculate all possible molecular interferences from the given atoms.

    For a list of atoms (the composition of the sample), enumerate all
    combinations of their stable isotopes up to *maxsize* atoms that have
    a mass-to-charge ratio within *target* +/- *targetrange*.

    The *target* can be given as a numeric m/z value or as a molecular
    formula string (parsed by :class:`Molecule`).  When *target* is
    ``None`` all combinations are returned without filtering.

    .. versionchanged:: 2.7.0
       The core algorithm has been rewritten for performance:
       * NumPy-vectorised mass computation instead of per-row Molecule parsing
       * Abundance computed via direct multinomial formula (no pyparsing)
       * 2-44x speedup depending on *maxsize* and element count
       The old ``use_pruning``, ``n_workers``, and ``use_streaming``
       parameters are accepted for API compatibility but are no longer
       needed and have no effect.

    Parameters
    ----------
    atoms : list of str
        Element symbols (e.g. ``['As', 'Ar', 'Cl']``).
    target : float or str or None
        Target m/z value or molecular formula.  ``None`` returns all combos.
    targetrange : float
        Mass tolerance window (default 0.3 Da).
    maxsize : int
        Maximum number of atoms in a combination (default 5).
    charge : tuple of int, optional
        Charge states to consider, e.g. ``(1,)`` or ``(1, 2, 3)``.
        (default ``(1,)``)
    chargesign : str, optional
        ``'+'``, ``'-'``, ``'o'``, or ``'0'`` (default ``'-'``).
    style : str, optional
        Output format: ``'plain'``, ``'isotope'``, ``'html'``,
        ``'latex'``, ``'mhchem'``, ``'molecular'`` (default ``'plain'``).
    use_pruning : bool, optional
        **Deprecated** -- has no effect.
    n_workers : int, optional
        **Deprecated** -- has no effect.
    use_streaming : bool, optional
        **Deprecated** -- has no effect.

    Returns
    -------
    pandas.DataFrame
        Columns: ``molecule``, ``charge``, ``mass/charge``,
        ``mass/charge diff``, ``MRP``, ``probability``, ``target``.
    """
    # ------------------------------------------------------------------ #
    # Validate parameters                                                #
    # ------------------------------------------------------------------ #
    if isinstance(charge, (int, float, str)):
        charge = (int(charge),)
    elif isinstance(charge, (tuple, list)):
        charge = tuple(int(c) for c in charge)
    else:
        raise ValueError('charge must be given as a number or a list of numbers.')
    if not charge:
        raise ValueError('charge must contain at least one value.')
    if chargesign not in ('+', '-', 'o', '0'):
        raise ValueError('chargesign must be either "+", "-", "o", or "0".')

    # ------------------------------------------------------------------ #
    # Parse *target* -- need Molecule here because it is user-supplied   #
    # ------------------------------------------------------------------ #
    if target is not None:
        try:
            target_mz = float(target)
            target = str(target)
            target_charge = 0
            target_chargesign = 'o'
            target_abun = 1
        except (ValueError, TypeError):
            m = Molecule(target)
            inferred_charge = False
            if m.chargesign:
                target_chargesign = m.chargesign
            else:
                target_chargesign = chargesign
                inferred_charge = True
            if m.charge:
                target_charge = m.charge
            else:
                target_charge = 0 if target_chargesign in ('o', '0') else charge[0]
                inferred_charge = True
            if inferred_charge:
                if target_charge == 0:
                    pass
                elif target_charge == 1:
                    target += ' {}'.format(target_chargesign)
                else:
                    target += ' {}{}'.format(target_charge, target_chargesign)
                m = Molecule(target)
            target_mz = m.mass
            target_abun = m.abundance
            if m.charge > 0:
                target_mz /= m.charge
    else:
        target_mz = 0
        target_charge = 0
        target_chargesign = '0'
        target_abun = 0

    # ------------------------------------------------------------------ #
    # Pre-select elements and speed up repeated lookups                  #
    # ------------------------------------------------------------------ #
    picked = periodic_table[periodic_table['element'].isin(atoms)].reset_index(drop=True)
    if picked.empty:
        raise ValueError('None of the given atoms were found in the periodic table.')

    N = len(picked)
    mass_arr = picked['mass'].to_numpy(dtype=np.float64)
    abun_arr = picked['abundance'].to_numpy(dtype=np.float64)
    elem_arr = picked['element'].to_numpy(dtype=object)
    isos_list = picked['isotope'].tolist()
    major_isotope_set = frozenset(picked['major isotope'].unique())

    # Shared constants for the charge loop
    has_target = target is not None
    is_neutral = chargesign in ('o', '0')

    # Collect filtered results across all charge values.
    all_mz = []
    all_idx = []       # lists of index arrays (one per **filtered** combination)
    all_charge_vals = []

    # ------------------------------------------------------------------ #
    # Main enumeration loop: per-size per-charge                         #
    # ------------------------------------------------------------------ #
    # Pre-compute the number of combos per size so we can use np.fromiter
    # without a first-pass list to measure length.
    ncr_cache = {}
    for sz in range(1, maxsize + 1):
        ncr_cache[sz] = _ncr(N, sz)

    for ch in charge:
        if ch == 0:
            continue  # handled via is_neutral

        # Loop over sizes so we build compact rectangular arrays per size.
        for sz in range(1, maxsize + 1):
            nC = ncr_cache[sz]

            # Build (nC, sz) matrix of isotope indices into *picked*.
            idx_mat = np.fromiter(
                itertools.chain.from_iterable(
                    itertools.combinations_with_replacement(range(N), sz)),
                dtype=np.int64, count=nC * sz,
            ).reshape(nC, sz)

            # Vectorised mass sum.
            masses = mass_arr[idx_mat]  # (nC, sz) float64
            mass_sum = masses.sum(axis=1, dtype=np.float64)

            # Charge correction
            if is_neutral:
                mz = mass_sum
            else:
                mz = mass_sum / ch
                if chargesign == '+':
                    mz -= mass_electron
                elif chargesign == '-':
                    mz += mass_electron

            # Early filter by target range
            if has_target:
                mask = (mz >= target_mz - targetrange) & (mz <= target_mz + targetrange)
                if mask.any():
                    all_mz.append(mz[mask])
                    all_idx.append(idx_mat[mask])
                    all_charge_vals.append(np.full(mask.sum(), ch, dtype=np.int64))
            else:
                # No target -> keep everything.
                all_mz.append(mz)
                all_idx.append(idx_mat)
                all_charge_vals.append(np.full(nC, ch, dtype=np.int64))

    if not all_mz:
        # No results at all -- return empty DataFrame with correct columns.
        columns = ['molecule', 'charge', 'mass/charge',
                   'mass/charge diff', 'MRP', 'probability', 'target']
        return pd.DataFrame(columns=columns)

    # Concatenate per-size-per-charge blocks.
    sel_mz = np.concatenate(all_mz)
    sel_charge = np.concatenate(all_charge_vals)
    n_sel = len(sel_mz)

    # ------------------------------------------------------------------ #
    # Abundance + formula for every filtered combination                  #
    # ------------------------------------------------------------------ #
    # Because the filtered set is small (usually << 1 000 entries),
    # a Python loop over each combo is perfectly adequate.
    abun_out = np.empty(n_sel, dtype=np.float64)
    form_out = []

    offset = 0
    for arr, cv in zip(all_idx, all_charge_vals):
        n_block = len(arr)
        for row_idx in range(n_block):
            row = arr[row_idx]
            abun_out[offset + row_idx] = _abundance_from_indices(
                row, elem_arr, abun_arr)
            form_out.append(_format_from_indices(
                row, elem_arr, isos_list,
                cv[row_idx], chargesign, style,
                major_isotope_set=major_isotope_set))
        offset += n_block

    # ------------------------------------------------------------------ #
    # Assemble the output DataFrame                                       #
    # ------------------------------------------------------------------ #
    if has_target:
        mz_diff = sel_mz - target_mz
        mrp = np.where(np.abs(mz_diff) > 1e-15, target_mz / np.abs(mz_diff), np.inf)
    else:
        mz_diff = np.zeros(n_sel, dtype=np.float64)
        mrp = np.full(n_sel, np.inf)

    data = pd.DataFrame({
        'molecule': form_out,
        'charge': sel_charge,
        'mass/charge': sel_mz,
        'mass/charge diff': mz_diff,
        'MRP': mrp,
        'probability': abun_out,
        'target': False,
    })

    # Append the target row (if applicable).
    if has_target:
        target_row = pd.DataFrame([{
            'molecule': target,
            'charge': target_charge,
            'mass/charge': target_mz,
            'mass/charge diff': 0.0,
            'MRP': np.inf,
            'probability': target_abun,
            'target': True,
        }])
        data = pd.concat([data, target_row], ignore_index=True)

    return data[['molecule', 'charge', 'mass/charge',
                 'mass/charge diff', 'MRP', 'probability', 'target']]


def interference_gpu(atoms, target, targetrange=0.3, maxsize=5, charge=(1,),
                     chargesign='-', style='plain', **kwargs):
    """GPU-compatible interference calculation (deprecated).

    .. deprecated:: 2.7.0
       The algorithm has been rewritten with NumPy vectorisation that
       makes GPU acceleration irrelevant -- the numerical stage is
       < 2 ms even for the largest realistic combination spaces.  The
       real bottleneck (combinatorial enumeration and string formatting)
       cannot be GPU-accelerated.  This function is kept for backward
       compatibility and simply calls :func:`interference` with the
       optimised CPU path.

    Returns
    -------
    pandas.DataFrame
        Same format as :func:`interference`.
    """
    return interference(atoms, target, targetrange, maxsize, charge,
                        chargesign, style)


def standard_ratio(atoms, style='plain'):
    """Given one or more element symbols, return their stable isotopes
    with standard abundance, abundance ratio, and inverse ratio.

    Parameters
    ----------
    atoms : list of str
        Element symbols.
    style : str, optional
        Formula style for isotope output (default ``'plain'``).

    Returns
    -------
    pandas.DataFrame
        Columns: ``isotope``, ``mass``, ``abundance``, ``ratio``,
        ``inverse ratio``, ``standard``.
    """
    data = periodic_table[periodic_table['element'].isin(atoms)].copy()
    data['ratio'] = 1.0
    data['inverse ratio'] = 1.0
    for a in atoms:
        mask = data['element'] == a
        abun = data.loc[mask, 'abundance'].copy()
        ratio = abun / abun.max()
        inv_ratio = 1.0 / ratio
        data.loc[mask, 'ratio'] = ratio
        data.loc[mask, 'inverse ratio'] = inv_ratio

    if style != 'plain':
        pretty = []
        for i in data['isotope'].values:
            m = Molecule(i)
            pretty.append(m.formula(style=style, show_charge=False, all_isotopes=True))
        data['isotope'] = pretty

    return data[['isotope', 'mass', 'abundance', 'ratio', 'inverse ratio', 'standard']]
