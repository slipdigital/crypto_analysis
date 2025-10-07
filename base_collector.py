"""
Base Collector for Polygon.io API
Provides common functionality for all Polygon.io data collectors
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, Optional

import requests


class BasePolygonCollector:
    """Base class for Polygon.io API collectors with common functionality"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        """Initialize the base collector with configuration"""
        self.config = self._load_config(config_path)
        self.base_url = self.config["api"]["polygon_base_url"]
        self.api_key = self.config["api"]["api_key"]
        self.rate_limit_delay = self.config["api"]["rate_limit_delay"]
        self.max_retries = self.config["api"]["max_retries"]
        self.timeout = self.config["api"]["timeout"]
        
        # Setup logging
        self._setup_logging()
        
        # Create directories
        self._create_directories()
        
        # Validate API key
        self._validate_api_key()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in configuration file: {config_path}")
    
    def _setup_logging(self):
        """Setup logging configuration - to be overridden by subclasses if needed"""
        log_dir = self.config["data"]["logs_directory"]
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(
            log_dir, 
            f"{self.__class__.__name__.lower()}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        logging.basicConfig(
            level=getattr(logging, self.config["logging"]["level"]),
            format=self.config["logging"]["format"],
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _create_directories(self):
        """Create necessary directories for data storage - can be overridden"""
        directories = [
            self.config["data"]["data_directory"],
            self.config["data"]["logs_directory"]
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.logger.debug(f"Created/verified directory: {directory}")
    
    def _validate_api_key(self):
        """Validate that API key is configured"""
        if self.api_key == "YOUR_POLYGON_API_KEY":
            self.logger.warning("Please set your Polygon.io API key in config/settings.json")
            self.logger.warning("Run 'python setup_polygon.py' to configure your API key")
    
    def _make_api_request(
        self, 
        endpoint: str, 
        params: Optional[Dict] = None, 
        skip_delay: bool = False
    ) -> Optional[Dict]:
        """
        Make API request with retry logic and rate limiting
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            skip_delay: Skip rate limiting delay (useful for concurrent requests)
            
        Returns:
            JSON response data or None on failure
        """
        if params is None:
            params = {}
        
        # Add API key to parameters
        params['apikey'] = self.api_key
        
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Making API request to: {url} (attempt {attempt + 1})")
                
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                
                # Rate limiting (can be skipped for concurrent requests)
                if not skip_delay:
                    time.sleep(self.rate_limit_delay)
                
                return response.json()
                
            except requests.exceptions.Timeout as e:
                self.logger.warning(f"API request timeout (attempt {attempt + 1}): {e}")
            except requests.exceptions.HTTPError as e:
                self.logger.warning(f"HTTP error (attempt {attempt + 1}): {e}")
                # Don't retry on 4xx errors (client errors)
                if 400 <= response.status_code < 500:
                    self.logger.error(f"Client error {response.status_code}, not retrying")
                    return None
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"API request failed (attempt {attempt + 1}): {e}")
            
            # Exponential backoff before retry
            if attempt < self.max_retries - 1:
                backoff_time = 2 ** attempt
                self.logger.debug(f"Waiting {backoff_time}s before retry...")
                time.sleep(backoff_time)
        
        self.logger.error(f"All API request attempts failed for {url}")
        return None
    
    def _validate_data(self, data: Dict, data_type: str) -> bool:
        """
        Validate data quality and completeness
        
        Args:
            data: Data to validate
            data_type: Type of data for validation rules
            
        Returns:
            True if data is valid, False otherwise
        """
        if not data:
            self.logger.warning(f"Empty data received for {data_type}")
            return False
        
        validation_rules = {
            "ticker_data": ['ticker', 'name'],
            "price_data": ['c'],  # close price
            "historical_data": ['results']
        }
        
        required_fields = validation_rules.get(data_type, [])
        
        for field in required_fields:
            if field not in data:
                self.logger.warning(f"Missing field '{field}' in {data_type}")
                return False
            
            # Check for None or empty values
            if data[field] is None:
                self.logger.warning(f"Null value for field '{field}' in {data_type}")
                return False
            
            # For list/dict fields, check if empty
            if isinstance(data[field], (list, dict)) and not data[field]:
                self.logger.warning(f"Empty value for field '{field}' in {data_type}")
                return False
        
        return True