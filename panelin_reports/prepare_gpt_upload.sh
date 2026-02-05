#!/bin/bash

##############################################################################
# GPT PDF Upload Preparation Script
# 
# This script prepares all files needed for GPT PDF generation
# and creates a ready-to-upload package.
##############################################################################

echo "============================================================"
echo "BMC Uruguay PDF Generation - GPT Upload Preparation"
echo "============================================================"
echo ""

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PANELIN_REPORTS="$BASE_DIR/panelin_reports"
ASSETS_DIR="$PANELIN_REPORTS/assets"
OUTPUT_DIR="$PANELIN_REPORTS/gpt_upload_package"

# Step 1: Check for logo
echo "Step 1: Checking for BMC Uruguay logo..."
echo "-------------------------------------------"

if [ -f "$ASSETS_DIR/bmc_logo.png" ]; then
    echo -e "${GREEN}✅ Logo found: $ASSETS_DIR/bmc_logo.png${NC}"
    ls -lh "$ASSETS_DIR/bmc_logo.png"
    echo ""
else
    echo -e "${RED}❌ Logo not found!${NC}"
    echo ""
    echo "Please add the BMC Uruguay logo to:"
    echo "  $ASSETS_DIR/bmc_logo.png"
    echo ""
    echo "Options:"
    echo "  1. Download from https://bmcuruguay.com.uy"
    echo "  2. Request from info@bmcuruguay.com.uy"
    echo "  3. Copy from existing files"
    echo ""
    echo "Required specifications:"
    echo "  - Format: PNG"
    echo "  - Resolution: 300 DPI minimum"
    echo "  - Size: ~800x300 pixels recommended"
    echo ""
    
    # Try to find logo in common locations
    echo "Searching for logo files in your system..."
    FOUND_LOGOS=$(find ~/Downloads -name "*bmc*.png" -o -name "*logo*.png" 2>/dev/null | head -5)
    
    if [ -n "$FOUND_LOGOS" ]; then
        echo ""
        echo "Found potential logo files:"
        echo "$FOUND_LOGOS"
        echo ""
        echo "If one of these is correct, copy it with:"
        echo "  cp [FILE_PATH] $ASSETS_DIR/bmc_logo.png"
    fi
    
    echo ""
    read -p "Press Enter when logo is ready, or Ctrl+C to exit..."
fi

# Step 2: Create upload package
echo ""
echo "Step 2: Creating GPT upload package..."
echo "-------------------------------------------"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Copy required files
echo "Copying files to package directory..."

cp "$PANELIN_REPORTS/pdf_generator.py" "$OUTPUT_DIR/" && echo "  ✅ pdf_generator.py"
cp "$PANELIN_REPORTS/pdf_styles.py" "$OUTPUT_DIR/" && echo "  ✅ pdf_styles.py"

if [ -f "$ASSETS_DIR/bmc_logo.png" ]; then
    cp "$ASSETS_DIR/bmc_logo.png" "$OUTPUT_DIR/" && echo "  ✅ bmc_logo.png"
fi

# Create instructions file
cat > "$OUTPUT_DIR/UPLOAD_INSTRUCTIONS.txt" << 'EOF'
GPT UPLOAD INSTRUCTIONS
=======================

Upload these 3 files to your GPT's Knowledge section:

1. pdf_generator.py
2. pdf_styles.py
3. bmc_logo.png

HOW TO UPLOAD:
1. Go to https://chat.openai.com/gpts/editor/
2. Find "Panelin - BMC Assistant" GPT
3. Click "Configure"
4. Scroll to "Knowledge" section
5. Click "Upload files"
6. Select all 3 files from this folder
7. Click "Save" at top-right

THEN UPDATE INSTRUCTIONS:
Copy the PDF Generation section from:
  GPT_PDF_INSTRUCTIONS.md

And paste it into your GPT's Instructions field.

DONE!
Your GPT can now generate professional PDFs.

Test with: "Genera cotización PDF de prueba"
EOF

echo "  ✅ UPLOAD_INSTRUCTIONS.txt"
echo ""

# Step 3: Verify package
echo "Step 3: Verifying package..."
echo "-------------------------------------------"

cd "$OUTPUT_DIR"
FILE_COUNT=$(ls -1 | wc -l)
echo "Package contains $FILE_COUNT files:"
ls -lh

echo ""
echo "Required files:"
if [ -f "pdf_generator.py" ]; then
    echo -e "  ${GREEN}✅ pdf_generator.py${NC}"
else
    echo -e "  ${RED}❌ pdf_generator.py${NC}"
fi

if [ -f "pdf_styles.py" ]; then
    echo -e "  ${GREEN}✅ pdf_styles.py${NC}"
else
    echo -e "  ${RED}❌ pdf_styles.py${NC}"
fi

if [ -f "bmc_logo.png" ]; then
    echo -e "  ${GREEN}✅ bmc_logo.png${NC}"
else
    echo -e "  ${YELLOW}⚠️  bmc_logo.png (missing - PDFs will work but no logo)${NC}"
fi

echo ""

# Step 4: Create GPT instructions snippet
echo "Step 4: Creating GPT instructions snippet..."
echo "-------------------------------------------"

cp "$PANELIN_REPORTS/GPT_PDF_INSTRUCTIONS.md" "$OUTPUT_DIR/"
echo "  ✅ GPT_PDF_INSTRUCTIONS.md (copy this into GPT Instructions)"

echo ""

# Step 5: Test PDF generation
echo "Step 5: Testing PDF generation..."
echo "-------------------------------------------"

cd "$BASE_DIR"
echo "Running test to verify everything works..."
python3 panelin_reports/test_pdf_generation.py > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PDF generation test PASSED${NC}"
    echo ""
    echo "Sample PDFs generated in:"
    echo "  $PANELIN_REPORTS/output/"
    ls -lh "$PANELIN_REPORTS/output/" | tail -3
else
    echo -e "${RED}❌ PDF generation test FAILED${NC}"
    echo "Please check for errors and try again"
fi

echo ""

# Final instructions
echo "============================================================"
echo "✅ Package ready for GPT upload!"
echo "============================================================"
echo ""
echo "📁 Upload package location:"
echo "   $OUTPUT_DIR"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Open upload package folder:"
echo "   open $OUTPUT_DIR"
echo ""
echo "2. Follow instructions in UPLOAD_INSTRUCTIONS.txt"
echo ""
echo "3. Upload these files to GPT Knowledge:"
echo "   • pdf_generator.py"
echo "   • pdf_styles.py"
echo "   • bmc_logo.png"
echo ""
echo "4. Copy GPT instructions from:"
echo "   GPT_PDF_INSTRUCTIONS.md"
echo ""
echo "5. Test with your GPT:"
echo "   \"Genera cotización PDF de prueba\""
echo ""
echo "============================================================"
echo ""
echo "Need help? Check GPT_FULL_IMPLEMENTATION_GUIDE.md"
echo ""
