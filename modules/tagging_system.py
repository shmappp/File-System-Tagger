import utils.json_util as json_util

class TaggingSystem:
    def __init__(self, tag_json):
        self.tag_json = tag_json
        self.tags = json_util.load_data(tag_json)
    
    def get_tags(self, path):
        return self.tags.get(path, [])

    def set_tags(self, path, tags):
        self.tags[path] = tags
        self.save_tags()
    
    def save_tags(self):
        json_util.save_data(self.tags, self.tag_json)