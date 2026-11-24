from agentguard_lite import Guard, Policy, ApprovalRequired, ToolDenied


def read_note():
    return 'Local demonstration note'


def send_message(message):
    return f'Demo only: would send {message!r}'


def approve(tool, args):
    print(f'Approve {tool} with {args!r}?')
    return input('Type yes to approve: ').strip().lower() == 'yes'


guard = Guard(Policy({'read_note', 'send_message'}, {'send_message'}),
              {'read_note': read_note, 'send_message': send_message}, approve)
if __name__ == '__main__':
    print(guard.call('read_note'))
    try:
        print(guard.call('send_message', message='Hello'))
    except (ApprovalRequired, ToolDenied) as exc:
        print(exc)
