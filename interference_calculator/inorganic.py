# -*- coding: utf-8 -*-
""" Template-based inorganic mass-spectrometry interference screening. """

import itertools

import numpy as np
import pandas as pd

from interference_calculator.molecule import Molecule, mass_electron, periodic_table


PLASMA_ELEMENTS = ('Ar', 'Ne', 'Kr', 'Xe', 'He')
COMMON_LIGANDS = ('H', 'C', 'N', 'O', 'F', 'S', 'Cl', 'Br', 'I')
BACKGROUND_MOLECULE_BASES = ('H', 'C', 'N', 'O', 'S', 'Cl')

GDMS_FORMATION_FACTORS = {
    'atomic': 1.0,
    'doubly charged': 1.0e-2,
    'oxide': 1.0e-3,
    'dioxide': 1.0e-5,
    'hydride': 1.0e-4,
    'hydroxide': 1.0e-5,
    'nitride': 1.0e-4,
    'carbide': 1.0e-4,
    'sulfide': 1.0e-5,
    'halide': 1.0e-5,
    'plasma adduct': 1.0e-4,
    'background molecule': 1.0e-5,
    'cluster': 1.0e-5,
    # Extended templates for maxsize >= 4
    'trioxide': 1.0e-7,
    'trihydride': 1.0e-6,
    'mixed oxide-hydride': 1.0e-6,
    # Extended templates for maxsize >= 5
    'tetraoxide': 1.0e-9,
}

ICP_MS_FORMATION_FACTORS = {
    'atomic': 1.0,
    'doubly charged': 1.0e-2,
    'oxide': 1.0e-2,
    'dioxide': 1.0e-5,
    'hydride': 1.0e-4,
    'hydroxide': 1.0e-3,
    'nitride': 1.0e-5,
    'carbide': 1.0e-5,
    'sulfide': 1.0e-5,
    'halide': 1.0e-4,
    'plasma adduct': 1.0e-3,
    'background molecule': 1.0e-4,
    'cluster': 1.0e-6,
    # Extended templates for maxsize >= 4
    'trioxide': 1.0e-7,
    'trihydride': 1.0e-6,
    'mixed oxide-hydride': 1.0e-6,
    # Extended templates for maxsize >= 5
    'tetraoxide': 1.0e-9,
}

SIMS_FORMATION_FACTORS = {
    'atomic': 1.0,
    'doubly charged': 1.0e-3,
    'oxide': 1.0e-2,
    'dioxide': 1.0e-4,
    'hydride': 1.0e-3,
    'hydroxide': 1.0e-4,
    'nitride': 1.0e-4,
    'carbide': 1.0e-3,
    'sulfide': 1.0e-4,
    'halide': 1.0e-4,
    'plasma adduct': 1.0e-6,
    'background molecule': 1.0e-4,
    'cluster': 1.0e-3,
    # Extended templates for maxsize >= 4
    'trioxide': 1.0e-6,
    'trihydride': 1.0e-5,
    'mixed oxide-hydride': 1.0e-5,
    # Extended templates for maxsize >= 5
    'tetraoxide': 1.0e-8,
}

FORMATION_FACTOR_PRESETS = {
    'gdms': GDMS_FORMATION_FACTORS,
    'icp-ms': ICP_MS_FORMATION_FACTORS,
    'sims': SIMS_FORMATION_FACTORS,
}

# Backwards-compatible name for callers that imported the original constant.
FORMATION_FACTORS = GDMS_FORMATION_FACTORS

ISOTOPE_MASSES = periodic_table.set_index('isotope')['mass'].to_dict()
ISOTOPE_MASS_UNCERTAINTIES = periodic_table.set_index('isotope').get(
    'mass uncertainty', pd.Series(dtype=float)
).to_dict()

LIGAND_TYPES = {
    'H': ('hydride', 1),
    'C': ('carbide', 1),
    'N': ('nitride', 1),
    'O': ('oxide', 1),
    'S': ('sulfide', 1),
    'F': ('halide', 1),
    'Cl': ('halide', 1),
    'Br': ('halide', 1),
    'I': ('halide', 1),
}


def inorganic_interference(atoms, target, targetrange=0.3, charge=(1, 2),
                           chargesign='+', maxsize=3, style='plain',
                           risk_preset='gdms', formation_factors=None,
                           matrix_atoms=None, plasma_atoms=None,
                           background_atoms=None, include_background=True):
    """Screen common inorganic mass-spectrometry interference candidates.

    This function is intentionally template-based. It prioritizes species that
    are common in GDMS and other inorganic mass-spectrometry workflows:
    atomic ions, doubly charged atomic ions, oxides, hydrides, simple
    non-metal adducts, plasma adducts, and small matrix clusters.
    """
    atoms = _normalize_atoms(atoms)
    charges = _normalize_charges(charge)
    risk_factors = _formation_factors(risk_preset, formation_factors)
    if chargesign not in ('+', '-', 'o', '0'):
        raise ValueError('chargesign must be either "+", "-", "o", or "0".')

    target_info = _target_info(target, charges, chargesign)
    candidates = _candidate_formulas(
        atoms, charges, chargesign, maxsize,
        matrix_atoms=matrix_atoms, plasma_atoms=plasma_atoms,
        background_atoms=background_atoms, include_background=include_background,
    )
    rows = []
    seen = set()

    for parts, species_type, species_charge in candidates:
        formula = _charged_formula(parts, species_charge, chargesign)
        if formula in seen:
            continue
        seen.add(formula)
        mz = _parts_mass_to_charge(parts, species_charge, chargesign)
        if target_info['has_target']:
            if not (target_info['mz'] - targetrange <= mz <= target_info['mz'] + targetrange):
                continue
            mz_diff = mz - target_info['mz']
            mrp = _required_mrp(target_info['mz'], mz_diff)
        else:
            mz_diff = 0.0
            mrp = np.inf

        mass_uncertainty = _parts_mass_uncertainty(parts)
        if species_charge:
            mz_uncertainty = mass_uncertainty / abs(species_charge)
        else:
            mz_uncertainty = mass_uncertainty
        molecule = Molecule(formula)
        label = molecule.formula(style=style)
        if target_info['has_target'] and label == target_info['label']:
            continue

        formation_factor = risk_factors.get(species_type, 1.0e-6)
        rows.append({
            'molecule': label,
            'type': species_type,
            'charge': species_charge,
            'mass/charge': mz,
            'mass/charge diff': mz_diff,
            'mass uncertainty': mass_uncertainty,
            'm/z uncertainty': mz_uncertainty,
            'MRP': mrp,
            'probability': molecule.abundance,
            'formation factor': formation_factor,
            'relative risk': molecule.abundance * formation_factor,
            'target': False,
        })

    data = pd.DataFrame(rows, columns=[
        'molecule', 'type', 'charge', 'mass/charge', 'mass/charge diff',
        'mass uncertainty', 'm/z uncertainty', 'MRP', 'probability',
        'formation factor', 'relative risk', 'target',
    ])
    if not data.empty and target_info['has_target']:
        data = data.assign(_abs_diff=data['mass/charge diff'].abs())
        data = data.sort_values(['_abs_diff', 'relative risk'], ascending=[True, False])
        data = data.drop(columns='_abs_diff')

    if target_info['has_target']:
        target_row = pd.DataFrame([{
            'molecule': target_info['label'],
            'type': 'target',
            'charge': target_info['charge'],
            'mass/charge': target_info['mz'],
            'mass/charge diff': 0.0,
            'mass uncertainty': target_info['mass_uncertainty'],
            'm/z uncertainty': target_info['mz_uncertainty'],
            'MRP': np.inf,
            'probability': target_info['abundance'],
            'formation factor': 1.0,
            'relative risk': target_info['abundance'],
            'target': True,
        }])
        if data.empty:
            data = target_row
        else:
            data = pd.concat([data, target_row], ignore_index=True)

    return data


def _normalize_atoms(atoms):
    unique_atoms = []
    for atom in atoms:
        if atom not in unique_atoms:
            unique_atoms.append(atom)
    return unique_atoms


def _normalize_charges(charge):
    if isinstance(charge, (int, float, str)):
        charges = (int(charge),)
    else:
        charges = tuple(int(c) for c in charge)
    if not charges:
        raise ValueError('charge must contain at least one value.')
    return charges


def _formation_factors(risk_preset, formation_factors):
    try:
        factors = dict(FORMATION_FACTOR_PRESETS[risk_preset])
    except KeyError:
        msg = 'risk_preset must be one of {}.'.format(
            ', '.join(sorted(FORMATION_FACTOR_PRESETS))
        )
        raise ValueError(msg)
    if formation_factors:
        factors.update(formation_factors)
    return factors


def _target_info(target, charges, chargesign):
    if target:
        try:
            return {
                'has_target': True,
                'label': str(target),
                'charge': 0,
                'mz': float(target),
                'mass_uncertainty': 0.0,
                'mz_uncertainty': 0.0,
                'abundance': 1.0,
            }
        except ValueError:
            molecule = Molecule(target)
            target_formula = target
            if not molecule.charge and chargesign not in ('o', '0'):
                target_formula = _charged_formula([target], charges[0], chargesign)
                molecule = Molecule(target_formula)
            if molecule.charge:
                mz_uncertainty = molecule.mass_uncertainty / abs(molecule.charge)
            else:
                mz_uncertainty = molecule.mass_uncertainty
            return {
                'has_target': True,
                'label': molecule.formula(),
                'charge': molecule.charge,
                'mz': _mass_to_charge(molecule),
                'mass_uncertainty': molecule.mass_uncertainty,
                'mz_uncertainty': mz_uncertainty,
                'abundance': molecule.abundance,
            }

    return {
        'has_target': False,
        'label': '',
        'charge': 0,
        'mz': 0.0,
        'mass_uncertainty': 0.0,
        'mz_uncertainty': 0.0,
        'abundance': 0.0,
    }


def _candidate_formulas(atoms, charges, chargesign, maxsize,
                        matrix_atoms=None, plasma_atoms=None,
                        background_atoms=None, include_background=True):
    if maxsize < 1:
        return

    selected = set(atoms)
    plasma = _role_atoms(atoms, plasma_atoms, PLASMA_ELEMENTS)
    background = _role_atoms(atoms, background_atoms, COMMON_LIGANDS)
    if matrix_atoms is not None:
        matrix = _normalize_atoms([a for a in matrix_atoms if a in selected])
    else:
        matrix = [
            a for a in atoms
            if a not in set(background) and a not in set(plasma)
        ]
    if not matrix:
        matrix = [a for a in atoms if a not in set(plasma)]

    # Atomic ions, including doubly charged ions if requested.
    for element in atoms:
        for isotope in _isotopes(element):
            for ch in charges:
                species_type = 'doubly charged' if abs(ch) == 2 else 'atomic'
                yield [isotope], species_type, ch

    if maxsize < 2 or chargesign in ('o', '0'):
        return

    # Generate molecular ions for all requested charge states
    # Note: Doubly charged molecules (MO2+, MH2+, etc.) are rare but possible
    for mol_charge in charges:
        # Matrix/background adducts such as MO+, MH+, MC+, MN+, and MCl+.
        for ligand, (species_type, count) in LIGAND_TYPES.items():
            if ligand not in selected:
                continue
            for base in matrix:
                if base == ligand:
                    continue
                for parts in _adduct_formulas(base, ligand, count):
                    yield parts, species_type, mol_charge

        # Dioxides are common enough to keep separate from generic clusters.
        if 'O' in selected and maxsize >= 3:
            for base in matrix:
                if base == 'O':
                    continue
                for parts in _adduct_formulas(base, 'O', 2):
                    yield parts, 'dioxide', mol_charge

        # Hydroxides such as MOH+ are common in wet ICP-MS backgrounds and can
        # also be useful screening candidates for residual gas chemistry.
        if {'O', 'H'}.issubset(selected) and maxsize >= 3:
            for base in matrix:
                if base in ('O', 'H'):
                    continue
                for parts in _multi_adduct_formulas(base, ('O', 'H')):
                    yield parts, 'hydroxide', mol_charge

        # Plasma adducts such as ArO+, ArN+, ArCl+, and ArM+.
        for plasma_element in plasma:
            for partner in atoms:
                if partner == plasma_element:
                    continue
                for parts in _binary_formulas(plasma_element, partner):
                    yield parts, 'plasma adduct', mol_charge

        # Common background ions such as CO+, CN+, NO+, O2+, H2O+, SO+, and
        # CO2+. These are intentionally limited to light/background elements so
        # the template remains much narrower than unrestricted enumeration.
        if include_background and maxsize >= 2:
            background_pool = [
                a for a in background
                if a in BACKGROUND_MOLECULE_BASES and a in selected
            ]
            for first, second in itertools.combinations_with_replacement(background_pool, 2):
                for parts in _binary_formulas(first, second):
                    yield parts, 'background molecule', mol_charge
            if 'O' in background_pool and maxsize >= 3:
                for base in background_pool:
                    if base == 'O':
                        continue
                    for parts in _adduct_formulas(base, 'O', 2):
                        yield parts, 'background molecule', mol_charge

        # Small matrix clusters. This captures common M2+ and MM'+ species without
        # falling back to full unrestricted enumeration.
        if maxsize >= 2:
            for first, second in itertools.combinations_with_replacement(matrix, 2):
                for parts in _binary_formulas(first, second):
                    yield parts, 'cluster', mol_charge

        # Extended templates for maxsize >= 4 (tri-oxides, tri-hydrides, etc.)
        if maxsize >= 4:
            # Trioxides (MO3+) - important for heavy elements
            if 'O' in selected:
                for base in matrix:
                    if base == 'O':
                        continue
                    for parts in _adduct_formulas(base, 'O', 3):
                        yield parts, 'trioxide', mol_charge
            
            # Trihydrides (MH3+) - less common but possible
            if 'H' in selected:
                for base in matrix:
                    if base == 'H':
                        continue
                    for parts in _adduct_formulas(base, 'H', 3):
                        yield parts, 'trihydride', mol_charge
            
            # Mixed adducts: MOH2+, MO2H+ (4 atoms total)
            if {'O', 'H'}.issubset(selected):
                for base in matrix:
                    if base in ('O', 'H'):
                        continue
                    # MO2H+
                    for parts in _multi_adduct_formulas(base, ('O', 'O', 'H')):
                        yield parts, 'mixed oxide-hydride', mol_charge
                    # MOH2+
                    for parts in _multi_adduct_formulas(base, ('O', 'H', 'H')):
                        yield parts, 'mixed oxide-hydride', mol_charge
        
        # Even larger clusters for maxsize >= 5
        if maxsize >= 5:
            # Tetraoxides (MO4+)
            if 'O' in selected:
                for base in matrix:
                    if base == 'O':
                        continue
                    for parts in _adduct_formulas(base, 'O', 4):
                        yield parts, 'tetraoxide', mol_charge
            
            # Larger mixed adducts: MO3H+, MO2H2+, MOH3+
            if {'O', 'H'}.issubset(selected):
                for base in matrix:
                    if base in ('O', 'H'):
                        continue
                    for parts in _multi_adduct_formulas(base, ('O', 'O', 'O', 'H')):
                        yield parts, 'mixed oxide-hydride', mol_charge
                    for parts in _multi_adduct_formulas(base, ('O', 'O', 'H', 'H')):
                        yield parts, 'mixed oxide-hydride', mol_charge
                    for parts in _multi_adduct_formulas(base, ('O', 'H', 'H', 'H')):
                        yield parts, 'mixed oxide-hydride', mol_charge


def _isotopes(element):
    return periodic_table.loc[periodic_table['element'] == element, 'isotope'].tolist()


def _role_atoms(atoms, explicit_atoms, defaults):
    if explicit_atoms is not None:
        selected = set(atoms)
        return _normalize_atoms([a for a in explicit_atoms if a in selected])
    return [a for a in atoms if a in defaults]


def _adduct_formulas(base, ligand, ligand_count):
    for base_isotope in _isotopes(base):
        for ligand_isotopes in itertools.combinations_with_replacement(_isotopes(ligand), ligand_count):
            yield [base_isotope] + list(ligand_isotopes)


def _multi_adduct_formulas(base, ligands):
    ligand_isotopes = [_isotopes(ligand) for ligand in ligands]
    for base_isotope in _isotopes(base):
        for isotopes in itertools.product(*ligand_isotopes):
            yield [base_isotope] + list(isotopes)


def _binary_formulas(first, second):
    if first == second:
        isotope_pairs = itertools.combinations_with_replacement(_isotopes(first), 2)
    else:
        isotope_pairs = itertools.product(_isotopes(first), _isotopes(second))
    for isotopes in isotope_pairs:
        yield list(isotopes)


def _charged_formula(parts, charge, chargesign):
    if charge == 0 or chargesign in ('o', '0'):
        return ' '.join(parts)
    if charge == 1:
        return '{} {}'.format(' '.join(parts), chargesign)
    return '{} {}{}'.format(' '.join(parts), charge, chargesign)


def _mass_to_charge(molecule):
    if molecule.charge:
        return molecule.mass / molecule.charge
    return molecule.mass


def _parts_mass_to_charge(parts, charge, chargesign):
    mass = sum(ISOTOPE_MASSES[part] for part in parts)
    if charge == 0 or chargesign in ('o', '0'):
        return mass
    if chargesign == '+':
        mass -= mass_electron * charge
    elif chargesign == '-':
        mass += mass_electron * charge
    return mass / charge


def _parts_mass_uncertainty(parts):
    counts = {}
    for part in parts:
        counts[part] = counts.get(part, 0) + 1
    terms = []
    for part, count in counts.items():
        uncertainty = ISOTOPE_MASS_UNCERTAINTIES.get(part, 0.0)
        if pd.notna(uncertainty):
            terms.append((uncertainty * count) ** 2)
    return float(np.sqrt(sum(terms)))


def _required_mrp(target_mz, mz_diff):
    if mz_diff == 0:
        return np.inf
    return target_mz / abs(mz_diff)
