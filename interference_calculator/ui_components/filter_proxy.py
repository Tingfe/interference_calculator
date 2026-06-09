"""Filter proxy for interference results.

This module provides InterferenceFilterProxy, a QSortFilterProxyModel that
supports advanced query syntax for filtering calculation results.

Query syntax (space-separated tokens, AND logic; | for OR within a token):
- Plain text: case-insensitive substring match in ALL columns.
- col:val      substring match — column 'col' contains 'val'.
- col=val      exact match (case-insensitive).
- col>N, col<N, col>=N, col<=N  numeric comparison.
- col~rx       regex match — 'col' matches Python re pattern.
- -token       negation — reject row if token appears in ANY column.
- expr1|expr2  OR within a single token (e.g. oxide|hydride).
"""

import re

from PyQt5 import QtCore


class InterferenceFilterProxy(QtCore.QSortFilterProxyModel):
    """Filter proxy for interference results supporting query syntax."""
    
    def __init__(self, parent=None):
        QtCore.QSortFilterProxyModel.__init__(self, parent=parent)
        self._filter_text = ''
        self.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

    def set_filter_text(self, text):
        self._filter_text = text
        self.invalidateFilter()

    def lessThan(self, left, right):
        """Compare raw DataFrame values directly — bypass DisplayRole HTML cost."""
        model = self.sourceModel()
        if model is None or not hasattr(model, '_data'):
            return super().lessThan(left, right)
        col = model._data.columns[left.column()]
        lv = model._data.iloc[left.row(), left.column()]
        rv = model._data.iloc[right.row(), right.column()]
        try:
            return float(lv) < float(rv)
        except (ValueError, TypeError):
            pass
        try:
            return str(lv).lower() < str(rv).lower()
        except (ValueError, TypeError):
            return super().lessThan(left, right)

    @staticmethod
    def _token_matches(token, data_row):
        """Return True if a single token matches the row (OR branches resolved)."""
        # Split on | for OR logic — if ANY sub-token matches, accept
        for sub in token.split('|'):
            sub = sub.strip()
            if not sub:
                continue
            if InterferenceFilterProxy._sub_token_matches(sub, data_row):
                return True
        return False

    @staticmethod
    def _sub_token_matches(token, data_row):
        """Match a single (non-OR) token against a row."""
        # Negation
        if token.startswith('-') and len(token) > 1:
            neg_val = token[1:].lower()
            for c in data_row.index:
                if neg_val in str(data_row[c]).lower():
                    return False
            return True

        # Regex operator ~
        if '~' in token:
            col, _, pat = token.partition('~')
            col = col.strip()
            pat = pat.strip()
            if col in data_row.index and pat:
                try:
                    return bool(re.search(pat, str(data_row[col])))
                except re.error:
                    return False
            return True

        # Exact match =
        if '=' in token and '>=' not in token and '<=' not in token:
            col, _, val = token.partition('=')
            col = col.strip()
            val = val.strip()
            if col in data_row.index:
                return str(data_row[col]).lower() == val.lower()
            return True

        # Comparison operators (longer ops first)
        for op in ('>=', '<='):
            if op in token:
                col, _, val_str = token.partition(op)
                col = col.strip()
                if col in data_row.index:
                    cell_val = data_row[col]
                    if cell_val == '' or (isinstance(cell_val, float) and np.isnan(cell_val)):
                        return False
                    try:
                        cv = float(cell_val)
                        qv = float(val_str)
                        if op == '>=':
                            return cv >= qv
                        if op == '<=':
                            return cv <= qv
                    except (ValueError, TypeError):
                        pass
                return True

        for op in ('>', '<'):
            if op in token:
                col, _, val_str = token.partition(op)
                col = col.strip()
                if col in data_row.index:
                    cell_val = data_row[col]
                    if cell_val == '' or (isinstance(cell_val, float) and np.isnan(cell_val)):
                        return False
                    try:
                        cv = float(cell_val)
                        qv = float(val_str)
                        if op == '>':
                            return cv > qv
                        if op == '<':
                            return cv < qv
                    except (ValueError, TypeError):
                        pass
                return True

        # Colon operator — substring match on named column
        if ':' in token:
            col, _, val = token.partition(':')
            col = col.strip()
            val = val.strip()
            if col in data_row.index:
                return val.lower() in str(data_row[col]).lower()
            return True

        # Default: search ALL columns
        token_lower = token.lower()
        for c in data_row.index:
            if token_lower in str(data_row[c]).lower():
                return True
        return False

    def filterAcceptsRow(self, source_row, source_parent):
        if not self._filter_text.strip():
            return True

        model = self.sourceModel()
        if model is None or not hasattr(model, '_data') or model._data is None:
            return True

        tokens = self._filter_text.strip().split()
        data_row = model._data.iloc[source_row]

        # AND logic across space-separated tokens
        for token in tokens:
            if not self._token_matches(token, data_row):
                return False

        return True


# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'np':
        import numpy as np
        return np
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
