"""
LangGraph Cyclical StateGraph Builder & Compiler.
"""

from typing import Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from config.settings import config
from data.database import db_manager
from domain.state import CompanyState
from domain.nodes import (
    studio_director_node,
    director_router,
    product_lead_node,
    system_architect_node,
    lead_developer_node,
    qa_security_lead_node,
    deployment_gate_node,
)


class StudioWorkflowBuilder:
    """Builder class constructing the cyclical LangGraph AI Software Studio."""

    def __init__(self, checkpointer: Optional[SqliteSaver] = None):
        if checkpointer is None:
            conn = db_manager.get_connection()
            self.checkpointer = SqliteSaver(conn)
        else:
            self.checkpointer = checkpointer

    def build_graph(self) -> StateGraph:
        """Construct graph nodes, standard edges, and cyclical routing."""
        workflow = StateGraph(CompanyState)

        # 1. Register Nodes
        workflow.add_node("Studio_Director", studio_director_node)
        workflow.add_node("Product_Lead", product_lead_node)
        workflow.add_node("System_Architect", system_architect_node)
        workflow.add_node("Lead_Developer", lead_developer_node)
        workflow.add_node("QA_Security_Lead", qa_security_lead_node)
        workflow.add_node("Deployment_Gate", deployment_gate_node)

        # 2. Add Feedback Loops (All specialist nodes return to Director)
        workflow.add_edge(START, "Studio_Director")
        workflow.add_edge("Product_Lead", "Studio_Director")
        workflow.add_edge("System_Architect", "Studio_Director")
        workflow.add_edge("Lead_Developer", "Studio_Director")
        workflow.add_edge("QA_Security_Lead", "Studio_Director")
        workflow.add_edge("Deployment_Gate", "Studio_Director")

        # 3. Add Dynamic Conditional Routing from Director
        workflow.add_conditional_edges(
            "Studio_Director",
            director_router,
            {
                "Studio_Director": "Studio_Director",
                "Product_Lead": "Product_Lead",
                "System_Architect": "System_Architect",
                "Lead_Developer": "Lead_Developer",
                "QA_Security_Lead": "QA_Security_Lead",
                "Deployment_Gate": "Deployment_Gate",
                "FINISH": END,
                "END": END,
            }
        )

        return workflow

    def compile(self):
        """Compile workflow with checkpointer and HITL interrupt gate."""
        workflow = self.build_graph()
        return workflow.compile(
            checkpointer=self.checkpointer,
            interrupt_before=["Deployment_Gate"]
        )


# Global compiled studio app instance
workflow_builder = StudioWorkflowBuilder()
studio_app = workflow_builder.compile()
