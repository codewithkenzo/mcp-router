# Tips for Future Claude Working with MCP Adapter

## Important Learning From Tests

1. **Always Check Actual Implementation**:
   - Look at the actual code implementation before writing tests
   - Check function signatures and parameter names carefully
   - Don't assume functions have certain parameters or return values

2. **Logger Handling in Tests**:
   - Python's logging system persists handlers between test runs
   - Clear existing handlers before testing: `logging.getLogger(name).handlers = []` 
   - Use `assertGreaterEqual` instead of direct equality for handler counts
   - Expect file resource warnings when manipulating handlers

3. **Tool Testing Considerations**:
   - Tool objects require specific parameters matching their implementation
   - Don't assume standard methods like `from_json` or `to_dict` exist

## Always Do These First

1. **Check for Documentation**:
   - Always look for documentation first in the `add_docs` folder
   - Read relevant files in `claude_learnings` for project context
   - Check the CHANGELOG.md for recent updates

2. **Execute Code Before Making Changes**:
   - Run examples to understand how they work before modifying them
   - Check logs for client/server interactions
   - Understand error patterns by testing

3. **Verify Environment Requirements**:
   - Check for .env files and required variables
   - Verify package versions with `pip list`
   - Look for package.json or requirements.txt for dependencies

## MCP Code Patterns I've Learned

1. **Client Initialization Pattern**:
   ```python
   client = MCPClient(
       StdioServerParameters(
           command="npx",
           args=["-y", "package-name"],
           env=None
       ),
       debug=True,
       log_file=Path("logs") / "client.log",
       client_name="descriptive_name"
   )
   ```

2. **Error Handling Pattern**:
   ```python
   try:
       # Operations with client
       result = await client.execute_tool(tool_name, tool_args)
   except Exception as e:
       client.logger.end_session("failed")
       print(f"Error: {str(e)}")
   else:
       client.logger.end_session("completed")
   finally:
       await client.close()  # Critical!
   ```

3. **Tool Call Extraction & Validation**:
   ```python
   response = await llm_client.send_message(prompt)
   tool_name, tool_args = llm_client.extract_tool_call(response)
   
   # Always validate before executing
   if tool_name and tool_args:
       result = await client.execute_tool(tool_name, tool_args)
   else:
       # Handle the error case
   ```

## Common MCP Servers & Packages

1. **Filesystem Server**:
   - Package: `@modelcontextprotocol/server-filesystem`
   - Key tools: read_file, write_file, create_directory, list_directory
   - Needs a base directory path

2. **Memory Server**:
   - Package: `@modelcontextprotocol/server-memory`
   - Key tools: create_entities, create_relations, read_graph, search_nodes
   - Persists entities and relationships in a graph

3. **Time Server**:
   - Package: `mcp-server-time` (Note: not "@modelcontextprotocol/server-time")
   - Key tools: current_time, convert_timezone, time_difference
   - No special configuration needed

## Troubleshooting Tips

1. **Check NPM Package Names**:
   - Some packages use `@modelcontextprotocol/server-X` pattern
   - Others use `mcp-server-X` pattern
   - When in doubt, use `npm search mcp-server` or check the docs

2. **Debug Client Connections**:
   - Set `debug=True` on clients for detailed logs
   - Check for initialization errors in logs
   - Verify server is starting properly

3. **Verify Tool Calls**:
   - Make sure tool_name matches exactly what the server provides
   - Validate tool_args match the expected schema
   - When tool calls fail, check if LLM is generating proper JSON

## Best Practices I've Observed

1. **Consistent Naming**:
   - Use descriptive client_name values (e.g., "filesystem", "memory")
   - Create sensible log file paths under a logs/ directory
   - Standardize code patterns across examples

2. **Robust Error Handling**:
   - Validate all tool calls before execution
   - Handle failures gracefully
   - Always close clients in finally blocks

3. **Clean Documentation**:
   - Add docstrings to methods
   - Include file-level docstrings
   - Use type hints for better code readability

4. **Proper Logging**:
   - Set up log directories before use
   - Use session logging for tracking statuses
   - Ensure logs capture the right level of detail

## Testing Best Practices

1. **Comprehensive Testing Setup**:
   - Create tests for each core component and LLM adapter
   - Use the `unittest` framework's mock capabilities
   - Test both success and error cases
   - Cover edge cases like invalid input data

2. **Mocking Async Functions**:
   - Use `AsyncMock` for async functions
   - Be careful with return values in async contexts
   - Properly chain mocks for complex dependencies
   - Use proper awaiting in test code

3. **Testing Tool Orchestration**:
   - Mock server parameters and clients
   - Test the routing of tools to correct clients
   - Verify tool validation works correctly
   - Test error handling for invalid tools/args

4. **Effective Coverage Reporting**:
   - Create a test runner that generates reports
   - Include date/time stamps in reports
   - Track coverage percentage
   - Aim for at least 80% code coverage

## What to Add to the Codebase Next

1. **Additional Examples**:
   - Web search using Brave API
   - Database operations with SQLite
   - Multi-server orchestration with more complex workflows

2. **Enhance Testing**:
   - Add integration tests for server interactions
   - Increase test coverage of Gemini and OpenAI implementations
   - Create end-to-end test examples

3. **Enhanced Documentation**:
   - More detailed README with setup instructions
   - Better in-code comments for complex operations

4. **Additional LLM Providers**:
   - Add support for more providers beyond OpenAI and Gemini
   - Standardize tool conversion patterns

Remember: Always execute code to verify it works! Don't just look at it.