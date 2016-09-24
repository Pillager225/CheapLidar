# utility functions

def clampToRange(self, x, lower, upper):
		if x < lower:
			return lower
		elif x > upper:
			return upper
		else:
			return x

# maps x which is in the range of in_min to in_max to x's corresponding
# value between out_min and out_max
def transform(self, x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
