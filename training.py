import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
import time
from sklearn.metrics import confusion_matrix,accuracy_score
import joblib

class MyApp(QMainWindow):

    def __init__(self):
        global dataset
        super().__init__()
        uic.loadUi("training.ui",self)
        self.klasifikasibtn.setEnabled(False)
        self.actionOpen.triggered.connect(self.getFileNames)
        self.klasifikasibtn.clicked.connect(self.training)

    def getFileNames(self):

        file_filter = 'Excel File (*.xlsx)'
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select a data file',
            directory='C:/Users/GL63-8SE-087ID/Desktop/Code/Mining IG/instaloader/komentar',
            filter=file_filter,
            initialFilter='Excel File (*.xlsx)')
        if len(response[0])!= 0:
            self.dataset = pd.read_excel(response[0], engine='openpyxl')
            self.klasifikasibtn.setEnabled(True)

    def confussionMatrix(self, aktual, prediksi):
        tp = sum((aktual == "spam") & (prediksi == "spam"))
        tn = sum((aktual == "not spam") & (prediksi == "not spam"))
        fn = sum((aktual == "not spam") & (prediksi == "spam"))
        fp = sum((aktual == "spam") & (prediksi == "not spam"))

        return tp, tn, fp, fn

    def hitungAkurasi(self, tp, tn, fn, fp):
        return ((tp + tn) / float(tp + tn + fn + fp)) * 100

    def training(self):
        X_train, X_test, Y_train, Y_test = train_test_split(self.dataset['stopwords'], self.dataset['label'], test_size=0.2,
                                                            random_state=42)
        # membuat feature vectors
        vectorizer = TfidfVectorizer(min_df=5,
                                     max_df=0.8,
                                     use_idf= True,
                                     smooth_idf= False,
                                     # norm= None,
                                     lowercase=False,
                                     ngram_range=(1, 1))

        train_vectors = vectorizer.fit_transform(X_train)
        test_vectors = vectorizer.transform(X_test)

        # print(train_vectors[0])
        classifier_linear = svm.SVC(kernel='linear',C=1)
        t0 = time.time()
        classifier_linear.fit(train_vectors, Y_train)

        prediction_linear_training = classifier_linear.predict(train_vectors)
        t1 = time.time()
        prediction_linear_testing = classifier_linear.predict(test_vectors)
        t2 = time.time()
        time_linear_train = t1 - t0
        time_linear_predict = t2 - t1

        #cm = confusion_matrix(Y_test, prediction_linear_testing)
        #tp, tn, fp, fn = self.confussionMatrix(Y_test, prediction_linear_testing)
        #print(cm)
        #print(self.hitungAkurasi(tp, tn, fp, fn))


        self.akurasiTrainingSVM.setText('{:.2f}% '.format(accuracy_score(Y_train, prediction_linear_training) * 100))
        self.akurasiTestingSVM.setText('{:.2f}% '.format(accuracy_score(Y_test, prediction_linear_testing) * 100))
        self.traintimeSVM.setText('%fs'% time_linear_train)
        self.testtimeSVM.setText('%fs' % time_linear_predict)

        joblib.dump(vectorizer, 'vectorizer.sav')
        joblib.dump(classifier_linear, 'svm_model.sav')

        MNB = MultinomialNB(alpha=1)
        t0 = time.time()
        MNB.fit(train_vectors.toarray(), Y_train)

        prediction_MNB_training = MNB.predict(train_vectors.toarray())
        t1 = time.time()
        prediction_MNB_testing = MNB.predict(test_vectors.toarray())
        t2 = time.time()
        time_MNB_train = t1 - t0
        time_MNB_predict = t2 - t1

        #cm = confusion_matrix(Y_test, prediction_MNB_testing)
        # tp, tn, fp, fn = self.confussionMatrix(Y_test, prediction_MNB_testing)
        # print(self.hitungAkurasi(tp, tn, fp, fn))
        #print(cm)
        self.akurasiTrainingNB.setText('{:.2f}% '.format(accuracy_score(Y_train, prediction_MNB_training) * 100))
        self.akurasiTestingNB.setText('{:.2f}% '.format(accuracy_score(Y_test, prediction_MNB_testing) * 100))
        self.traintimeNB.setText('%fs' % time_MNB_train)
        self.testtimeNB.setText('%fs' % time_MNB_predict)

        # review = 'mutih wajah cek ig'
        # review_vector = vectorizer.transform([review])  # vectorizing
        # print(classifier_linear.predict(review_vector))
        joblib.dump(MNB, 'nb_model.sav')

if __name__ == '__main__':
    app = QApplication(sys.argv)

    myApp = MyApp()
    myApp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')