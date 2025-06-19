import os
import pandas as pd
from langchain_groq import ChatGroq
from langchain.agents import tool
from langchain import hub
from langgraph.prebuilt import create_react_agent
from IPython.display import display, Markdown
from io import BytesIO
import base64
from db_utils import get_sql_db, fix_common_sql_typos, GROQ_API_KEY
from charts import plot_and_encode_dashboard, pie_chart
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

# === LLM ===
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0,
)

# === Database & Tools ===
db = get_sql_db()

@tool("SQL + Plot Tool", return_direct=True)
def run_sql_and_plot(sql_query: str) -> str:
    """Run a SQL query and generate charts if applicable."""
    try:
        sql_query = fix_common_sql_typos(sql_query)
        df = pd.read_sql(sql_query, db._engine)
    except Exception as e:
        return f"SQL Error: {e}"

    if df.empty:
        return "No results found."

    # Show query results
    table_md = df.to_markdown(index=False)
    display(Markdown(f"**Query Result Table:**\n\n{table_md}"))

    x = df[df.columns[0]].astype(str).tolist()
    y = pd.to_numeric(df[df.columns[1]], errors='coerce').tolist()
    filtered = [(xi, yi) for xi, yi in zip(x, y) if not pd.isna(yi)]

    if not filtered:
        return "No numeric data to plot."

    x, y = zip(*filtered)
    x, y = list(x), list(y)
    top_x, top_y = x[:10], y[:10]
    label = df.columns[1]

    # Chart setup
    plot_funcs = [
        lambda ax: ax.bar(x, y, color='#c3a87f', width=0.1, label=label),
        lambda ax: ax.plot(x, y, color='#c3a87f', marker='o', label=label),
        lambda ax: pie_chart(ax, top_x, top_y),
        lambda ax: ax.barh(x, y, color='#c3a87f', height=0.4, label=label)
    ]
    chart_types = ["bar", "line", "pie", "barh"]

    dashboard_image = plot_and_encode_dashboard(
        plot_funcs,
        [x, x, top_x, x],
        [y, y, top_y, y],
        chart_types
    )
    if dashboard_image:
        try:
            buffer = BytesIO()
            dashboard_image.save(buffer, format="PNG")
            img_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return f"__chart__:{img_data}"
        except Exception as e:
            return f"Chart render error: {e}"
    else:
        return f"**Query Result Table:**\n\n{table_md}"



# === Tools & Agent Setup ===
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = [t for t in toolkit.get_tools() if t.name != "run_sql_and_plot"]
tools.append(run_sql_and_plot)

prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
system_message = prompt_template.format(dialect="SQLite", top_k=5) + "\nEnsure correct SQL syntax, e.g., include a space in LIMIT clauses like LIMIT 3."
agent_executor = create_react_agent(llm, tools, prompt=system_message)

# Setup tools & agent here...

def run_query_and_get_response(query: str) -> str:
    result = agent_executor.invoke({"messages": [("user", query)]})

    if isinstance(result, dict) and "messages" in result:
        for msg in reversed(result["messages"]):
            if hasattr(msg, "content") and msg.content:
                return msg.content

    if isinstance(result, dict) and "output" in result:
        return result["output"]

    if hasattr(result, "__iter__") and not isinstance(result, str):
        for msg in result:
            if hasattr(msg, "content") and msg.content:
                return msg.content

    return str(result)


if __name__ == "__main__":
    query = "Which country's customers spent the most? Please show a chart."
    response = run_query_and_get_response(query)
    print(response)


