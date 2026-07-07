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

import copy
import itertools
from collections import Counter

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

SAMPLE_ACTIVITY_LEVELS = {
    'absent': 0.0,
    'none': 0.0,
    'ultra_trace': 1.0e-9,
    'ultra-trace': 1.0e-9,
    'very_low': 1.0e-8,
    'very-low': 1.0e-8,
    'trace': 1.0e-6,
    'low': 1.0e-4,
    'medium': 1.0e-2,
    'high': 1.0e-1,
    'major': 1.0,
    'matrix': 1.0,
    'plasma': 1.0,
}

GDMS_BACKGROUND_DEFAULT = {
    'O': 'medium',
    'H': 'medium',
    'C': 'low',
    'N': 'low',
    'Cl': 'very_low',
    'S': 'very_low',
}

GDMS_BACKGROUND_LOW = {
    'O': 'low',
    'H': 'low',
    'C': 'low',
    'N': 'very_low',
    'Cl': 'very_low',
    'S': 'very_low',
}

ARGON_PLASMA = {'Ar': 'plasma'}

# These sample profiles are qualitative screening priors, not certified
# composition limits. They encode common GDMS use cases: the dominant matrix,
# likely alloying/trace elements, residual-gas/background chemistry, and Ar
# plasma. Users should replace ppm values with their own material certificate
# or preliminary GDMS result when quantitative ranking matters.
SAMPLE_PROFILE_PRESETS = {
    'high-purity-aluminum': {
        'name': 'High purity aluminum',
        'label_en': 'High purity Al',
        'label_zh': '高纯铝',
        'matrix': {'Al': 0.99999},
        'expected_impurities_ppm': {
            'Fe': 10.0,
            'Si': 20.0,
            'Mg': 5.0,
            'Cu': 1.0,
        },
        'background': GDMS_BACKGROUND_DEFAULT,
        'plasma': ARGON_PLASMA,
        'description': 'Pure metal matrix with common Al impurities and GDMS residual gas species.',
        'description_zh': '单质铝基体，包含常见铝中杂质和 GDMS 残余气体背景。',
        'unknown_element_activity': 'trace',
    },
    'high-purity-copper': {
        'name': 'High purity copper',
        'label_en': 'High purity Cu',
        'label_zh': '高纯铜',
        'matrix': {'Cu': 0.99999},
        'expected_impurities_ppm': {
            'Ag': 10.0,
            'Fe': 5.0,
            'Ni': 5.0,
            'Zn': 5.0,
            'Pb': 2.0,
            'Sn': 2.0,
        },
        'background': GDMS_BACKGROUND_LOW,
        'plasma': ARGON_PLASMA,
        'description': 'Pure Cu matrix with common metallic impurities.',
        'description_zh': '单质铜基体，包含常见金属杂质。',
        'unknown_element_activity': 'trace',
    },
    'high-purity-iron': {
        'name': 'High purity iron',
        'label_en': 'High purity Fe',
        'label_zh': '高纯铁',
        'matrix': {'Fe': 0.9999},
        'expected_impurities_ppm': {
            'Mn': 20.0,
            'Si': 20.0,
            'Ni': 10.0,
            'Cr': 10.0,
            'Cu': 5.0,
        },
        'background': GDMS_BACKGROUND_DEFAULT,
        'plasma': ARGON_PLASMA,
        'description': 'Pure Fe matrix with common steelmaking residual elements.',
        'description_zh': '单质铁基体，包含钢铁材料常见残留元素。',
        'unknown_element_activity': 'trace',
    },
    'high-purity-nickel': {
        'name': 'High purity nickel',
        'label_en': 'High purity Ni',
        'label_zh': '高纯镍',
        'matrix': {'Ni': 0.9999},
        'expected_impurities_ppm': {
            'Fe': 20.0,
            'Co': 20.0,
            'Cu': 10.0,
            'Cr': 10.0,
            'Mn': 5.0,
            'Si': 5.0,
        },
        'background': GDMS_BACKGROUND_LOW,
        'plasma': ARGON_PLASMA,
        'description': 'Pure Ni matrix with Fe/Co/Cu/Cr residuals commonly reviewed in Ni materials.',
        'description_zh': '单质镍基体，包含镍材料中常关注的 Fe/Co/Cu/Cr 等残留。',
        'unknown_element_activity': 'trace',
    },
    'high-purity-titanium': {
        'name': 'High purity titanium',
        'label_en': 'High purity Ti',
        'label_zh': '高纯钛',
        'matrix': {'Ti': 0.999},
        'expected_impurities_ppm': {
            'Fe': 50.0,
            'Al': 20.0,
            'V': 20.0,
            'Ni': 10.0,
            'Cr': 10.0,
            'Si': 10.0,
            'Mo': 5.0,
        },
        'background': {
            'O': 'medium',
            'H': 'low',
            'C': 'low',
            'N': 'low',
            'Cl': 'very_low',
            'S': 'very_low',
        },
        'plasma': ARGON_PLASMA,
        'description': 'Ti matrix with interstitial/background O/H/C/N and common metallic residuals.',
        'description_zh': '钛基体，考虑 O/H/C/N 间隙/背景元素及常见金属残留。',
        'unknown_element_activity': 'trace',
    },
    'high-purity-silicon': {
        'name': 'High purity silicon',
        'label_en': 'High purity Si',
        'label_zh': '高纯硅',
        'matrix': {'Si': 0.99999},
        'expected_impurities_ppm': {
            'B': 1.0,
            'P': 1.0,
            'Al': 2.0,
            'Fe': 2.0,
            'Ca': 2.0,
            'Na': 2.0,
            'K': 1.0,
            'Cu': 1.0,
        },
        'background': {
            'O': 'medium',
            'H': 'low',
            'C': 'low',
            'N': 'very_low',
            'Cl': 'very_low',
            'S': 'very_low',
        },
        'plasma': ARGON_PLASMA,
        'description': 'Si matrix with semiconductor-relevant dopants and metallic impurities.',
        'description_zh': '硅基体，包含半导体材料常关注的掺杂/金属杂质。',
        'unknown_element_activity': 'trace',
    },
    'high-purity-magnesium': {
        'name': 'High purity magnesium',
        'label_en': 'High purity Mg',
        'label_zh': '高纯镁',
        'matrix': {'Mg': 0.9999},
        'expected_impurities_ppm': {
            'Al': 20.0,
            'Zn': 20.0,
            'Mn': 10.0,
            'Fe': 5.0,
            'Si': 5.0,
            'Ca': 5.0,
            'Cu': 2.0,
            'Ni': 1.0,
        },
        'background': GDMS_BACKGROUND_DEFAULT,
        'plasma': ARGON_PLASMA,
        'description': 'Pure Mg matrix with common light-alloy residuals.',
        'description_zh': '镁基体，包含轻合金材料常见残留元素。',
        'unknown_element_activity': 'trace',
    },
    'aluminum-alloy': {
        'name': 'Aluminum alloy',
        'label_en': 'Al alloy',
        'label_zh': '铝合金',
        'matrix': {
            'Al': 0.97,
            'Mg': 0.01,
            'Si': 0.008,
            'Cu': 0.005,
            'Mn': 0.005,
            'Zn': 0.005,
            'Fe': 0.005,
            'Ti': 0.001,
        },
        'background': GDMS_BACKGROUND_DEFAULT,
        'plasma': ARGON_PLASMA,
        'description': 'Generic Al-alloy screening profile covering common alloying additions.',
        'description_zh': '通用铝合金筛查画像，覆盖常见合金化元素。',
        'unknown_element_activity': 'trace',
    },
    'stainless-steel': {
        'name': 'Stainless steel',
        'label_en': 'Stainless steel',
        'label_zh': '不锈钢',
        'matrix': {
            'Fe': 0.68,
            'Cr': 0.18,
            'Ni': 0.10,
            'Mn': 0.02,
            'Mo': 0.02,
        },
        'expected_impurities_ppm': {
            'Si': 5000.0,
            'C': 800.0,
            'P': 450.0,
            'S': 300.0,
            'Cu': 3000.0,
            'Co': 1000.0,
        },
        'background': {
            'O': 'low',
            'H': 'low',
            'N': 'low',
            'Cl': 'very_low',
        },
        'plasma': ARGON_PLASMA,
        'description': 'Fe-Cr-Ni matrix with common stainless steel alloying and residual elements.',
        'description_zh': 'Fe-Cr-Ni 基体，包含不锈钢常见合金化及残留元素。',
        'unknown_element_activity': 'trace',
    },
    'nickel-base-alloy': {
        'name': 'Nickel-base alloy',
        'label_en': 'Ni-base alloy',
        'label_zh': '镍基合金',
        'matrix': {
            'Ni': 0.55,
            'Cr': 0.18,
            'Fe': 0.10,
            'Mo': 0.06,
            'Co': 0.03,
            'Nb': 0.03,
            'Al': 0.01,
            'Ti': 0.01,
        },
        'expected_impurities_ppm': {
            'Mn': 5000.0,
            'Si': 3000.0,
            'Cu': 2000.0,
            'C': 800.0,
            'P': 300.0,
            'S': 150.0,
        },
        'background': {
            'O': 'low',
            'H': 'low',
            'N': 'low',
            'Cl': 'very_low',
        },
        'plasma': ARGON_PLASMA,
        'description': 'Generic superalloy-style Ni-Cr-Fe-Mo/Nb screening profile.',
        'description_zh': '通用镍基高温合金式 Ni-Cr-Fe-Mo/Nb 筛查画像。',
        'unknown_element_activity': 'trace',
    },
    'copper-base-alloy': {
        'name': 'Copper-base alloy',
        'label_en': 'Cu-base alloy',
        'label_zh': '铜基合金',
        'matrix': {
            'Cu': 0.92,
            'Zn': 0.04,
            'Sn': 0.02,
            'Ni': 0.01,
            'Pb': 0.005,
            'Fe': 0.003,
        },
        'expected_impurities_ppm': {
            'Al': 1000.0,
            'Mn': 1000.0,
            'Si': 500.0,
            'Ag': 500.0,
        },
        'background': GDMS_BACKGROUND_LOW,
        'plasma': ARGON_PLASMA,
        'description': 'Generic brass/bronze-style Cu alloy screening profile.',
        'description_zh': '通用黄铜/青铜式铜基合金筛查画像。',
        'unknown_element_activity': 'trace',
    },
    'silicate-glass': {
        'name': 'Silicate or glass matrix',
        'label_en': 'Silicate / glass',
        'label_zh': '硅酸盐 / 玻璃',
        'matrix': {
            'O': 0.50,
            'Si': 0.35,
            'Al': 0.05,
            'Na': 0.04,
            'Ca': 0.03,
            'Mg': 0.02,
            'K': 0.01,
        },
        'expected_impurities_ppm': {
            'Fe': 1000.0,
            'Ti': 500.0,
            'Mn': 100.0,
            'P': 100.0,
            'B': 100.0,
        },
        'background': {
            'H': 'low',
            'C': 'low',
            'N': 'very_low',
            'Cl': 'very_low',
            'S': 'very_low',
        },
        'plasma': ARGON_PLASMA,
        'description': 'Oxide/silicate matrix where O and Si are true matrix components.',
        'description_zh': '氧化物/硅酸盐基体，O 和 Si 作为真实基体参与先验。',
        'unknown_element_activity': 'trace',
    },
    'graphite-carbon': {
        'name': 'Graphite or carbon matrix',
        'label_en': 'Graphite / carbon',
        'label_zh': '石墨 / 碳基体',
        'matrix': {'C': 0.999},
        'expected_impurities_ppm': {
            'B': 10.0,
            'Si': 10.0,
            'Fe': 5.0,
            'Ca': 5.0,
            'Al': 5.0,
            'Na': 2.0,
            'K': 2.0,
        },
        'background': {
            'O': 'medium',
            'H': 'low',
            'N': 'low',
            'S': 'very_low',
            'Cl': 'very_low',
        },
        'plasma': ARGON_PLASMA,
        'description': 'Carbon matrix with common ash-forming impurities and surface oxygen/hydrogen.',
        'description_zh': '碳基体，包含常见灰分杂质及表面 O/H 背景。',
        'unknown_element_activity': 'trace',
    },
}

SAMPLE_PROFILE_ALIASES = {
    'high_purity_aluminum': 'high-purity-aluminum',
    'high purity aluminum': 'high-purity-aluminum',
    'high-purity-aluminium': 'high-purity-aluminum',
    'high_purity_aluminium': 'high-purity-aluminum',
    'high purity aluminium': 'high-purity-aluminum',
    'pure-aluminum': 'high-purity-aluminum',
    'pure_aluminum': 'high-purity-aluminum',
    'pure aluminium': 'high-purity-aluminum',
    'pure-aluminium': 'high-purity-aluminum',
    'aluminum': 'high-purity-aluminum',
    'aluminium': 'high-purity-aluminum',
    'al': 'high-purity-aluminum',
    'high_purity_copper': 'high-purity-copper',
    'high purity copper': 'high-purity-copper',
    'pure-copper': 'high-purity-copper',
    'pure_copper': 'high-purity-copper',
    'copper': 'high-purity-copper',
    'cu': 'high-purity-copper',
    'high_purity_iron': 'high-purity-iron',
    'high purity iron': 'high-purity-iron',
    'pure-iron': 'high-purity-iron',
    'pure_iron': 'high-purity-iron',
    'iron': 'high-purity-iron',
    'fe': 'high-purity-iron',
    'high_purity_nickel': 'high-purity-nickel',
    'high purity nickel': 'high-purity-nickel',
    'pure-nickel': 'high-purity-nickel',
    'pure_nickel': 'high-purity-nickel',
    'nickel': 'high-purity-nickel',
    'ni': 'high-purity-nickel',
    'high_purity_titanium': 'high-purity-titanium',
    'high purity titanium': 'high-purity-titanium',
    'pure-titanium': 'high-purity-titanium',
    'pure_titanium': 'high-purity-titanium',
    'titanium': 'high-purity-titanium',
    'ti': 'high-purity-titanium',
    'high_purity_silicon': 'high-purity-silicon',
    'high purity silicon': 'high-purity-silicon',
    'pure-silicon': 'high-purity-silicon',
    'pure_silicon': 'high-purity-silicon',
    'silicon': 'high-purity-silicon',
    'si': 'high-purity-silicon',
    'high_purity_magnesium': 'high-purity-magnesium',
    'high purity magnesium': 'high-purity-magnesium',
    'pure-magnesium': 'high-purity-magnesium',
    'pure_magnesium': 'high-purity-magnesium',
    'magnesium': 'high-purity-magnesium',
    'mg': 'high-purity-magnesium',
    'aluminium-alloy': 'aluminum-alloy',
    'aluminium_alloy': 'aluminum-alloy',
    'aluminum_alloy': 'aluminum-alloy',
    'al alloy': 'aluminum-alloy',
    'al-alloy': 'aluminum-alloy',
    'stainless': 'stainless-steel',
    'stainless_steel': 'stainless-steel',
    'stainless steel': 'stainless-steel',
    'steel': 'stainless-steel',
    'nickel_base_alloy': 'nickel-base-alloy',
    'nickel base alloy': 'nickel-base-alloy',
    'nickel alloy': 'nickel-base-alloy',
    'ni-base-alloy': 'nickel-base-alloy',
    'ni_base_alloy': 'nickel-base-alloy',
    'copper_base_alloy': 'copper-base-alloy',
    'copper base alloy': 'copper-base-alloy',
    'copper alloy': 'copper-base-alloy',
    'cu-base-alloy': 'copper-base-alloy',
    'cu_base_alloy': 'copper-base-alloy',
    'brass': 'copper-base-alloy',
    'bronze': 'copper-base-alloy',
    'silicate': 'silicate-glass',
    'silicate_glass': 'silicate-glass',
    'silicate glass': 'silicate-glass',
    'glass': 'silicate-glass',
    'graphite': 'graphite-carbon',
    'carbon': 'graphite-carbon',
    'graphite_carbon': 'graphite-carbon',
    'graphite carbon': 'graphite-carbon',
}


def inorganic_interference(atoms, target, targetrange=0.3, charge=(1, 2),
                           chargesign='+', maxsize=3, style='plain',
                           risk_preset='gdms', formation_factors=None,
                           matrix_atoms=None, plasma_atoms=None,
                           background_atoms=None, include_background=True,
                           sample_profile=None):
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
    sample_profile : dict or str, optional
        Sample-specific prior information used to weight candidate risk.
        The built-in ``'high-purity-aluminum'`` preset treats Al as matrix,
        common alloying/impurity elements as ppm-level species, and O/H/C/N/Cl/S
        as background activity terms. A custom profile can provide
        ``matrix``, ``expected_impurities_ppm``, ``background``, ``plasma``, and
        ``unknown_element_activity`` fields.

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
          (or sample-weighted risk when sample_profile is supplied)
        - sample prior: Sample/source activity prior (when sample_profile is supplied)
        - expected relative intensity: Weighted risk score (when sample_profile is supplied)
        - risk rationale: Elements and activity terms used in the weighting
          (when sample_profile is supplied)
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
    sample_context = _sample_context(sample_profile)
    if atoms is None and sample_context is not None:
        atoms = []
    atoms = _normalize_atoms(atoms)
    if sample_context is not None:
        atoms = _normalize_atoms(list(atoms) + sample_context['atoms'])
    charges = _normalize_charges(charge)
    risk_factors = _formation_factors(risk_preset, formation_factors)
    if chargesign not in ('+', '-', 'o', '0'):
        raise ValueError('chargesign must be either "+", "-", "o", or "0".')

    target_info = _target_info(target, charges, chargesign)
    candidate_matrix_atoms = matrix_atoms
    candidate_plasma_atoms = plasma_atoms
    candidate_background_atoms = background_atoms
    if sample_context is not None:
        if candidate_matrix_atoms is None:
            candidate_matrix_atoms = sample_context['sample_atoms']
        if candidate_plasma_atoms is None:
            candidate_plasma_atoms = sample_context['plasma_atoms']
        if candidate_background_atoms is None:
            candidate_background_atoms = sample_context['background_atoms']

    candidates = _candidate_formulas(
        atoms, charges, chargesign, maxsize,
        matrix_atoms=candidate_matrix_atoms, plasma_atoms=candidate_plasma_atoms,
        background_atoms=candidate_background_atoms,
        include_background=include_background,
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
        unweighted_risk = molecule.abundance * formation_factor
        sample_prior, risk_rationale = _sample_prior(parts, sample_context)
        weighted_risk = unweighted_risk * sample_prior
        row = {
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
            'relative risk': weighted_risk,
            'target': False,
        }
        if sample_context is not None:
            row.update({
                'sample prior': sample_prior,
                'unweighted relative risk': unweighted_risk,
                'expected relative intensity': weighted_risk,
                'risk rationale': risk_rationale,
            })
        rows.append(row)

    columns = [
        'molecule', 'type', 'charge', 'mass/charge', 'mass/charge diff',
        'mass uncertainty', 'm/z uncertainty', 'MRP', 'probability',
        'formation factor', 'relative risk', 'target',
    ]
    if sample_context is not None:
        columns = columns[:-1] + [
            'sample prior', 'unweighted relative risk',
            'expected relative intensity', 'risk rationale',
        ] + columns[-1:]
    data = pd.DataFrame(rows, columns=columns)
    if not data.empty and target_info['has_target']:
        data = data.assign(_abs_diff=data['mass/charge diff'].abs())
        data = data.sort_values(['_abs_diff', 'relative risk'], ascending=[True, False])
        data = data.drop(columns='_abs_diff')
    elif not data.empty and sample_context is not None:
        data = data.sort_values('relative risk', ascending=False)

    if target_info['has_target']:
        target_payload = {
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
        }
        if sample_context is not None:
            target_payload.update({
                'sample prior': 1.0,
                'unweighted relative risk': target_info['abundance'],
                'expected relative intensity': target_info['abundance'],
                'risk rationale': 'target ion',
            })
        target_row = pd.DataFrame([target_payload], columns=columns)
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


def _sample_context(sample_profile):
    if sample_profile is None:
        return None
    profile = _resolve_sample_profile(sample_profile)
    activities = {}
    roles = {}
    atoms = []

    def add_atom(element, activity, role):
        if not element:
            return
        value = max(float(activity), 0.0)
        activities[element] = value
        roles[element] = role
        if element not in atoms:
            atoms.append(element)

    for element, value in _profile_mapping(profile.get('matrix')).items():
        add_atom(element, _activity_value(value, default='matrix'), 'matrix')

    impurity_sources = (
        'expected_impurities_ppm', 'impurities_ppm',
        'expected_impurities', 'impurities',
    )
    for key in impurity_sources:
        for element, value in _profile_mapping(profile.get(key)).items():
            if key.endswith('_ppm'):
                activity = _ppm_activity(value)
            else:
                activity = _impurity_activity(value)
            add_atom(element, activity, 'impurity')

    for element, value in _profile_mapping(profile.get('background')).items():
        add_atom(element, _activity_value(value, default='medium'), 'background')

    for element, value in _profile_mapping(profile.get('plasma')).items():
        add_atom(element, _activity_value(value, default='plasma'), 'plasma')

    direct_keys = ('element_activity', 'element_activities', 'element_weights')
    for key in direct_keys:
        for element, value in _profile_mapping(profile.get(key)).items():
            add_atom(element, _activity_value(value, default='trace'), 'specified')

    default_activity = _activity_value(
        profile.get('unknown_element_activity',
                    profile.get('default_activity', 'trace')),
        default='trace',
    )
    return {
        'activities': activities,
        'roles': roles,
        'atoms': atoms,
        'sample_atoms': [
            atom for atom in atoms
            if roles.get(atom) in ('matrix', 'impurity', 'specified')
        ],
        'background_atoms': [
            atom for atom in atoms
            if roles.get(atom) == 'background'
        ],
        'plasma_atoms': [
            atom for atom in atoms
            if roles.get(atom) == 'plasma'
        ],
        'default_activity': default_activity,
    }


def _resolve_sample_profile(sample_profile):
    if isinstance(sample_profile, str):
        key = sample_profile.strip().lower().replace('_', '-')
        key = SAMPLE_PROFILE_ALIASES.get(key, key)
        try:
            return copy.deepcopy(SAMPLE_PROFILE_PRESETS[key])
        except KeyError:
            msg = 'sample_profile must be a dict or one of {}.'.format(
                ', '.join(sorted(SAMPLE_PROFILE_PRESETS))
            )
            raise ValueError(msg)
    if not isinstance(sample_profile, dict):
        raise TypeError('sample_profile must be a dict, str, or None.')
    return copy.deepcopy(sample_profile)


def _profile_mapping(value):
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        return {value: None}
    try:
        return {element: None for element in value}
    except TypeError:
        return {}


def _activity_value(value, default='trace'):
    if value is None:
        return SAMPLE_ACTIVITY_LEVELS[default]
    if isinstance(value, dict):
        for key in ('activity', 'fraction', 'weight', 'level'):
            if key in value:
                return _activity_value(value[key], default=default)
        if 'ppm' in value:
            return _ppm_to_activity(value['ppm'])
        return SAMPLE_ACTIVITY_LEVELS[default]
    if isinstance(value, str):
        key = value.strip().lower().replace(' ', '_')
        if key in SAMPLE_ACTIVITY_LEVELS:
            return SAMPLE_ACTIVITY_LEVELS[key]
        return float(key)
    return float(value)


def _impurity_activity(value):
    if value is None:
        return SAMPLE_ACTIVITY_LEVELS['trace']
    if isinstance(value, dict):
        if 'ppm' in value:
            return _ppm_to_activity(value['ppm'])
        if 'fraction' in value:
            return _activity_value(value['fraction'])
        if 'activity' in value:
            return _activity_value(value['activity'])
        return SAMPLE_ACTIVITY_LEVELS['trace']
    if isinstance(value, str):
        key = value.strip().lower().replace(' ', '_')
        if key in SAMPLE_ACTIVITY_LEVELS:
            return SAMPLE_ACTIVITY_LEVELS[key]
        return _ppm_to_activity(float(key))
    numeric = float(value)
    if numeric > 1.0:
        return _ppm_to_activity(numeric)
    return max(numeric, 0.0)


def _ppm_activity(value):
    if value is None:
        return SAMPLE_ACTIVITY_LEVELS['trace']
    if isinstance(value, dict) and 'ppm' in value:
        return _ppm_to_activity(value['ppm'])
    return _ppm_to_activity(value)


def _ppm_to_activity(value):
    return max(float(value), 0.0) * 1.0e-6


def _sample_prior(parts, sample_context):
    if sample_context is None:
        return 1.0, ''
    counts = Counter(_element_from_isotope(part) for part in parts)
    prior = 1.0
    rationale = []
    for element in sorted(counts):
        count = counts[element]
        activity = sample_context['activities'].get(
            element, sample_context['default_activity'])
        role = sample_context['roles'].get(element, 'unknown')
        prior *= activity ** count
        suffix = '^{}'.format(count) if count > 1 else ''
        rationale.append('{}:{}={}{}'.format(
            element, role, _format_activity(activity), suffix))
    return prior, '; '.join(rationale)


def _element_from_isotope(isotope):
    text = str(isotope)
    while text and text[0].isdigit():
        text = text[1:]
    return text


def _format_activity(value):
    return '{:.3g}'.format(value)


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
