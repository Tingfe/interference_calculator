#!/usr/bin/env python
"""
Logging and diagnostics system for Interference Calculator.

This module provides comprehensive logging, error tracking, and diagnostic
export functionality to help with debugging and support.
"""

import logging
import sys
import os
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


class DiagnosticInfo:
    """Collects diagnostic information about the application state."""
    
    def __init__(self):
        self.system_info = {}
        self.application_info = {}
        self.error_history: List[Dict[str, Any]] = []
    
    def collect_system_info(self) -> Dict[str, Any]:
        """Collect system information."""
        import platform
        
        self.system_info = {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation(),
            'os_name': os.name,
            'timestamp': datetime.now().isoformat()
        }
        
        return self.system_info
    
    def collect_application_info(self, version: str = "2.6.0") -> Dict[str, Any]:
        """Collect application information."""
        self.application_info = {
            'name': 'Interference Calculator',
            'version': version,
            'working_directory': os.getcwd(),
            'executable': sys.executable
        }
        
        return self.application_info
    
    def add_error(self, error_type: str, message: str, 
                  traceback_str: str = "", context: Dict[str, Any] = None) -> None:
        """Add an error to the error history."""
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': message,
            'traceback': traceback_str,
            'context': context or {}
        }
        self.error_history.append(error_record)
    
    def export_diagnostics(self, output_path: str = None) -> str:
        """Export all diagnostic information to a JSON file."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"diagnostics_{timestamp}.json"
        
        diagnostics = {
            'system_info': self.system_info or self.collect_system_info(),
            'application_info': self.application_info or self.collect_application_info(),
            'error_history': self.error_history,
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(diagnostics, f, indent=2, ensure_ascii=False)
        
        return output_path


# Global diagnostic info instance
diagnostic_info = DiagnosticInfo()


class InterferenceCalculatorLogger:
    """
    Custom logger for Interference Calculator.
    
    Provides structured logging with different levels and handlers
    for console, file, and diagnostic tracking.
    """
    
    def __init__(self, name: str = "interference_calculator", 
                 log_level: int = logging.INFO,
                 log_file: str = None):
        """
        Initialize the logger.
        
        Args:
            name: Logger name
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional log file path
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # Prevent adding duplicate handlers
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(console_format)
            self.logger.addHandler(console_handler)
            
            # File handler (if specified)
            if log_file:
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)  # Log everything to file
                file_format = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
                )
                file_handler.setFormatter(file_format)
                self.logger.addHandler(file_handler)
        
        # Collect initial diagnostics
        diagnostic_info.collect_system_info()
        diagnostic_info.collect_application_info()
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log a debug message."""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """Log an info message."""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """Log a warning message."""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, exc_info: bool = False, 
              context: Dict[str, Any] = None, *args, **kwargs) -> None:
        """
        Log an error message and track it in diagnostics.
        
        Args:
            message: Error message
            exc_info: Whether to include exception traceback
            context: Additional context information
        """
        self.logger.error(message, *args, exc_info=exc_info, **kwargs)
        
        # Track error in diagnostics
        if exc_info:
            tb_str = traceback.format_exc()
        else:
            tb_str = ""
        
        diagnostic_info.add_error(
            error_type="ERROR",
            message=message,
            traceback_str=tb_str,
            context=context
        )
    
    def critical(self, message: str, exc_info: bool = False,
                 context: Dict[str, Any] = None, *args, **kwargs) -> None:
        """
        Log a critical error and track it in diagnostics.
        
        Args:
            message: Critical error message
            exc_info: Whether to include exception traceback
            context: Additional context information
        """
        self.logger.critical(message, *args, exc_info=exc_info, **kwargs)
        
        # Track critical error in diagnostics
        if exc_info:
            tb_str = traceback.format_exc()
        else:
            tb_str = ""
        
        diagnostic_info.add_error(
            error_type="CRITICAL",
            message=message,
            traceback_str=tb_str,
            context=context
        )
    
    def exception(self, message: str, context: Dict[str, Any] = None,
                  *args, **kwargs) -> None:
        """
        Log an exception with full traceback.
        
        Args:
            message: Exception message
            context: Additional context information
        """
        self.logger.exception(message, *args, **kwargs)
        
        # Track exception in diagnostics
        tb_str = traceback.format_exc()
        diagnostic_info.add_error(
            error_type="EXCEPTION",
            message=message,
            traceback_str=tb_str,
            context=context
        )
    
    def set_level(self, level: int) -> None:
        """Change the logging level."""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(level)
    
    def get_log_file_path(self) -> Optional[str]:
        """Get the current log file path if configured."""
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                return handler.baseFilename
        return None
    
    def export_diagnostics(self, output_path: str = None) -> str:
        """Export diagnostic information to a file."""
        return diagnostic_info.export_diagnostics(output_path)


# Global logger instance
logger = InterferenceCalculatorLogger()


def setup_logging(log_level: str = "INFO", log_file: str = None) -> InterferenceCalculatorLogger:
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    
    Returns:
        Configured logger instance
    """
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    level = level_map.get(log_level.upper(), logging.INFO)
    
    global logger
    logger = InterferenceCalculatorLogger(log_level=level, log_file=log_file)
    
    logger.info(f"Logging initialized at {log_level} level")
    if log_file:
        logger.info(f"Log file: {log_file}")
    
    return logger


def get_logger() -> InterferenceCalculatorLogger:
    """Get the global logger instance."""
    return logger
