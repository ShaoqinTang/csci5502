'''
(a) Temporal change of 'high' and 'low' attributes
(b) Boxplot for 'open' and 'close' attributes
(c) 10-bin equal-width histogram for 'volume' attribute 
(d) Any plot that interests you
'''
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime
import csv


pdf = PdfPages('Werthman_Robert_HW2.pdf')

def ReadInAttributeFromCSV(fileName, attribute):
	attributeValues = []
	f = open(fileName, 'r')
	# Create a csv reader that stores the each column of the first line of the file
	# as keys and then the rest of the lines of each column as values for those keys
	reader = csv.DictReader(f)
	for row in reader:
		if attribute in row:
			if attribute != 'date':
				value = float(row[attribute])
				attributeValues.append(value)
			else:
				date = datetime.datetime.strptime(row[attribute],'%Y/%m/%d')
				attributeValues.append(date)
	f.close()
	return attributeValues

def TemporalChange(filename):
	'''
	Source: https://stackoverflow.com/questions/1574088/plotting-time-in-python-with-matplotlib
	Source: http://matplotlib.org/users/pyplot_tutorial.html
	Source: http://matplotlib.org/faq/howto_faq.html
	Source: https://stackoverflow.com/questions/10824156/matplotlib-legend-location-numbers

	'''
	low = ReadInAttributeFromCSV(filename, 'low')
	high = ReadInAttributeFromCSV(filename, 'high')
	dates = ReadInAttributeFromCSV(filename, 'date')

	fig = plt.figure()
	low, = plt.plot(dates, low,'ro')
	high, = plt.plot(dates, high, 'bo')

	# rotate and align the tick labels so they look better
	fig.autofmt_xdate()

	plt.title('Low and High Attributes vs. Date')
	plt.xlabel('Date')
	plt.ylabel('Attribute Value')
	plt.legend(['Low Attribute', 'High Attribute'], loc=9, numpoints=1)
	plt.savefig(pdf,format='pdf')
	plt.close()

def main():
	TemporalChange('HD.csv')
	pdf.close()


if __name__ == '__main__':
	main()