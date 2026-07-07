"""Background worker for interference calculation.

This module provides CalculationWorker, a QObject designed to run in a
QThread for non-blocking interference calculations with progress reporting.
"""

import numpy as np
from PyQt5 import QtCore


class CalculationWorker(QtCore.QObject):
    """Background worker for interference calculation."""

    progress = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal(object)  # pd.DataFrame
    error = QtCore.pyqtSignal(str)

    def __init__(self, atoms, mz, targetrange, maxsize, charge, chargesign,
                 risk_preset=None, instrument_mrp=0, language='en',
                 sample_profile=None):
        QtCore.QObject.__init__(self)
        self.atoms = atoms
        self.mz = mz
        self.targetrange = targetrange
        self.maxsize = maxsize
        self.charge = charge
        self.chargesign = chargesign
        self.risk_preset = risk_preset
        self.instrument_mrp = instrument_mrp
        self.language = language
        self.sample_profile = sample_profile
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    @QtCore.pyqtSlot()
    def run(self):
        """Perform the calculation in a background thread."""
        try:
            self.progress.emit(0)
            if self._cancelled:
                return
            if self.risk_preset:
                from interference_calculator.inorganic import inorganic_interference
                data = inorganic_interference(
                    self.atoms, self.mz, targetrange=self.targetrange,
                    maxsize=self.maxsize, charge=self.charge,
                    chargesign=self.chargesign, risk_preset=self.risk_preset,
                    sample_profile=self.sample_profile)
            if self._cancelled:
                return

            # ── Post-process DataFrame (was in _on_calc_finished) ──
            target_mask = data['target'].astype(bool)
            if target_mask.any():
                target_mz = data.loc[target_mask, 'mass/charge'].iat[0]
            else:
                target_mz = None

            if target_mz:
                data.attrs['delta_reference'] = 'theoretical_target_mz'
                data.attrs['delta_reference_mz'] = float(target_mz)
                data['Δppm'] = data['mass/charge diff'] / target_mz * 1e6
            else:
                data.attrs['delta_reference'] = 'none'
                data.attrs['delta_reference_mz'] = np.nan
                data['Δppm'] = np.nan

            if self.instrument_mrp:
                data['resolved'] = (data['MRP'] <= self.instrument_mrp).astype(object)
                data.loc[target_mask, 'resolved'] = ''
            else:
                data['resolved'] = ''

            data.index = range(1, data.shape[0] + 1)
            # ── End post-process ──

            self.progress.emit(100)
            self.finished.emit(data)
        except Exception as exc:
            self.error.emit(str(exc))


# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'np':
        import numpy as np
        return np
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
