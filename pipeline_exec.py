from pipeline_func import load_model, unload_model, return_cords, draw_rectangles, get_color_dif, get_main_colors_from_part_of_frame
import cv2
import json

class Pipeline:

    def __init__(self, pipeline_name):
        self.pipeline_name = pipeline_name
        self.seq = {}
        self.config = []
        self.models = []
        self.ethalon_color = None
        self.cords = None
        self.colors_count = None
        self.colors = None
        self.cap = cv2.VideoCapture(1)
        self.frame = None

        with open('pipelines/{}.json'.format(pipeline_name)) as f:
            root = json.loads(f.read())

            self.config = root['config']

            for row in root['sequence']:
                splitted_row = row.split(' ')
                key = splitted_row[0]
                value = splitted_row[1]
                self.seq[key] = value
        if 'models' in self.config:
            for model in self.config['models']:
                self.models.append(load_model(self.pipeline_name, model))
        if 'ethalon_color' in self.config:
            self.ethalon_color = self.config['ethalon_color']

    def execute(self):

        _, self.frame = self.cap.read()

        for key, value in self.seq.items():
            if key == 'get_cords':
                print("cords")
                self.cords = return_cords(self.models[int(value)], self.frame)
            elif key == 'get_colors':
                print("colors")
                self.colors = get_main_colors_from_part_of_frame(self.frame, self.cords, int(value))
                self.colors_count = int(value)
            elif key == 'draw_rects':
                print("rects")
                self.frame = draw_rectangles(int(value.split('_')[0]), int(value.split('_')[1]), self.ethalon_color, self.colors,
                                             self.colors_count, self.frame, self.cords)

    def get_frame(self):
        return self.frame
