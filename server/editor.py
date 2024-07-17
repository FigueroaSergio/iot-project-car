
import cv2
import numpy as np
import matplotlib.pyplot as plt


class Editor:
    def __init__(self,image):
        self.img =image
        self.init={
           'Point-0-x':0,
           'Point-0-y':128, 
           'Point-1-x':0,
           'Point-1-y':0,
           'Point-2-x':128,
           'Point-2-y':0,
            'Point-3-x':128,
           'Point-3-y':128,
           'min-line':20,
           'threshold':8,
            'step':0,
            'c-lower-x':0,
            'c-lower-y':0,
            'c-lower-z':0,
            'c-upper-x':255,
            'c-upper-y':255,
            'c-upper-z':190,


        }
        
        width, height = self.img.shape[:2]
        print(width,height)
        self.bottom_left  = [self.init['Point-0-x'],self.init['Point-0-y']]
        self.top_left     = [self.init['Point-1-x'], self.init['Point-1-y']]
        self.top_right = [self.init['Point-2-x'],self.init['Point-2-y']]
        self.bottom_right    = [self.init['Point-3-x'], self.init['Point-3-y']]
        self.points = [self.bottom_left,self.top_left,self.bottom_right,self.top_right]
        cv2.namedWindow('Track')
        self.loading=True
        self.createTrackbars(self.img)
        self.createTrackbars_colors()
        self.loading=False
        self.render(None)
    
    def createTrackbars(self,img):

        width, height = img.shape[:2]
       
        for i,point in enumerate(self.points):
           
            cv2.createTrackbar(f'Point-{i}-x','Track',int(point[0]),height,self.render)
            cv2.createTrackbar(f'Point-{i}-y','Track',int(point[1]),width,self.render)
        cv2.createTrackbar(f'Step','Track',0,4,self.render)
        cv2.createTrackbar(f'min-line','Track',self.init['min-line'],500,self.render)
        cv2.createTrackbar(f'threshold','Track',self.init['threshold'],500,self.render)



    def createTrackbars_colors(self):
        print('colors')
       
        cv2.createTrackbar(f'c-lower-x','Track',self.init['c-lower-x'],255,self.render)
       
        cv2.createTrackbar(f'c-lower-y','Track',self.init['c-lower-y'],255,self.render)
       
        cv2.createTrackbar(f'c-lower-z','Track',self.init['c-lower-z'],255,self.render)
       
        
        cv2.createTrackbar(f'c-upper-x','Track',self.init['c-upper-x'],255,self.render)
       
        cv2.createTrackbar(f'c-upper-y','Track',self.init['c-upper-y'],255,self.render)
       
        cv2.createTrackbar(f'c-upper-z','Track',self.init['c-upper-z'],255,self.render)

    def region_selection(self,image):
        """
        Determine and cut the region of interest in the input image.
        Parameters:
            image: we pass here the output from canny where we have 
            identified edges in the frame
        """
        # create an array of the same size as of the input image 
        mask = np.zeros_like(image)   
        # if you pass an image with more then one channel
        if len(image.shape) > 2:
            channel_count = image.shape[2]
            ignore_mask_color = (255,) * channel_count
        # our image only has one channel so it will go under "else"
        else:
              # color of the mask polygon (white)
            ignore_mask_color = 255
        # creating a polygon to focus only on the road in the picture
        # we have created this polygon in accordance to how the camera was placed

        vertices = np.array([self.points], dtype=np.int32)
        # filling the polygon with white color and generating the final mask
        r=cv2.fillPoly(mask, vertices, ignore_mask_color)
        # performing Bitwise AND on the input image and mask to get only the edges on the road
        masked_image = cv2.bitwise_and(image, mask)
        return masked_image
    
    def hough_transform(self,image):
        min_line= cv2.getTrackbarPos(f'min-line','Track')
        thresh= cv2.getTrackbarPos(f'threshold','Track')
        return  cv2.HoughLinesP(image, 1, np.pi/180, threshold=thresh, minLineLength=min_line, maxLineGap=50)
    def average_slope_intercept(self,lines):
        """
        Find the slope and intercept of the left and right lanes of each image.
        Parameters:
            lines: output from Hough Transform
        """
        left_lines    = [] #(slope, intercept)
        left_weights  = [] #(length,)
        right_lines   = [] #(slope, intercept)
        right_weights = [] #(length,)
        for line in lines:
            for x1, y1, x2, y2 in line:
                if x1 == x2:
                    continue
                # calculating slope of a line
                slope = (y2 - y1) / (x2 - x1)
                # calculating intercept of a line
                intercept = y1 - (slope * x1)
                # calculating length of a line
                length = np.sqrt(((y2 - y1) ** 2) + ((x2 - x1) ** 2))
                # slope of left lane is negative and for right lane slope is positive
                if slope < 0:
                    left_lines.append((slope, intercept))
                    left_weights.append((length))
                else:
                    right_lines.append((slope, intercept))
                    right_weights.append((length))
        # 
        left_lane  = np.dot(left_weights,  left_lines) / np.sum(left_weights)  if len(left_weights) > 0 else None
        right_lane = np.dot(right_weights, right_lines) / np.sum(right_weights) if len(right_weights) > 0 else None
        return left_lane, right_lane
   
    def pixel_points(self,y1, y2, line):
        """
        Converts the slope and intercept of each line into pixel points.
            Parameters:
                y1: y-value of the line's starting point.
                y2: y-value of the line's end point.
                line: The slope and intercept of the line.
        """
        if line is None:
            return None
        slope, intercept = line
        x1 = int((y1 - intercept)/slope)
        x2 = int((y2 - intercept)/slope)
        y1 = int(y1)
        y2 = int(y2)
        return ((x1, y1), (x2, y2))
    def lane_lines(self, image, lines):
        """
        Create full lenght lines from pixel points.
            Parameters:
                image: The input test image.
                lines: The output lines from Hough Transform.
        """
        if(lines is None):
            return None
        left_lane, right_lane = self.average_slope_intercept(lines)
        y1 = image.shape[0]
        y2 = y1 * 0.6
        left_line  = self.pixel_points(y1, y2, left_lane)
        right_line = self.pixel_points(y1, y2, right_lane)
        return left_line, right_line
    def draw_lane_lines(self,image, lines, color=[255, 0, 0], thickness=12):
        """
        Draw lines onto the input image.
            Parameters:
                image: The input test image (video frame in our case).
                lines: The output lines from Hough Transform.
                color (Default = red): Line color.
                thickness (Default = 12): Line thickness. 
        """
        line_image = np.zeros_like(image)
        if(lines is None):
            return image
        for line in lines:
            if line is not None:
                cv2.line(line_image, *line,  color, thickness)
        return cv2.addWeighted(image, 1.0, line_image, 1.0, 0.0)
    def setImage(self,image):
        # print('set image')
        self.img =image
    def render(self,a):
        if(self.loading):
            return
        img=np.copy(self.img)
        # cv2.imshow('origina',img)
        r =self.process(img)
        # cv2.imshow('view', r)
    def process(self,img):

        for i in range(4):
            x=cv2.getTrackbarPos(f'Point-{i}-x','Track')
            y=cv2.getTrackbarPos(f'Point-{i}-y','Track')
            self.points[i]=[x,y]
            circle = cv2.circle(img,[x,y],10,(0,255,0),cv2.FILLED)
        step = cv2.getTrackbarPos(f'Step','Track')
        try:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            lower_color=np.array([
                cv2.getTrackbarPos(f'c-lower-x','Track'),
                cv2.getTrackbarPos(f'c-lower-y','Track'),
                cv2.getTrackbarPos(f'c-lower-z','Track')
                ])
            upper_color=np.array([ 
                cv2.getTrackbarPos(f'c-upper-x','Track'),
                cv2.getTrackbarPos(f'c-upper-y','Track'),
                cv2.getTrackbarPos(f'c-upper-z','Track')
                ])
            # print(lower_color,upper_color)
            mask = cv2.inRange(hsv, lower_color, upper_color)
            if(step==0):
                return mask
            
            # cv2.imshow('mask',mask)
            edges = cv2.Canny(mask, 50, 150)
            if(step==1):
                return edges
            # cv2.imshow('edges',mask)
            region=self.region_selection(edges)
            # cv2.imshow('region',region)
            if(step==2):
                return region
            line_image = img
            angles = []
            points=[]
            
            lines = self.hough_transform(region)
            l=self.lane_lines(img, lines)
            result = self.draw_lane_lines(img, self.lane_lines(img, lines))
            if(step==3):
                return result
            # cv2.imshow('result',result)
            if l is not None:
                lines = []
                left_line, right_line= l
                if left_line is not None:
                    left_line= (left_line[0][0],left_line[0][1],left_line[1][0],left_line[1][0],left_line[1][1])
                    lines.append(left_line)
                if right_line is not None:
                    right_line= (right_line[0][0],right_line[0][1],right_line[1][0],right_line[1][0],right_line[1][1])
                    lines.append(right_line)
            if lines is not None:
                for line in lines:
                    for x1, y1, x2, y2 in line:
                        cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 3)

                        # Calcola l'angolo tra i punti (x1, y1) e (x2, y2)
                        angle = np.arctan2((y2 - y1), (x2 - x1)) * 180 / np.pi
                        angles.append(angle)

                        # Aggiungi i punti (x1, y1) e (x2, y2) alla lista points
                        points.append(((x1, y1), (x2, y2)))
            # cv2.imshow('lines',line_image)
            if angles:
                median_angle = np.median(angles)
                if median_angle is not None:
                    if median_angle > 0:
                        corrected_angle = median_angle + 53
                    else:
                        corrected_angle = median_angle + 90

                    height, width, _ = img.shape
                    steer_length = 200
                    center_x = width // 2
                    center_y = height
                    end_x = int(center_x + steer_length * np.cos(np.radians(corrected_angle)))
                    end_y = int(center_y - steer_length * np.sin(np.radians(corrected_angle)))

                    # Disegna la linea di sterzata
                    cv2.line(line_image, (center_x, center_y), (end_x, end_y), (255, 0, 0), 5)

                    plt.title(f"Angolo Mediano di Sterzata: {corrected_angle:.2f} gradi")
                else:
                    plt.title("Nessuna Linea Rilevata")
            else:
                plt.title("Nessuna Linea Rilevata")
            if(step==4):
                return line_image

            # Mostra l'immagine finale con le linee e i punti

           
          
        except Exception as e:
            print(e)
            return img

        




    


# img = cv2.imread("img.jpg", cv2.IMREAD_COLOR)
# print(img.shape)
# cv2.namedWindow('Track')
# cv2.resizeWindow('Track',360,240)
# cv2.createTrackbar('width','Track',0,100,setWidth)
# cv2.createTrackbar('height','Track',0,100,setHeight)
# render()
# Editor(cv2.imread('img.jpg', cv2.IMREAD_COLOR))
# cv2.waitKey(0) 
  
# # closing all open windows 
# cv2.destroyAllWindows() 

