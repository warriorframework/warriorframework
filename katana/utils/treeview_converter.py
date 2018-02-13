class TreeviewConverter:

    def __init__(self, json_data):
        self.original_data = json_data
        self.converted_data = []

    def convert(self, element=None):
        converted_data = []
        if element is None:
            element = self.original_data
        if isinstance(element, dict):
            for key, value in element.iteritems():
                if key.startswith("@"):
                    key = key[1:]
                if isinstance(value, dict) or isinstance(value, list):
                    converted_data.append(self._create_node("{0}:".format(key)))
                    converted_data[len(converted_data) - 1]["nodes"] = []
                    if isinstance(value, dict):
                        for el, val in value.iteritems():
                            converted_data[len(converted_data)-1]["nodes"].extend(self.convert(element={el: val}))
                    elif isinstance(value, list):
                        count = -1
                        for el in value:
                            if key == "step":
                                converted_data[len(converted_data) - 1]["nodes"].append(self._create_node("{0}: {1}".format("TS", el["@TS"])))
                                count += 1
                                converted_data[len(converted_data) - 1]["nodes"][count]["nodes"] = []
                                converted_data[len(converted_data) - 1]["nodes"][count]["nodes"].extend(self.convert(element=el))
                            else:
                                new_node = self.convert(element=el)
                                if isinstance(new_node, list):
                                    converted_data[len(converted_data)-1]["nodes"].extend(new_node)
                                else:
                                    converted_data[len(converted_data) - 1]["nodes"].append(new_node)
                else:
                    converted_data.append(self._create_node("{0}: {1}".format(key, value)))
        elif isinstance(element, list):
            for el in element:
                converted_data.append(self.convert(element=el))
        else:
            converted_data = self._create_node("{0}".format(element))
        return converted_data

    @staticmethod
    def _create_node(text):
        """
        :param text:
        :param icon:
        :return:
        """
        node = {
            "text": text,
            "selectable": False,
            "color": "#000000",
            "backColor": "#FFFFFF"
        }
        return node
