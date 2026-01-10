"""
Base calculator class for indicator calculators.

All calculator classes should inherit from BaseCalculator and implement the calculate method.
"""
from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, Any, Optional


class BaseCalculator(ABC):
    """Base class for indicator calculators."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the calculator with optional configuration.
        
        Args:
            config: Dictionary containing calculator-specific configuration
        """
        self.config = config or {}
    
    @abstractmethod
    def calculate(self, date: date, **kwargs) -> float:
        """
        Calculate the indicator value for a given date.
        
        Args:
            date: The date to calculate the indicator for
            **kwargs: Additional arguments for the calculation
            
        Returns:
            float: The indicator value (should be between -1.0 and 1.0)
            
        Raises:
            ValueError: If the calculation fails or data is unavailable
        """
        pass
    
    def validate_value(self, value: float) -> float:
        """
        Validate and clamp the indicator value to the valid range [-1.0, 1.0].
        
        Args:
            value: The calculated value
            
        Returns:
            float: The clamped value
        """
        if value < -1.0:
            return -1.0
        elif value > 1.0:
            return 1.0
        return value
    
    def get_description(self) -> str:
        """
        Get a description of what this calculator computes.
        
        Returns:
            str: Description of the indicator calculation
        """
        return self.__class__.__name__
