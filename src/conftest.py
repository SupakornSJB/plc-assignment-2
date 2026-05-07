import sys

# Remove 'src' from sys.path to prevent Python from importing
# src/ast_node instead of the built-in ast_node module
sys.path = [p for p in sys.path if not p.endswith('src') and not p.endswith('src\\')]