from pipeline_abilities.find_item import FindItem
from pipeline_abilities.find_color import FindColor


class CreatePipeline:
    def __init__(self, pipeline, root, pipeline_name):

        self.pipeline_sequence = pipeline
        self.pipeline_name = pipeline_name
        self.root = root

        self.terminal()

    def terminal(self):
        for action in self.pipeline_sequence:
            if action == 'Find item':
                FindItem(self.pipeline_name, self.root)
                continue
            elif action == 'Find color':
                FindColor(self.pipeline_name, self.root)
                continue
