import sys
import os
import importlib
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("module_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("module_test")

# Modules to test
modules_to_test = [
    "fastapi",
    "uvicorn",
    "streamlit",
    "pandas",
    "numpy",
    "sqlalchemy",
    "plotly",
    "pydantic",
    "requests",
    "dotenv",
    "psutil"
]

def test_import(module_name):
    """Test importing a module and print its version if possible"""
    try:
        module = importlib.import_module(module_name.split('==')[0])
        version = getattr(module, "__version__", "unknown")
        logger.info(f"✅ {module_name} imported successfully (version: {version})")
        return True
    except ImportError as e:
        logger.error(f"❌ Could not import {module_name}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Error while importing {module_name}: {str(e)}")
        return False

def test_numpy_compatibility():
    """Test numpy-specific functionality that might be used in our code"""
    try:
        import numpy as np
        logger.info(f"NumPy version: {np.__version__}")
        
        # Check attributes that might be used
        attributes = ["bool_", "int_", "float_", "int64", "float64", "array", "ndarray"]
        for attr in attributes:
            if hasattr(np, attr):
                logger.info(f"✅ numpy.{attr} is available")
            else:
                logger.warning(f"❌ numpy.{attr} is NOT available")
                
        # Try to create arrays and check dtypes
        logger.info("Testing array creation...")
        arr = np.array([1, 2, 3])
        logger.info(f"Array dtype: {arr.dtype}")
        
        return True
    except Exception as e:
        logger.error(f"NumPy compatibility test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting module compatibility tests")
    
    # Test Python version
    logger.info(f"Python version: {sys.version}")
    
    # Test imports
    success = True
    for module in modules_to_test:
        if not test_import(module):
            success = False
    
    # Test numpy specifically
    numpy_ok = test_numpy_compatibility()
    
    if success and numpy_ok:
        logger.info("✅ All module tests passed successfully!")
        return True
    else:
        logger.error("❌ Some module tests failed. Check the logs for details.")
        return False

if __name__ == "__main__":
    main() 