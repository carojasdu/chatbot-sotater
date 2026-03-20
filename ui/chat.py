import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agent.graph import build_agent


@st.cache_resource
def get_agent():
    return build_agent()


def render_chat_tab(project_name: str) -> None:
    """Render the chat interface with the LangGraph agent."""
    if "chat_histories" not in st.session_state:
        st.session_state["chat_histories"] = {}
    if "agent_messages" not in st.session_state:
        st.session_state["agent_messages"] = {}

    display_history = st.session_state["chat_histories"].setdefault(project_name, [])
    agent_messages = st.session_state["agent_messages"].setdefault(project_name, [])

    for msg in display_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about a topic to explore..."):
        display_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Inject project name into the user message so tools know which project to use
        augmented_prompt = f"[Project: {project_name}]\n\n{prompt}"
        agent_messages.append(HumanMessage(content=augmented_prompt))

        agent = get_agent()

        with st.chat_message("assistant"):
            try:
                with st.status("Thinking...", expanded=True) as status:
                    response = agent.invoke(
                        {"messages": agent_messages},
                    )

                    # Process response messages for display
                    for msg in response["messages"][len(agent_messages):]:
                        if isinstance(msg, AIMessage) and msg.tool_calls:
                            for tc in msg.tool_calls:
                                st.write(f"Using tool: **{tc['name']}**")
                                args_display = ", ".join(
                                    f"{k}={v!r}" for k, v in tc["args"].items()
                                    if k != "project_name"
                                )
                                if args_display:
                                    st.caption(args_display)
                        elif isinstance(msg, ToolMessage):
                            st.caption(f"Tool result: {msg.content[:150]}...")

                    status.update(label="Done", state="complete", expanded=False)

                # Get the final AI message
                final_messages = response["messages"]
                final_response = ""
                for msg in reversed(final_messages):
                    if isinstance(msg, AIMessage) and not msg.tool_calls:
                        final_response = msg.content
                        break

                st.markdown(final_response)
                display_history.append({"role": "assistant", "content": final_response})
                st.session_state["agent_messages"][project_name] = response["messages"]

            except Exception as e:
                error_msg = f"Something went wrong: {e}"
                st.error(error_msg)
                display_history.append({"role": "assistant", "content": error_msg})
                # Remove the failed user message from agent history to avoid broken state
                agent_messages.pop()
