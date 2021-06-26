import unittest
from src.disevent import *



class StateMachineTest(unittest.TestCase):
    def test_convert_self_state(self):
        m = StateMachine("convert_self_state")
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

    def test_elevator(self):
        m = StateMachine("elevator")
        m.input_port("A_up", latency=1)
        m.input_port("A_close", latency=1)
        m.output_port("D1_closedown", latency=1)
        m.output_port("D2_stop", latency=1)
        m.output_port("D3_closeup", latency=1)

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
        test_data = [
            ({'A_up': None, 'A_close': False},{'D2_stop': None, 'D2_stop': None, 'D1_closedown': None, 'D3_closeup': None}),
            ({'A_down': None, 'A_close': False},{'D2_stop': None, 'D2_stop': None, 'D1_closedown': None, 'D3_closeup': None})

        ]
        for a, d in test_data:
            source_events = [source_event(k, v, 0) for k, v in a.items()]
            actual = m.execute(*source_events)
            expect = {}
            expect.update(actual)
            expect.update(d)
            self.assertEqual(actual, expect)



class NodeTest(unittest.TestCase):
    def test_convert_self_state(self):
        n = Node("convert_self_state", lambda a: not a if isinstance(a, bool) else None)
        n.input("A", 1)
        n.output("B", 1)
        test_data = [
            (False, True),
            (False, True),
            (None, None),
        ]
        for a, b in test_data:
            self.assertEqual(n.activate({"A": a}), [source_event("B", b, 1)])

    def test_add_convert(self):
        n = Node("convert", lambda a, b: a and b if isinstance(a, bool) and isinstance(b, bool) else None)
        n.input("A", 1)
        n.input("B", 1)
        n.output("C", 1)
        test_data = [
            (None, False, None),
            (False, False, False),
            (True, False, False),
            (False, True, False),
            (True, True, True),
        ]
        for a, b, c in test_data:
            self.assertEqual(n.activate({"A": a, "B": b}), [source_event("C", c, 1)])

    def test_convert(self):
        def convert(a):
            if a == 0: return (0, 1)
            if a == 1: return (1, 0)
            return (None, None)

        n = Node("convert", convert)
        n.input("A", 1)
        n.output("D1", 1)
        n.output("D0", 2)
        test_data = [
            (0, 0, 1),
            (1, 1, 0),
            (None, None, None),
        ]
        for a, d1, d0 in test_data:
            self.assertEqual(n.activate({"A": a}), [source_event("D1", d1, 1), source_event("D0", d0, 2)])


if __name__ == '__main__':
    unittest.main()
