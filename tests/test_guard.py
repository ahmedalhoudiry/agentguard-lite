import unittest
from agentguard_lite import ApprovalRequired, Decision, Guard, Policy, ToolDenied


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.tools = {'read': lambda: 'ok', 'send': self.calls.append}
        self.policy = Policy({'read', 'send'}, {'send'})

    def test_default_deny(self):
        self.assertEqual(Policy().decide('read'), Decision.DENY)
        with self.assertRaises(ToolDenied):
            Guard(Policy(), self.tools).call('read')

    def test_read_allowed(self):
        self.assertEqual(Guard(self.policy, self.tools).call('read'), 'ok')

    def test_unregistered_tool(self):
        with self.assertRaises(ToolDenied):
            Guard(Policy({'missing'}), self.tools).call('missing')

    def test_invalid_policy(self):
        with self.assertRaises(ValueError):
            Policy({'read'}, {'send'})

    def test_no_approval_callback(self):
        with self.assertRaises(ApprovalRequired):
            Guard(self.policy, self.tools).call('send')
        self.assertEqual(self.calls, [])

    def test_rejected_approval(self):
        with self.assertRaises(ApprovalRequired):
            Guard(self.policy, self.tools, lambda *_: False).call('send')
        self.assertEqual(self.calls, [])

    def test_truthy_not_approval(self):
        with self.assertRaises(ApprovalRequired):
            Guard(self.policy, self.tools, lambda *_: 1).call('send')

    def test_approved_call(self):
        guard = Guard(self.policy, {'send': lambda message: self.calls.append(message)},
                      lambda name, args: name == 'send' and args['message'] == 'hello')
        guard.call('send', message='hello')
        self.assertEqual(self.calls, ['hello'])

    def test_approval_mutation_does_not_change_args(self):
        def approve(name, args):
            args['message']['text'] = 'changed'
            return True
        guard = Guard(self.policy, {'send': lambda message: message}, approve)
        self.assertEqual(guard.call('send', message={'text': 'original'}), {'text': 'original'})

    def test_policy_copies_sets(self):
        allowed = {'read'}
        policy = Policy(allowed)
        allowed.add('send')
        self.assertEqual(policy.decide('send'), Decision.DENY)

    def test_approval_callback_failure_propagates(self):
        def fail(*_):
            raise RuntimeError('approval service offline')
        with self.assertRaises(RuntimeError):
            Guard(self.policy, self.tools, fail).call('send')
        self.assertEqual(self.calls, [])
