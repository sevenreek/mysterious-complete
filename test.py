class DataSource():
    def __init__(self, value):
        self.value = value

class Data():
    def __init__(self, datasource:DataSource):
        self.datasource = datasource
    @property
    def value(self):
        return self.datasource.value
    @value.setter
    def value(self, value):
        self.datasource.value = value

ds = DataSource('hello')
d = Data(ds)
print(d.value)
ds.value = 'world'
print(vars(d))