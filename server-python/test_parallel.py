import multiprocessing as mp

import time




def parallel(x):
    time.sleep(2)
    print "finishing calculating for %s" % x
    return x * x



def apply_async_with_callback():
    pool = mp.Pool(processes=3)
    outputs = pool.map(parallel, [1, 2, 3])
    pool.close()
    pool.join()
    print outputs

apply_async_with_callback()

