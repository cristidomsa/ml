from random import normalvariate
from scipy.misc import imread, imsave

import matplotlib.pyplot as plt
import numpy as np
import inspect

class RandomizeDistort():

    def __init__(self, sizex, sizey, incline=True, distort=True):
        
        self.yPoint = lambda x1,x2,y1,m: int(round(m*(x2-x1) + y1))
        self.yDiff = lambda y1,y2: y1-y2

        self.slope = lambda x1,x2,y1,y2: (y2-y1)/((x2-x1)*1.000)

        self.yIntersect = lambda x1,x2,y1,y2,m1,m2: int(round(((m2*(x1-y1/m1-m2*x2) + y2))/(1-m2/m1)))
        self.xIntersect = lambda x1,y1,y2,m: int(round((y2-y1)/m + x1))

        self.coef_distance = lambda s: self.size_y*1.000/s
        self.coef_weight = lambda s: s*1.000/self.size_x

        self.size_x, self.size_y = (sizex, sizey)

        #TODO: randomize slides
        self.slides = 9

        self.interval = self.size_y / self.slides

        self.x_values = [0]
        self.y_values = [self.size_x]

        self.top_distort = ()
        self.bottom_distort = ()

        #TODO: randomize angle
        self.anglepos = 0.098

        #TODO: randomize incline
        self.incline = 50

        self.mask = []

        self.result = []

    #TODO: create randomize function for basic values
    def _randomize(self, weight=1):
        pass

    def _normalize(self):

        for i,_ in enumerate(self.y_values): self.y_values[i] -= min(self.y_values)

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
    
    def _randomizeDistort(self):

        #TODO: randomize angles
        self.top_distort = (0,self.size_x, -0.060)
        self.bottom_distort = (0,min(self.y_values),0.020)

    def _distort(self):
        
        x1,y1,m1 = self.top_distort
        x2,y2,m2 = self.bottom_distort

        for i in range(0, len(self.y_values)/2):
            self.y_values[i] -= self.yDiff(self.size_x, self.yPoint(x1, self.x_values[i], y1, m1))
        
        for i in range(len(self.y_values)/2, len(self.y_values)):
            self.y_values[i] += self.yDiff(self.yPoint(x2, self.x_values[i], y2, m2), 0)

    def _mirrorPoints(self):

        self.x_values.extend([xval for xval in self.x_values])
        self.y_values.extend([yval-self.size_x for yval in self.y_values])

    def _incline(self):
        
        step = self.size_y / self.incline
        
        for i, x in enumerate(self.x_values):
            self.y_values[i] += x/step

    #TODO:
    def _compute_coef(self):
        pass
    
    def _fillLine(self, x, top_px, bottom_px):
        for y in range(bottom_px, top_px):
            self.mask[y][x] = 0

    def _fillSegment(self, index):

        x1, x2, y1, y2 = self.x_values[index-1], \
                         self.x_values[index], \
                         self.y_values[index-1], \
                         self.y_values[index]

        x3, x4, y3, y4 = self.x_values[self.slides+index-1],\
                         self.x_values[self.slides+index], \
                         self.y_values[self.slides+index-1], \
                         self.y_values[self.slides+index]

        top_slope = self.slope(x1,x2,y1,y2)
        bottom_slope = self.slope(x3,x4,y3,y4)

        for x in range(x1, x2):
            top_px = self.yPoint(x1, x, y1, top_slope)
            bottom_px = self.yPoint(x3, x, y3, bottom_slope)
            self._fillLine(x, top_px, bottom_px)

    def _fillMask(self):
        
        self.mask = np.zeros([max(self.y_values), max(self.x_values), 4], dtype=np.uint8)
        self.mask.fill(255)

        segment = 1
        while segment < self.slides:
            self._fillSegment(segment)
            segment +=1
            
        imsave("matrix.png",self.mask)

    #TODO: create generator (yield)
    def compute(self):
        self._randomizeXPoints()
        self._randomizeYPoints()
        self._mirrorPoints()

        if min(self.y_values) < 0: self._normalize()

        self._randomizeDistort()
        self._distort()

        if min(self.y_values) < 0: self._normalize()

        self._incline()

        if min(self.y_values) < 0: self._normalize()

        self._fillMask()

    def generate(self, source):

        ind_x = 0
        for i in range(0, len(self.mask[0]) - 1):
            ind_y = 0
            for j in range(0, len(self.mask) - 1):
                try:
                    if self.mask[j][i].all() == 0:
                        self.mask[j][i] = source[ind_y][ind_x]
                        ind_y += 1
                except Exception:
                    pass
            ind_x +=1
        
        imsave('result.png', self.mask)

    def display(self, var='values'):

        print 'caller name --->', inspect.stack()[1][3]

        print 'size:', self.size_x, '*', self.size_y
        print 'last', self.y_values[len(self.y_values)/2 - 1] - self.y_values[-1]
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
            print 'coef (distance, weight)', self.coef_distance(x3), self.coef_weight(y3)
            plt.plot([x1, x3], [y1, y3], 'ro-')
            plt.plot([x2, x3], [y2, y3], 'ro-')
            #guidelines
            plt.plot([0, x3], [y3, y3], 'ro-')
            plt.plot([self.size_y, self.size_y], [0, self.size_x], 'go-')
            plt.show()

        if var == 'plot':
            plt.plot(self.x_values, self.y_values, 'ro')
            plt.show()

if __name__ == "__main__":
    
    bar = imread('input.png')
    
    c = RandomizeDistort(len(bar), len(bar[0]))
    c.compute()
    c.generate(bar)