import cv2
import numpy as np
import torch

from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie1976

# All funcs related to AI

def load_model(pipeline_name, weights):
    return torch.hub.load('ultralytics/yolov5', 'custom', path='pipelines/{}/{}'.format(pipeline_name, weights))


def unload_model(model):
    del model


def return_cords(model, frame):
    results = model(frame)

    results = results.pandas().xyxy[0].to_dict(orient="records")

    cords = []

    for result in results:
        x1 = int(result['xmin'])
        y1 = int(result['ymin'])
        x2 = int(result['xmax'])
        y2 = int(result['ymax'])
        cords.append([x1, y1, x2, y2])

    return cords


# All funcs related to color comparison

def get_color_dif(color1=None, color2=None):
    if color1 is None or color2 is None:
        return -1

    lab_color_1 = cv2.cvtColor(np.uint8([[color1]]), cv2.COLOR_RGB2LAB)[0][0]
    color_1 = LabColor(lab_l=lab_color_1[0], lab_a=lab_color_1[1], lab_b=lab_color_1[2])

    lab_color_2 = cv2.cvtColor(np.uint8([[color2]]), cv2.COLOR_RGB2LAB)[0][0]
    color_2 = LabColor(lab_l=lab_color_2[0], lab_a=lab_color_2[1], lab_b=lab_color_2[2])

    return delta_e_cie1976(color_1, color_2)


def get_main_colors_from_part_of_frame(frame, cords, colors_count):
    colors = []
    main_frame = frame
    for cord in cords:
        frame = main_frame[cord[1]:cord[3], cord[0]:cord[2]]

        pixels = np.float32(frame.reshape(-1, 3))

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
        flags = cv2.KMEANS_RANDOM_CENTERS

        _, labels, palettes = cv2.kmeans(pixels, colors_count, None, criteria, 10, flags)
        colors.append([[palette[0], palette[1], palette[2]] for palette in palettes])
    return colors


# All funcs related to drawing

def draw_rectangles(bg_offset, min_threshold, ethalon_color, comparison_colors, colors_count, frame, cords):
    if colors_count == 0:
        return -1

    j = 0
    for cord in cords:
        for i in range(colors_count):
            delta = get_color_dif(ethalon_color, comparison_colors[j][i])

            if bg_offset > delta > min_threshold:
                cv2.rectangle(frame, (cord[0], cord[1]), (cord[2], cord[3]), (0, 0, 255), 2)
                break
            elif delta <= min_threshold:
                cv2.rectangle(frame, (cord[0], cord[1]), (cord[2], cord[3]), (0, 255, 0), 2)
                break
        j += 1

    return frame