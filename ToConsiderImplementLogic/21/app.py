"""
服务器应用模块
提供MCP代码检索服务实现
"""

import os
import sys
import logging
import argparse
import locale
import asyncio

if sys.platform == 'win32':
    os.system('chcp 65001')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
else:
    if locale.getpreferredencoding().upper() != 'UTF-8':
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp.server.stdio import stdio_server

from mcp_code_indexer.config import Config
from mcp_code_indexer.indexer import CodeIndexer
from mcp_code_indexer.search_engine import SearchEngine
from mcp_code_indexer.mcp_formatter import McpFormatter

# 
from server.mcp_server import setup_mcp_server

class MpcLogFilter(logging.Filter):
    """过滤MCP服务器的底层日志"""
    def filter(self, record):
        if record.name.startswith('mcp.server.lowlevel'):
            return False
        return True

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logging.basicConfig(handlers=[NullHandler()])

logging.getLogger('mcp').setLevel(logging.CRITICAL)
logging.getLogger('chromadb').setLevel(logging.CRITICAL)
logging.getLogger('sentence_transformers').setLevel(logging.CRITICAL)
logging.getLogger('tree_sitter').setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)

async def run_server(server):
    """
    运行带有stdio传输的MCP服务器
    
    Args:
        server: MCP服务器实例
        
    Returns:
        无返回值
    """
    async with stdio_server() as (read_stream, write_stream):
        from mcp.server.models import InitializationOptions
        from mcp.server.lowlevel import NotificationOptions
        
        init_options = InitializationOptions(
            server_name="mcp-code-indexer",
            server_version="0.1.0",
            capabilities=server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            )
        )
        
        await server.run(read_stream, write_stream, init_options)

def main():
    """
    主函数，启动MCP服务器
    
    Returns:
        无返回值
    """
    parser = argparse.ArgumentParser(description='MCP Code Retrieval Service')
    parser.add_argument('--config', type=str, help='Configuration file path')
    
    args = parser.parse_args()
    
    try:
        # 加载配置
        config = Config(args.config)
        indexer = CodeIndexer(config)
        search_engine = SearchEngine(config, indexer)
        formatter = McpFormatter()
        
        server = setup_mcp_server(config, indexer, search_engine, formatter)
        
        def handle_exit(signum, frame):
            sys.exit(0)
        
        import signal
        signal.signal(signal.SIGINT, handle_exit)
        signal.signal(signal.SIGTERM, handle_exit)
        
        asyncio.run(run_server(server))
        
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        sys.exit(1)

if __name__ == '__main__':
    main()