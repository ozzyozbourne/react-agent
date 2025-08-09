from typing import List
from typing_extensions import TypedDict
from dotenv import load_dotenv
load_dotenv()
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph
from chains import generate_chain, reflect_chain

REFLECT = "reflect"
GENERATE = "generate"

class GraphState(TypedDict):
    messages: List[BaseMessage]

def generation_node(state: GraphState) -> GraphState:
    """Generate a new tweet based on the current messages."""
    messages = state["messages"]
    response = generate_chain.invoke({"messages": messages})
    return {"messages": messages + [response]}

def reflection_node(state: GraphState) -> GraphState:
    """Generate critique and reflection on the current messages."""
    messages = state["messages"]
    reflection = reflect_chain.invoke({"messages": messages})
    return {"messages": messages + [reflection]}

def should_continue(state: GraphState) -> str:
    """Determine whether to continue or end the conversation."""
    messages = state["messages"]
    if len(messages) > 6: return END
    return REFLECT

builder = StateGraph(GraphState)
builder.add_node(GENERATE, generation_node)
builder.add_node(REFLECT, reflection_node)
builder.set_entry_point(GENERATE)
builder.add_conditional_edges(
    GENERATE,
    should_continue,
    {
        END: END,           # If function returns END, go to END
        REFLECT: REFLECT,   # If function returns REFLECT, go to REFLECT
    }
)

builder.add_edge(REFLECT, GENERATE)
graph = builder.compile()

# print("Graph Structure:")
# print(graph.get_graph().draw_mermaid())
# print("\nASCII Graph:")
# graph.get_graph().print_ascii()

def printOut(response):
    print("\n" + "="*50)
    print("CONVERSATION FLOW:")
    print("="*50)

    # Print all messages in the conversation
    for i, message in enumerate(response["messages"]):
        role = message.__class__.__name__
        content = message.content
        print(f"\n{i+1}. {role}:")
        print("-" * 30)
        print(content)


if __name__ == "__main__":
    initial_message = HumanMessage(content="""Make this tweet better:
@LangChainAI
— newly Tool Calling feature is seriously underrated.
After a long wait, it's here- making the implementation of agents across different models with function calling - super easy.
Made a video covering their newest blog post""")

    inputs: GraphState = {"messages": [initial_message]}
    response = graph.invoke(inputs)
    printOut(response)
