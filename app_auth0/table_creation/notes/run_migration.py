import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from create_enhanced_notes import upgrade, downgrade

def main():
    """Run the migration script."""
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        print("Running downgrade...")
        downgrade()
    else:
        print("Running upgrade...")
        upgrade()

if __name__ == '__main__':
    main() 