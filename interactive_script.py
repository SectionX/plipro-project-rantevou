class Test:

    def __init__(self):
        self.data = [[1, 2, 3, 4], [5, 6, 7, 8]]

    def __iter__(self, start):
        return self.__next__(start)

    def __next__(self, start):
        index = 0
        for list in self.data:
            for item in list:
                index += 1
                if index < start:
                    continue
                yield item


test = Test()
for item in test:
    print(item)
