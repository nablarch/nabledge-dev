#!/bin/bash
# Master script to run all mapping creation steps

set -e  # Exit on error

echo "================================================================================"
echo "Nablarch v6 Mapping Creation - All Steps"
echo "================================================================================"
echo ""

# Check if openpyxl is installed
if ! python3 -c "import openpyxl" 2>/dev/null; then
    echo "Error: openpyxl is not installed"
    echo "Please install it with: pip install openpyxl"
    exit 1
fi

# Step 1-3: Create initial mapping with path-based categorization
echo "Running Step 1-3: Initial mapping creation..."
python3 doc/mapping-creation/work-v6/create-mapping-v6.py
echo ""

# Step 4: AI judgment categorization
echo "Running Step 4: AI judgment categorization..."
python3 doc/mapping-creation/work-v6/categorize-ai-judgment-v6.py
echo ""

# Step 5: Processing pattern verification
echo "Running Step 5: Processing pattern verification..."
python3 doc/mapping-creation/work-v6/verify-patterns-v6.py
echo ""

# Step 6-10: Finalize mapping
echo "Running Step 6-10: Finalize mapping..."
python3 doc/mapping-creation/work-v6/finalize-mapping-v6.py
echo ""

# Step 11: Export to Excel
echo "Running Step 11: Export to Excel..."
python3 doc/mapping-creation/work-v6/export-to-excel-v6.py
echo ""

echo "================================================================================"
echo "All steps completed successfully!"
echo ""
echo "Output files:"
echo "  - doc/mapping-creation/work-v6/mapping-v6.json"
echo "  - doc/mapping-creation/work-v6/mapping-v6.json.stats.txt"
echo "  - doc/mapping-creation/work-v6/mapping-v6.json.xlsx"
echo "================================================================================"
