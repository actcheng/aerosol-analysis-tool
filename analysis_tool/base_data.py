import pickle

class Data():
    def __init__(self):
        pass

    def load_pickle(self,pickle_name):
        with open(pickle_name, "rb") as output_file:
            self.__dict__.update(pickle.load(output_file).__dict__)
        print(f'Data loaded from {pickle_name}')

    def save_pickle(self,pickle_name):
        with open(pickle_name, "wb") as output_file:
            pickle.dump(self, output_file)
        print(f'Data saved to {pickle_name}')

