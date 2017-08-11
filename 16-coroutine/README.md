Sample code for Chapter 16 - "Coroutines"

From the book "Fluent Python" by Luciano Ramalho (O'Reilly, 2015)
http://shop.oreilly.com/product/0636920032519.do

collections.namedtuple() 可以直接赋值：

Event = collections.namedtuple('Event', 'time proc action')
taix1 = Event(0, 1, 'pick up')
t, p, a = taix1

此时t p a分别为0 1 'pick up'
