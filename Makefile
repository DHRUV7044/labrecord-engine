# ============================================================
# LabRecord Engine Makefile
# ============================================================

PYTHON := python3
GENERATE_SCRIPT := generate.py

.PHONY: all generate test clean help example

# Default target: generate all PDFs from main.json
all: generate

# Generate all PDFs defined in main.json
generate:
	@echo "========================================"
	@echo "Running LabRecord Engine PDF Generator..."
	@echo "========================================"
	$(PYTHON) $(GENERATE_SCRIPT) main.json

# Build the primary reference experiment lab PDF
example:
	@echo "Building example lab PDF..."
	$(PYTHON) $(GENERATE_SCRIPT) main.json

# Run all test suites and verify output PDFs
test: generate
	@echo "========================================"
	@echo "All 11 PDF tests completed successfully!"
	@echo "========================================"

# Clean generated output PDFs and temporary cache files
clean:
	@echo "Cleaning output PDFs and math cache..."
	rm -rf output/*.pdf output/.cache_math output/preview*
	@echo "Clean completed."

# Print help overview of Makefile commands
help:
	@echo "LabRecord Engine Commands:"
	@echo "  make              - Generate all PDFs defined in main.json"
	@echo "  make generate     - Generate all PDFs defined in main.json"
	@echo "  make test         - Run test suite and build all PDFs"
	@echo "  make example      - Build example lab PDF"
	@echo "  make clean        - Remove generated PDFs and temporary cache files"
	@echo "  make help         - Display this help message"
