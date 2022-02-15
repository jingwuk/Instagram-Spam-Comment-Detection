import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
import pandas as pd
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory  # library stemming
import re  # library regex cleaning data
import unidecode
from nltk.corpus import stopwords  # stopwords
from nltk.tokenize import word_tokenize  # library tokenizing
import joblib
from normalisasibhs import normalisasi
from slangword import slangwords


class MyApp(QMainWindow):

    def __init__(self):
        global df
        self.df = pd.DataFrame()
        super().__init__()
        uic.loadUi("testing.ui",self)
        self.preprocessingbtn.clicked.connect(self.preprocessing)
        self.testingbtn.clicked.connect(self.testing)

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

    def testing(self):

        vectorizer = joblib.load('vectorizer.sav')
        classifier_linear = joblib.load('svm_model.sav')
        review_vector = vectorizer.transform(self.df['stopwords'][0])
        self.hasilSVM.setText(classifier_linear.predict(review_vector)[0])

        MNB = joblib.load('nb_model.sav')
        self.hasilNB.setText(MNB.predict(review_vector)[0])

    def preprocessing(self):
        text = str(self.textEdit.toPlainText())
        if (len(text) != 0):
            self.df = pd.DataFrame({'kalimat':  {0: text}})

            datakalimat = self.df['kalimat']

            #casefolding lowercase

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

            # stemming

            hasilstemming = []
            for kalimat in hasilslangword:
                proses = self.StemmingBahasa(kalimat)
                hasilstemming.append(proses)

            self.df['stemming'] = hasilstemming

            # proses stopword removal

            hasilstopwords = []
            for kalimat in hasilstemming:
                proses = self.StopwordsRemove(kalimat)
                hasilstopwords.append(proses)

            self.df['stopwords'] = hasilstopwords
            self.updateTable()
            #print(self.df)

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