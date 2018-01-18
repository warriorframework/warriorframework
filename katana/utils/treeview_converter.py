class TreeviewConverter:

    def __init__(self, json_data):
        self.original_data = json_data
        self.converted_data = []

    def convert(self):
        return self.original_data

    @staticmethod
    def _create_node(text, icon="glyphicon glyphicon-stop"):
        node = {
            "text": text,
            "icon": icon,
            "selectedIcon": icon,
            "color": "#000000",
            "backColor": "#FFFFFF",
            "href": "#node-1",
            "selectable": True,
            "state": {
                "checked": True,
                "disabled": True,
                "expanded": True,
                "selected": True
            },
            "tags": ["available"],
            "nodes": []
        }
        return node