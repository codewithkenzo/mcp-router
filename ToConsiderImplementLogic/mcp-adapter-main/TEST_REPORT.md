# Test Report

## Date and Time
Generated on: 2025-03-08 01:51:40

## Test Results

### Unit Tests
```
```

### Coverage Report
```
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/__init__.py                       0      0   100%
src/core/__init__.py                  4      0   100%
src/core/client.py                   62      7    89%   32, 71-73, 85-87
src/core/logger.py                   42      0   100%
src/core/orchestrator.py             78     17    78%   73-80, 85-89, 108, 134-136
src/core/tools.py                    47      6    87%   55, 71-75
src/llm/__init__.py                   4      0   100%
src/llm/base.py                      48      4    92%   23, 28, 33, 38
src/llm/gemini.py                    62     25    60%   25-27, 42-44, 62-64, 72-74, 80-100
src/llm/openai.py                    61     29    52%   22-24, 53-55, 69-71, 75-102
tests/core/__init__.py                0      0   100%
tests/core/test_client.py           105      1    99%   203
tests/core/test_logger.py            68      1    99%   130
tests/core/test_orchestrator.py     109      2    98%   75, 225
tests/core/test_tools.py             76      1    99%   166
tests/llm/__init__.py                 0      0   100%
tests/llm/test_base.py               87     18    79%   15-16, 20-21, 25-26, 31-43, 155
tests/llm/test_gemini.py             95      1    99%   184
tests/llm/test_openai.py            134      1    99%   257
---------------------------------------------------------------
TOTAL                              1082    113    90%
```

## Coverage Summary
Total coverage: 90%
✅ Coverage threshold met: 90% (target: 80%)
