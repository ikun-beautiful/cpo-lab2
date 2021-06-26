Computational Process Organization lab2 

## Title: StateMachine

eDSL for finite state machine (mealy).

## List of group members

- Liu honggang

  - ID: 202320048

    

- Fu wei

  -  ID: 202320049

  

## Laboratory work number: 2

## Variant description

eDSL for finite state machine (mealy).

- Visualization as a state diagram (GraphViz DOT) or table (ASCII).
- Provide complex an example like a controller for an elevator, crossroad with a traffific light, etc.

## Synopsis 

- mealy finite state machine - elevator design concept
- Design StateMachine Class
- StateMachineTest
- Input data control 
- StateMachine Visualization
- Conclusion

### mealy finite state machine - elevator design concept

### Design StateMachine Class

arg_type: Restrict input data to a specific type

```python
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
```

Args_1: Restrict the length of the input parameter to 1

```python
    def args_1(f):
        def trace(self, *args, **kwargs):
            if len(args) == 1:
                return f(self, *args, **kwargs)
            else:
                print("Wrong Input!")
                return 'Wrong Input!'

        return trace
```

Args_0: Restrict the length of the input parameter to 0

```python
    def args_0(f):
        def trace(self, *args, **kwargs):
            if len(args) == 0:
                return f(self, *args, **kwargs)
            else:
                print("Wrong Input!")
                return 'Wrong Input!'

        return trace
```

### StateMachineTest

Convert_state: To change the elevator's state

```python
    def test_convert_state(self):
        m = StateMachine("convert_state")
        m.input_port("A", latency=1)
        m.output_port("B", latency=1)
        n = m.add_node("convert", lambda a: not a if isinstance(a, bool) else None)
        n.input("A", latency=1)
        n.output("B", latency=1)
        m.execute(
         source_event("A", True, 0),
         source_event("A", False, 5),
         )
        self.assertEqual(m.state_history, [
         (0, {'A': None}),
         (2, {'A': True}),
         (4, {'A': True, 'B': False}),
         (7, {'A': False, 'B': False}),
         (9, {'A': False, 'B': True}),
         ])
        self.assertListEqual(m.event_history, [
         event(clock=2, node=n, var='A', val=True),
         event(clock=4, node=None, var='B', val=False),
         event(clock=7, node=n, var='A', val=False),
         event(clock=9, node=None, var='B', val=True),
         ])
```

Add_load: 

```python
 def add_load(a, b):
            n = m.add_node("!{} -> {}".format(a, b), lambda a: not a if isinstance(a, bool) else None)
            n.input(a, latency=1)
            n.output(b, latency=1)
```



add_convert: 

```python
        def add_convert(a, b, c):
            n = m.add_node("{} and {} -> {}".format(a, b, c),
                           lambda a, b: a and b if isinstance(a, bool) and isinstance(b, bool) else None)
            n.input(a, 1)
            n.input(b, 1)
            n.output(c, 1)
```

Elevator: Realize the state transition of elevator

```python
 def test_elevator(self):
        m = StateMachine("elevator")
        m.input_port("A_unoverload",latency=1)
        m.input_port("A_up",latency=1)
        m.output_port("D0_closeup",latency=1)
        m.output_port("D1_closedown", latency=1)
        m.output_port("D2_openstop", latency=1)

        
        def add_load(a, b):
            n = m.add_node("!{} -> {}".format(a, b), lambda a: not a if isinstance(a, bool) else None)
            n.input(a, latency=1)
            n.output(b, latency=1)

        def add_convert(a, b, c):
            n = m.add_node("{} and {} -> {}".format(a, b, c),
                           lambda a, b: a and b if isinstance(a, bool) and isinstance(b, bool) else None)
            n.input(a, 1)
            n.input(b, 1)
            n.output(c, 1)
        add_load("A_close", "A_open")
        add_load("A_up", "A_down")

        add_convert("A_close", "A_down", "D1_closedown")
        add_convert("A_close", "A_up", "D3_closeup")
        add_convert("A_open", "A_up", "D2_stop")
        add_convert("A_open", "A_down", "D2_stop")
        
```



### Input data control 

In this part, I try to implement the goals: 

- develop a set of decorators, which allows checking input data (types and values);

- decorate all public API of the developed library ;

- develop unit tests for checking the modifified library safety.

As we designed in Design StateMachine Class, and we apply them in the function. 

```
 @arg_type(1, str)
    def input_port(self, name, latency=1):
@arg_type(1, str)
    def output_port(self, name, latency=1):
@arg_type(1, str)
    def add_node(self, name, function):
@arg_type(2, int)
    def _source_events2events(self, source_events, clock):
 @args_1
    def _pop_next_event(self, events):
@args_0
    def _state_initialize(self):
@args_0
    def visualize(self):
@arg_type(1, str)
    def input(self, name, latency=1):
@arg_type(1, str)
    def output(self, name, latency=1):
 @arg_type(1, dict)
    def activate(self, state):    

```





### StateMachine Visualization



### Conclusion

1.The application of decorator pattern is necessary to effectively limit the format of input data and enhance the robustness of the code

2.Graphviz is a handy tool for data visualization, turning obscure lines of code into readable ones