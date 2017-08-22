import time


def calc(results):
    for line in results:
        time.sleep(1)
        yield len(line)


def gen_count_line(f):
    results = []
    for line in f:
        results.append(line)
    return calc(results)


def call_in_with():
    with open('README.md') as f:
        results = gen_count_line(f)
    print('1:', time.time())
    print(results)
    print('2:', time.time())
    for i in results:
        print(i)
    print('3:', time.time())


if __name__ == '__main__':
    call_in_with()
