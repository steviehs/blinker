# some constants DO NOT CHANGE
GT = 1  # greater than >
LT = 0  # less than <
DC = -1  # don't care

class ThreeAxis:
    def __init__(self,x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z


class SumBuffer:
    def __init__(self, size_max, filter_max=300):
        self.max = size_max
        self.data = []
        self.sum = 0
        self.cur = 0
        self.filter_max = filter_max
        for i in range(1, size_max + 1):
            self.data.append(0)

    def append(self, x):
        if abs(x) >= self.filter_max:
            x = 0
        # now for the fast part: we do not have to sum up but just alter the actual sum
        #print("cur: ",self.cur)
        self.sum = self.sum - self.data[self.cur]
        self.sum = self.sum + x
        self.data[self.cur] = x
        self.cur = int((self.cur + 1) % self.max)

    def getsum(self):
        """ Return a list of elements from the oldest to the newest. """
        return self.sum

    def compare_sum(self, comparator, trigger):
        if comparator == DC:
            return True
        if comparator == LT and sum(self.data) < trigger:
            return True
        if comparator == GT and sum(self.data) > trigger:
            return True
        return False


class ThreeAxisBuffer:
    def __init__(self, size_max, filter_x, filter_y, filter_z):
        self.buff_x = SumBuffer(size_max, filter_x)
        self.buff_y = SumBuffer(size_max, filter_y)
        self.buff_z = SumBuffer(size_max, filter_z)

    def append(self, object):
        self.buff_x.append(object.x)
        self.buff_y.append(object.y)
        self.buff_z.append(object.z)

    def getsum(self):
        return (self.buff_x.getsum(), self.buff_y.getsum(), self.buff_z.getsum())

    def compare_sum(self, xcomp, xtrig, ycomp, ytrig, zcomp, ztrig):
        return self.buff_x.compare_sum(xcomp, xtrig) \
               and self.buff_y.compare_sum(ycomp, ytrig) \
               and self.buff_z.compare_sum(zcomp, ztrig)

    def getstr(self, format):
        newformat = format + " " + format + " " + format
        return newformat % (self.buff_x.getsum(), self.buff_y.getsum(), self.buff_z.getsum())

# this is for testing the class
if __name__ == "__main__":
    mtb = ThreeAxisBuffer(10, 10, 10, 10)

    for i in range(1, 30):
        to = ThreeAxis(1.2,2.2,3.3)
        mtb.append(to)

    print(mtb.getstr("% 5.2f"))

    if mtb.compare_sum(GT,10,DC,0,DC,0):
        print("X > 10")

