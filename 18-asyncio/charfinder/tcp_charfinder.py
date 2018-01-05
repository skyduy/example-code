#!/usr/bin/env python3

# BEGIN TCP_CHARFINDER_TOP
import sys
import asyncio
import concurrent
from charfinder import UnicodeNameIndex  # <1>

CRLF = b'\r\n'
PROMPT = b'?> '

index = None  # <2>


def load_index():
    import time
    global index
    index = UnicodeNameIndex()
    time.sleep(2)


@asyncio.coroutine
def handle_queries(reader, writer):  # <3>
    while True:  # <4>
        writer.write(PROMPT)  # can't yield from!  # <5>
        # It should especially be used
        # when a possibly large amount of data is written to the transport
        yield from writer.drain()
        data = yield from reader.readline()  # <7>
        try:
            query = data.decode().strip()
        except UnicodeDecodeError:  # <8>
            query = '\x00'
        client = writer.get_extra_info('peername')  # <9>
        print('Received from {}: {!r}'.format(client, query))  # <10>
        if query:
            if ord(query[:1]) < 32:  # <11>
                break
            lines = list(index.find_description_strs(query))  # <12>
            if lines:
                writer.writelines(line.encode() + CRLF for line in lines)  # <13>  # NOQA
            writer.write(index.status(query, len(lines)).encode() + CRLF)  # <14>  # NOQA

            yield from writer.drain()  # <15>
            print('Sent {} results'.format(len(lines)))  # <16>

    print('Close the client socket')  # <17>
    writer.close()  # <18>
# END TCP_CHARFINDER_TOP


# BEGIN TCP_CHARFINDER_MAIN
def main(address='127.0.0.1', port=2323):  # <1>
    port = int(port)
    loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor(5)
    loop.run_in_executor(executor, load_index)
    server_coro = asyncio.start_server(handle_queries, address, port,
                                       loop=loop)  # <2>
    server = loop.run_until_complete(server_coro)  # <3>
    # 此时server_coro执行完毕，但server已经处于运行状态

    host = server.sockets[0].getsockname()  # <4>
    print('Serving on {}. Hit CTRL-C to stop.'.format(host))  # <5>
    try:
        loop.run_forever()  # <6> 与server并存运行
    except KeyboardInterrupt:  # CTRL+C pressed
        print('\nWaiting for executor shutdown and server close...')

    server.close()  # <7> 先关闭server协程
    loop.run_until_complete(server.wait_closed())  # <8> 等待server协程关闭
    executor.shutdown(wait=True)  # 确保读取预数据关闭
    loop.close()  # <9> 关闭主流程
    print('Server shutting down success.')


if __name__ == '__main__':
    main(*sys.argv[1:])  # <10>
# END TCP_CHARFINDER_MAIN
