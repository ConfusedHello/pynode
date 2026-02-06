import pynode_core
import random
from typing import List, Dict, Any, Optional, Union, Tuple

def pause(time: int):
    pynode_core.add_event(pynode_core.EventPause(time))

def delay(func, time: int, args: List[Any] = [], repeat: bool = False) -> int:
    def execute():
        pynode_core.execute_function(func, args)
    if repeat:
        delay_id = pynode_core.timer.set_interval(execute, time)
        pynode_core.PynodeCoreGlobals.delay_type[delay_id] = 1
        return delay_id
    else:
        delay_id = pynode_core.timer.set_timeout(execute, time)
        pynode_core.PynodeCoreGlobals.delay_type[delay_id] = 0
        return delay_id

def cancel_delay(delay_id: int):
    if delay_id in pynode_core.PynodeCoreGlobals.delay_type:
        if pynode_core.PynodeCoreGlobals.delay_type[delay_id] == 1:
            pynode_core.timer.clear_interval(delay_id)
        else:
            pynode_core.timer.clear_timeout(delay_id)
        del pynode_core.PynodeCoreGlobals.delay_type[delay_id]

def clear_delays():
    delay_ids = list(pynode_core.PynodeCoreGlobals.delay_type.keys())
    for delay_id in delay_ids:
        cancel_delay(delay_id)

def print_debug(value: Any):
    pynode_core.do_print(str(value) + "\n")

def register_click_listener(func):
    pynode_core.PynodeCoreGlobals.click_listener_func["f"] = func

class Color:
    RED: 'Color'
    GREEN: 'Color'
    BLUE: 'Color'
    YELLOW: 'Color'
    WHITE: 'Color'
    LIGHT_GREY: 'Color'
    GREY: 'Color'
    DARK_GREY: 'Color'
    BLACK: 'Color'
    TRANSPARENT: 'Color'

    def __init__(self, red: int, green: int, blue: int, transparent: bool = False):
        self._red = red
        self._green = green
        self._blue = blue
        self._transparent = transparent

    @staticmethod
    def rgb(red: int, green: int, blue: int) -> 'Color':
        return Color(red, green, blue)

    def hex_string(self) -> str:
        if self._transparent: return "transparent"
        else: return "#%02x%02x%02x" % (self._red, self._green, self._blue)

    def __str__(self) -> str:
        return f"({self._red},{self._green},{self._blue})"

    def __repr__(self) -> str:
        return f"Color({self._red}, {self._green}, {self._blue}, transparent={self._transparent})"

    @property
    def red(self) -> int: return self._red
    @property
    def green(self) -> int: return self._green
    @property
    def blue(self) -> int: return self._blue

Color.RED = Color(180, 0, 0)
Color.GREEN = Color(0, 150, 0)
Color.BLUE = Color(0, 0, 200)
Color.YELLOW = Color(255, 215, 0)
Color.WHITE = Color(255, 255, 255)
Color.LIGHT_GREY = Color(199, 199, 199)
Color.GREY = Color(127, 127, 127)
Color.DARK_GREY = Color(82, 82, 82)
Color.BLACK = Color(0, 0, 0)
Color.TRANSPARENT = Color(0, 0, 0, True)

class CustomStyle:
    def __init__(self, size: int, color: Color, outline: Optional[Color] = Color.TRANSPARENT):
        self._size = size
        self._color = color
        self._outline = outline
        self._has_outline = outline is not None

    def data(self, element: Any) -> str:
        return f"{self._size},{self._color.hex_string()},{element._color.hex_string() if self._outline is None else self._outline.hex_string()},{self._has_outline}"

    def __repr__(self) -> str:
        return f"CustomStyle(size={self._size}, color={self._color}, outline={self._outline})"

class Node:
    def __init__(self, id: Optional[Any] = None, value: Optional[Any] = None):
        if id is None:
            self._id = pynode_core.next_user_id()
        else:
            self._id = id
            
        self._value = value if value is not None else self._id
        self._incident_edges: List['Edge'] = []
        self._attributes: Dict[str, Any] = {}
        self._priority = 0
        self._position: Optional[List[int]] = None
        self._is_pos_relative = False
        self._labels: List[str] = ["", ""]
        self._size = 12
        self._color = Color.DARK_GREY
        self._value_style = CustomStyle(13, Color.WHITE, None)
        self._label_styles: List[CustomStyle] = [CustomStyle(10, Color.GREY), CustomStyle(10, Color.GREY)]
        self._internal_id = pynode_core.next_global_id()

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, new_value: Any):
        self._value = new_value
        pynode_core.add_event(pynode_core.Event(pynode_core.js_node_set_value, [self._internal_id, str(new_value) if new_value is not None else ""]), self)

    def set_value(self, value: Any) -> 'Node':
        self.value = value
        return self

    @property
    def incident_edges(self) -> List['Edge']:
        return list(self._incident_edges)

    @property
    def incoming_edges(self) -> List['Edge']:
        return [e for e in self._incident_edges if not e.directed or e.target == self]

    @property
    def outgoing_edges(self) -> List['Edge']:
        return [e for e in self._incident_edges if not e.directed or e.source == self]

    def adjacent_nodes(self) -> List['Node']:
        return [e.source if e.target is self else e.target for e in self._incident_edges]

    def predecessor_nodes(self) -> List['Node']:
        return [e.source if e.target is self else e.target for e in self.incoming_edges]

    def successor_nodes(self) -> List['Node']:
        return [e.source if e.target is self else e.target for e in self.outgoing_edges]

    def degree(self) -> int: return len(self._incident_edges)
    def indegree(self) -> int: return len(self.incoming_edges)
    def outdegree(self) -> int: return len(self.outgoing_edges)

    def set_attribute(self, name: str, value: Any) -> 'Node':
        self._attributes[name] = value
        return self

    def attribute(self, name: str) -> Any:
        return self._attributes.get(name)

    @property
    def priority(self) -> int:
        return self._priority

    @priority.setter
    def priority(self, value: int):
        self._priority = value

    def set_priority(self, value: int) -> 'Node':
        self.priority = value
        return self

    @property
    def position(self) -> Optional[Tuple[int, int]]:
        # Note: Function should be used asynchronously in the online version. Call it in delayed and/or click listener functions.
        data = pynode_core.get_data((pynode_core.Event(pynode_core.js_node_get_position, [self._internal_id])))
        if graph.has_node(self) and data is not None and data[0] is not None and data[1] is not None:
            return int(data[0]), int(data[1])
        elif self._position is None:
            return None
        else:
            if self._is_pos_relative and data is not None and data[2] is not None and data[3] is not None:
                return int(self._position[0] * data[2]), int(self._position[1] * data[3])
            else:
                return int(self._position[0]), int(self._position[1])

    @position.setter
    def position(self, pos: Optional[Tuple[int, int]]):
        if pos is None:
            self.set_position(None, None)
        else:
            self.set_position(pos[0], pos[1])

    def set_position(self, x: Optional[int], y: Optional[int] = None, relative: bool = False) -> 'Node':
        self._position = [x, y]
        if x is None or y is None: self._position = None
        self._is_pos_relative = relative
        pynode_core.add_event(pynode_core.Event(pynode_core.js_node_set_position, [self._internal_id, x, y, relative]), self)
        return self

    def set_label(self, text: str, label_id: int = 0) -> 'Node':
        self._labels[label_id] = text
        pynode_core.add_event(pynode_core.Event(pynode_core.js_node_set_label, [self._internal_id, str(text) if text is not None else "", label_id]), self)
        return self

    def label(self, label_id: int = 0) -> str:
        return self._labels[label_id]

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, new_size: int):
        self._size = new_size
        pynode_core.add_event(pynode_core.Event(pynode_core.js_node_set_size, [self._internal_id, new_size]), self)

    def set_size(self, size: int) -> 'Node':
        self.size = size
        return self

    @property
    def color(self) -> Color:
        return self._color

    @color.setter
    def color(self, new_color: Color):
        self._color = new_color
        pynode_core.add_event(pynode_core.Event(pynode_core.js_node_set_color, [self._internal_id, new_color.hex_string(), self._value_style.data(self)]), self)

    def set_color(self, color: Color) -> 'Node':
        self.color = color
        return self

    def set_text_size(self, size: int) -> 'Node':
        self._value_style._size = size
        pynode_core.add_event(pynode_core.Event(pynode_core.js_node_set_value_style, [self._internal_id, self._value_style.data(self)]), self)
        return self

    def set_text_color(self, color: Color) -> 'Node':
        self._value_style._color = color
        pynode_core.add_event(pynode_core.Event(pynode_core.js_node_set_value_style, [self._internal_id, self._value_style.data(self)]), self)
        return self
    
    def set_value_style(self, size: int = None, color: Color = None, outline: int = -1) -> 'Node':
        self._value_style = CustomStyle(self._value_style._size if size is None else size, self._value_style._color if color is None else color, self._value_style._outline if outline == -1 else outline)
        pynode_core.add_event(pynode_core.Event(pynode_core.js_node_set_value_style, [self._internal_id, self._value_style.data(self)]), self)
        return self

    def set_label_style(self, size: int = None, color: Color = None, outline: Color = None, label_id: int = None) -> 'Node':
        if label_id is None or (label_id != 0 and label_id != 1):
            style1 = CustomStyle(self._label_styles[0]._size if size is None else size, self._label_styles[0]._color if color is None else color, self._label_styles[0]._outline if outline is None else outline)
            style2 = CustomStyle(self._label_styles[1]._size if size is None else size, self._label_styles[1]._color if color is None else color, self._label_styles[1]._outline if outline is None else outline)
            self._label_styles[0] = style1
            self._label_styles[1] = style2
            pynode_core.add_event(pynode_core.Event(pynode_core.js_node_set_label_style, [self._internal_id, self._label_styles[0].data(self), 0]), self)
            pynode_core.add_event(pynode_core.Event(pynode_core.js_node_set_label_style, [self._internal_id, self._label_styles[1].data(self), 1]), self)
        else:
            style = CustomStyle(self._label_styles[label_id]._size if size is None else size,Color.WHITE if color is None else color, outline)
            self._label_styles[label_id] = style
            pynode_core.add_event(pynode_core.Event(pynode_core.js_node_set_label_style, [self._internal_id, self._label_styles[label_id].data(self), label_id]), self)
        return self

    def highlight(self, color: Color = None, size: int = None) -> None:
        if color is None: color = Color.RED # default color if not specified
        if size is None: size = self._size * 1.5
        pynode_core.add_event(pynode_core.Event(pynode_core.js_node_highlight, [self._internal_id, size, color.hex_string() if color is not None else None]), self)

    def id(self) -> Any:
        return self._id

    def _data(self) -> Dict[str, Any]:
        d = {"id": self._internal_id, "label": str(self._value) if self._value is not None else "", "labelStyle": self._value_style.data(self), "topRightLabel": str(self._labels[0]) if self._labels[0] is not None else "", "topLeftLabel": str(self._labels[1]) if self._labels[1] is not None else "", "topRightLabelStyle": self._label_styles[0].data(self), "topLeftLabelStyle": self._label_styles[1].data(self), "r": self._size, "color": self._color.hex_string(), "fixed": (self._position is not None), "static": (self._position is not None), "ax": 0, "ay": 0, "rx": 0.0, "ry": 0.0, "relativePosition": False}
        if self._position is not None:
            if self._is_pos_relative:
                d["relativePosition"] = True
                d["rx"] = self._position[0]; d["ry"] = self._position[1]
            else:
                d["ax"] = self._position[0]; d["ay"] = self._position[1]
                d["x"] = self._position[0]; d["y"] = self._position[1]
        return d

    def __hash__(self) -> int:
        return hash(self._id)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Node):
            return self._id == other._id
        return False

    def __lt__(self, other: Any) -> bool: return self._priority < other._priority if isinstance(other, Node) else NotImplemented
    def __le__(self, other: Any) -> bool: return self._priority <= other._priority if isinstance(other, Node) else NotImplemented
    def __gt__(self, other: Any) -> bool: return self._priority > other._priority if isinstance(other, Node) else NotImplemented
    def __ge__(self, other: Any) -> bool: return self._priority >= other._priority if isinstance(other, Node) else NotImplemented

    def __str__(self) -> str:
        return str(self._id)
    
    def __repr__(self) -> str:
        return f"Node(id={self._id}, value={self._value})"

class Edge:
    def __init__(self, source: Node, target: Node, weight: Optional[Any] = None, directed: bool = False):
        self._source = source
        self._target = target
        self._weight = weight
        self._directed = directed
        self._attributes: Dict[str, Any] = {}
        self._priority = 0
        self._width = 2
        self._color = Color.LIGHT_GREY
        self._weight_style = CustomStyle(10, Color.GREY)
        self._internal_id = pynode_core.next_global_id()

    @property
    def source_node(self) -> Node:
        return self._source
    
    @property
    def target_node(self) -> Node:
        return self._target

    # Retained for compatibility but updated to be cleaner or deprecated if we wanted
    def source(self, target: Node = None) -> Node:
        # Deprecated usage behavior
        if target is not None: return self.other_node(target)
        return self._source

    def target(self, source: Node = None) -> Node:
        # Deprecated usage behavior
        if source is not None: return self.other_node(source)
        return self._target

    @property
    def weight(self) -> Any:
        return self._weight
    
    @weight.setter
    def weight(self, new_weight: Any):
        self._weight = new_weight
        pynode_core.add_event(pynode_core.Event(pynode_core.js_edge_set_weight, [self._internal_id, str(new_weight) if new_weight is not None else ""]), self)

    def set_weight(self, weight: Any = None) -> 'Edge':
        self.weight = weight
        return self

    @property
    def directed(self) -> bool:
        return self._directed
    
    @directed.setter
    def directed(self, is_directed: bool):
        self._directed = is_directed
        pynode_core.add_event(pynode_core.Event(pynode_core.js_edge_set_directed, [self._internal_id, self._directed]), self)

    def set_directed(self, directed: bool = True) -> 'Edge':
        self.directed = directed
        return self

    def other_node(self, node: Node) -> Node:
        if self._source is node or self._source == node:
            return self._target
        return self._source

    def set_attribute(self, name: str, value: Any) -> 'Edge':
        self._attributes[name] = value
        return self

    def attribute(self, name: str) -> Any:
        return self._attributes.get(name)

    @property
    def priority(self) -> int:
        return self._priority
    
    @priority.setter
    def priority(self, val: int):
        self._priority = val

    def set_priority(self, value: int) -> 'Edge':
        self.priority = value
        return self

    @property
    def width(self) -> int:
        return self._width
    
    @width.setter
    def width(self, w: int):
        self._width = w
        pynode_core.add_event(pynode_core.Event(pynode_core.js_edge_set_width, [self._internal_id, w]), self)

    def set_width(self, width: int = 2) -> 'Edge':
        self.width = width
        return self

    @property
    def color(self) -> Color:
        return self._color
    
    @color.setter
    def color(self, c: Color):
        self._color = c
        pynode_core.add_event(pynode_core.Event(pynode_core.js_edge_set_color, [self._internal_id, c.hex_string()]), self)

    def set_color(self, color: Color = Color.LIGHT_GREY) -> 'Edge':
        self.color = color
        return self

    def set_weight_style(self, size: int = None, color: Color = None, outline: Color = None) -> 'Edge':
        self._weight_style = CustomStyle(self._weight_style._size if size is None else size, self._weight_style._color if color is None else color, self._weight_style._outline if outline is None else outline)
        pynode_core.add_event(pynode_core.Event(pynode_core.js_edge_set_weight_style, [self._internal_id, self._weight_style.data(self)]), self)
        return self

    def highlight(self, color: Color = None, width: int = None) -> None:
        if color is None: color = Color.RED # default
        if width is None: width = self._width * 2
        pynode_core.add_event(pynode_core.Event(pynode_core.js_edge_highlight, [self._internal_id, width, color.hex_string() if color is not None else None]), self)

    def traverse(self, initial_node: Node = None, color: Color = Color.RED, keep_path: bool = True) -> None:
        if not graph.has_edge(self): return
        start: Optional[Node] = graph.node(initial_node) if initial_node is not None else self._source
        if start is None or not graph.has_node(start): return
        pynode_core.add_event(pynode_core.Event(pynode_core.js_edge_traverse, [self._internal_id, start._internal_id, color.hex_string(), keep_path]), self)

    def _data(self) -> Dict[str, Any]:
        d = {"id": self._internal_id, "source": self._source._internal_id, "target": self._target._internal_id, "weight": str(self._weight) if self._weight is not None else "", "directed": self._directed, "lineWidth": self._width, "weightStyle": self._weight_style.data(self), "stroke": self._color.hex_string()}
        return d

    def __hash__(self) -> int:
        return hash(self._internal_id)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Edge):
            return self._internal_id == other._internal_id
        return False

    def __lt__(self, other: Any) -> bool: return self._priority < other._priority if isinstance(other, Edge) else NotImplemented
    def __le__(self, other: Any) -> bool: return self._priority <= other._priority if isinstance(other, Edge) else NotImplemented
    def __gt__(self, other: Any) -> bool: return self._priority > other._priority if isinstance(other, Edge) else NotImplemented
    def __ge__(self, other: Any) -> bool: return self._priority >= other._priority if isinstance(other, Edge) else NotImplemented

    def __str__(self) -> str:
        return f"({self._source}, {self._target})"

    def __repr__(self) -> str:
        return f"Edge(source={self._source}, target={self._target}, weight={self._weight}, directed={self._directed})"

class Graph:
    def __init__(self):
        self._nodes: Dict[Any, Node] = {}
        self._edges: List[Edge] = []
        self._has_edge_cache: Dict[Edge, bool] = {}
        self._spread = 80

    def add_node(self, node_or_id: Union[Node, Any] = None, **kwds) -> Node:
        # Compatibility with old signature add_node(*args, **kwds)
        # Old: args[0] might be ID, or Node object. kwds["node"] or kwds["id"]
        
        n: Node
        if isinstance(node_or_id, Node):
            n = node_or_id
        elif node_or_id is not None:
            n = Node(id=node_or_id, value=kwds.get("value"))
        elif "node" in kwds:
            n = kwds["node"]
        elif "id" in kwds:
             n = Node(id=kwds["id"], value=kwds.get("value"))
        else:
             n = Node(**kwds)

        if n.id() in self._nodes:
            raise Exception(f"Duplicate node '{n.id()}'")
            
        self._nodes[n.id()] = n
        pynode_core.add_event(pynode_core.Event(pynode_core.js_add_node, [n._data()]))
        pause(25)
        return n

    def remove_node(self, node: Union[Node, Any]) -> Node:
        n = self.node(node)
        if n is None: return None
        
        pynode_core.enable_events(False)
        for e in n.incident_edges:
            self.remove_edge(e)
        pynode_core.enable_events(True)
        
        del self._nodes[n.id()]
        pynode_core.add_event(pynode_core.Event(pynode_core.js_remove_node, [n._internal_id]))
        pause(25)
        return n

    def node(self, id: Union[Node, Any]) -> Optional[Node]:
        if isinstance(id, Node):
            # Check if this specific node object is in the graph or if a node with this ID is
            if id.id() in self._nodes:
                return self._nodes[id.id()]
            return None
        elif id in self._nodes:
            return self._nodes[id]
        else:
            return None

    def nodes(self) -> List[Node]:
        return list(self._nodes.values())

    def __iter__(self):
        return iter(self._nodes.values())
        
    def __contains__(self, item: Union[Node, Edge]) -> bool:
        if isinstance(item, Node):
            return self.has_node(item)
        elif isinstance(item, Edge):
            return self.has_edge(item)
        return False

    def add_edge(self, u_or_edge: Union[Node, Any, Edge], v: Union[Node, Any] = None, weight: Any = None, directed: bool = False, **kwds) -> Edge:
        # Compatibility handling
        e: Edge
        if isinstance(u_or_edge, Edge):
            e = u_or_edge
        elif "edge" in kwds:
            e = kwds["edge"]
        else:
            # Assume u, v signature
            source_arg = u_or_edge
            target_arg = v
            
            # Handle old kwds fallback if v is None
            if source_arg is None and "source" in kwds: source_arg = kwds["source"]
            if target_arg is None and "target" in kwds: target_arg = kwds["target"]
            if weight is None and "weight" in kwds: weight = kwds["weight"]
            if not directed and "directed" in kwds: directed = kwds["directed"]
            
            e = Edge(source_arg, target_arg, weight, directed)

        if self.has_edge(e):
            raise Exception(f"Instance of edge '{e}' already in graph.")

        original_source = e._source
        original_target = e._target
        
        # Resolve source/target to actual Node objects in the graph
        resolved_source = self.node(e.source_node)
        resolved_target = self.node(e.target_node)
        
        if resolved_source is None: raise Exception(f"Node '{original_source}' doesn't exist.")
        if resolved_target is None: raise Exception(f"Node '{original_target}' doesn't exist.")

        e._source = resolved_source
        e._target = resolved_target

        e._source._incident_edges.append(e)
        e._target._incident_edges.append(e)
        self._edges.append(e)
        self._has_edge_cache[e] = True
        
        pynode_core.add_event(pynode_core.Event(pynode_core.js_add_edge, [e._data()]))
        return e

    def remove_edge(self, edge: Union[Edge, Node, Any], v: Union[Node, Any] = None, directed: bool = False, **kwds) -> Union[Edge, List[Edge]]:
        remove_multiple = False
        target_edge: Edge = None
        
        if isinstance(edge, Edge):
            target_edge = edge
        elif "edge" in kwds:
            target_edge = kwds["edge"]
        else:
            # Arguments provided for node1, node2 to remove multiple
            node1 = edge
            node2 = v
            # Fallbacks
            if node1 is None and "node1" in kwds: node1 = kwds["node1"]
            if node2 is None and "node2" in kwds: node2 = kwds["node2"]
            if not directed and "directed" in kwds: directed = kwds["directed"]
            remove_multiple = True
            
        if remove_multiple:
            edge_list = self.edges_between(node1, node2, directed)
            self.remove_all(edge_list)
            return edge_list
        else:
            if target_edge._source and target_edge in target_edge._source._incident_edges:
                target_edge._source._incident_edges.remove(target_edge)
            if target_edge._target and target_edge in target_edge._target._incident_edges:
                target_edge._target._incident_edges.remove(target_edge)
            
            if target_edge in self._edges:
                self._edges.remove(target_edge)
                
            if target_edge in self._has_edge_cache:
                del self._has_edge_cache[target_edge]
                
            pynode_core.add_event(pynode_core.Event(pynode_core.js_remove_edge, [target_edge._internal_id]))
            return target_edge

    def edges(self) -> List[Edge]:
        return list(self._edges)

    def set_directed(self, directed: bool = True):
        for e in self._edges:
            e.set_directed(directed)

    def has_node(self, node: Union[Node, Any]) -> bool:
        return self.node(node) is not None

    def has_edge(self, edge: Edge) -> bool:
        return edge in self._has_edge_cache

    def adjacent(self, node1: Union[Node, Any], node2: Union[Node, Any], directed: bool = False) -> bool:
        n1 = self.node(node1)
        n2 = self.node(node2)
        if n1 is None or n2 is None: return False
        
        neighbors = n1.successor_nodes() if directed else n1.adjacent_nodes()
        # Identity check is safest
        for n in neighbors:
            if n is n2: return True
        return False

    def adjacent_directed(self, source: Union[Node, Any], target: Union[Node, Any]) -> bool:
        return self.adjacent(source, target, True)

    def edges_between(self, node1: Union[Node, Any], node2: Union[Node, Any], directed: bool = False) -> List[Edge]:
        n1 = self.node(node1)
        n2 = self.node(node2)
        if n1 is None or n2 is None: return []
        
        edge_list = n1.outgoing_edges if directed else n1.incident_edges
        return [edge for edge in edge_list if edge.target_node is n2 or edge.source_node is n2]

    def edges_between_directed(self, source: Union[Node, Any], target: Union[Node, Any]) -> List[Edge]:
        return self.edges_between(source, target, True)

    def adjacency_matrix(self) -> Dict[Any, Dict[Any, int]]:
        m = {}
        for r in self._nodes.values():
            row = {}
            for c in self._nodes.values(): row[c.id()] = 0
            m[r.id()] = row
        for r in self._nodes.values():
            for c in r.successor_nodes():
                m[r.id()][c.id()] += 1
        return m

    @staticmethod
    def random(order: int, size: int, connected: bool = True, multigraph: bool = False, initial_id: int = 0) -> List[Union[Node, Edge]]:
        nodes: List[Node] = []
        edges: List[Edge] = []
        adjacency_matrix = [[0 for c in range(order)] for r in range(order)]
        edges_remaining = size
        id_list = random.sample(range(initial_id, initial_id + order), order)
        
        for i in range(order):
            node = Node(id_list[i])
            if connected and edges_remaining > 0 and len(nodes) > 0:
                connected_node = nodes[random.randint(0, len(nodes) - 1)]
                if random.randint(0, 1) == 0:
                    edges.append(Edge(node, connected_node))
                else:
                    edges.append(Edge(connected_node, node))
                
                # Update adjacency tracking for random generation logic
                u_idx = id_list[i] - initial_id
                v_idx = connected_node.id() - initial_id
                adjacency_matrix[u_idx][v_idx] += 1
                adjacency_matrix[v_idx][u_idx] += 1
                edges_remaining -= 1
            nodes.append(node)
            
        possible_edges = [(i, j) for i in range(order) for j in range(order)]
        random.shuffle(possible_edges)
        
        for e in possible_edges:
            if edges_remaining <= 0: break
            u_idx, v_idx = e[0], e[1]
            
            if (adjacency_matrix[u_idx][v_idx] == 0 and u_idx != v_idx) or multigraph:
                # Need to lookup nodes by index in our local list or create edges by ID?
                # The original code did `Edge(e[0] + initial_id, ...)` which implied Edge constructor took IDs. 
                # But Edge constructor takes usage of `node()` which resolves IDs.
                # However, we have the node objects in `nodes` list corresponding to `id_list`.
                # Let's find the nodes by index to be safe.
                # id_list[u_idx] is the ID.
                # nodes[i] was created in order.
                
                # Careful: possible_edges indices are 0..order-1. nodes list is 0..order-1.
                u_node = nodes[u_idx] 
                v_node = nodes[v_idx]
                
                edges.append(Edge(u_node, v_node))
                adjacency_matrix[u_idx][v_idx] += 1
                adjacency_matrix[v_idx][u_idx] += 1
                edges_remaining -= 1
                
        return nodes + edges

    def add_all(self, elements: List[Union[Node, Edge, Any]]):
        new_elements = []
        pynode_core.enable_events(False)
        for x in elements:
            if isinstance(x, Node):
                new_elements.append((0, self.add_node(x)._data()))
            elif isinstance(x, Edge):
                new_elements.append((1, self.add_edge(x)._data()))
            else:
                # Assume it's a node ID
                new_elements.append((0, self.add_node(Node(x))._data()))
        pynode_core.enable_events(True)
        pynode_core.add_event(pynode_core.Event(pynode_core.js_add_all, [new_elements]))
        pause(55)

    def remove_all(self, elements: List[Union[Node, Edge, Any]]):
        new_elements = []
        pynode_core.enable_events(False)
        for x in elements:
            if isinstance(x, Node):
                val = self.remove_node(x)
                if val: new_elements.append((0, val._data()))
            elif isinstance(x, Edge):
                val = self.remove_edge(x)
                if val: new_elements.append((1, val._data()))
            else:
                val = self.remove_node(self.node(x))
                if val: new_elements.append((0, val._data()))
        pynode_core.enable_events(True)
        pynode_core.add_event(pynode_core.Event(pynode_core.js_remove_all, [new_elements]))
        pause(55)

    def order(self) -> int: return len(self._nodes)
    def size(self) -> int: return len(self._edges)

    def set_spread(self, spread: int = 80):
        self._spread = spread
        pynode_core.add_event(pynode_core.Event(pynode_core.js_set_spread, [spread]))

    def clear(self):
        self._reset()
        pynode_core.add_event(pynode_core.Event(pynode_core.js_clear, []))

    def _reset(self):
        self._nodes = {}
        self._edges = []
        self._has_edge_cache = {}

def _exec_code(src):
    namespace = globals().copy()
    namespace["__name__"] = "__main__"
    exec(src, namespace)

def _execute_function(func, args):
    func(*args)

graph = Graph()
