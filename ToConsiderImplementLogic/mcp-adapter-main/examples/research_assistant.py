"""
Research Assistant Example

This example demonstrates a practical research assistant that:
1. Creates and manages research notes on topics
2. Uses memory to track relationships between research topics
3. Leverages AI to summarize and connect information

This showcases:
- Integration of Filesystem and Memory MCP servers
- Use of AI for content generation and organization
- Practical note-taking and knowledge management workflow
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Third-party imports
from dotenv import load_dotenv
from mcp import StdioServerParameters

# Local imports
from src.llm import OpenAIAdapter
from src.core import MCPClient, MCPTools

# Load environment variables
load_dotenv()

async def main() -> None:
    """
    Run the research assistant example.
    
    This function demonstrates creating an AI-powered research assistant using:
    - Filesystem MCP server for note storage
    - Memory MCP server for knowledge graph management
    - OpenAI LLM for generating content and tool calls
    """
    # Setup logging directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Load configuration
    desktop_path = os.getenv('DESKTOP_PATH')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not desktop_path or not openai_api_key:
        print("ERROR: Both DESKTOP_PATH and OPENAI_API_KEY must be set in .env file")
        return
    
    # Define research directory path
    research_dir = Path(desktop_path) / "research_notes"
    
    # Configure MCP servers
    fs_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", desktop_path],
        env=None
    )
    
    mem_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-memory"],
        env=None
    )
    
    # Initialize clients
    fs_client = MCPClient(
        fs_params,
        debug=True,
        log_file=log_dir / "fs_client.log",
        client_name="filesystem"
    )
    
    mem_client = MCPClient(
        mem_params,
        debug=True,
        log_file=log_dir / "mem_client.log",
        client_name="memory"
    )
    
    # Initialize LLM adapter
    llm_client = OpenAIAdapter(
        model_name='gpt-4o-mini',
        debug=True,
        log_file=log_dir / "openai.log"
    )
    
    try:
        # Get tools from both clients
        fs_tools = await fs_client.get_tools()
        mem_tools = await mem_client.get_tools()
        
        # Create MCPTools instance and add tools
        tools = MCPTools()
        tools.add(fs_tools)
        tools.add(mem_tools)
        
        # Configure LLM with tools
        await llm_client.prepare_tools(tools)
        await llm_client.configure(openai_api_key)
        
        # 1. Create research directory
        print("\n=== Setting up Research Directory ===")
        dir_prompt = f"Create a directory at '{research_dir}' if it doesn't exist. This will store our research notes."
        response = await llm_client.send_message(dir_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Validate tool call
        if tool_name and tool_args:
            dir_result = await fs_client.execute_tool(tool_name, tool_args)
            print(f"Directory setup result: {dir_result}")
        else:
            print("Failed to extract tool call for directory creation")
            return
        
        # 2. Create research note on AI Ethics
        print("\n=== Creating Research Note on AI Ethics ===")
        ai_ethics_topic = "AI Ethics"
        ai_ethics_filename = "ai_ethics.md"
        ai_ethics_filepath = research_dir / ai_ethics_filename
        
        note_prompt = f"""
        Create a comprehensive research note on {ai_ethics_topic}.
        
        The note should:
        1. Have a proper markdown heading structure
        2. Include an introduction to AI Ethics
        3. Cover key principles (like fairness, transparency)
        4. Mention current challenges
        5. End with open questions for further research
        
        Save this as {ai_ethics_filepath}
        """
        
        response = await llm_client.send_message(note_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Validate tool call
        if tool_name and tool_args:
            note_result = await fs_client.execute_tool(tool_name, tool_args)
            print(f"Note creation result: {note_result}")
        else:
            print("Failed to extract tool call for note creation")
            return
        
        # 3. Add to Memory Graph
        print("\n=== Adding Note to Knowledge Graph ===")
        memory_prompt = f"""
        Create a memory entity in the knowledge graph:
        
        1. Create an entity named "{ai_ethics_topic}" with type "research_note"
        2. Add the following observations:
           - filepath: {ai_ethics_filepath}
           - created: {datetime.now().strftime('%Y-%m-%d')}
           - summary: A research note about key principles and challenges in AI Ethics
        """
        
        response = await llm_client.send_message(memory_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Validate tool call
        if tool_name and tool_args:
            memory_result = await mem_client.execute_tool(tool_name, tool_args)
            print(f"Memory creation result: {memory_result}")
        else:
            print("Failed to extract tool call for memory creation")
            return
        
        # 4. Create related note on Algorithmic Bias
        print("\n=== Creating Related Note on Algorithmic Bias ===")
        algorithmic_bias_topic = "Algorithmic Bias"
        algorithmic_bias_filename = "algorithmic_bias.md"
        algorithmic_bias_filepath = research_dir / algorithmic_bias_filename
        
        related_prompt = f"""
        Create a research note on {algorithmic_bias_topic} that relates to {ai_ethics_topic}.
        
        The note should:
        1. Have a proper markdown heading structure
        2. Explain how bias occurs in algorithms
        3. Connect to the broader topic of {ai_ethics_topic}
        4. Include examples of algorithmic bias
        5. Suggest approaches to reduce bias
        
        Save this as {algorithmic_bias_filepath}
        """
        
        response = await llm_client.send_message(related_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Validate tool call
        if tool_name and tool_args:
            related_result = await fs_client.execute_tool(tool_name, tool_args)
            print(f"Related note creation result: {related_result}")
        else:
            print("Failed to extract tool call for related note creation")
            return
        
        # 5. Add second note to memory and create relationship
        print("\n=== Creating Knowledge Relationship ===")
        relation_prompt = f"""
        1. First, create a memory entity named "{algorithmic_bias_topic}" with type "research_note" and these observations:
           - filepath: {algorithmic_bias_filepath}
           - created: {datetime.now().strftime('%Y-%m-%d')}
           - summary: Research on bias in algorithms and AI systems
        
        2. Then create a relationship between "{algorithmic_bias_topic}" and "{ai_ethics_topic}" with relation type "subtopic_of"
        """
        
        # First create the entity
        response = await llm_client.send_message(relation_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        if tool_name == "create_entities" and tool_args:
            # Create the entity
            entity_result = await mem_client.execute_tool(tool_name, tool_args)
            print(f"Entity creation result: {entity_result}")
            
            # Now create the relationship in a separate step
            relation_prompt_2 = f"""
            Now that we have both entities, create a relationship between "{algorithmic_bias_topic}" and "{ai_ethics_topic}" with relation type "subtopic_of"
            """
            
            response = await llm_client.send_message(relation_prompt_2)
            tool_name, tool_args = llm_client.extract_tool_call(response)
            
            if tool_name and tool_args:
                relation_result = await mem_client.execute_tool(tool_name, tool_args)
                print(f"Relationship creation result: {relation_result}")
            else:
                print("Failed to extract tool call for relationship creation")
        else:
            print("Failed to extract tool call for entity creation")
        
        # 6. Query the knowledge graph
        print("\n=== Querying Knowledge Graph ===")
        query_prompt = "Read the entire knowledge graph to see all entities and their relationships"
        response = await llm_client.send_message(query_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Validate tool call
        if tool_name and tool_args:
            query_result = await mem_client.execute_tool(tool_name, tool_args)
            
            # Format the result nicely
            if isinstance(query_result, dict) and 'content' in query_result:
                for item in query_result['content']:
                    if item.get('type') == 'text':
                        try:
                            graph_data = json.loads(item['text'])
                            print("Knowledge Graph Contents:")
                            print(json.dumps(graph_data, indent=2))
                        except json.JSONDecodeError:
                            print(f"Knowledge Graph Contents (not JSON format): {item['text']}")
        else:
            print("Failed to extract tool call for knowledge graph query")
        
        # 7. Generate summary of research
        print("\n=== Generating Research Summary ===")
        summary_prompt = f"""
        Based on our notes about {ai_ethics_topic} and {algorithmic_bias_topic}, create a summary
        that highlights the key points, connections, and future research directions.
        
        Save this summary as {research_dir / "research_summary.md"}
        """
        
        response = await llm_client.send_message(summary_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Validate tool call
        if tool_name and tool_args:
            summary_result = await fs_client.execute_tool(tool_name, tool_args)
            print(f"Summary creation result: {summary_result}")
        else:
            print("Failed to extract tool call for summary creation")
        
        # Log completion status
        fs_client.logger.end_session("completed")
        mem_client.logger.end_session("completed")
        llm_client.logger.end_session("completed")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        fs_client.logger.end_session("failed")
        mem_client.logger.end_session("failed")
        llm_client.logger.end_session("failed")
    finally:
        # Close clients
        await fs_client.close()
        await mem_client.close()

if __name__ == "__main__":
    asyncio.run(main())