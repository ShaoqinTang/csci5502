import csv
import os
import Robert_Werthman_HW2


fileContent = [
		("date","close","volume","open","high","low"),
		("2016/01/28","94.0900","55622370.0000","93.7900","94.5200","92.3900"),
		("2016/01/27","93.4200","133059000.0000","96.0400","96.6289","93.3400")
]

def CreateTestFile():
	'''
	Source: https://pymotw.com/2/csv/
	'''
	f = open('test1.csv', 'w')
	writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
	writer.writerows(fileContent)
	f.close()

def RemoveTestFile(filePath):
	os.remove(filePath)

def ReadInAttributeFromCSVTest(filename):
	l = Robert_Werthman_HW2.ReadInAttributeFromCSV(filename, 'close')
	test("ReadInAttributeFromCSVTest1",(l == [float("94.0900"),float("93.4200")]))

	l = Robert_Werthman_HW2.ReadInAttributeFromCSV(filename, 'volume')
	test("ReadInAttributeFromCSVTest2",(l == [float("55622370.0000"),float("133059000.0000")]))


def test(testName, bool):
	if bool:
		print testName + " Passed."
	else:
		print testName + " Failed."

def main():
	CreateTestFile()
	ReadInAttributeFromCSVTest('test1.csv')
	RemoveTestFile('test1.csv')

if __name__ == "__main__":
	main()