#!/usr/bin/env python3
import importlib

MODULES = [
    "clickup_brain_time_travel",
    "clickup_brain_dimension_hopping",
    "clickup_brain_neural_interface",
    "clickup_brain_metaverse",
    "clickup_brain_holographic",
    "clickup_brain_telepathic",
]

def test_imports():
    for name in MODULES:
        importlib.import_module(name)








