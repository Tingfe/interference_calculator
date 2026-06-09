#!/usr/bin/env python
"""Tests for the logging and diagnostics system."""

import pytest
import os
import sys
import json
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from interference_calculator.logging_system import (
    InterferenceCalculatorLogger, DiagnosticInfo, 
    setup_logging, get_logger, diagnostic_info
)
import logging


class TestDiagnosticInfo:
    """Test DiagnosticInfo class."""
    
    def test_create_diagnostic_info(self):
        """Test creating DiagnosticInfo instance."""
        diag = DiagnosticInfo()
        assert diag.error_history == []
        assert diag.system_info == {}
        assert diag.application_info == {}
    
    def test_collect_system_info(self):
        """Test collecting system information."""
        diag = DiagnosticInfo()
        info = diag.collect_system_info()
        
        assert 'platform' in info
        assert 'python_version' in info
        assert 'timestamp' in info
        assert info['os_name'] == os.name
    
    def test_collect_application_info(self):
        """Test collecting application information."""
        diag = DiagnosticInfo()
        info = diag.collect_application_info(version="2.6.0")
        
        assert info['name'] == 'Interference Calculator'
        assert info['version'] == '2.6.0'
        assert 'working_directory' in info
    
    def test_add_error(self):
        """Test adding error to history."""
        diag = DiagnosticInfo()
        diag.add_error(
            error_type="ERROR",
            message="Test error",
            traceback_str="Traceback...",
            context={'key': 'value'}
        )
        
        assert len(diag.error_history) == 1
        error = diag.error_history[0]
        assert error['type'] == "ERROR"
        assert error['message'] == "Test error"
        assert error['context']['key'] == 'value'
    
    def test_add_multiple_errors(self):
        """Test adding multiple errors."""
        diag = DiagnosticInfo()
        
        for i in range(5):
            diag.add_error("ERROR", f"Error {i}")
        
        assert len(diag.error_history) == 5
    
    def test_export_diagnostics(self):
        """Test exporting diagnostics to file."""
        diag = DiagnosticInfo()
        diag.collect_system_info()
        diag.collect_application_info()
        diag.add_error("ERROR", "Test error")
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            output_path = diag.export_diagnostics(temp_path)
            
            assert os.path.exists(output_path)
            
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            assert 'system_info' in data
            assert 'application_info' in data
            assert 'error_history' in data
            assert len(data['error_history']) == 1
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_diagnostics_auto_path(self):
        """Test exporting diagnostics with auto-generated path."""
        diag = DiagnosticInfo()
        diag.collect_system_info()
        
        output_path = diag.export_diagnostics()
        
        assert os.path.exists(output_path)
        assert output_path.startswith('diagnostics_')
        assert output_path.endswith('.json')
        
        # Cleanup
        if os.path.exists(output_path):
            os.unlink(output_path)


class TestInterferenceCalculatorLogger:
    """Test InterferenceCalculatorLogger class."""
    
    def test_create_logger(self):
        """Test creating logger instance."""
        log = InterferenceCalculatorLogger(name="test_logger")
        assert log.logger is not None
        assert log.logger.name == "test_logger"
    
    def test_logger_levels(self):
        """Test different logging levels."""
        log = InterferenceCalculatorLogger(name="test_levels", log_level=logging.DEBUG)
        
        # Should not raise exceptions
        log.debug("Debug message")
        log.info("Info message")
        log.warning("Warning message")
        log.error("Error message")
    
    def test_log_error_with_tracking(self):
        """Test that errors are tracked in diagnostics."""
        log = InterferenceCalculatorLogger(name="test_error_track")
        
        initial_count = len(diagnostic_info.error_history)
        log.error("Test error message")
        
        assert len(diagnostic_info.error_history) > initial_count
    
    def test_log_exception_with_traceback(self):
        """Test exception logging with traceback."""
        log = InterferenceCalculatorLogger(name="test_exception")
        
        try:
            result = 1 / 0
        except Exception:
            log.exception("Division by zero occurred")
        
        # Check that error was tracked
        assert len(diagnostic_info.error_history) > 0
        last_error = diagnostic_info.error_history[-1]
        assert last_error['type'] == "EXCEPTION"
        assert 'ZeroDivisionError' in last_error['traceback']
    
    def test_log_critical_with_tracking(self):
        """Test critical error logging and tracking."""
        log = InterferenceCalculatorLogger(name="test_critical")
        
        initial_count = len(diagnostic_info.error_history)
        log.critical("Critical failure")
        
        assert len(diagnostic_info.error_history) > initial_count
        last_error = diagnostic_info.error_history[-1]
        assert last_error['type'] == "CRITICAL"
    
    def test_set_log_level(self):
        """Test changing log level."""
        log = InterferenceCalculatorLogger(name="test_level_change", log_level=logging.WARNING)
        
        # Change to DEBUG
        log.set_level(logging.DEBUG)
        assert log.logger.level == logging.DEBUG
    
    def test_log_with_context(self):
        """Test logging with additional context."""
        log = InterferenceCalculatorLogger(name="test_context")
        
        context = {'user': 'test_user', 'action': 'calculate'}
        log.error("Error with context", context=context)
        
        last_error = diagnostic_info.error_history[-1]
        assert last_error['context']['user'] == 'test_user'
        assert last_error['context']['action'] == 'calculate'
    
    def test_export_diagnostics_from_logger(self):
        """Test exporting diagnostics through logger."""
        log = InterferenceCalculatorLogger(name="test_export")
        log.error("Test error for export")
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            output_path = log.export_diagnostics(temp_path)
            assert os.path.exists(output_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestSetupLogging:
    """Test setup_logging function."""
    
    def test_setup_with_default_level(self):
        """Test setup with default INFO level."""
        log = setup_logging(log_level="INFO")
        assert log is not None
        assert isinstance(log, InterferenceCalculatorLogger)
    
    def test_setup_with_debug_level(self):
        """Test setup with DEBUG level."""
        log = setup_logging(log_level="DEBUG")
        assert log.logger.level == logging.DEBUG
    
    def test_setup_with_warning_level(self):
        """Test setup with WARNING level."""
        log = setup_logging(log_level="WARNING")
        assert log.logger.level == logging.WARNING
    
    def test_setup_with_log_file(self):
        """Test setup with log file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_path = f.name
        
        try:
            # Create a fresh logger to avoid handler conflicts
            log = InterferenceCalculatorLogger(name="test_file_logger", log_file=temp_path)
            
            # Write a test message
            log.info("Test message to file")
            
            # Flush handlers to ensure content is written
            for handler in log.logger.handlers:
                handler.flush()
            
            # Close handlers
            for handler in log.logger.handlers:
                handler.close()
            
            # Check file exists and has content
            assert os.path.exists(temp_path)
            with open(temp_path, 'r') as f:
                content = f.read()
            assert len(content) > 0
            assert "Test message to file" in content
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_setup_invalid_level_defaults_to_info(self):
        """Test that invalid level defaults to INFO."""
        log = setup_logging(log_level="INVALID")
        assert log.logger.level == logging.INFO


class TestGetLogger:
    """Test get_logger function."""
    
    def test_get_global_logger(self):
        """Test getting global logger instance."""
        log = get_logger()
        assert log is not None
        assert isinstance(log, InterferenceCalculatorLogger)
    
    def test_get_logger_returns_same_instance(self):
        """Test that get_logger returns consistent instance."""
        log1 = get_logger()
        log2 = get_logger()
        assert log1 is log2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
