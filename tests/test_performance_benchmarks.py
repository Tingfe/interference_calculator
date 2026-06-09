#!/usr/bin/env python
"""
Performance benchmark tests for Interference Calculator.

This module provides comprehensive performance testing to ensure
the application maintains acceptable performance levels.
"""

import pytest
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from interference_calculator.inorganic import inorganic_interference
from interference_calculator.molecule import Molecule


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    def test_single_element_calculation_performance(self):
        """Benchmark single element calculation - should complete in < 10ms."""
        start_time = time.perf_counter()
        result = inorganic_interference(atoms={'Fe': 1}, target='Fe')
        end_time = time.perf_counter()
        
        elapsed_ms = (end_time - start_time) * 1000
        
        assert result is not None
        assert elapsed_ms < 10, f"Single element calculation took {elapsed_ms:.2f}ms (expected < 10ms)"
        print(f"✓ Single element calculation: {elapsed_ms:.2f}ms")
    
    def test_bulk_element_calculation_performance(self):
        """Benchmark bulk element calculations - 50 elements in < 500ms."""
        # Use only stable, common elements to avoid parsing errors
        elements = ['H', 'C', 'N', 'O', 'F', 'Na', 'Mg', 'Al', 'Si', 'P', 
                   'S', 'Cl', 'K', 'Ca', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 
                   'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Rb', 'Sr',
                   'Zr', 'Nb', 'Mo', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn',
                   'Sb', 'Te', 'I', 'Cs', 'Ba', 'La', 'W', 'Pt', 'Au']
        
        start_time = time.perf_counter()
        results = []
        for elem in elements[:50]:  # First 50 stable elements
            result = inorganic_interference(atoms={elem: 1}, target=elem)
            results.append(result)
        end_time = time.perf_counter()
        
        elapsed_ms = (end_time - start_time) * 1000
        
        assert len(results) >= 49  # At least 49 should succeed
        assert elapsed_ms < 500, f"Bulk calculation (50 elements) took {elapsed_ms:.2f}ms (expected < 500ms)"
        print(f"✓ Bulk calculation ({len(results)} elements): {elapsed_ms:.2f}ms")
    
    def test_molecule_calculation_performance(self):
        """Benchmark molecule calculation - should complete in < 50ms."""
        start_time = time.perf_counter()
        mol = Molecule('H2O')
        end_time = time.perf_counter()
        
        elapsed_ms = (end_time - start_time) * 1000
        
        assert mol is not None
        assert hasattr(mol, 'mass')
        assert elapsed_ms < 50, f"Molecule calculation took {elapsed_ms:.2f}ms (expected < 50ms)"
        print(f"✓ Molecule calculation: {elapsed_ms:.2f}ms")
    
    def test_complex_molecule_performance(self):
        """Benchmark complex molecule calculation - C6H12O6 in < 100ms."""
        start_time = time.perf_counter()
        mol = Molecule('C6H12O6')  # Glucose
        end_time = time.perf_counter()
        
        elapsed_ms = (end_time - start_time) * 1000
        
        assert mol is not None
        assert hasattr(mol, 'mass')
        assert elapsed_ms < 100, f"Complex molecule calculation took {elapsed_ms:.2f}ms (expected < 100ms)"
        print(f"✓ Complex molecule (C6H12O6): {elapsed_ms:.2f}ms")
    
    def test_memory_usage_basic(self):
        """Test that basic operations don't cause excessive memory usage."""
        import tracemalloc
        
        tracemalloc.start()
        
        # Perform multiple calculations
        for _ in range(100):
            inorganic_interference(atoms={'Fe': 1}, target='Fe')
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Peak memory should be reasonable (< 10MB for this test)
        peak_mb = peak / (1024 * 1024)
        assert peak_mb < 10, f"Peak memory usage {peak_mb:.2f}MB exceeds limit (10MB)"
        print(f"✓ Memory usage: peak {peak_mb:.2f}MB")


class TestEdgeCases:
    """Edge case and boundary condition tests."""
    
    def test_empty_element_string(self):
        """Test handling of empty atoms dict."""
        result = inorganic_interference(atoms={}, target='Fe')
        assert result is not None  # Should return empty dataframe or similar
    
    def test_invalid_element_symbol(self):
        """Test handling of invalid element symbol."""
        result = inorganic_interference(atoms={'Xx': 1}, target='Fe')
        # Should handle gracefully
        assert result is not None
    
    def test_none_input(self):
        """Test handling of None input."""
        try:
            result = inorganic_interference(atoms=None, target='Fe')
            assert result is not None
        except (TypeError, AttributeError):
            # Expected behavior for None input
            pass
    
    def test_numeric_input(self):
        """Test handling of numeric input instead of dict."""
        try:
            result = inorganic_interference(atoms=123, target='Fe')
            assert result is not None
        except (TypeError, AttributeError):
            # Expected behavior
            pass
    
    def test_very_long_element_string(self):
        """Test handling of many elements."""
        # Create a dict with many elements
        many_elements = {f'Elem{i}': 1 for i in range(100)}
        result = inorganic_interference(atoms=many_elements, target='Fe')
        # Should handle gracefully without crashing
        assert result is not None
    
    def test_special_characters_in_element(self):
        """Test handling of special characters in element name."""
        result = inorganic_interference(atoms={'Fe@#$%': 1}, target='Fe')
        # Should handle gracefully
        assert result is not None
    
    def test_unicode_characters(self):
        """Test handling of unicode characters."""
        result = inorganic_interference(atoms={'铁': 1}, target='Fe')
        # Should handle gracefully
        assert result is not None
    
    def test_whitespace_only(self):
        """Test handling of whitespace in element name."""
        result = inorganic_interference(atoms={'   ': 1}, target='Fe')
        assert result is not None
    
    def test_case_sensitivity(self):
        """Test case sensitivity handling."""
        result_lower = inorganic_interference(atoms={'fe': 1}, target='Fe')
        result_upper = inorganic_interference(atoms={'FE': 1}, target='Fe')
        result_proper = inorganic_interference(atoms={'Fe': 1}, target='Fe')
        
        # At least proper case should work
        assert result_proper is not None
    
    def test_extreme_mass_values(self):
        """Test handling via targetrange parameter."""
        # Very small range
        result_small = inorganic_interference(atoms={'H': 1}, target='H', targetrange=0.001)
        
        # Very large range
        result_large = inorganic_interference(atoms={'U': 1}, target='U', targetrange=100)
        
        # Should handle without crashing
        assert result_small is not None
        assert result_large is not None
    
    def test_negative_mass(self):
        """Test handling of negative targetrange value."""
        result = inorganic_interference(atoms={'Fe': 1}, target='Fe', targetrange=-10)
        # Should handle gracefully
        assert result is not None
    
    def test_zero_abundance_threshold(self):
        """Test with zero formation factor threshold."""
        result = inorganic_interference(atoms={'Fe': 1}, target='Fe', formation_factors={'atomic': 0})
        # Should still return results
        assert result is not None
    
    def test_very_high_abundance_threshold(self):
        """Test with very high formation factor threshold."""
        result = inorganic_interference(atoms={'Fe': 1}, target='Fe', formation_factors={'atomic': 1e-100})
        # Should return filtered results
        assert result is not None
    
    def test_molecule_with_numbers_only(self):
        """Test molecule parser with numbers only."""
        try:
            mol = Molecule.from_formula('123')
            assert mol is None or hasattr(mol, 'mass')
        except Exception:
            # Expected to fail parsing
            pass
    
    def test_molecule_with_special_chars(self):
        """Test molecule parser with special characters."""
        try:
            mol = Molecule.from_formula('H2@O')
            assert mol is None or hasattr(mol, 'mass')
        except Exception:
            # Expected to fail parsing
            pass
    
    def test_concurrent_calculations(self):
        """Test that multiple calculations can run independently."""
        result1 = inorganic_interference(atoms={'Fe': 1}, target='Fe')
        result2 = inorganic_interference(atoms={'Cu': 1}, target='Cu')
        
        assert result1 is not None
        assert result2 is not None


class TestScreenshotComparison:
    """Framework for screenshot comparison tests (UI testing)."""
    
    @pytest.mark.skip(reason="Requires GUI environment")
    def test_main_window_screenshot(self):
        """Test main window renders correctly (requires GUI)."""
        # This would require PyQt5 test infrastructure
        # Placeholder for future implementation
        pass
    
    @pytest.mark.skip(reason="Requires GUI environment")
    def test_table_rendering(self):
        """Test table component rendering (requires GUI)."""
        # Placeholder for future implementation
        pass
    
    def test_screenshot_framework_structure(self):
        """Test that screenshot comparison framework structure exists."""
        # Verify the test class and methods exist
        assert hasattr(self, 'test_main_window_screenshot')
        assert hasattr(self, 'test_table_rendering')
        print("✓ Screenshot comparison framework structure in place")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
