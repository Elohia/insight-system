"""
涟漪意识流 ContextEngine
三层记忆架构：模糊层 + 精确层 + 深度层
"""

__version__ = "2.3.0"

from .ripple import Ripple
from .subconscious import SubconsciousEntry
from .three_layer_memory import ThreeLayerMemory

__all__ = ['Ripple', 'SubconsciousEntry', 'ThreeLayerMemory']
