import tqdm
import time

num = 100
iter_done = range(num)
iter_done_decorations = tqdm.tqdm(iter_done, total=num)

for i in iter_done_decorations:
    time.sleep(0.05)
