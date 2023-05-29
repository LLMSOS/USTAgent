"""Agent for working with pandas objects."""
from typing import Any, Dict, List, Optional

from langchain.agents.agent import AgentExecutor
# from langchain.agents.agent_toolkits.pandas.prompt import PREFIX, SUFFIX
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains.llm import LLMChain
from langchain.tools.python.tool import PythonAstREPLTool

PREFIX = """
You are working with a pandas dataframe in Python. The name of the dataframe is `df`.
When asked about the date, time, location, instructor, course code, section name, section id code, you use course_section dataframe to answer.
Otherwise, use course_info dataframe to answer the question. Within course_info dataframe:
'ATTRIBUTES' gives the special attributes of a course.
'DESCRIPTION' gives detailed information of a course.
'EXCLUSION' lists the courses cannot be taken with the current course.
'PRE-RERQUISITE' lists the courses that are required to take before the current course.

You should use the tools below to answer the question posed of you:"""

SUFFIX = """
This is the result of `print(df_course_section.head())`:
{df_course_section}

This is the result of `print(df_course_info.head())`
{df_course_info}

Begin!
Question: {input}
{agent_scratchpad}"""

def create_course_agent(
    llm: BaseLanguageModel,
    df_course_section: Any,
    df_course_info: Any,
    callback_manager: Optional[BaseCallbackManager] = None,
    prefix: str = PREFIX,
    suffix: str = SUFFIX,
    input_variables: Optional[List[str]] = None,
    verbose: bool = False,
    return_intermediate_steps: bool = False,
    max_iterations: Optional[int] = 15,
    max_execution_time: Optional[float] = None,
    early_stopping_method: str = "force",
    agent_executor_kwargs: Optional[Dict[str, Any]] = None,
    **kwargs: Dict[str, Any],
) -> AgentExecutor:
    """Construct a pandas agent from an LLM and dataframe."""
    try:
        import pandas as pd
    except ImportError:
        raise ValueError(
            "pandas package not found, please install with `pip install pandas`"
        )

    if not isinstance(df_course_section, pd.DataFrame):
        raise ValueError(f"Expected pandas object, got {type(df_course_section)}")
    
    if not isinstance(df_course_info, pd.DataFrame):
        raise ValueError(f"Expected pandas object, got {type(df_course_info)}")

    if input_variables is None:
        input_variables = ["df_course_section", "df_course_info", "input", "agent_scratchpad"]
    tools = [PythonAstREPLTool(locals={"df_course_section": df_course_section, "df_course_info": df_course_info})]
    # , PythonAstREPLTool(locals={"df_course_info": df_course_info})]
    prompt = ZeroShotAgent.create_prompt(
        tools, prefix=prefix, suffix=suffix, input_variables=input_variables
    )
    partial_prompt = prompt.partial(df_course_section=str(df_course_section.head(2).to_markdown()), df_course_info=str(df_course_info.head(2).to_markdown()))
    llm_chain = LLMChain(
        llm=llm,
        prompt=partial_prompt,
        callback_manager=callback_manager,
    )
    tool_names = [tool.name for tool in tools]
    agent = ZeroShotAgent(
        llm_chain=llm_chain,
        allowed_tools=tool_names,
        callback_manager=callback_manager,
        **kwargs,
    )
    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        callback_manager=callback_manager,
        verbose=verbose,
        return_intermediate_steps=return_intermediate_steps,
        max_iterations=max_iterations,
        max_execution_time=max_execution_time,
        early_stopping_method=early_stopping_method,
        **(agent_executor_kwargs or {}),
    )
