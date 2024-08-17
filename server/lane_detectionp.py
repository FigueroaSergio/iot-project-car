import cv2
import numpy as np

class LaneDetector:
    def __init__(self, image):
        self.img = image
        '''
        parametri buoni per telefono fra
        '''
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

    def apply_threshold(self):
        '''
        Data immagine restituisce maschera binaria immagine bianco nero con i filtri sopra scritti per c
        'c-lower-x' e 'c-upper-x': Limiti inferiori e superiori per il canale Hue (colore).
        'c-lower-y' e 'c-upper-y': Limiti inferiori e superiori per il canale Saturation (saturazione).
        'c-lower-z' e 'c-upper-z': Limiti inferiori e superiori per il canale Value (luminosità).
        '''
        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        lower_color = np.array([self.init['c-lower-x'], self.init['c-lower-y'], self.init['c-lower-z']])
        upper_color = np.array([self.init['c-upper-x'], self.init['c-upper-y'], self.init['c-upper-z']])
        mask = cv2.inRange(hsv, lower_color, upper_color)
        return mask

    def detect_lines(self, mask):
        '''
        Canny trova i bordi nella maschera.
        La Trasformata di Hough per le linee nell'immagine con i bordi

        restituisce array di linee rilevate rappresentate come punti finali (x1, y1, x2, y2).

        '''
        edges = cv2.Canny(mask, 50, 150)
        lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=self.init['threshold'],
                                minLineLength=self.init['min-line'], maxLineGap=150)
        return lines
    
    
    def draw_lane_area(self, lines):
        '''
        Disegna un'area di corsia sull'immagine utilizzando le linee rilevate e calcola il centro della corsia

            Le linee rilevate vengono suddivise in linee a sinistra e a destra basate sulla loro inclinazione

        Restituisce:
                img (numpy.ndarray): Immagine originale con l'area della corsia disegnata.
                lane_center (float): Coordinata x del centro della corsia rispetto all'immagine, se le linee sono rilevate; altrimenti None.
        '''
        if lines is not None:
            height, width = self.img.shape[:2]
            left_line_points = []
            right_line_points = []

            for line in lines:
                for x1, y1, x2, y2 in line:
                    slope = (y2 - y1) / (x2 - x1) if (x2 - x1) != 0 else 0
                    if slope < 0:
                        left_line_points.extend([(x1, y1), (x2, y2)])
                    else:
                        right_line_points.extend([(x1, y1), (x2, y2)])
            #si ordina i punti y in ordine decrescente significa che i primi sono quelli lontani dall'orizzonte 
            #ed è piu facile disegnare la corsia
            if left_line_points and right_line_points:
                left_line_points = sorted(left_line_points, key=lambda x: x[1], reverse=True)
                right_line_points = sorted(right_line_points, key=lambda x: x[1], reverse=True)

                # Create a polygon to represent the lane area
                pts = np.array(left_line_points + right_line_points[::-1], dtype=np.int32)
                cv2.fillPoly(self.img, [pts], (0, 255, 0))  # Fill the polygon with green color

                # Calculate lane center for steering
                left_base = np.mean([pt[0] for pt in left_line_points[:2]])
                right_base = np.mean([pt[0] for pt in right_line_points[:2]])
                lane_center = (left_base + right_base) / 2

                return self.img, lane_center

        return self.img, None
