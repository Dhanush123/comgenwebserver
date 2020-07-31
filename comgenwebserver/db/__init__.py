class Repository(object):
    def __init__(self, adapter=None):
        self.client = adapter()

    def find_all(self, selector):
        return self.client.find_all(selector)

    def find(self, selector):
        return self.client.find(selector)

    def create(self, comgen):
        return self.client.create(comgen)

    def update(self, selector, comgen):
        return self.client.update(selector, comgen)

    def delete(self, selector):
        return self.client.delete(selector)
