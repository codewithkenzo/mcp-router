import the
import requests
import html2text
from readability.readability import Document
from itertools import islice
from duckduckgo_search import DDGS
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class SearchDDGInput(BaseModel):
    query: str = Field(description="Enter the keyword you want to search for")


@tool(args_schema=SearchDDGInput)
def search_ddg(query, max_result_num=5):
    """
    ## Tool Description
    This tool is for performing web searches using DuckDuckGo.

    ## How the Tool Works
    1. Search the web according to the keywords the user wants to search
    2. Assistant will return the search results to the user in the following format:

    ## Return value format

    Returns
    -------
    List[Dict[str, str]]:
    - title
    - snippet
    - url
    """

    # [1] Conduct a web search
    res = DDGS().text(query, region="jp-jp", safesearch="off", backend="lite")

    # [2] Decompose the result list and put it back
    return [
        {
            "title": r.get("title", ""),
            "snippet": r.get("body", ""),
            "url": r.get("href", ""),
        }
        for r in islice(res, max_result_num)
    ]


class FetchPageInput(BaseModel):
    url: str = Field()


@tool(args_schema=FetchPageInput)
def fetch_page(url, page_num=0, timeout_sec=10):
    """
    ## Tool Description
    This tool retrieves the text from a web page at a specified URL.
    It helps to get more information

    ## How the Tool Works
    1. The user enters the URL of a web page
    2. Assistant returns the HTTP response status code and the body of the message to user.

    ## Set the return value
    Returns
    -------
    Dict[str, Any]:
    - status: str
    - page_content
      - title: str
      - content: str
      - has_next: bool
    """

    try:
        response = requests.get(url, timeout=timeout_sec)
        response.encoding = "utf-8"
    except requests.exceptions.Timeout:
        return {
            "page_content": {
                "error_message": "Could not download page due to Timeout Error. Please try to fetch other pages."
            },
        }

    doc = Document(response.text)
    title = doc.title()
    html_content = doc.summary()
    content = html2text.html2text(html_content)

    chunk_size = 1000 * 3 # [Increase chunk_size]
    content = content[:chunk_size]

    return {
        "page_content": {
            "title": title,
            "content": content, # chunks[page_num], will be undivided and made into content
            "has_next": False,  # page_num < len(chunks) - 1
        },
    }


class SlackThreadHistoryInput(BaseModel):
    channel_id: str = Field(description="Slack channel ID")
    thread_ts: str = Field(description="Thread timestamp")


@tool(args_schema=SlackThreadHistoryInput)
def get_slack_thread_history(channel_id: str, thread_ts: str):
    """
    ## Tool Description
    This is a tool to get the conversation history of Slack threads.

    ## How the Tool Works
    1. Using the specified channel ID and thread timestamp
    2. Call the Slack API to get conversation history
    3. Return conversation history in chronological order

    ## Return value format
    List[Dict[str, str]]:
    - user: User ID
    - text: Message content
    - ts: timestamp
    """
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    
    try:
        response = client.conversations_replies(
            channel=channel_id,
            ts=thread_ts,
            inclusive=True
        )
        
        return [
            {
                "user": msg.get("user", ""),
                "text": msg.get("text", ""),
                "ts": msg.get("ts", "")
            }
            for msg in response["messages"]
        ]
    except SlackApiError as e:
        return {"error": f"Slack API error: {e.response['error']}"}


class SlackMessageInput(BaseModel):
    channel_id: str = Field(description="Slack channel ID")
    text: str = Field(description="Message to send")
    thread_ts: str = Field(description="Thread timestamp (optional)")


@tool(args_schema=SlackMessageInput)
def send_slack_message(channel_id: str, text: str, thread_ts: str = None):
    """
    ## Tool Description
    This is a tool for sending messages to Slack.

    ## How the Tool Works
    1. Use the specified channel ID and message content
    2. Optionally specify a thread timestamp
    3. Call the Slack API to send a message

    ## Return value format
    Dict[str, str]:
    - ts: timestamp of the message sent
    """
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=text,
            thread_ts=thread_ts
        )
        
        return {"ts": response["ts"]}
    except SlackApiError as e:
        return {"error": f"Slack API error: {e.response['error']}"}


all_tools = [search_ddg, fetch_page, get_slack_thread_history, send_slack_message]