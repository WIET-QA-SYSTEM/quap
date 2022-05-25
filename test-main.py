from qa.system import QASystem
from qa.dataset import UploadedDataset, PrefetchedDataset

import sys


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise ValueError('pass arguments')

    if sys.argv[2] not in ['data', 'squad']:
        raise ValueError('unsupported dataset')

    if sys.argv[1] == 'ask':
        if sys.argv[2] in ['data']:
            dataset = UploadedDataset(sys.argv[2])
            q = 'When did the siege of Mariupol start?'
        else:
            dataset = PrefetchedDataset(sys.argv[2])
            q = 'Where was Beyonce born?'

        system = QASystem('deepset/roberta-base-squad2')

        r = system.ask(dataset, q)

        print(r)
    elif sys.argv[1] == 'eval':
        if sys.argv[2] in ['data']:
            raise ValueError('eval can be called only for prefetched')

        dataset = PrefetchedDataset('squad')
        system = QASystem('deepset/roberta-base-squad2')

        r = system.evaluate_reader(dataset)

        print(r)
    else:
        raise ValueError('unknown argument')
