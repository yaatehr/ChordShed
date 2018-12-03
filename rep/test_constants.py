from math import sqrt
from kivy.core.window import Window



kTotalArea = Window.height * Window.width
kSquareLen = sqrt(kTotalArea)


kGemRingRadius = kSquareLen * .1
kGemRingWidth = kGemRingRadius * .2
kGemRingColor = (1,1,0)
kGemRingHit = (0,1,0)
kGemRingMiss = (1,.2,.5)

kGemCircleSize = (2 * kGemRingRadius - kGemRingWidth,) * 2
kGemCircleColor = (1,1,1)

