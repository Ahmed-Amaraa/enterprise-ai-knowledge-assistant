'''from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.core.config import GEMINI_API_KEY
from app.services.rag_service import RagService

# 1. Initialize the existing RAG service for database queries
rag_service = RagService()

# 2. Define the Search Tool that the Agent can call
@tool
def search_knowledge_base(query: str) -> str:
    """Searches the internal enterprise knowledge base for documents, 
    policies, files, and text chunks. Use this tool whenever the user 
    asks questions about company data or internal topics.
    """
    # Generate query embedding
    query_vector = rag_service.embed_query(query)
    
    # Query Qdrant
    results = rag_service.search_chunks(query_vector=query_vector, top_k=5)
    
    # Build context string
    context = rag_service.build_context(results, min_score=0.4)
    return context if context else "No relevant documents found."


# 3. Define the LangGraph State
class AgentState(TypedDict):
    # add_messages appends new messages to the existing list instead of overwriting
    messages: Annotated[Sequence[BaseMessage], add_messages]


# 4. Initialize Gemini with Tool-binding capability
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.2
)

# Bind the search tool to the model
tools = [search_knowledge_base]
llm_with_tools = llm.bind_tools(tools)


# 5. Define Graph Nodes
def call_agent(state: AgentState):
    """Executes the LLM agent to decide on next action."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# 6. Define Conditional Edges / Router logic
def should_continue(state: AgentState):
    """Determines whether to route to the tool executor node or stop."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the LLM produced a tool call request, transition to tools node
    if getattr(last_message, "tool_calls", None):
        return "tools"
    # Otherwise, finish execution
    return END


# 7. Compile the Workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", call_agent)
workflow.add_node("tools", ToolNode(tools))

# Add connections
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)
workflow.add_edge("tools", "agent")  # Loop back to agent after executing tools

# Compile graph
agent_graph = workflow.compile()'''


'''

Step 3: Integrate with API Routes
Now, modify 

backend/app/api/routes/rag.py
 to execute this graph for chats.

We will convert database message history into LangChain's HumanMessage and AIMessage wrappers, execute the graph, and return the agent's final message.

Example modification for the /chat route:
python
from langchain_core.messages import HumanMessage, AIMessage
from app.services.agentic_rag_service import agent_graph
# Replace the inner execution block inside @router.post("/chat")
@router.post("/chat")
async def chat_rag(
    payload: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = db.query(Conversation).filter(
        Conversation.id == payload.conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    # 1. Fetch conversation history from SQL DB and convert to LangChain classes
    past_messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at.asc()).all()
    langchain_history = []
    for msg in past_messages:
        if msg.role == "user":
            langchain_history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            langchain_history.append(AIMessage(content=msg.content))
    # Append the new user message
    langchain_history.append(HumanMessage(content=payload.question))
    # 2. Run the LangGraph agentic workflow
    try:
        inputs = {"messages": langchain_history}
        outputs = agent_graph.invoke(inputs)
        
        # Get the final response from the last message in state
        final_message = outputs["messages"][-1]
        answer = final_message.content
        
        # 3. Optional: Extract sources from tool runs
        sources = []
        for msg in outputs["messages"]:
            if msg.type == "tool" and msg.name == "search_knowledge_base":
                # Parsing sources from the tool's return context, or tracking it in graph state
                pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent RAG Error: {str(e)}")
    # 4. Save messages to DB and return response (same as your current flow)
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=payload.question
    )
    db.add(user_msg)
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer
    )
    db.add(assistant_msg)
    
    conversation.updated_at = datetime.utcnow()
    db.commit()
    return {
        "answer": answer,
        "content": answer,
        "sources": sources,
        "conversation_id": str(conversation.id)
    }
Step 4: Add Web Search (Optional Agent Upgrade)
If you want the search to be even more powerful, you can add a secondary tool for web search (e.g., using TavilySearch or DuckDuckGoSearch).

python
from langchain_community.tools import DuckDuckGoSearchRun
web_search_tool = DuckDuckGoSearchRun()
tools = [search_knowledge_base, web_search_tool]
The Gemini agent will automatically choose the most appropriate search source depending on the query (e.g., Qdrant for company questions, or DuckDuckGo for general external knowledge).


'''