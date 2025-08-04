from dotenv import load_dotenv
import os
import logging
from typing import Annotated, Literal, TypedDict, List, Dict, Any, Optional
from langgraph.graph.message import add_messages, AnyMessage
from langchain_community.utilities import SQLDatabase
from langchain_groq.chat_models import ChatGroq
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.tools import Tool
from pydantic import BaseModel
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableWithFallbacks, RunnableLambda
from langgraph.graph import StateGraph, START, END
from langgraph.errors import GraphRecursionError
from langgraph.prebuilt import ToolNode
from sqlalchemy.engine import URL
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
import re
from langchain_core.tools import tool

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")


# === LOGGING SETUP (Console logging DISABLED - ALL LEVELS TO FILE) ===
def get_logger(name: str) -> logging.Logger:
    """
    Create and return a logger that saves ALL log levels to file only (no console output).
    Captures DEBUG, INFO, WARNING, ERROR, CRITICAL - everything under control.
    Avoids duplicate handlers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Capture everything from DEBUG and above
    logger.propagate = False
    if logger.handlers:
        return logger  # Prevent adding handlers multiple times
    # Create logs directory
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    # Daily log file
    log_file = os.path.join(log_dir, f"{name}.log")
    # File handler only (NO console handler) - Set to DEBUG to capture ALL levels
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.DEBUG)  # Ensure all levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) are written
    # Enhanced formatter to clearly show all log levels
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(formatter)
    # Add handler
    logger.addHandler(fh)
    return logger

logger = get_logger("SQLAgent")


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    retry_count: Optional[int]


class QueryInput(BaseModel):
    query: str

class SQLAgent:

    def __init__(
            self,
            db_path: str,
            # connection_string: str,
            model_name: str = "llama3-70b-8192"
    ):
         """
        Initialize the SQL Agent with a database connection and LLM configuration.

        """
         
         logger.info("Initializing sql Agent!!!")
         self.connection_string = f"sqlite:///{db_path}"
         self.db = SQLDatabase.from_uri(self.connection_string)
         logger.info(f"Database connection established: {self.connection_string}")

         self.llm = ChatGroq(model=model_name, api_key=api_key)
         logger.info(f"llm initialized: {model_name}")

        # Setup components
         self._setup_tools()
         self._setup_prompts()
         self._build_graph()
         logger.info("Setup completed!") 

    def _setup_tools(self) -> None:
        """Set up the required tools for database interaction."""
        # Initialize toolkit and extract basic tools

        logger.info("Setting up tools....")
        toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        logger.info("SQLDatabaseToolkit initialized.")
        tools = toolkit.get_tools()
        logger.info(f"Extracted {len(tools)} tools from the toolkit.")


        # Extract standard tools
        self.list_tables_tool = next(
            tool for tool in tools if tool.name == "sql_db_list_tables"
        )
        logger.info("List tables tool initialized.")
        self.get_schema_tool = next(
            tool for tool in tools if tool.name == "sql_db_schema"
        )
        logger.info("Get schema tool initialized.")

    
         # Define the query execution tool
        
        def db_query_tool(query: str) -> str:
            result = self.db.run_no_throw(query)
            logger.info(f"Executing query: {query}")
            if not result:
                logger.error("Query is not correct.")
                return "Error: Query failed. Please rewrite your query and try again."
            return result

        self.db_query_tool = Tool.from_function(
            name="db_query_tool",
            func=db_query_tool,
            args_schema=QueryInput,
            description=(
                "Execute a SQL query against the database and get back the result."
                "If the query is not correct, an error message will be returned."
                "If an error is returned, rewrite the query, check the query, and try again."
            )
        )   

        # @tool
        # def db_query_tool(query: str) -> str:
        #     """
        #     Execute a SQL query against the database and get back the result.
        #     If the query is not correct, an error message will be returned.
        #     If an error is returned, rewrite the query, check the query, and try again.
        #     """
        #     result = self.db.run_no_throw(query)
        #     if not result:
        #         return "Error: Query failed. Please rewrite your query and try again."
        #     return result

        # self.db_query_tool = db_query_tool



    def _setup_prompts(self) -> None:
        """Set up the system prompts for query generation and checking."""
        # Query generation prompt
        logger.info("Setting up prompts for SQL Agent...")
        self.query_gen_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
**You are an SQL expert with a strong focus on precision and clarity. Your role is to assist with SQL query generation, analysis of query results, and interpretation to answer user questions.** 

Follow these instructions carefully:

1. **Understand the Task**: 
   - Identify the user's question, the relevant table schemas (if provided), the executed query (if any), and the query result or error (if present).

2. **Handle Scenarios**:
   - **If no executed query or query result exists**: Create a syntactically correct MySQL query to answer the user's question. 
     - Ensure the query is designed for readability and does not make any DML (INSERT, UPDATE, DELETE, DROP) changes to the database.
     - Respond with only the query statement. For example: SELECT id, name FROM pets;.
   - **If a query was executed but returned an error**: Respond by repeating the exact error message. For example: "Error: Pets table doesn't exist.".
   - **If a query was executed successfully**: Interpret the results and respond with an answer in the format: Answer: <<question answer>>.
   - **If the user's question is unclear or the query results do not provide a clear answer**: State that additional clarification or information is needed.

3. **Adhere to Best Practices**:
   - Write queries using proper indentation for clarity.
   - Use aliases, filtering, and ordering where necessary for optimized and comprehensible results.
""",
                ),
                ("placeholder", "{messages}"),
            ]
        )
        logger.info("Query generation prompt compelted.")
         
        logger.info("Setting up query checking prompt...")
        # Query checking prompt
        self.query_check_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are a SQL expert with a strong attention to detail.
Double check the SQLite query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

You will call the appropriate tool to execute the query after running this check.
""",
                ),
                ("placeholder", "{messages}"),
            ]
        )
        logger.info("Query checking prompt compelted.")

    def _create_tool_node_with_fallback(self, tools: list) -> RunnableWithFallbacks:
        """
        Create a tool node with error handling.

        Args:
            tools: List of tools to include in the node

        Returns:
            A tool node with error handling fallbacks
        """
        

        logger.info("Creating tool node with fallback with error handling")
        def handle_tool_error(state: Dict) -> Dict:
            """Handle errors from tool execution."""
            error = state.get("error")  
            tool_calls = state["messages"][-1].tool_calls

            logger.error(f"Tool execution failed: {error}")

            return {
                "messages": [
                    ToolMessage(
                        content=f"Error {repr(error)}\nplease fix your mistakes.",
                        tool_call_id=tc["id"],
                    )
                    for tc in tool_calls
                ]
            }

        return ToolNode(tools).with_fallbacks(
            [RunnableLambda(handle_tool_error)], exception_key="error"
        )

    def _build_graph(self) -> None:
        """Build the LangGraph workflow."""

        logger.info("Building the LangGraph workflow...")
        # Initialize graph
        workflow = StateGraph(State)

        # Define node functions
        def first_tool_call(state: State) -> Dict[str, List[AIMessage]]:
            """Initial node to list database tables."""
            logger.info("Executing first tool call to list database tables.")
            return {
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[
                            {
                                "name": "sql_db_list_tables",
                                "args": {},
                                "id": "tool_abcd123",
                            }
                        ],
                    )
                ]
            }

        def model_check_query(state: State) -> Dict[str, List[AIMessage]]:
            """Check if the SQL query is correct before executing it."""
            logger.info("Checking the SQL query for correctness.")
            query_check = self.query_check_prompt | self.llm.bind_tools(
                [self.db_query_tool]
            )
            logger.info("Executing query check...")

            logger.info(f"Current messages in model query check: {state['messages'][-1]}")

            return {
                "messages": [query_check.invoke({"messages": [state["messages"][-1]]})]
            }

        def model_get_schema(state: State) -> Dict[str, List[AIMessage]]:
            """Get database schema information."""
            logger.info("Retrieving database schema information.")
            messages = state["messages"]
            schema_selection_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """
You are a database schema analyzer. Based on the user's question and the list of available tables, 
you need to intelligently select ALL tables that might be relevant to answer the question.

IMPORTANT GUIDELINES:
1. For questions about students, grades, courses, etc. - select ALL related tables (students, grades, enrollments, courses, etc.)
2. For questions about orders, customers, products - select ALL related tables (customers, orders, order_items, products, etc.)
3. When in doubt, it's better to select MORE tables rather than fewer
4. Tables are often connected through foreign keys - consider relationships
5. You can pass multiple table names to sql_db_schema tool separated by commas

Examples:
- Question: "What are John's grades?" → Get schemas for: students, grades, enrollments, courses
- Question: "Show customer orders" → Get schemas for: customers, orders, order_items, products

Based on the user's question and available tables, call sql_db_schema with ALL potentially relevant table names.
        """,
                    ),
                    ("placeholder", "{messages}"),
                ]
            )
            schema_chain = schema_selection_prompt | self.llm.bind_tools(
                [self.get_schema_tool]
            )
            response = schema_chain.invoke({"messages": messages})

            logger.info(f"Current messages from model get schema: {response}")
            logger.info("Invoking get schema tool...")
            return {"messages": [response]}

        query_gen = self.query_gen_prompt | self.llm

        def query_gen_node(state: State) -> Dict[str, List[AIMessage]]:
            """Generate SQL query based on user question and context."""
            logger.info("Generating SQL query from user question.")
            message = query_gen.invoke(state)
            logger.info(f"Generated message in query gen node: {message}")
            return {"messages": [message]}

        # Define edge conditions
        def should_continue(state: State) -> Literal[END, "correct_query", "query_gen"]:
            """Determine next step based on current state."""

            logger.info("Determining next step based on current state.")
            messages = state["messages"]
            last_message = messages[-1]
            logger.info(
                f"Last message content in should continue: {last_message.content}"
            )

            if last_message.content.startswith("Answer:"):
                logger.info("Answer found in last message, ending workflow.")
                return END
            if last_message.content.startswith("Error:"):
                logger.info("Error found in last message, generating new query.")
                return "query_gen"
            else:
                logger.info("No specific instruction found, correcting query.")
                return "correct_query"

        # Add nodes to graph
        logger.info("Adding nodes....")
        workflow.add_node("first_tool_call", first_tool_call)
        logger.info("First tool call node added!!")

        workflow.add_node(
            "list_tables_tool",
            self._create_tool_node_with_fallback([self.list_tables_tool]),
        )
        logger.info("List tables tool node added.")

        workflow.add_node(
            "get_schema_tool",
            self._create_tool_node_with_fallback([self.get_schema_tool]),
        )
        logger.info("Get schema tool node added.")
        

        workflow.add_node("model_get_schema", model_get_schema)
        logger.info("Model get schema node added.")

        workflow.add_node("query_gen", query_gen_node)
        logger.info("Query generation node added.")


        workflow.add_node("correct_query", model_check_query)
        logger.info("Model check query node added.")


        workflow.add_node(
            "execute_query", self._create_tool_node_with_fallback([self.db_query_tool])
        )
        logger.info("Execute query node added.")

        
        # Add edges
        logger.info("Adding edges to the workflow...")

        workflow.add_edge(START, "first_tool_call")
        logger.info("Edge: START → first_tool_call")

        workflow.add_edge("first_tool_call", "list_tables_tool")
        logger.info("Edge: first_tool_call → list_tables_tool")
        
        workflow.add_edge("list_tables_tool", "model_get_schema")
        logger.info("Edge: List tables tool -> model get schema edge added.")

        workflow.add_edge("model_get_schema", "get_schema_tool")
        logger.info("Edge: model get schema -> get schema tool edge added.")
        
        workflow.add_edge("get_schema_tool", "query_gen")
        logger.info("Edge: Get schema tool -> query generation edge added.")

        workflow.add_conditional_edges(
            "query_gen",
            should_continue,
        )
        logger.info("Edge: Conditional edges for query generation added.")

        workflow.add_edge("correct_query", "execute_query")
        logger.info("Edge: Correct query -> execute query edge added.")

        workflow.add_edge("execute_query", "query_gen")
        logger.info("Edge: Execute query -> query generation edge added.")

        # Compile the workflow into a runnable
        logger.info("Compiling the workflow !!!!")
        self.app = workflow.compile()
        logger.info("Workflow compiled successfully !!!!")

    def query(self, question: str) -> Dict[str, Any]:
        """
        Execute a query against the database using the agent.

        Args:
            question: Natural language question to answer using the database

        Returns:
            Dictionary containing the SQL query and answer
        """
        logger.info(f"Received query: {question}")
        try:
            messages = self.app.invoke({"messages": [HumanMessage(content=question)]})
            final_sql_query = self._extract_final_sql_query(messages)
            logger.info(f"Final SQL query extracted: {final_sql_query}")

            last_message = messages["messages"][-1]
            content = last_message.content
            logger.info(f"Last message content: {content}")

            result = {"sql_query": final_sql_query, "answer": None}

            if content and content.startswith("Answer:"):
                result["answer"] = content.split("Answer:", 1)[1].strip()
                logger.info(f"Result extracted: {result}")

            return result

        except GraphRecursionError:
            logger.error("Graph recursion error occurred. Unable to process the query.")

            return {
                "sql_query": None,
                "answer": "Unable to process the query with the current context. Please review the input and try again.",
            }

    def _extract_final_sql_query(self, messages: Dict) -> Optional[str]:
        logger.info("Extracting final SQL query from messages...")

    #     # First check tool_calls
    #     for msg in messages.get("messages", []):
    #      if hasattr(msg, "tool_calls"):
    #         for tool_call in msg.tool_calls:
    #             if tool_call.get("name") == "db_query_tool":
    #                 args = tool_call.get("args", {})
    #                 if "query" in args:
    #                     return args["query"]
    
    # # Then fallback to text-based extraction
        for msg in reversed(messages.get("messages", [])):
            self.logger.info(f"Messages for final sql: {msg}")
            if hasattr(msg, "content") and msg.content:
                content = msg.content
                if "SELECT" in content.upper():
                    query = re.search(r"SELECT.*?;", content, re.IGNORECASE | re.DOTALL)
                    if query:
                        self.logger.info("SQL query found in message content.")
                        sql_query = query.group(0).strip()
                        self.logger.info(f"SQL query found: {sql_query}")
                        return sql_query
        return None

       