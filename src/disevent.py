from collections import OrderedDict, namedtuple
import copy


event = namedtuple("Event", "clock node var val")
source_event = namedtuple("SourceEvent", "var val latency")


class StateMachine(object):

    def __init__(self, name="anonymous"):
        self.name = name
        self.inputs = OrderedDict()
        self.outputs = OrderedDict()
        self.nodes = []
        self.state_history = []
        self.event_history = []

    def arg_type(num_args, type_args):
        def trace(f):
            def traced(self, *args, **kwargs):
                # print("{}(*{}, **{}) START".format(f.__name__, args, kwargs))
                if type(args[num_args - 1]) == type_args:
                    return f(self, *args, **kwargs)
                else:
                    print("Wrong Input!")
                    print(type(args[num_args - 1]))
                    return 'Wrong Input!'

            return traced

        return trace

    @arg_type(1, str)
    def input_port(self, name, latency=1):

        self.inputs[name] = latency

    @arg_type(1, str)
    def output_port(self, name, latency=1):

        self.outputs[name] = latency

    @arg_type(1, str)
    def add_node(self, name, function):

        node = Node(name, function)
        self.nodes.append(node)
        return node

    @arg_type(2, int)
    def _source_events2events(self, source_events, clock):
        events = []
        for se in source_events:
            source_latency = clock + se.latency + self.inputs.get(se.var, 0)
            if se.var in self.outputs:
                target_latency = self.outputs[se.var]
                events.append(event(
                    clock=source_latency + target_latency,
                    node=None,
                    var=se.var,
                    val=se.val,
                ))
            for node in self.nodes:
                if se.var in node.inputs:
                    target_latency = node.inputs[se.var]
                    events.append(event(
                        clock=clock + source_latency + target_latency,
                        node=node,
                        var=se.var,
                        val=se.val,
                    ))
        return events

    def args_1(f):
        def trace(self, *args, **kwargs):
            if len(args) == 1:
                return f(self, *args, **kwargs)
            else:
                print("Wrong Input!")
                return 'Wrong Input!'

        return trace

    @args_1
    def _pop_next_event(self, events):

        assert len(events) > 0
        events = sorted(events, key=lambda e: e.clock)
        event = events.pop(0)
        return event, events

    def args_0(f):
        def trace(self, *args, **kwargs):
            if len(args) == 0:
                return f(self, *args, **kwargs)
            else:
                print("Wrong Input!")
                return 'Wrong Input!'

        return trace

    @args_0
    def _state_initialize(self):
        env = {}
        for var in self.inputs:
            env[var] = None
        return env

    def args_3(f):
        def trace(self, *args, **kwargs):
            if len(args) == 3:
                return f(self, *args, **kwargs)
            else:
                print("Wrong Input!")
                return 'Wrong Input!'

        return trace

    # @args_3
    def execute(self, *source_events, limit=100, events=None):

        if events is None: events = []
        state = self._state_initialize()
        clock = 0
        self.state_history = [(clock, copy.copy(state))]
        while (len(events) > 0 or len(source_events) > 0) and limit > 0:
            limit -= 1
            new_events = self._source_events2events(source_events, clock)
            events.extend(new_events)
            if len(events) == 0: break
            event, events = self._pop_next_event(events)
            state[event.var] = event.val
            clock = event.clock
            source_events = event.node.activate(state) if event.node else []
            self.state_history.append((clock, copy.copy(state)))
            self.event_history.append(event)
        if limit == 0: print("limit reached")
        return state

    @args_0
    def visualize(self):

        res = []
        res.append("digraph G {")
        res.append(" rankdir=LR;")
        for v in self.inputs:
            res.append(" {}[shape=rarrow];".format(v))
        for v in self.outputs:
            res.append(" {}[shape=rarrow];".format(v))
        for i, n in enumerate(self.nodes):
            res.append(' n_{}[label="{}"];'.format(i, n.name))
        for i, n in enumerate(self.nodes):
            for v in n.inputs:
                if v in self.inputs:
                    res.append(' {} -> n_{};'.format(v, i))
            for j, n2 in enumerate(self.nodes):
                if i == j: continue
                for v in n.inputs:
                    if v in n2.outputs:
                        res.append(' n_{} -> n_{}[label="{}"];'.format(j, i, v))
            for v in n.outputs:
                if v in self.outputs:
                    res.append(' n_{} -> {};'.format(i, v))
        res.append("}")
        return "\n".join(res)


class Node(object):

    def __init__(self, name, function):
        self.function = function
        self.name = name
        self.inputs = OrderedDict()
        self.outputs = OrderedDict()

    def __repr__(self):
        return "{} inputs: {} outputs: {}".format(self.name, self.inputs, self.outputs)

    def arg_type(num_args, type_args):
        def trace(f):
            def traced(self, *args, **kwargs):
                # print("{}(*{}, **{}) START".format(f.__name__, args, kwargs))
                if type(args[num_args - 1]) == type_args:
                    return f(self, *args, **kwargs)
                else:
                    print("Wrong Input!")
                    print(type(args[num_args - 1]))
                    return 'Wrong Input!'

            return traced

        return trace

    @arg_type(1, str)
    def input(self, name, latency=1):

        assert name not in self.inputs
        self.inputs[name] = latency

    @arg_type(1, str)
    def output(self, name, latency=1):

        assert name not in self.outputs
        self.outputs[name] = latency

    @arg_type(1, dict)
    def activate(self, state):

        args = []
        for v in self.inputs:
            args.append(state.get(v, None))
        res = self.function(*args)
        if not isinstance(res, tuple):
            res = (res,)
        output_events = []
        for var, val in zip(self.outputs, res):
            latency = self.outputs[var]
            output_events.append(
                source_event(var, val, latency)
            )
        return output_events
