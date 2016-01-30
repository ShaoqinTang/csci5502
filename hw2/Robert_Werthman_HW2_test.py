import csv
import os
import Robert_Werthman_HW2


fileContent1 = [
		("date","close","volume","open","high","low"),
		("2016/01/28","94.0900","55622370.0000","93.7900","94.5200","92.3900"),
		("2016/01/27","93.4200","133059000.0000","96.0400","96.6289","93.3400")
]

fileContent2 = [
		("date","close","volume","open","high","low"),
		("2016/01/28","94.0900","55622370.0000","93.7900","94.5200","73600"),
		("2016/01/27","93.4200","133059000.0000","96.0400","96.6289","98000"),
		("2016/01/27","93.4200","133059000.0000","96.0400","96.6289","12000")
]

fileContent3 = [
		("date","close","volume","open","high","low"),
		("2016/01/28","94.0900","55622370.0000","93.7900","94.5200","1"),
		("2016/01/27","93.4200","133059000.0000","96.0400","96.6289","2"),
		("2016/01/27","93.4200","133059000.0000","96.0400","96.6289","3")
]

def Min_MaxTest(filename):
	l = Robert_Werthman_HW2.ReadInAttributeFromCSV(filename, 'low')
	l = Robert_Werthman_HW2.Min_Max(l)
	test("Min_MaxTest1", (l == [(float(73600),float(0.7162790697674418)),(float(98000),float(1)),(float(12000),float(0))]))

def Z_ScoreTest(filename):
	l = Robert_Werthman_HW2.ReadInAttributeFromCSV(filename, 'low')
	#l = Robert_Werthman_HW2.Z_Score(l)
	print Robert_Werthman_HW2.Mean(l)
	print Robert_Werthman_HW2.StandardDeviation(l, Robert_Werthman_HW2.Mean(l))
	#test("Z_ScoreTest1", (l == [(float(54000),float(0)),(float(73600),float(0)),(float(16000),float(0))]))

def ReadInAttributeFromCSVTest(filename):
	l = Robert_Werthman_HW2.ReadInAttributeFromCSV(filename, 'close')
	test("ReadInAttributeFromCSVTest1",(l == [float("94.0900"),float("93.4200")]))

	l = Robert_Werthman_HW2.ReadInAttributeFromCSV(filename, 'volume')
	test("ReadInAttributeFromCSVTest2",(l == [float("55622370.0000"),float("133059000.0000")]))

	l = Robert_Werthman_HW2.ReadInAttributeFromCSV(filename, 'date')
	test("ReadInAttributeFromCSVTest3",(l == 1))

def CreateTestFile(filename, filecontent):
	'''
	Source: https://pymotw.com/2/csv/
	'''
	f = open(filename, 'w')
	writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
	writer.writerows(filecontent)
	f.close()

def RemoveTestFile(filePath):
	os.remove(filePath)

def test(testName, bool):
	if bool:
		print testName + " Passed."
	else:
		print testName + " Failed."

def main():
	CreateTestFile('test1.csv', fileContent1)
	ReadInAttributeFromCSVTest('test1.csv')
	CreateTestFile('test2.csv', fileContent2)
	Min_MaxTest('test2.csv')
	CreateTestFile('test3.csv', fileContent3)
	Z_ScoreTest('test3.csv')

	RemoveTestFile('test1.csv')
	RemoveTestFile('test2.csv')
	RemoveTestFile('test3.csv')

if __name__ == "__main__":
	main()