#Assignment based on MAGIC Gamma Telescope Data Set ( http://archive.ics.uci.edu/ml/datasets/MAGIC+Gamma+Telescope )

import matplotlib.pyplot as plt
from numpy.random import rand

def splitData(data):
    '''
    Take each line of the data and split it into a 
    list delimited by a comma

    Creates a list of lists
    '''
    splitData = []
    for line in data:
        line = line.split(',')
        splitData.append(line)
    return splitData

def findIthData(data, ithAttribute):
    '''
    Go through the data and return a list 
    of the ith attribute for each line of the data
    '''
    ithData = []
    for line in data:
        line = line[ithAttribute-1]
        ithData.append(line)
    return ithData

def main():
	f = open("magic04.data.txt", 'r')
	data=f.readlines();
	f.close()


	# Split each line of the data delimited by a comma into a list
	data = splitData(data)

	# set the data to a list of the the 4th attribute of the data
	fourthData = findIthData(data,4)

	# set the data to a list of the the 5th attribute of the data
	fifthData = findIthData(data,5)


	# Convert each element in the data from a string to a float
	# Source: https://stackoverflow.com/questions/3371269/call-int-function-on-every-list-element-in-python
	fourthdData = [float(x) for x in fourthData]
	fifthdData = [float(x) for x in fifthData]

	# Plot the attributes as a scatter plot
	# Source: https://stackoverflow.com/questions/12444716/how-do-i-set-figure-title-and-axes-labels-font-size-in-matplotlib
	fig = plt.figure()
	plt.scatter(fourthData, fifthData)
	fig.suptitle('Scatter Plot of 4th vs 5th Attributes of Data Set')
	plt.xlabel("4th Attribute")
	plt.ylabel("5th Attribute")
	plt.grid(True)
	#plt.show()
	# Save plot as pdf
	# Source: http://matplotlib.org/faq/howto_faq.html#save-multiple-plots-to-one-pdf-file
	plt.savefig('Werthman_Robert_HW1.pdf', format='pdf')

    

if __name__ == "__main__":
    main()