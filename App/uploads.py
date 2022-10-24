import time
import numpy as np


def getNewName(file_type):

    new_name = time.strftime(file_type+'-%Y%m%d%H%M%S', time.localtime())

    ranlist = np.random.randint(0, 10, 3)

    for i in ranlist:
        new_name += str(i)

    new_name += '.jpg'

    return new_name
