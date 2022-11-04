#import time
#import numpy as np
from App.models import Campaign

def getNewName(file_type, campaign_code):

   # new_name = time.strftime(file_type+'-%Y%m%d%H%M%S', time.localtime())
    new_name = str(campaign_code) + '.png'
    #ranlist = np.random.randint(0, 10, 3)

    #for i in ranlist:
    #    new_name += str(i)

    #new_name += '.jpg'

    return new_name
