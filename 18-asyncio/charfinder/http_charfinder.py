#!/usr/bin/env python3

import sys
import asyncio
import concurrent
from aiohttp import web

from charfinder import UnicodeNameIndex

TEMPLATE_NAME = 'http_charfinder.html'
CONTENT_TYPE = 'text/html;'
SAMPLE_WORDS = ('bismillah chess cat circled Malayalam digit'
                ' Roman face Ethiopic black mark symbol dot'
                ' operator Braille hexagram').split()

ROW_TPL = '<tr><td>{code_str}</td><th>{char}</th><td>{name}</td></tr>'
LINK_TPL = '<a href="/?query={0}" title="find &quot;{0}&quot;">{0}</a>'
LINKS_HTML = ', '.join(LINK_TPL.format(word) for word in
                       sorted(SAMPLE_WORDS, key=str.upper))


index = None  # <2>


def load_index():
    import time
    global index
    index = UnicodeNameIndex()
    time.sleep(2)


with open(TEMPLATE_NAME) as tpl:
    template = tpl.read()
template = template.replace('{links}', LINKS_HTML)


# BEGIN HTTP_CHARFINDER_HOME
def home(request):  # <1>
    query = request.GET.get('query', '').strip()  # <2>
    print('Query: {!r}'.format(query))  # <3>
    if query:  # <4>
        descriptions = list(index.find_descriptions(query))
        res = '\n'.join(ROW_TPL.format(**descr._asdict())
                        for descr in descriptions)
        msg = index.status(query, len(descriptions))
    else:
        descriptions = []
        res = ''
        msg = 'Enter words describing characters.'

    html = template.format(query=query, result=res,  # <5>
                           message=msg)
    print('Sending {} results'.format(len(descriptions)))  # <6>
    return web.Response(content_type=CONTENT_TYPE, text=html)  # <7>
# END HTTP_CHARFINDER_HOME


# BEGIN HTTP_CHARFINDER_SETUP
@asyncio.coroutine
def init(loop, address, port):  # <1>
    app = web.Application(loop=loop)  # <2>
    app.router.add_route('GET', '/', home)  # <3>
    handler = app.make_handler()  # <4>
    server = yield from loop.create_server(handler,
                                           address, port)  # <5>
    return server.sockets[0].getsockname()  # <6>


def main(address="127.0.0.1", port=8888):
    port = int(port)
    loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor(5)
    loop.run_in_executor(executor, load_index)
    host = loop.run_until_complete(init(loop, address, port))  # <7>
    # 此时创建服务这一协程已经完毕，服务处于运行状态
    print('Serving on {}. Hit CTRL-C to stop.'.format(host))
    try:
        loop.run_forever()  # <8> 服务和主流程并存
    except KeyboardInterrupt:  # CTRL+C pressed
        pass
    print('\nWaiting server shutting down.')
    executor.shutdown(wait=True)  # 确保读取预数据关闭
    loop.close()  # <9> 关闭主循环流程，web server会自动关闭？


if __name__ == '__main__':
    main(*sys.argv[1:])
# END HTTP_CHARFINDER_SETUP
