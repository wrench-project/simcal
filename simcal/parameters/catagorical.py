from simcal.parameters.base import Base as BaseParameter


class Categorical(BaseParameter):
    def __init__(self, categories):
        super().__init__()
        self.categories = categories

    def get_categories(self):
        return self.categories
