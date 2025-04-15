from langchain_core.prompts import ChatPromptTemplate

# Question routing prompt
ROUTE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert in routing user queries to vector stores or web searches.
The Vector Store contains documents related to agents, prompt engineering, and adversarial attacks.
Please use Vector Store for questions on these topics, otherwise use a web search.
    ("human", "{question}")
])

# Document evaluation prompt
GRADE_DOCUMENTS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a grader who evaluates the relevance of retrieved documents to a user's question.
If a document contains keywords or meanings that relate to the user's question, rate it as relevant.
The goal is to eliminate obvious false positives; it doesn't have to be a rigorous test.
Give a binary score "yes" or "no" to indicate whether the document is relevant to your question.
    ("human", "Retrieved document: \n\n {document} \n\n User question: {question}")
])

# Answer generating prompts
GENERATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Slackbot assistant. Please answer the user's question using the conversation history below.
    
Conversation History:
{context}

Please keep the following points in mind when answering:
- Answer naturally, taking into account the flow of the conversation
- Don't repeat anything that has already been covered in the conversation
- When adding new information, please explain it according to the flow of the conversation.
    ("human", "Question: {question}")
])

# Question rewrite prompts
REWRITE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a question rewriter that transforms input questions into better versions optimized for VectorStore search.
Look at the question and infer the questioner's intent/meaning to create better questions for vector search.
    ("human", "Here is the initial question: \n\n {question} \n Formulate an improved question.")
])

# Hallucination assessment prompts
HALLUCINATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the grader assessing whether the production of the LLM is based on/supported by a set of acquired facts.
Give a binary score "yes" or "no". "yes" means that the answer is based/supported by a set of facts.
    ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}")
])

# Answer evaluation prompts
ANSWER_GRADE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the grader who evaluates whether the answer addresses/solves the question.
Give a binary score "yes" or "no". "yes" means that the answer solves the question.
    ("human", "User question: \n\n {question} \n\n LLM generation: {generation}")
])