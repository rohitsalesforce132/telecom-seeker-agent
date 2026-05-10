"""Configuration for Telecom Seeker Agent."""
import os


class Config:
    def __init__(
        self,
        data_dir: str = None,
        max_steps: int = 15,
        min_steps_for_learning: int = 4,
        graph_expansion_depth: int = 3,
        mode: str = "local",
    ):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "..", "data")
        self.max_steps = max_steps
        self.min_steps_for_learning = min_steps_for_learning
        self.graph_expansion_depth = graph_expansion_depth
        self.mode = mode
