import streamlit as st

from projects.manager import create_project, get_doc_registry, list_projects


def render_sidebar() -> str | None:
    """Render the sidebar with project selector. Returns the active project name or None."""
    with st.sidebar:
        st.title("Sotater")
        st.caption("State-of-the-art research assistant")

        projects = list_projects()
        options = ["+ New project"] + projects

        selected = st.selectbox("Project", options, index=0 if not projects else 1)

        if selected == "+ New project":
            with st.form("new_project_form"):
                new_name = st.text_input("Project name")
                new_desc = st.text_input("Description (optional)")
                submitted = st.form_submit_button("Create")

                if submitted and new_name:
                    sanitized = new_name.strip().lower().replace(" ", "-")
                    try:
                        create_project(sanitized, new_desc)
                        st.session_state["active_project"] = sanitized
                        st.rerun()
                    except FileExistsError:
                        st.error(f"Project '{sanitized}' already exists.")
            return None

        st.session_state["active_project"] = selected

        doc_count = len(get_doc_registry(selected))
        st.metric("Indexed documents", doc_count)

        return selected
