from simcal.parameters.base import Base


class Categorical(Base):
    def __init__(self, categories):
        super().__init__()
        self.categories = categories

    def get_categories(self):
        return self.categories
