from typing import List
from typing_extensions import TypedDict
from dotenv import load_dotenv
load_dotenv()
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph
from chains import generate_chain, reflect_chain
import fire

REFLECT = "reflect"
GENERATE = "generate"

class GraphState(TypedDict):
    messages: List[BaseMessage]

def generation_node(state: GraphState) -> GraphState:
    """Generate security analysis based on the current messages."""
    messages = state["messages"]
    response = generate_chain.invoke({"messages": messages})
    return {"messages": messages + [response]}

def reflection_node(state: GraphState) -> GraphState:
    """Generate deeper security critique and additional findings."""
    messages = state["messages"]
    reflection = reflect_chain.invoke({"messages": messages})
    return {"messages": messages + [reflection]}

def should_continue(state: GraphState) -> str:
    """Determine whether to continue or end the analysis."""
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

print("Graph Structure:")
print(graph.get_graph().draw_mermaid())
print("\nASCII Graph:")
graph.get_graph().print_ascii()

def printSecurityReport(response):
    print("\n" + "="*70)
    print("🔒 SECURITY ANALYSIS REPORT")
    print("="*70)

    analysis_round = 0
    for i, message in enumerate(response["messages"]):
        role = message.__class__.__name__
        content = message.content

        if role == "HumanMessage":
            print("\n📋 CODE ANALYZED:")
            print("-" * 50)
            preview = content.split("Analyze this code for security vulnerabilities:\n", 1)[-1][:300]
            print(preview + "..." if len(content) > 300 else preview)
        else:
            if i % 2 == 1:
                analysis_round += 1
                print(f"\n🔍 ANALYSIS ROUND {analysis_round}:")
            else:
                print(f"\n🎯 REFLECTION {analysis_round}:")
            print("-" * 50)
            print(content)


def analyze(code):
    """Analyze code for security vulnerabilities."""
    initial_message = HumanMessage(
        content=f"Analyze this code for security vulnerabilities:\n{code}"
    )
    response = graph.invoke({"messages": [initial_message]})
    printSecurityReport(response)

if __name__ == "__main__": fire.Fire(analyze)
