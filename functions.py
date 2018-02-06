import os
import sys
import math

def os_command(cmd,info="OS Command Failed!"):
    '''Command PC's operating system to do something'''

    #Check arguments
    if type(cmd) is not str or type(info) is not str:
        print("Wrong OS Command!")
        sys.exit(1)

    #Conduct the command on operating system terminal
    if os.system(cmd)!=0:
        print(info)
        sys.exit(1)

def from_dict(dictionary,key,alert="No such key!"):
    '''
    Get a value from dictionary.
    If key not found, print an alert and exit.
    '''

    if key in dictionary:
        return dictionary[key]
    else:
        print(alert)
        sys.exit(1)

def is_equal(rgba1,rgba2):
    '''Check if two pixels are equal except alpha value'''

    for n in range(0,3):
        if math.fabs(rgba1[n]-rgba2[n])>5:
            return False
    return True

def is_different(rgba1,rgba2):
    '''Check if two pixels are different except alpha value'''

    for n in range(0,3):
        if math.fabs(rgba1[n]-rgba2[n])>20:
            return True
    return False
