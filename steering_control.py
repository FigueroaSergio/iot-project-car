# steering_control.py

import numpy as np

def calculate_steering_angle(frame, lane_center):
    '''
    Calcola l'angolo di sterzata necessario per mantenere il veicolo al centro della corsia e determina la direzione di sterzata

    Parametri:
    - frame: L'immagine corrente del video (frame) utilizzata per ottenere le dimensioni dell'immagine.
    - lane_center: La coordinata orizzontale del centro della corsia rilevato nell'immagine. Se None, significa che la corsia non è stata rilevata.

    Restituisce:
    - steering_angle: L'angolo di sterzata in gradi calcolato in base alla deviazione del centro della corsia dal centro dell'immagine.
    - direction: Una stringa che indica la direzione di sterzata ("Right", "Left" o "Straight") basata sull'angolo di sterzata.

    
    - Calcola la deviazione del centro della corsia dal centro dell'immagine.
    - Usa la deviazione e l'altezza dell'immagine per calcolare l'angolo di sterzata in gradi.
    L'angolo di sterzata viene calcolato utilizzando la funzione arctan, che restituisce l'arcotangente della deviazione rispetto all'altezza dell'immagine.
      La formula è steering_angle = np.arctan(deviation / height) * (180 / np.pi).

    Arcotangente calcola l'angolo (in radianti) il cui tangente è il rapporto tra la deviazione 
    e l'altezza dell'immagine. Questo rapporto considera quanto la deviazione del centro della corsia (in pixel) è "lontana
    " rispetto all'altezza dell'immagine.

    Conversione in Gradi: Il risultato dell'arcotangente è inizialmente in radianti. Moltiplichiamo per 180 / np.pi per convertire questo valore in gradi.
    - Determina la direzione di sterzata in base all'angolo: se l'angolo è maggiore di 5 gradi, la direzione è "Right"; se è minore di -5 gradi, la direzione è "Left"; altrimenti, la direzione è "Straight".
    - Se la corsia non è rilevata, restituisce "Straight" come direzione e 0 come angolo di sterzata.

    I valori -9 e 9 li ho messi manualmente ma potrebbero essere da cambiare(ingrandire) o cambiare metodo di decisione angolo in base a prove
    '''
    height, width = frame.shape[:2]
    steering_angle=90
    direction='Straight'
    if lane_center is not None:
        deviation = lane_center - (width / 2)
        steering_angle = np.arctan(deviation / height) * (180 / np.pi)
        
        if steering_angle >= 9 :
            direction = "Right"
        if steering_angle < -9 :
            direction = "Left"
            
    
    return steering_angle, direction
