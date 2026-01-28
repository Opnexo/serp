import sys
from importlib.metadata import entry_points

print(f"Python executable: {sys.executable}")
print("Checking 'serp.modules.api' entry points:")

# Python 3.10+ select interface
try:
    eps = entry_points().select(group="serp.modules.api")
except AttributeError:
    # Older python fallback (though project uses 3.11+)
    eps = entry_points().get("serp.modules.api", [])

for ep in eps:
    print(f"  - Name: {ep.name}")
    print(f"    Value: {ep.value}")
    print(f"    Module: {ep.module}")

print("\nChecking 'serp.modules' entry points:")
try:
    eps_main = entry_points().select(group="serp.modules")
except AttributeError:
    eps_main = entry_points().get("serp.modules", [])

for ep in eps_main:
    print(f"  - Name: {ep.name}")
    print(f"    Value: {ep.value}")
