

        
import cv2
import numpy as np
import matplotlib.pyplot as plt
import logging
import math

import time
from lane_detectionp import LaneDetector  # Import your lane detection class
from steering_control import calculate_steering_angle  # Import your steering control function


class Editor:
    def __init__(self, image, opts={}):
        self.img = image
        height,width = self.img.shape[:2]

        self.init = {
            'Point-0-x': opts.get('Point-0-x',0),
            'Point-0-y': opts.get('Point-0-y',height),
            'Point-1-x': opts.get('Point-1-x',0),
            'Point-1-y': opts.get('Point-1-y',0),
            'Point-2-x': opts.get('Point-2-x',width),
            'Point-2-y': opts.get('Point-2-y',0),
            'Point-3-x': opts.get('Point-3-x',width),
            'Point-3-y': opts.get('Point-3-y',height),
            'min-line': opts.get('min-line',20),
            'threshold': opts.get('threshold',8),
            'step': opts.get('step',4),
            'c-lower-x': opts.get('c-lower-x',0),
            'c-lower-y': opts.get('c-lower-y',0),
            'c-lower-z': opts.get('c-lower-z',0),
            'c-upper-x': opts.get('c-upper-x',120),
            'c-upper-y': opts.get('c-upper-y',110),
            'c-upper-z': opts.get('c-upper-z',120),
        }
        
        
        self.last_update_time = time.time()  # Track the last time drawing and calculation were done
        self.update_interval = 1.0   # certi calcoli da fare ogni 10 frames
        self.curr_steering_angle = 90
        
        print(f"Image dimensions: {width}x{height}")
        
        # Initialize points for the polygon region
        self.bottom_left = [self.init['Point-0-x'], self.init['Point-0-y']]
        self.top_left = [self.init['Point-1-x'], self.init['Point-1-y']]
        self.top_right = [self.init['Point-2-x'], self.init['Point-2-y']]
        self.bottom_right = [self.init['Point-3-x'], self.init['Point-3-y']]
        self.points = [self.bottom_left, self.top_left, self.top_right, self.bottom_right]
        cv2.namedWindow('Track')
        self.loading = True
        self.createTrackbars(self.img)
        self.createTrackbars_colors()
        self.loading = False
        self.render(None)
    
    def createTrackbars(self, img):
        width, height = img.shape[:2]
        for i, point in enumerate(self.points):
            cv2.createTrackbar(f'Point-{i}-x', 'Track', int(point[0]), height, self.render)
            cv2.createTrackbar(f'Point-{i}-y', 'Track', int(point[1]), width, self.render)
        cv2.createTrackbar(f'Step', 'Track', self.init['step'], 5, self.render)
        cv2.createTrackbar(f'min-line', 'Track', self.init['min-line'], 500, self.render)
        cv2.createTrackbar(f'threshold', 'Track', self.init['threshold'], 500, self.render)

    def createTrackbars_colors(self):
        print('Setting up color trackbars...')
        cv2.createTrackbar(f'c-lower-x', 'Track', self.init['c-lower-x'], 255, self.render)
        cv2.createTrackbar(f'c-lower-y', 'Track', self.init['c-lower-y'], 255, self.render)
        cv2.createTrackbar(f'c-lower-z', 'Track', self.init['c-lower-z'], 255, self.render)
        cv2.createTrackbar(f'c-upper-x', 'Track', self.init['c-upper-x'], 255, self.render)
        cv2.createTrackbar(f'c-upper-y', 'Track', self.init['c-upper-y'], 255, self.render)
        cv2.createTrackbar(f'c-upper-z', 'Track', self.init['c-upper-z'], 255, self.render)

    ### USATI PER Step 1-4
    def region_selection(self, image):
        mask = np.zeros_like(image)
        if len(image.shape) > 2:
            channel_count = image.shape[2]
            ignore_mask_color = (255,) * channel_count
        else:
            ignore_mask_color = 255
        vertices = np.array([self.points], dtype=np.int32)
        cv2.fillPoly(mask, vertices, ignore_mask_color)
        masked_image = cv2.bitwise_and(image, mask)
        return masked_image
    
    def hough_transform(self, image):
        min_line = cv2.getTrackbarPos(f'min-line', 'Track')
        thresh = cv2.getTrackbarPos(f'threshold', 'Track')
        return cv2.HoughLinesP(image, 1, np.pi/180, threshold=thresh, minLineLength=min_line, maxLineGap=50)
        
    def make_points(self, frame, line):
        height, width, _ = frame.shape
        slope, intercept = line
        y1 = height  # bottom of the frame
        y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

        # bound the coordinates within the frame
        x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
        x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
        return [[x1, y1, x2, y2]]
    
    def average_slope_intercept(self, lines, frame):
        """
        This function combines line segments into one or two lane lines
        If all line slopes are < 0: then we only have detected left lane
        If all line slopes are > 0: then we only have detected right lane
        """
        lane_lines = []
        if lines is None:
            logging.info('No lines segments detected')
            return lane_lines

        height, width, _ = frame.shape
        left_fit = []
        right_fit = []

        boundary = 1/3
        left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
        right_region_boundary = width * boundary # right lane line segment should be on left 2/3 of the screen

        for line in lines:
            for x1, y1, x2, y2 in line:
                if x1 == x2:
                    logging.info('skipping vertical line segment (slope=inf): %s' % lines)
                    continue
                fit = np.polyfit((x1, x2), (y1, y2), 1)
                slope = fit[0]
                intercept = fit[1]
                if slope < 0:
                    if x1 < left_region_boundary and x2 < left_region_boundary:
                        left_fit.append((slope, intercept))
                else:
                    if x1 > right_region_boundary and x2 > right_region_boundary:
                        right_fit.append((slope, intercept))

        left_fit_average = np.average(left_fit, axis=0)
        if len(left_fit) > 0:
            lane_lines.append(self.make_points(frame, left_fit_average))

        right_fit_average = np.average(right_fit, axis=0)
        if len(right_fit) > 0:
            lane_lines.append(self.make_points(frame, right_fit_average))

        # print('lane lines: %s' %lane_lines)  # [[[316, 720, 484, 432]], [[1009, 720, 718, 432]]]

        return lane_lines
    
    def pixel_points(self, y1, y2, line):
        if line is None:
            return None
        slope, intercept = line
        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)
        y1 = int(y1)
        y2 = int(y2)
        return ((x1, y1), (x2, y2))
    
    def lane_lines(self, image, lines):
        if lines is None:
            return None
        return self.average_slope_intercept(lines,image)
    
    def draw_lane_lines(self, image, lines, color=[255, 0, 0], thickness=12):
        line_image = np.zeros_like(image)
        if lines is None:
            return image
        for line in lines:
            if line is not None:
                for x1, y1, x2, y2 in line:
                    cv2.line(line_image, (x1, y1), (x2, y2), color, thickness)
        return cv2.addWeighted(image, 1.0, line_image, 1.0, 0.0)
    
    def setImage(self, image):
        self.img = image
    
    def render(self, a):
        if self.loading:
            return
        img = np.copy(self.img)
        r = self.process(img)
    ###
    def compute_steering_angle(self,frame, lane_lines):
        """ Find the steering angle based on lane line coordinate
            We assume that camera is calibrated to point to dead center
        """
        if(lane_lines is None):
            # print("No lines")
            return -90
        if len(lane_lines) == 0:
            logging.info('No lane lines detected, do nothing')
            return -90

        height, width, _ = frame.shape
        if len(lane_lines) == 1:
            logging.debug('Only detected one lane line, just follow it. %s' % lane_lines[0])
            x1, _, x2, _ = lane_lines[0][0]
            x_offset = x2 - x1
        else:
            _, _, left_x2, _ = lane_lines[0][0]
            _, _, right_x2, _ = lane_lines[1][0]
            camera_mid_offset_percent = 0.02 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
            mid = int(width / 2 * (1 + camera_mid_offset_percent))
            x_offset = (left_x2 + right_x2) / 2 - mid

        # find the steering angle, which is angle between navigation direction to end of center line
        y_offset = int(height / 2)

        angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
        angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
        steering_angle = angle_to_mid_deg + 90  # this is the steering angle needed by picar front wheel

        logging.debug('new steering angle: %s' % steering_angle)
        return steering_angle

    def stabilize_steering_angle(self,curr_steering_angle, new_steering_angle, num_of_lane_lines, max_angle_deviation_two_lines=5, max_angle_deviation_one_lane=1):
        """
        Using last steering angle to stabilize the steering angle
        This can be improved to use last N angles, etc
        if new angle is too different from current angle, only turn by max_angle_deviation degrees
        """
        if num_of_lane_lines == 2 :
            # if both lane lines detected, then we can deviate more
            max_angle_deviation = max_angle_deviation_two_lines
        else :
            # if only one lane detected, don't deviate too much
            max_angle_deviation = max_angle_deviation_one_lane

        angle_deviation = new_steering_angle - curr_steering_angle
        if abs(angle_deviation) > max_angle_deviation:
            stabilized_steering_angle = int(curr_steering_angle
                                            + max_angle_deviation * angle_deviation / abs(angle_deviation))
        else:
            stabilized_steering_angle = new_steering_angle
        logging.info('Proposed angle: %s, stabilized angle: %s' % (new_steering_angle, stabilized_steering_angle))
        return stabilized_steering_angle

    def display_heading_line(self,frame, steering_angle, line_color=(0, 0, 255), line_width=5, ):
        heading_image = np.zeros_like(frame)
        height, width, _ = frame.shape

        # figure out the heading line from steering angle
        # heading line (x1,y1) is always center bottom of the screen
        # (x2, y2) requires a bit of trigonometry

        # Note: the steering angle of:
        # 0-89 degree: turn left
        # 90 degree: going straight
        # 91-180 degree: turn right 
        steering_angle_radian = steering_angle / 180.0 * math.pi
        x1 = int(width / 2)
        y1 = height
        x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
        y2 = int(height / 2)

        cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
        heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

        return heading_image

    def steer(self, frame, lane_lines):
        lines = len(lane_lines) if lane_lines is not None else 0
        new_steering_angle = self.compute_steering_angle(frame, lane_lines)
        self.curr_steering_angle = self.stabilize_steering_angle(self.curr_steering_angle, new_steering_angle, lines)
        return self.display_heading_line(frame, self.curr_steering_angle)

    def process(self, img):
        for i in range(4):
            x=cv2.getTrackbarPos(f'Point-{i}-x','Track')
            y=cv2.getTrackbarPos(f'Point-{i}-y','Track')
            self.points[i]=[x,y]
            circle = cv2.circle(img,[x,y],5,(0,255,0),cv2.FILLED)
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
            result = self.draw_lane_lines(img, l)
            if(step==3):
                return result
            # cv2.imshow('result',result)
           #metto il codice dentro l'if se no rompe tutto quell'errore
            if(step==4):
                print(f"Steering Angle: {self.curr_steering_angle:.2f} degrees")
                return self.steer(result,l)
            if(step==5):
                '''
                calcolo diverso delle linee, usa lane_detectionp.py e steering_control.py
                '''
                current_time = time.time()
                
                # Initialize LaneDetector with the current image
                lane_detector = LaneDetector(img)


                # Draw lane area and get lane center
                img_with_lane_area, lane_center = lane_detector.draw_lane_area(lines)

                # Check if it's time to update the drawing and steering calculations
                if current_time - self.last_update_time >= self.update_interval:
                    # Calculate steering angle and direction
                    steering_angle, direction = calculate_steering_angle(img, lane_center)
                    self.curr_steering_angle= steering_angle
                    # Print steering angle and direction to the terminal
                    print(f"Steering Angle: {steering_angle:.2f} degrees")
                    print(f"Direction: {direction}")

                    # Update the last update time
                    self.last_update_time = current_time
                else:
                    # Use default values if not updating
                    steering_angle, direction = 0, "Straight"

                # Annotate the image with the steering angle and direction
                

                # Return the image with lane area and annotations
                return img_with_lane_area
            # Mostra l'immagine finale con le linee e i punti

           
          
        except Exception as e:
            print(e)
            return img
        

    def setImage(self, image):
        self.img = image

    
    '''
    def process(self, img):
        for i in range(4):
            x = cv2.getTrackbarPos(f'Point-{i}-x', 'Track')
            y = cv2.getTrackbarPos(f'Point-{i}-y', 'Track')
            self.points[i] = [x, y]
            cv2.circle(img, [x, y], 10, (0, 255, 0), cv2.FILLED)
        
        step = cv2.getTrackbarPos(f'Step', 'Track')
        
        try:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            lower_color = np.array([
                cv2.getTrackbarPos(f'c-lower-x', 'Track'),
                cv2.getTrackbarPos(f'c-lower-y', 'Track'),
                cv2.getTrackbarPos(f'c-lower-z', 'Track')
            ])
            upper_color = np.array([ 
                cv2.getTrackbarPos(f'c-upper-x', 'Track'),
                cv2.getTrackbarPos(f'c-upper-y', 'Track'),
                cv2.getTrackbarPos(f'c-upper-z', 'Track')
            ])
            
            mask = cv2.inRange(hsv, lower_color, upper_color)
            if step == 0:
                return mask
            
            edges = cv2.Canny(mask, 50, 150)
            if step == 1:
                return edges
            
            region = self.region_selection(edges)
            if step == 2:
                return region
            
            line_image = img
            angles = []
            points = []
            
            lines = self.hough_transform(region)
            lane_lines = self.lane_lines(img, lines)
            
            if step == 3:
                if self.frame_count % self.draw_interval == 0:  # Draw less frequently
                    result = self.draw_lane_lines(img, lane_lines)
                      # Simulate reduced drawing frequency
                    return result
                else:
                    print(f"Skipping draw at frame {self.frame_count}")
            
            if step == 4:
                if self.frame_count % self.draw_interval == 0:  # Draw less frequently
                    # Draw lane lines on the image
                    result = self.draw_lane_lines(img, lane_lines)
                    
                    angles = []
                    
                    if isinstance(lines, tuple) and len(lines) == 2:
                        left_line, right_line = lines
                        
                        # Process left line
                        if left_line is not None and isinstance(left_line, tuple) and len(left_line) == 2:
                            x1, y1 = left_line[0]
                            x2, y2 = left_line[1]
                            if x2 != x1:
                                angle = np.arctan2((y2 - y1), (x2 - x1)) * 180 / np.pi
                                angles.append(angle)
                        
                        # Process right line
                        if right_line is not None and isinstance(right_line, tuple) and len(right_line) == 2:
                            x1, y1 = right_line[0]
                            x2, y2 = right_line[1]
                            if x2 != x1:
                                angle = np.arctan2((y2 - y1), (x2 - x1)) * 180 / np.pi
                                angles.append(angle)
                    
                    if angles:
                        median_angle = np.median(angles)
                        print(f"Median Angle: {median_angle:.2f} degrees")

                        # Map the angle to steering values
                        # Adjust these values based on your calibration
                        steering_angle = 74 - median_angle  # 74 is assumed to be the neutral position
                        steering_angle = np.clip(steering_angle, 30, 110)  # Clip to the range [30, 110]
                        
                        print(steering_angle)
                    else:
                        print("boh")
                        return line_image  # Default to straight if no valid an
                    # Simulate reduced drawing frequency
                    return line_image

        except Exception as e:
            print(f"Error processing image at step {step}: {e}")
            return img  # Return original image in case of error
        '''