class Screen:
    type = "CON"
    state = None
    required_fields = []

    def __init__(self, data, errors=None):
        if self.type not in ["CON", "END"]:
            raise ValueError("screen type must be either 'CON' or 'END' ")
        assert self.state
        self.data = data
        # check whether all required fields are filled
        self.check_fields()
        self.errors = errors

    def check_fields(self):
        for field in self.required_fields:
            if field not in self.data.keys():
                raise Exception("{} field must be in screen data".format(field))

    def render(self):
        """renders the screen UI """
        raise NotImplementedError("render must be implemented ")

    def next_screen(self, current_input):
        """gets the next screen based on current input"""
        if self.type == "END":
            pass
        raise NotImplementedError

    def error_screen(self, errors):
        self.errors = errors
        return self
