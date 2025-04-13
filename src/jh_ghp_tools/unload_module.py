import sys
import importlib

def unload_module(module_name):
    """Unload a module from sys.modules."""
    if module_name in sys.modules:
        del sys.modules[module_name]
        print(f"Module '{module_name}' has been unloaded.")
    else:
        print(f"Module '{module_name}' is not loaded.")

def reload_module(module_name):
    """Reload a module."""
    try:
        module = importlib.import_module(module_name)
        importlib.reload(module)
        print(f"Module '{module_name}' has been reloaded.")
    except ModuleNotFoundError:
        print(f"Module '{module_name}' could not be found.")
    except Exception as e:
        print(f"An error occurred while reloading module '{module_name}': {e}")

if __name__ == "__main__":
    module_name = "jh_ghp_tools"
    
    # Unload the module
    unload_module(module_name)
    
    # Reload the module
    reload_module(module_name)