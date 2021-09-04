class Screen:
    state = None
    skip_input = False
    required_fields = []

    def __init__(self, data, errors=None, context=None):
        assert self.state
        self.data = data
        # check whether all required fields are filled
        self.check_fields()
        self.errors = errors
        self.context = context

    def check_fields(self):
        if self.data is None:
            self.data = {}
        for field in self.required_fields:
            if field not in self.data.keys():
                raise Exception("{} field must be in screen data".format(field))

    def render(self):
        """renders the screen UI """
        raise NotImplementedError("render must be implemented ")

    def next_screen(self, current_input):
        """gets the next screen based on current input"""
        return None

    def error_screen(self, errors):
        self.errors = errors
        return self

    def set_context(self, context):
        self.context = context
