import sys
import os
import math
import time
import random
import types
import json
from PIL import Image
import calculator
from functions import os_command,from_dict

class Game():
    '''
    Automatically play wechat game--"Jump Jump" when ADB is ready.
    For instance:

    <codes--

    tmp=Game()
    tmp.auto_jump(100) #Jump 100 steps

    --codes>

    Besides Game.auto_jump, there are two more public interfaces designed
    to shot screen(Game.screenshot) and tap on screen(Game.input_swipe).
    For instance:

    <codes--

    tmp=Game()
    tmp.screenshot("tmp.png") #Screenshot image path is "./tmp.png"
    tmp.input_swipe((10,10),1000) #Tap on (10,10) for 1000 ms

    --codes>
    '''

    def __init__(self,config_file_path="game_config.json"):
        '''Load game parameters and init core data'''

        #Check arguments
        if type(config_file_path) is not str:
            print("Wrong arguments for Game.__init__!")
            sys.exit(1)

        #Obtain a dictionary from configuration file
        try:
            fp=open(config_file_path)
        except FileNotFoundError:
            print("Configuration File for game.py Not Found!")
            sys.exit(1)
        else:
            conf=json.load(fp)
            fp.close()

        #Load game parameters
        alert="game.py Configuration File Error!"
        self.screen_size=from_dict(conf,"screen_size",alert)#{"width":1080,"height":1920}
        self.tap_area=from_dict(conf,"tap_area",alert)#{"left":0,"top":0,"right":540,"bottom":540}
        self.serial_num=from_dict(conf,"serial_num",alert)#"cf11a7d9"
        self.sleep_time=from_dict(conf,"sleep_time",alert)#5
        self.dists=from_dict(conf,"dists",alert)#[50,90,150,200,250,295,330,440,525,alert]
        self.factors=from_dict(conf,"factors",alert)#[11,7,2.1,1.92,1.86,1.82,1.78,1.76,1.71,1.68,alert]
        self.screenshot_name=from_dict(conf,"screenshot_name",alert)#"current_sc.png"
        self.last_screenshot_name=from_dict(conf,"last_screenshot_name",alert)#"last_sc.png"
        self.pawn_img_name=from_dict(conf,"pawn_img_name",alert)#"fst_step.png"

        #Check game parameters
        pass

        #Init core data
        self.dist=0
        self.factor=0
        self.tap_pos=[0,0]
        self.tap_time=0

    def screenshot(self,screenshot_name):
        '''Create a screenshot of cellphone and pull it into PC'''
        #Check arguments
        if type(screenshot_name) is not str:
            print("Game.screenshot was invoked with wrong screenshot_name!")
            sys.exit(1)

        #Screenshot
        cmd="adb -s {} shell screencap -p /sdcard/{}"\
            .format(self.serial_num,screenshot_name)
        info="Error occurred when making a screenshot!"
        os_command(cmd,info)

        #Pull screenshot
        cmd="adb -s {} pull /sdcard/{}"\
            .format(self.serial_num,screenshot_name)
        info="Error occurred when pulling screenshot!"
        os_command(cmd,info)

        #Remove the screenshot in android device
        cmd="adb -s {} shell rm /sdcard/{}"\
            .format(self.serial_num,screenshot_name)
        info="Error occurred when removing screenshot in android device!"
        os_command(cmd,info)

    def __cal_tappos(self):
        '''Determine where to tap on in cellphone'''

        #Generate a random position
        tap_pos=[]
        tap_pos.append(random.randrange(self.tap_area["left"],self.tap_area["right"]))
        tap_pos.append(random.randrange(self.tap_area["top"],self.tap_area["bottom"]))
        self.tap_pos=tap_pos


    def __cal_factor(self):
        '''
        Determine the jump factor according to the distance calculated
        from screenshot
        '''

        temp_dists=self.dists[:]
        temp_dists.append(self.dist)
        temp_dists.sort()
        index=temp_dists.index(self.dist)
        try:
            self.factor=self.factors[index]
        except IndexError:
            print("Wrong factors or dists!")
            sys.exit(1)

    def __cal_taptime(self):
        '''Figure out how much time to tap for on cellphone's screen'''

        #Calculate distance between pawn and target by calculater.py
        helper=calculator.Calculator(self.screenshot_name)
        self.dist=helper.cal_dist()

        #Determine the jump factor by invoking self.__cal_factor
        self.__cal_factor()

        #Figure out tap_time
        self.tap_time=int(self.dist*self.factor)

    def input_swipe(self,tap_pos,tap_time):
        '''Tap cellphone's screen on certain position for certain time'''

        #Check arguments
        if type(tap_pos) is not list or \
           len(tap_pos)!=2 or \
           type(tap_pos[0]) is not int or \
           type(tap_pos[1]) is not int:
            print("Game().input_swipe was invoked with wrong tap_pos!")
            sys.exit(1)

        if type(tap_time) is not int and \
           type(tap_time) is not float:
            print("Game().input_swipe was invoked with wrong tap_time!")
            sys.exit(1)

        #Send a swipe command to cellphone
        cmd="adb -s {} shell input swipe".format(self.serial_num)
        for coord in tap_pos:
            cmd+=" {}".format(coord)
        for coord in tap_pos:
            cmd+=" {}".format(coord)
        cmd+=" {}".format(tap_time)
        os_command(cmd)

    def __dispose_screenshots(self):
        '''Do something after pawn's jump such as clearing screenshot images'''

        #Rename screenshot image in PC as self.last_screenshot_name
        cmd="mv {} {}".format(self.screenshot_name,self.last_screenshot_name)
        info="Error occurred when renaming screenshot in PC"
        os_command(cmd,info)

    def auto_jump(self,max_steps):
        '''Make pawn jump for specified steps'''

        for step in range(1,max_steps+1):

            #Display current step
            print("step -- {}".format(step))

            #Make a screenshot of game and pull it into PC
            self.screenshot(self.screenshot_name)
            print("Screenshot Done!")

            #Analyse the screenshot and figure out swipe time
            print("Calculating... ...",end="",flush=True)
            self.__cal_tappos()
            self.__cal_taptime()
            print("Done!")
            print("tap_position-- ",self.tap_pos)
            #print("distance=",self.dist,\
            #      " factor=",self.factor,\
            #      " tap_time=",self.tap_time)

            #Make a swipe in the game
            print("Inputting a swipe... ...",end="",flush=True)
            self.input_swipe(self.tap_pos,self.tap_time)
            print("Done!")

            #Deal with screenshots in PC and android device
            print("Clearing... ...",end="",flush=True)
            self.__dispose_screenshots()
            print("Done!")

            #Wait some time to make sure that pawn has completely done this jump
            print("Waitting for {}s... ...".format(self.sleep_time),\
                  end="",flush=True)
            time.sleep(self.sleep_time)
            print("Ready!\n")

if __name__=="__main__":
    print("game.py is not imported")
    pass
