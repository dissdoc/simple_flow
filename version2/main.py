from version2.store import Store
from version2.flow import Flow
from version2.utils import load


if __name__ == '__main__':

    data = load()
    store = Store.to_data(data)
    flow = Flow(store)

    command = ''
    while command != 'exit':
        if command == 'back':
            flow.previous()
        elif command == 'next':
            flow.forward()
        elif command.startswith('help'):
            flow.similar(intent=command.split(' ')[1])
        else:
            flow.next(command)

        flow.before_event()
        command = input(r"~> ")
        flow.after_event()
