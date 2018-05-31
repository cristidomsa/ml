from random import normalvariate, vonmisesvariate
from scipy.misc import imread, imsave

import matplotlib.pyplot as plt
import numpy as np

class RandomizeDistort():

    def __init__(self, sizex, sizey, incline=True, distort=True):
        
        self.yPoint = lambda x1,x2,y1,m: int(round(m*(x2-x1) + y1))

        self.slope = lambda x1,x2,y1,y2: (y2-y1)/((x2-x1)*1.000)

        self.yIntersect = lambda x1,x2,y1,y2,m1,m2: int(round(((m2*(x1-y1/m1-m2*x2) + y2))/(1-m2/m1)))
        self.xIntersect = lambda x1,y1,y2,m: int(round((y2-y1)/m + x1))

        self.coef_distance = lambda s: s/self.size_y
        self.coef_weight = lambda s: s/self.size_x

        self.size_x, self.size_y = (sizex, sizey)

        #TODO: randomize slides
        self.slides = 10

        self.interval = self.size_y / self.slides

        self.x_values = [0]
        self.y_values = [self.size_x]

        self.top_distort = ()
        self.bottom_distort = ()

        #TODO: randomize angle
        self.anglepos = 0.098

        #TODO: randomize incline
        self.incline = 100

        self.fill = []

        self.matrix = None

    def _incline(self, index=0):

        step = self.size_y / index
        
        for el in self.x_values:
            self.y_values[self.x_values.index(el)] += el/step

    def _randomizeXPoints(self):

        #TODO: randomize slides
        self.x_values.extend([int(normalvariate(i/2, 100/self.slides)) for i in [100,300,500,700,900,1200,1500,1800]])

        self.x_values[-1] = self.size_y

    def _randomizeYPoints(self):

        i = 0
        while i < len(self.x_values) - 1:
            
            angle = self.anglepos if (i % 2 == 0) else -self.anglepos
            self.y_values.append(self.yPoint(self.x_values[i], self.x_values[i+1], self.y_values[i], angle))
            i+=1

        self._incline(index=self.incline)

        diff = self.size_x - min(self.y_values)

        for y in self.y_values: self.y_values[self.y_values.index(y)] += diff
    
    def _randomizeDistort(self):

        #TODO: randomize angles
        self.top_distort = (0,self.size_x, -0.090)
        self.bottom_distort = (0,min(self.y_values),0.020)

        self.display('distort')

    def _mirrorPoints(self):

        self.x_values.extend([xval for xval in self.x_values])
        self.y_values.extend([yval-self.size_x for yval in self.y_values])

    def _fillMask(self):

        for i in self.x_values:
            index = self.x_values.index(i)
            for j in range(self.y_values[len(self.y_values)/2 + index], self.y_values[index]):
                self.fill.append((i,j))
        
        x = self.x_values[0]+1
        for segment in range(1, len(self.x_values)/2):
            while x < self.x_values[segment]:
                x1 = self.x_values[segment-1]
                x2 = self.x_values[segment]
                y1 = self.y_values[segment-1]
                y2 = self.y_values[segment]
                slope = self.slope(x1, x2, y1, y2)

                for y in range(self.y_values[len(self.y_values)/2+segment-1], y1):
                    self.fill.append((x,self.yPoint(x1, x, y, slope)))
                x+=1
    
    def compute(self):
        self._randomizeXPoints()
        self._randomizeYPoints()
        self._mirrorPoints()

        self._randomizeDistort()

        self._fillMask()
        self.matrix = self.fillMatrix(incline=100)

    def fillMatrix(self, incline=0):

        foo = np.zeros([max(self.y_values) + incline, self.size_y +1, 4], dtype=np.uint8)
        foo.fill(255)

        for x,y in self.fill:
            foo[y,x] = 0
        
        imsave("Result.png",foo)
        return foo

    def display(self, var='values'):

        if var == 'values':
            print "X axis values: ", self.x_values
            print "y axis values: ", self.y_values

        if var == 'distort':
            print 'top->', self.top_distort
            x1,y1,m1 = self.top_distort
            print 'bottom->', self.bottom_distort
            x2,y2,m2 = self.bottom_distort
            y3 = self.yIntersect(x1,x2,y1,y2,m1,m2)
            x3 = self.xIntersect(x1,y1,y3,m1)
            print 'intersect->', x3, y3
            plt.plot([x1, x3], [y1, y3], 'ro-')
            plt.plot([x2, x3], [y2, y3], 'ro-')
            #guidelines
            plt.plot([0, x3], [y3, y3], 'ro-')
            plt.plot([self.size_y, self.size_y], [0, self.size_x], 'go-')
            plt.axis([0, x3+100, -450, 450])
            plt.show()

        if var == 'plot':
            plt.plot(self.x_values, self.y_values, 'ro')
            plt.axis([0, 700, 0, 150])
            plt.show()
        
        #plt.plot([x for x, _ in self.fill], [y for _, y in self.fill], 'ro')
        #plt.savefig("test.png")
        
    def generate(self, source):

        print self.size_x, '->', self.size_y

        ind_x = 0
        for i in range(0, len(self.matrix[0]) - 1):
            ind_y = 0
            for j in range(0, len(self.matrix) - 1):
                if self.matrix[j][i].all() == 0:
                    self.matrix[j][i] = source[ind_y][ind_x]
                    ind_y += 1
            ind_x +=1
        
        imsave('test_result.png', self.matrix)

if __name__ == "__main__":
    
    bar = imread('img_test.png')
    
    c = RandomizeDistort(len(bar), len(bar[0]))
    c.compute()
    c.generate(bar)

    #c.display()