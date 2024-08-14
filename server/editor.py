import cv2
import numpy as np
import time
import matplotlib.pyplot as plt

class Editor:
    def __init__(self, image):
        self.img = image
        self.init = {
            'Point-0-x': 0,
            'Point-0-y': 128,
            'Point-1-x': 0,
            'Point-1-y': 0,
            'Point-2-x': 128,
            'Point-2-y': 0,
            'Point-3-x': 128,
            'Point-3-y': 128,
            'min-line': 20,
            'threshold': 8,
            'step': 0,
            'c-lower-x': 84,
            'c-lower-y': 0,
            'c-lower-z': 160,
            'c-upper-x': 255,
            'c-upper-y': 95,
            'c-upper-z': 255,
        }
        
        # Create trackbars
        cv2.namedWindow('Track')
        self.loading=True
        self.createTrackbars()
        self.createTrackbars_colors()
        self.loading=False
        self.render()
         # Ensure trackbars are initialized before rendering
        


    def createTrackbars(self):
        height, width = self.img.shape[:2]
        
        for i in range(4):
            cv2.createTrackbar(f'Point-{i}-x', 'Track', int(self.init[f'Point-{i}-x']), width, self.update)
            cv2.createTrackbar(f'Point-{i}-y', 'Track', int(self.init[f'Point-{i}-y']), height, self.update)
        
        cv2.createTrackbar('Step', 'Track', self.init['step'], 4, self.update)
        cv2.createTrackbar('min-line', 'Track', self.init['min-line'], 500, self.update)
        cv2.createTrackbar('threshold', 'Track', self.init['threshold'], 500, self.update)

    def createTrackbars_colors(self):
        cv2.createTrackbar('c-lower-x', 'Track', self.init['c-lower-x'], 255, self.update)
        cv2.createTrackbar('c-lower-y', 'Track', self.init['c-lower-y'], 255, self.update)
        cv2.createTrackbar('c-lower-z', 'Track', self.init['c-lower-z'], 255, self.update)
        cv2.createTrackbar('c-upper-x', 'Track', self.init['c-upper-x'], 255, self.update)
        cv2.createTrackbar('c-upper-y', 'Track', self.init['c-upper-y'], 255, self.update)
        cv2.createTrackbar('c-upper-z', 'Track', self.init['c-upper-z'], 255, self.update)

    def update(self, value):
        if(self.loading):
            return
        img=np.copy(self.img)
        # cv2.imshow('origina',img)
        r =self.process(img)
        # cv2.imshow('view', r)
        # cv2.imshow('view', r)
        # cv2.imshow('view', r)
    
    def region_selection(self, image):
        mask = np.zeros_like(image)
        ignore_mask_color = 255
        vertices = np.array([self.get_points()], dtype=np.int32)
        cv2.fillPoly(mask, vertices, ignore_mask_color)
        masked_image = cv2.bitwise_and(image, mask)
        return masked_image
    
    def hough_transform(self, image):
        min_line = cv2.getTrackbarPos('min-line', 'Track')
        thresh = cv2.getTrackbarPos('threshold', 'Track')
        return cv2.HoughLinesP(image, 1, np.pi/180, threshold=thresh, minLineLength=min_line, maxLineGap=50)

    def average_slope_intercept(self, lines):
        left_lines, left_weights = [], []
        right_lines, right_weights = [], []
        for line in lines:
            for x1, y1, x2, y2 in line:
                if x1 == x2:
                    continue
                slope = (y2 - y1) / (x2 - x1)
                intercept = y1 - (slope * x1)
                length = np.sqrt(((y2 - y1) ** 2) + ((x2 - x1) ** 2))
                if slope < 0:
                    left_lines.append((slope, intercept))
                    left_weights.append(length)
                else:
                    right_lines.append((slope, intercept))
                    right_weights.append(length)
        left_lane = np.dot(left_weights, left_lines) / np.sum(left_weights) if len(left_weights) > 0 else None
        right_lane = np.dot(right_weights, right_lines) / np.sum(right_weights) if len(right_weights) > 0 else None
        return left_lane, right_lane

    def pixel_points(self, y1, y2, line):
        if line is None:
            return None
        slope, intercept = line
        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)
        return ((x1, y1), (x2, y2))

    def get_points(self):
        points = []
        for i in range(4):
            x = cv2.getTrackbarPos(f'Point-{i}-x', 'Track')
            y = cv2.getTrackbarPos(f'Point-{i}-y', 'Track')
            points.append([x, y])
        return points

    def process(self, img):
        try:
            step = cv2.getTrackbarPos('Step', 'Track')
        except cv2.error as e:
            print(f"Error getting trackbar position: {e}")
            return img  # Return the original image if the trackbar position cannot be retrieved

        self.img = img.copy()
        
        if step == 0:
            return img
        
        try:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            lower_color = np.array([cv2.getTrackbarPos(f'c-lower-x', 'Track'),
                                    cv2.getTrackbarPos(f'c-lower-y', 'Track'),
                                    cv2.getTrackbarPos(f'c-lower-z', 'Track')])
            upper_color = np.array([cv2.getTrackbarPos(f'c-upper-x', 'Track'),
                                    cv2.getTrackbarPos(f'c-upper-y', 'Track'),
                                    cv2.getTrackbarPos(f'c-upper-z', 'Track')])
            mask = cv2.inRange(hsv, lower_color, upper_color)
        except cv2.error as e:
            print(f"Error processing the image: {e}")
            return img  # Return the original image if the image processing fails

        if step == 1:
            return cv2.Canny(mask, 50, 150)
        
        region = self.region_selection(mask)
        if step == 2:
            return region
        
        if step == 3 or step == 4:
            try:
                lines = self.hough_transform(region)
                l = self.lane_lines(img, lines)
                print(l)
                line_image = self.draw_lane_lines(img, l)
                angles = []
                points = []
                
                if step == 4:
                    steering_angle = self.calculate_steering_angle(self.lane_lines(img, lines))
                    self.display_steering_angle(line_image, steering_angle)
                    print(steering_angle)
            except cv2.error as e:
                print(f"Error during line processing: {e}")
                return img  # Return the original image if line processing fails
                
            return line_image
        
        return img


    def lane_lines(self, image, lines):
        if lines is None:
            return None
        height = image.shape[0]
        left_line, right_line = self.average_slope_intercept(lines)
        left_line = self.pixel_points(height, int(height * 0.6), left_line)
        right_line = self.pixel_points(height, int(height * 0.6), right_line)
        return left_line, right_line

    def draw_lane_lines(self, image, lines, color=(0, 255, 0), thickness=5):
        if lines is None:
            return image
        left_line, right_line = lines
        if left_line is not None:
            cv2.line(image, left_line[0], left_line[1], color, thickness)
        if right_line is not None:
            cv2.line(image, right_line[0], right_line[1], color, thickness)
        time.sleep(1)
        return image

    def calculate_steering_angle(self, lines):
        if lines is None:
            return 74  # Default to straight if no lines are detected
        
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
            
            return steering_angle
        else:
            return 74  # Default to straight if no valid angles

    def display_steering_angle(self, img, angle):
        cv2.putText(img, f'Steering Angle: {angle:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    def render(self):
        processed_img = self.process(self.img)
        cv2.imshow('view-1', processed_img)
        cv2.waitKey(1)
          
