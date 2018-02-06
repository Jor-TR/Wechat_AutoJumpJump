from PIL import Image,ImageDraw
import math
import sys
import json
from functions import is_equal,is_different,from_dict

class Calculator():
    '''
    Figure out the distance between pawn and target place.
    For instance:

    <codes--

    tmp=Calculator("screenshot.png","pawn.png")
    #Create a marked image and return the distance
    distance=tmp.cal_dist(True,"check.png")

    --codes>
    '''

    def __init__(self,main_img_path,config_file_path="calculator_config.json"):
        '''Load parameters, init temporary variables and init core data'''

        #Check arguments
        if type(main_img_path) is not str or \
           type(config_file_path) is not str:
            print("Wrong arguments for Calculator.__init__!")
            sys.exit(1)

        #Obtain a dictionary from configuration file
        try:
            fp=open(config_file_path)
        except FileNotFoundError:
            print("Configuration File for calculator.py Not Found!")
            sys.exit(1)
        else:
            conf=json.load(fp)
            fp.close()

        #Load parameters
        alert="calculator.py Configuration File Error!"
        self.pawn_img_path=from_dict(conf,"pawn_img_path",alert)
        self.size=from_dict(conf,"size",alert)#(1080,1920)
        self.search_area_whole=from_dict(conf,"search_area_whole",alert)#{"left":10,"top":500,"right":1000,"bottom":1500}
        self.search_area_left=from_dict(conf,"search_area_left",alert)#{"left":100,"top":500,"right":540,"bottom":1500}
        self.search_area_right=from_dict(conf,"search_area_right",alert)#{"left":540,"top":500,"right":1000,"bottom":1500}
        self.main_flag_pos=from_dict(conf,"main_flag_pos",alert)#{"x":336,"y":921}
        self.other_flag_pos=from_dict(conf,"other_flag_pos",alert)#[{"x":336,"y":1125}]

        #Check parameters
        pass

        #Init temporary variables
        self.main_img=Image.open(main_img_path)
        self.pawn_img=Image.open(self.pawn_img_path)
        self.flag_pos_diff=[{"delta_x":pos["x"]-self.main_flag_pos["x"],\
                             "delta_y":pos["y"]-self.main_flag_pos["y"]}\
                              for pos in self.other_flag_pos]
        self.flag_rgba=self.pawn_img.getpixel((self.main_flag_pos["x"],self.main_flag_pos["y"]))
        self.other_flag_rgba=[self.pawn_img.getpixel((pos["x"],pos["y"]))\
                              for pos in self.other_flag_pos]
        self.background_rgba=self.main_img.getpixel((100,100))
        self.pawn_atleft=True
        self.center_x=self.size["width"]/2

        #Init core data
        self.pawn_pos=None
        self.target_pos=None

    def cal_dist(self,make_img=False,img_name="cal_dist.png"):
        '''Calculate the distance between pawn and target place'''

        #Check arguments
        if type(make_img) is not bool or \
           type(img_name) is not str:
            print("Calculator.cal_dist was invoked with wrong parameters!")
            sys.exit(1)

        #Calculate both positions of pawn and target
        self.__cal_pawn_pos()
        self.__cal_target_pos()

        #Return distance and create a new image with position marks if necessary
        if self.pawn_pos!=None and self.target_pos!=None:
            if make_img==True:
                #Generate an image with position marks
                painter=ImageDraw.Draw(self.main_img)
                painter.line([self.pawn_pos,100,self.pawn_pos,1900],fill="white",width=2)
                painter.line([self.target_pos,100,self.target_pos,1900],fill="red",width=2)
                self.main_img.save(img_name)
            return math.fabs(self.target_pos-self.pawn_pos)
        else:
            return None

    def __cal_pawn_pos(self):
        '''Find pawn's position'''

        #Specify a search area
        search_area=self.search_area_whole

        #Search and find the first pixel that is equal to the main flag pixel
        break_flag=False
        for y in range(search_area["top"],search_area["bottom"]):
            if break_flag==True:
                break
            for x in range(search_area["left"],search_area["right"]):
                current_rgba=self.main_img.getpixel((x,y))
                if is_equal(self.flag_rgba,current_rgba)==True:
                    #Further examination using other flag pixels
                    another_rgba=self.main_img.getpixel((\
                                 x+self.flag_pos_diff[0]["delta_x"],\
                                 y+self.flag_pos_diff[0]["delta_y"]\
                                 ))
                    if is_equal(self.other_flag_rgba[0],another_rgba)==True:
                            pawn_temp_x=x
                            pawn_temp_y=y
                            break_flag=True
                            break

        #Find all of the pixels in current line that is equal to the main flag pixel
        pawn_pos_list=[]
        for x in range(pawn_temp_x,search_area["right"]):
            current_rgba=self.main_img.getpixel((x,pawn_temp_y))
            if is_equal(self.flag_rgba,current_rgba)==True:
                pawn_pos_list.append(x)
            else:
                break

        #Choose central pixel's position as pawn's position
        length=len(pawn_pos_list)
        if length>0:
            self.pawn_pos=pawn_pos_list[math.floor(length/2)]
            if self.pawn_pos>self.center_x:
                self.pawn_atleft=False
        else:
            print("pawn_pos not found!")
            sys.exit()
                    #~ if is_equal(self.flag_rgba,another_rgba)==True:
                        #~ self.pawn_pos=x
                        #~ break_flag=True
                        #~ break
        #~ if self.pawn_pos==None:
            #~ print("self.pawn_pos is still None!")
            #~ sys.exit()
        #~ else:
            #~ if self.pawn_pos>self.center_x:
                #~ self.pawn_atleft=False

    def __cal_target_pos(self):
        '''Find target's position'''

        #Specify a search area according to pawn's positon
        if self.pawn_atleft==True:
            search_area=self.search_area_right
        else:
            search_area=self.search_area_left

        #Search and find the first pixel that is different with background
        break_flag=False
        for y in range(search_area["top"],search_area["bottom"]):
            if break_flag==True:
                break
            for x in range(search_area["left"],search_area["right"]):
                current_rgba=self.main_img.getpixel((x,y))
                if is_different(self.background_rgba,current_rgba)==True:
                    target_temp_x=x
                    target_temp_y=y
                    break_flag=True
                    break

        #Find all of the pixels in current line that is different with background
        target_pos_list=[]
        for x in range(target_temp_x,search_area["right"]):
            current_rgba=self.main_img.getpixel((x,target_temp_y))
            if is_different(self.background_rgba,current_rgba)==True:
                target_pos_list.append(x)
            else:
                break

        #Choose central pixel's position as target's position
        length=len(target_pos_list)
        if length>0:
            self.target_pos=target_pos_list[math.floor(length/2)]

if __name__=="__main__":
    print("calculator.py is not imported")
    pass
