from dotenv import load_dotenv
load_dotenv()
import os
import uuid
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from fastmcp import FastMCP
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import bs4
from langchain_community.document_loaders import WebBaseLoader
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.vectorstores import InMemoryVectorStore



prompts = ChatPromptTemplate.from_template(
    """
    You are a helpful assistant.
    Use the following pieces of context to answer the users question.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    {context}
    Question: {question}
    """
)

bs4_strainer = bs4.SoupStrainer(class_=["title", "content"])
web_loader = WebBaseLoader(
    web_paths= (
        "https://python.langchain.com/docs/get_started/introduction",
    ),
    bs_kwargs={
        "parse_only": bs4_strainer
    },
    requests_kwargs={
        "timeout": 30
    }
)

file_content = web_loader.load()

text_splitters = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitters.split_documents(file_content)
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
db = InMemoryVectorStore.from_documents(docs, embeddings)


api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set")

llm = ChatOpenAI(model="gpt-3.5-turbo",
                 api_key = api_key,
                 )

@tool
def retriever_tool(query):
    """retrieve the most relative and latest answer based on the given query.

    Args:
        query: the given query to search for.

    Returns:
        return the most relative and lastest answer based on the query.
    """
    retrieve = db.as_retriever()
    retrieve_tool = retrieve.similarity_search(query, k=5)
    serialize_rsp = "\n\n".join([f"['Title: {doc.metadata.get('title', '')}'\n'Content : {doc.page_content}'" for doc in retrieve_tool])
    return serialize_rsp



mcp = FastMCP("rag_agents")
@mcp.tool()
def rag_agents(query: str, thread_id: str , user_id: str):
    """search for the query from websites, and return to the user.

    Args:
        query: the query from user.

    Return:
        return the answer.
    """

    if not thread_id:
        thread_id = str(uuid.uuid4())
    if not  user_id:
        user_id = str(uuid.uuid4())

    agents = create_react_agent(
        llm= llm,
        tools=[retriever_tool],
        checkpointer= InMemorySaver(),
        prompt = prompts
    )

    full_prompt = prompts.format(question=query)

    init_state = {
        "messages": [HumanMessage(content=full_prompt)]
    }
    config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}

    agents_res = agents.invoke(init_state,  config=config)
    return agents_res["messages"][-1].content


if __name__ == "__main__":
    mcp.run()



