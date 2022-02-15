import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog,QTableWidgetItem,QHeaderView
from PyQt5 import uic, QtWidgets
import pandas as pd
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory  # library stemming
import re  # library regex cleaning data
import unidecode
from nltk.corpus import stopwords  # stopwords
from nltk.tokenize import word_tokenize  # library tokenizing
from normalisasibhs import normalisasi
from slangword import slangwords

class MyApp(QMainWindow):

    def __init__(self):
        global df
        self.df = pd.DataFrame()
        super().__init__()
        uic.loadUi("preprocessing.ui",self)
        self.progressBar.setValue(0)
        self.preprocessingbtn.setEnabled(False)
        self.actionSave.setEnabled(False)
        self.actionOpen.triggered.connect(self.getFileNames)
        self.actionSave.triggered.connect(self.savefile)
        self.tambahDatabtn.clicked.connect(self.addItem)
        self.preprocessingbtn.clicked.connect(self.preprocessing)

    def addItem(self):
        radiobuttons = str(self.find_checked_radiobutton(self.labelGroupBox.findChildren(QtWidgets.QRadioButton)))
        text = str(self.textEdit.toPlainText())
        if ((len(text) != 0) and (len(radiobuttons) != 0)):
            self.df2 = pd.DataFrame({'kalimat':  {0: text},'label':{0: radiobuttons}})
            if (len(self.df.index) == 0):
                self.df = self.df2
            else:
                self.df = self.df.append(self.df2, ignore_index=True)
            self.updateTable()
            self.preprocessingbtn.setEnabled(True)
            self.actionSave.setEnabled(True)
        #print(self.df)
    def find_checked_radiobutton(self, radiobuttons):
        for items in radiobuttons:
            if items.isChecked():
                checked_radiobutton = items.text()
                return checked_radiobutton

    def updateTable(self):
        nRows, nColumns = self.df.shape
        self.tableWidget.setColumnCount(nColumns)
        self.tableWidget.setRowCount(nRows)

        self.tableWidget.setHorizontalHeaderLabels((self.df.columns))
        #self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for i in range(self.tableWidget.rowCount()):
            for j in range(self.tableWidget.columnCount()):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(self.df.iloc[i, j])))

    def savefile(self):
        file_filter = 'Excel File (*.xlsx)'
        response = QFileDialog.getSaveFileName(
            parent=self,
            caption='Save',
            directory='C:/Users/GL63-8SE-087ID/Desktop/Code/Mining IG/instaloader/komentar',
            filter=file_filter,
            initialFilter='Excel File (*.xlsx)'
        )
        path = response[0]
        if(len(self.df.index) != 0):
            self.df.to_excel(path,index=None, engine='openpyxl')
    def getFileNames(self):

        file_filter = 'Excel File (*.xlsx)'
        response = QFileDialog.getOpenFileNames(
            parent=self,
            caption='Select a data file',
            directory='C:/Users/GL63-8SE-087ID/Desktop/Code/Mining IG/instaloader/komentar',
            filter=file_filter,
            initialFilter='Excel File (*.xlsx)'
        )
        for path in response[0]:
            #print(path)
            temporary = pd.read_excel(path, engine='openpyxl')
            temporary.kalimat = temporary.kalimat.astype(str)
            if (len(temporary.index) == 0):
                self.df = temporary
            else:
                self.df = self.df.append(temporary, ignore_index=True)
            self.updateTable()
            self.preprocessingbtn.setEnabled(True)
            self.actionSave.setEnabled(True)
        #print(self.df)

    def preprocessing(self):
        self.progressBar.setValue(0)
        count = 0

        datakalimat = self.df['kalimat']

        # casefolding lowercase

        hasilcasefold = []
        for kalimat in datakalimat:
            proses = self.CaseFold(kalimat)
            hasilcasefold.append(proses)

        self.df['casefolding'] = hasilcasefold

        # cleaning

        hasilcleaning = []
        for kalimat in hasilcasefold:
            proses = self.Cleaning(kalimat)
            hasilcleaning.append(proses)

        self.df['cleaning'] = hasilcleaning

        hasilnormalisasi = []
        for kalimat in hasilcleaning:
            proses = normalisasi(kalimat)
            hasilnormalisasi.append(proses)

        self.df['normalisasi'] = hasilnormalisasi

        hasilslangword = []
        for kalimat in hasilnormalisasi:
            proses = slangwords(kalimat)
            hasilslangword.append(proses)

        self.df['slangword'] = hasilslangword

        self.df.drop_duplicates(subset='slangword', keep='first', inplace=True)  # menghapus duplikasi data
        index_names = self.df[self.df['slangword'] == "nan"].index  # mencari index dari dataframe kosong
        self.df.drop(index_names, inplace=True)  # menghapus dataframe yg kosong setelah slangword

        hasilslangword = self.df['slangword']
        jumlahdata = len(self.df.index)

        self.progressBar.setMaximum(jumlahdata)

        # stemming

        hasilstemming = []
        for kalimat in hasilslangword:
            proses = self.StemmingBahasa(kalimat)
            hasilstemming.append(proses)
            count += 1
            self.progressBar.setValue(count)

        self.df['stemming'] = hasilstemming

        # proses stopword removal

        hasilstopwords = []
        for kalimat in hasilstemming:
            proses = self.StopwordsRemove(kalimat)
            hasilstopwords.append(proses)

        self.df['stopwords'] = hasilstopwords
        index_names = self.df[~self.df['stopwords'].astype(bool)].index  # mencari index dari dataframe kosong
        self.df.drop(index_names, inplace=True) # hapus index dataframe kosong setelah stopwords removal
        #print(self.df)
        self.df = pd.concat([self.df.loc[self.df['label'] == l].sample(self.df.label.value_counts().min()) for l in self.df.label.unique()])  # menyamakan jumlah spam dan not spam
        #print(self.df)
        self.updateTable()

    def CaseFold(self, kalimat):
        kalimat = kalimat.lower()
        return kalimat

    def Cleaning(self, kalimat):
        kalimat = re.sub('@[^\s]+', ' ', kalimat)  # menghapus username
        kalimat = re.sub('#[^\s]+', ' ', kalimat)  # menghapus hashtag
        kalimat = re.sub('((www\.[^\s]+)|(https?://[^\s]+))|([^\s]+\.com)', ' ', kalimat)  # menghapus url
        kalimat = re.sub('\d', '', kalimat)  # menghapus angka
        kalimat = re.sub('_', ' ', kalimat)  # menghapus undescore
        kalimat = unidecode.unidecode(kalimat)  # mengganti accented character menjadi normal character
        kalimat = re.sub('\W', ' ', kalimat)  # menghapus selain [A-Z a-z 0-9 _]
        kalimat = " ".join(kalimat.split())  # menghilangkan spasi berlebih
        kalimat = re.sub(r"(.)\1+", r"\1", kalimat)  # menghapus duplicate string
        kalimat = re.sub(r"(\b\S\b)", '', kalimat)  # menghapus kata dengan 1 huruf
        return kalimat

    def StemmingBahasa(self, sentence):
        stemmerfactory = StemmerFactory()
        stemmer = stemmerfactory.create_stemmer()
        kalimat = stemmer.stem(sentence)
        return kalimat

    def StopwordsRemove(self, sentence):
        additional = ['ah', 'ber', 'nya', 'ny', 'nyah', 'kan', 'ya', 'yh', 'yah', 'iyah', 'yuk', 'loh', 'oh', 'deh',
                      'dong', 'dll','lho', 'kakak', 'kok', 'mu']
        datastopwords = set().union(stopwords.words("Indonesian"), additional)
        kata = word_tokenize(sentence)  # tokenizing
        kalimat_baru = []
        for w in kata:
            if w not in datastopwords:
                kalimat_baru.append(w)
        return kalimat_baru

if __name__ == '__main__':
    app = QApplication(sys.argv)

    myApp = MyApp()
    myApp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')