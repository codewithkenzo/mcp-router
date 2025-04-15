#!/bin/bash
set -e

# Activate virtual environment
source venv/bin/activate

# Create TEST_REPORT.md file with header and date/time
echo "# Test Report" > TEST_REPORT.md
echo "" >> TEST_REPORT.md
echo "## Date and Time" >> TEST_REPORT.md
echo "Generated on: $(date '+%Y-%m-%d %H:%M:%S')" >> TEST_REPORT.md
echo "" >> TEST_REPORT.md
echo "## Test Results" >> TEST_REPORT.md
echo "" >> TEST_REPORT.md

# Run all tests and append to TEST_REPORT.md
echo "Running all tests..."
echo "### Unit Tests" >> TEST_REPORT.md
echo '```' >> TEST_REPORT.md
python -m unittest discover tests | tee -a TEST_REPORT.md
echo '```' >> TEST_REPORT.md
echo "" >> TEST_REPORT.md

# Run coverage and append to TEST_REPORT.md
echo "Running tests with coverage..."
echo "### Coverage Report" >> TEST_REPORT.md
echo '```' >> TEST_REPORT.md
python -m coverage run -m unittest discover tests && python -m coverage report -m | tee -a TEST_REPORT.md
echo '```' >> TEST_REPORT.md

# Check coverage percentage and report success/failure
COVERAGE=$(python -m coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')
echo "" >> TEST_REPORT.md
echo "## Coverage Summary" >> TEST_REPORT.md
echo "Total coverage: $COVERAGE%" >> TEST_REPORT.md

if (( $(echo "$COVERAGE >= 80.0" | bc -l) )); then
    echo "✅ Coverage threshold met: $COVERAGE% (target: 80%)" >> TEST_REPORT.md
    echo "Coverage threshold met: $COVERAGE% (target: 80%)"
else
    echo "❌ Coverage threshold not met: $COVERAGE% (target: 80%)" >> TEST_REPORT.md
    echo "Coverage threshold not met: $COVERAGE% (target: 80%)"
    exit 1
fi

echo "All tests completed successfully!"
echo "Test report generated: TEST_REPORT.md"