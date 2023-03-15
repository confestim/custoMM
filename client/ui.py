from PyQt5.QtWidgets import *

app = QApplication([])
w = QWidget()
w.resize(600,600)
w.setWindowTitle("custoMM")
w.show()
button = QPushButton(w)

def on_button_clicked():
    connector.start()
    alert = QMessageBox()
    alert.setText('You clicked the button!')
    alert.exec()

button.clicked.connect(on_button_clicked)
button.show()
app.exec()

