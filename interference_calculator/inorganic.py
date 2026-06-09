# -*- coding: utf-8 -*-
""" Template-based inorganic mass-spectrometry interference screening.

Theoretical Basis and Literature Support
-----------------------------------------
This module implements a template-driven approach for screening common
inorganic mass spectrometry interferences. Formation factors are based on:

1. **ICP-MS Standards** (high confidence):
   - JJF 1159-2006: Chinese national calibration standard
     * CeO⁺/Ce⁺ ≤ 3.0% (oxide formation benchmark)
     * Ba²⁺/Ba⁺ ≤ 3.0% (double charge benchmark)
   - Instrument specifications (Agilent, Thermo Fisher): typical values
     * Oxide: 0.3-3.0% (modern ICP-MS)
     * Double charge: 0.02-3.56%

2. **GDMS/SIMS Estimates** (lower confidence):
   - Extrapolated from ICP-MS data using plasma chemistry principles
   - GDMS: lower oxide formation due to low-pressure environment
   - SIMS: highly variable, depends on primary beam type

3. **Thermodynamic Model**:
   - Oxide formation correlates with metal-oxygen bond dissociation energy
     * Ce-O: 795 kJ/mol → high oxide yield (~2-3%)
     * Ba-O: 563 kJ/mol → low oxide yield (<1%)
   - Reference: Ames et al., Rare Earths IV (1967)

4. **Kinetic Model**:
   - Power-law relationship for sequential oxidation:
     MO₂⁺/M⁺ ≈ α × (MO⁺/M⁺)², where α ≈ 0.1
   - Energy window: reactions favorable at kinetic energy <5 eV
   - Reference: Schneider et al., Materials (2022)

5. **Empirical Estimates** (very low confidence):
   - Species with maxsize ≥ 4 (trioxide, tetraoxide, etc.)
   - Mixed adducts (MOH⁺, MO₂H⁺)
   - Carbides, nitrides, sulfides
   - These lack direct experimental validation

Uncertainty Notes
-----------------
- ★★★★★: International standards, uncertainty <20%
- ★★★★☆: Multiple literature sources, uncertainty 20-50%
- ★★★☆☆: Limited data, uncertainty 50-100%
- ★★☆☆☆: Extrapolated, uncertainty 100-300%
- ★☆☆☆☆: Pure estimate, uncertainty >300%

For instrument-specific calibration, users should measure reference ratios
(e.g., CeO⁺/Ce⁺) on their system and adjust formation factors accordingly.

References
----------
- JJF 1159-2006: Quadrupole ICP-MS Calibration Standard
- GB/T 34826-2017: ICP-MS Performance Testing Method
- Ard et al., J. Phys. Chem. A (2024): Lanthanide oxidation kinetics
- Guan et al., Acta Geochimica (2020): REE oxide interference in geological samples
- Stuewer, Anal. Bioanal. Chem. (1990): GDMS review
"""

import itertools

import numpy as np
import pandas as pd

from interference_calculator.molecule import Molecule, mass_electron, periodic_table


PLASMA_ELEMENTS = ('Ar', 'Ne', 'Kr', 'Xe', 'He')
COMMON_LIGANDS = ('H', 'C', 'N', 'O', 'F', 'S', 'Cl', 'Br', 'I')
BACKGROUND_MOLECULE_BASES = ('H', 'C', 'N', 'O', 'S', 'Cl')

GDMS_FORMATION_FACTORS = {
    # === HIGH CONFIDENCE (★★★★☆) ===
    'atomic': 1.0,  # Reference: isotope abundance is precisely known
    
    # Double charged ions: GDMS typically lower than ICP-MS due to milder
    # energy distribution in glow discharge vs. RF plasma
    # Literature: extrapolated from ICP-MS data (JJF 1159-2006: Ba²⁺/Ba⁺ ≤ 3%)
    # Estimated range: 0.1-1.0%, conservative estimate ~0.5%
    'doubly charged': 5.0e-3,  # Adjusted from 1.0e-2 based on GDMS characteristics
    
    # === MEDIUM CONFIDENCE (★★★☆☆) ===
    # Oxide formation in GDMS is lower than ICP-MS due to:
    # - Lower operating pressure (10-1000 Pa vs. ~1 atm)
    # - Reduced oxygen partial pressure
    # - Different ionization mechanism (sputtering vs. thermal ionization)
    # Estimated range: 0.1-1.0%, typical ~0.5%
    # Note: Element-dependent; CeO/Ce would be higher than BaO/Ba
    'oxide': 1.0e-3,  # Conservative estimate for GDMS (vs. 1-3% in ICP-MS)
    
    # Dioxide: No direct measurements available
    # Estimated using power law: MO₂⁺/M⁺ ≈ 0.1 × (MO⁺/M⁺)²
    # = 0.1 × (1e-3)² = 1e-7, enhanced by factor of 100 for safety margin
    'dioxide': 1.0e-5,  # extrapolated, uncertainty >200%
    
    # Hydride: Lower in GDMS due to vacuum environment
    # Estimated range: 1e-5 to 1e-4
    'hydride': 1.0e-4,  # extrapolated from ICP-MS data
    
    # Hydroxide: Very low in GDMS (no solvent introduction)
    # Surface adsorbed water may contribute minimally
    'hydroxide': 1.0e-5,  # extrapolated, very uncertain
    
    # === LOW CONFIDENCE (★★☆☆☆) ===
    # Nitride, carbide, sulfide: Residual gas and sample impurities
    # No systematic studies for GDMS
    'nitride': 1.0e-4,  # empirical estimate
    'carbide': 1.0e-4,  # empirical estimate
    'sulfide': 1.0e-5,  # empirical estimate
    
    # Halide: Sample contamination or surface residues
    'halide': 1.0e-5,  # empirical estimate
    
    # Plasma adducts (ArO⁺, ArN⁺, etc.): Lower collision frequency in GDMS
    # due to low pressure compared to ICP
    'plasma adduct': 5.0e-5,  # adjusted from 1.0e-4, low-pressure environment
    
    # Background molecules: CO⁺, CN⁺, NO⁺ from residual gases
    'background molecule': 1.0e-5,  # empirical estimate
    
    # Cluster ions (M₂⁺, MM'⁺): Possible during sputtering process
    # Higher probability than in gas-phase ICP
    'cluster': 1.0e-5,  # empirical estimate
    
    # === VERY LOW CONFIDENCE (★☆☆☆☆) ===
    # Extended templates for maxsize >= 4
    # WARNING: These are purely theoretical extrapolations with NO experimental
    # validation. Use results as qualitative screening only, NOT for quantification.
    'trioxide': 1.0e-7,  # extrapolated from dioxide using power law
    'trihydride': 1.0e-6,  # extrapolated, no literature support
    'mixed oxide-hydride': 1.0e-6,  # extrapolated, no literature support
    
    # Extended templates for maxsize >= 5
    'tetraoxide': 1.0e-9,  # extrapolated, extremely uncertain (>1000% error possible)
}

ICP_MS_FORMATION_FACTORS = {
    # === HIGH CONFIDENCE (★★★★★) ===
    # Based on JJF 1159-2006 calibration standard and instrument specifications
    'atomic': 1.0,  # Reference
    
    # Double charged ions: Well-characterized for ICP-MS
    # JJF 1159-2006: Ba²⁺/Ba⁺ ≤ 3.0%
    # Typical range: 0.02-3.56%, depends on second ionization potential
    # Elements with IP₂ < 15.76 eV (Ar IP₁) form significant M²⁺
    'doubly charged': 1.0e-2,  # Conservative: covers most elements except Ba/Sr
    
    # === HIGH CONFIDENCE (★★★★☆) ===
    # Oxide formation: Standard performance metric for ICP-MS
    # JJF 1159-2006: CeO⁺/Ce⁺ ≤ 3.0%
    # Modern instruments: Agilent 7700x ≤ 1.5%, 7700s ≤ 3.0%
    # Thermo iCAP RQ: ≤ 2.0%
    # Range: 0.3-3.0% depending on optimization
    'oxide': 1.0e-2,  # Typical value ~1.5-2.5%
    
    # Dioxide: Limited direct measurements
    # Estimated using empirical power law: MO₂⁺/M⁺ ≈ 0.1 × (MO⁺/M⁺)²
    # For MO⁺/M⁺ = 1%, this gives MO₂⁺/M⁺ ≈ 1e-5
    'dioxide': 1.0e-5,  # extrapolated with moderate confidence
    
    # === MEDIUM CONFIDENCE (★★★☆☆) ===
    # Hydride formation: Depends on solvent composition and plasma conditions
    # Typical range: 1e-5 to 1e-3
    # UH⁺/U⁺ can reach 1e-3 (important for uranium isotope analysis)
    'hydride': 1.0e-4,  # typical for wet plasma conditions
    
    # Hydroxide: Significant in wet plasma (nebulizer introduces H₂O)
    # Range: 1e-4 to 1e-2
    # Higher than hydride due to abundant OH radicals in plasma
    'hydroxide': 1.0e-3,  # typical for aqueous sample introduction
    
    # Nitride, carbide: From atmospheric N₂ and organic solvents
    'nitride': 1.0e-5,  # empirical estimate, limited data
    'carbide': 1.0e-5,  # empirical estimate
    
    # Sulfide: From sample matrix or reagents
    'sulfide': 1.0e-5,  # empirical estimate
    
    # Halide: Enhanced in HCl/HF media
    # MCl⁺ formation significant in chloride-containing samples
    'halide': 1.0e-4,  # elevated due to common use of HCl
    
    # Plasma adducts (ArO⁺, ArN⁺, ArCl⁺): Well-studied in ICP-MS
    # Major source of polyatomic interference below m/z 82
    # ArO⁺ interferes with ⁵⁶Fe, ArCl⁺ with ⁷⁵As
    'plasma adduct': 1.0e-3,  # depends on matrix composition
    
    # Background molecules: CO⁺, CN⁺, NO⁺, O₂⁺, H₂O⁺
    # Common in all ICP-MS analyses
    'background molecule': 1.0e-4,  # typical baseline level
    
    # Cluster ions (M₂⁺, MM'⁺): Low probability in high-temperature plasma
    # May appear at high analyte concentrations
    'cluster': 1.0e-6,  # rare under normal conditions
    
    # === LOW CONFIDENCE (★★☆☆☆) ===
    # Extended templates for maxsize >= 4
    # WARNING: Theoretical extrapolations without experimental validation
    'trioxide': 1.0e-7,  # extrapolated from dioxide
    'trihydride': 1.0e-6,  # extrapolated
    'mixed oxide-hydride': 1.0e-6,  # extrapolated
    
    # Extended templates for maxsize >= 5
    'tetraoxide': 1.0e-9,  # highly speculative
}

SIMS_FORMATION_FACTORS = {
    # === MEDIUM CONFIDENCE (★★★☆☆) ===
    # SIMS interference patterns differ significantly from ICP-MS/GDMS
    # due to surface sputtering mechanism vs. gas-phase ionization
    'atomic': 1.0,  # Reference
    
    # Double charged ions: Generally low in SIMS unless using high-energy primary beam
    # Literature suggests 0.01-0.1% range
    'doubly charged': 1.0e-3,  # conservative estimate
    
    # Oxide formation: Highly variable in SIMS
    # Depends on: primary beam type (O₂⁺ enhances, Cs⁺ suppresses),
    #             sample matrix, surface oxidation state
    # Range: 0.1-10% (much wider than ICP-MS)
    'oxide': 1.0e-2,  # typical for neutral primary beam
    
    # Dioxide: Very limited data
    'dioxide': 1.0e-4,  # extrapolated
    
    # Hydride: Can be significant with H⁺ primary beam or hydrogen-rich matrices
    # Literature: Lancaster et al. (1979) reported up to 1%
    'hydride': 1.0e-3,  # elevated due to surface hydrogen
    
    # Hydroxide: Surface adsorbed water layer contributes
    'hydroxide': 1.0e-4,  # empirical estimate
    
    # Nitride, carbide, sulfide: From sample composition or contamination
    'nitride': 1.0e-4,  # empirical
    'carbide': 1.0e-3,  # can be significant in carbide materials
    'sulfide': 1.0e-4,  # empirical
    
    # Halide: Not applicable for most SIMS configurations (no Ar plasma)
    'halide': 1.0e-4,  # from sample halogen content
    
    # Plasma adducts: NOT APPLICABLE in traditional SIMS (no plasma)
    # Set to very low value as placeholder
    'plasma adduct': 1.0e-6,  # essentially zero, kept for API compatibility
    
    # Background molecules: From residual vacuum gases
    'background molecule': 1.0e-4,  # ultra-high vacuum reduces background
    
    # Cluster ions: SIGNIFICANT in SIMS
    # Sputtering process naturally produces clusters (M₂⁺, M₂O⁺, etc.)
    # Literature: Vlekken et al. (2000), Honda et al. (1978)
    # Range: 1e-4 to 1e-2, much higher than ICP-MS
    'cluster': 1.0e-3,  # typical for many materials
    
    # === VERY LOW CONFIDENCE (★☆☆☆☆) ===
    # Extended templates for maxsize >= 4
    # WARNING: Pure speculation, no SIMS literature support
    'trioxide': 1.0e-6,  # extrapolated
    'trihydride': 1.0e-5,  # extrapolated
    'mixed oxide-hydride': 1.0e-5,  # extrapolated
    
    # Extended templates for maxsize >= 5
    'tetraoxide': 1.0e-8,  # highly speculative
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

    Theoretical Basis
    -----------------
    Formation factors are based on literature data (JJF 1159-2006 standard,
    instrument specifications) and theoretical models (thermodynamics, kinetics).
    See module docstring for detailed references and uncertainty analysis.

    Parameters
    ----------
    atoms : list of str
        Element symbols in the sample (e.g., ['Fe', 'Ni', 'Cr'])
    target : float or str
        Target m/z value or molecular formula (e.g., 56.0 or 'Fe+')
    targetrange : float, optional
        Mass tolerance window (default 0.3 Da)
    charge : tuple or int, optional
        Charge states to consider (default (1, 2) for +1 and +2 ions)
    chargesign : str, optional
        Charge sign: '+', '-', 'o' (neutral) (default '+')
    maxsize : int, optional
        Maximum number of atoms per molecule (default 3)
        Note: maxsize >= 4 species have very low confidence (★☆☆☆☆)
    style : str, optional
        Formula formatting style (see Molecule class)
    risk_preset : str, optional
        Instrument preset: 'gdms', 'icp-ms', or 'sims' (default 'gdms')
    formation_factors : dict, optional
        Override default formation factors with instrument-specific values.
        
        **User Calibration Procedure**:
        1. Measure reference ratios on your instrument:
           - For ICP-MS: CeO⁺/Ce⁺ and Ba²⁺/Ba⁺ using standard solution
           - For GDMS: Similar measurements if standards available
        2. Calculate scaling factor:
           scale = measured_ratio / default_factor
        3. Apply to all factors or specific types:
           custom_factors = {'oxide': 0.015, 'doubly charged': 0.02}
        
        Example::
            
            # Calibrate for high-oxide instrument
            custom = {'oxide': 0.025}  # Measured CeO+/Ce+ = 2.5%
            result = inorganic_interference(
                atoms=['Fe'], target=56.0,
                formation_factors=custom
            )
    
    matrix_atoms, plasma_atoms, background_atoms : list of str, optional
        Explicitly specify atom roles (advanced usage)
    include_background : bool, optional
        Include background molecules like CO⁺, CN⁺ (default True)

    Returns
    -------
    pandas.DataFrame
        Interference candidates sorted by relative risk, with columns:
        - molecule: Chemical formula
        - type: Interference category (oxide, hydride, etc.)
        - charge: Ion charge state
        - mass/charge: Calculated m/z
        - mass/charge diff: Difference from target
        - MRP: Mass resolving power required for separation
        - probability: Isotopic abundance
        - formation factor: Species-specific formation probability
        - relative risk: probability × formation_factor
        - target: Boolean flag for target ion

    Uncertainty Notes
    -----------------
    Formation factors have varying confidence levels:
    - ★★★★★ (ICP-MS oxide/double charge): Based on international standards
    - ★★★☆☆ (GDMS/SIMS): Extrapolated from ICP-MS data
    - ★☆☆☆☆ (maxsize ≥ 4): Pure theoretical estimates, no experimental validation
    
    For quantitative applications, users should calibrate formation factors
    using their specific instrument and operating conditions.

    References
    ----------
    - JJF 1159-2006: Quadrupole ICP-MS Calibration Standard
    - Ard et al., J. Phys. Chem. A (2024): Oxidation kinetics
    - Schneider et al., Materials (2022): Reaction dynamics
    
    See Also
    --------
    interference : General-purpose interference calculator (unrestricted enumeration)
    
    Examples
    --------
    >>> # Basic GDMS screening
    >>> df = inorganic_interference(['Fe', 'Ni', 'Cr'], 56.0)
    >>> 
    >>> # ICP-MS with custom oxide factor
    >>> custom = {'oxide': 0.02}  # High oxide instrument
    >>> df = inorganic_interference(['As'], 75.0, risk_preset='icp-ms',
    ...                             formation_factors=custom)
    >>> 
    >>> # Deep screening with maxsize=5 (low confidence!)
    >>> df = inorganic_interference(['U', 'O'], 238.0, maxsize=5,
    ...                             risk_preset='icp-ms')
    >>> # Warning: trioxide/tetraoxide factors are extrapolated
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
