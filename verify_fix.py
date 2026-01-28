import importlib.util
import sys
import os


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Mock the relative import of pdf_styles
# pdf_generator.py does: from .pdf_styles import BMCStyles, QuotationConstants
# We need to make sure it can find it.
# Since we are loading it as a module, we can just add the directory to sys.path

dir_path = os.path.abspath("Panelin_GPT/01_UPLOAD_FILES")
sys.path.append(dir_path)

# Mock pdf_styles if needed, but it should be in the same dir
try:
    pdf_gen = load_module("pdf_generator", os.path.join(dir_path, "pdf_generator.py"))
    QuotationDataFormatter = pdf_gen.QuotationDataFormatter
except Exception as e:
    print(f"Error loading module: {e}")
    sys.exit(1)


def test_bugs():
    print("Testing Bug 1: Length_m vs length_m")
    item_with_capital = {
        "name": "Test Product",
        "unit_base": "ml",
        "Length_m": 5.0,
        "quantity": 2,
        "unit_price_usd": 10.0,
    }

    total = QuotationDataFormatter.calculate_item_total(item_with_capital)
    print(f"Calculated total for Length_m: {total} (Expected: 100.0)")
    assert total == 100.0

    print("\nTesting Bug 2: total_usd population")
    products = [item_with_capital]
    accessories = []
    fixings = []

    totals = QuotationDataFormatter.calculate_totals(products, accessories, fixings, 0)

    print(f"Totals calculated: {totals['subtotal']}")
    print(f"Item total_usd after calculation: {item_with_capital.get('total_usd')}")

    assert item_with_capital.get("total_usd") == 100.0
    print("Bug 2 Fixed: total_usd is now populated in the item!")


if __name__ == "__main__":
    try:
        test_bugs()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback

        traceback.print_exc()
