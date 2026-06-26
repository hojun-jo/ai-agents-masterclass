import os

import streamlit as st


def is_debug_mode() -> bool:

    env_value = os.getenv("DEBUG_MODE", "")
    return env_value.strip().lower() in {"1", "true", "yes", "on"}
