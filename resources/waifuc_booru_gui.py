import sys
import os
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton, QFileDialog, QSpinBox, QMessageBox, QCompleter
from PyQt5.QtCore import QSettings, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from waifuc.action import NoMonochromeAction, FilterSimilarAction, TaggingAction, PersonSplitAction, FaceCountAction, FirstNSelectAction, CCIPAction, ModeConvertAction, ClassFilterAction, RandomFilenameAction, AlignMinSizeAction
from waifuc.export import TextualInversionExporter
from waifuc.source import DanbooruSource, GelbooruSource

class MultiWordCompleter(QCompleter):
    def __init__(self, *args, **kwargs):
        super(MultiWordCompleter, self).__init__(*args, **kwargs)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterMode(Qt.MatchContains)
        self.setCompletionMode(QCompleter.PopupCompletion)

    def pathFromIndex(self, index):
        path = QCompleter.pathFromIndex(self, index)
        words = self.widget().text().split()
        if len(words) > 1:
            path = f"{' '.join(words[:-1])} {path}"
        return path

    def splitPath(self, path):
        words = path.split()
        if len(words) > 1:
            return [words[-1]]
        return [path]

class CrawlerThread(QThread):
    finished = pyqtSignal()

    def __init__(self, source, search_term, resize_size, enable_tagging, max_count, output_path):
        QThread.__init__(self)
        self.source = source
        self.search_term = search_term
        self.resize_size = resize_size
        self.enable_tagging = enable_tagging
        self.max_count = max_count
        self.output_path = output_path

    def run(self):
        s = self.source([self.search_term])
        s.attach(
            ModeConvertAction('RGB', 'white'),
            FilterSimilarAction('all'),
            AlignMinSizeAction(self.resize_size),
            TaggingAction(force=self.enable_tagging),
            FilterSimilarAction('all'),
            FirstNSelectAction(self.max_count),
            RandomFilenameAction(ext='.png'),
        ).export(
            TextualInversionExporter(self.output_path)
        )
        self.finished.emit()

class WaifucGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadSettings()
        self.crawler_thread = None
        self.loadAutoCompleteData()

    def initUI(self):
        layout = QVBoxLayout()

        # 1. Source selection
        self.source_combo = QComboBox()
        self.source_combo.addItems(['Danbooru', 'Gelbooru'])
        self.source_combo.currentTextChanged.connect(self.onSourceChanged)
        layout.addWidget(QLabel('Source:'))
        layout.addWidget(self.source_combo)

        # 2. Search term with autocomplete
        self.search_term = QLineEdit()
        self.completer = MultiWordCompleter()
        self.search_term.setCompleter(self.completer)
        layout.addWidget(QLabel('Search Term:'))
        layout.addWidget(self.search_term)

        # 3. Resize size
        self.resize_size = QSpinBox()
        self.resize_size.setRange(100, 10000)
        self.resize_size.setValue(1500)
        layout.addWidget(QLabel('Resize Size:'))
        layout.addWidget(self.resize_size)

        # 4. Tagging checkbox
        self.tagging_checkbox = QCheckBox('Enable Tagging')
        self.tagging_checkbox.setChecked(True)
        layout.addWidget(self.tagging_checkbox)

        # 5. Max crawling count
        self.max_count = QSpinBox()
        self.max_count.setRange(1, 1000)
        self.max_count.setValue(200)
        layout.addWidget(QLabel('Max Crawling Count:'))
        layout.addWidget(self.max_count)

        # 6. Output path
        self.output_path = QLineEdit()
        self.browse_button = QPushButton('Browse')
        self.browse_button.clicked.connect(self.browseFolder)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.output_path)
        path_layout.addWidget(self.browse_button)
        layout.addWidget(QLabel('Output Path:'))
        layout.addLayout(path_layout)

        # Start button
        self.start_button = QPushButton('Start Crawling')
        self.start_button.clicked.connect(self.startCrawling)
        layout.addWidget(self.start_button)

        # Progress info
        layout.addWidget(QLabel('Note: You can check the progress bar in the command prompt window.'))

        self.setLayout(layout)
        self.setWindowTitle('Waifuc Crawler GUI')
        self.show()

    def loadAutoCompleteData(self):
        model = QStandardItemModel()
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'danbooru.csv')
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:  # skip empty rows
                        item = QStandardItem(row[0])
                        model.appendRow(item)
        except FileNotFoundError:
            print(f"Warning: {csv_path} not found. Autocomplete feature will not work.")
        except Exception as e:
            print(f"Error loading CSV file: {e}")

        self.completer.setModel(model)

    def browseFolder(self):
        current_path = self.output_path.text()
        start_path = current_path if os.path.isdir(current_path) else os.path.expanduser("~")
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", start_path)
        if folder:
            self.output_path.setText(folder)

    def loadSettings(self):
        settings = QSettings('WaifucCrawler', 'Settings')
        self.source_combo.setCurrentText(settings.value('source', 'Danbooru'))
        self.search_term.setText(settings.value('search_term', ''))
        self.resize_size.setValue(int(settings.value('resize_size', 1500)))
        self.tagging_checkbox.setChecked(settings.value('enable_tagging', 'true') == 'true')
        self.max_count.setValue(int(settings.value('max_count', 200)))
        self.output_path.setText(settings.value('output_path', ''))

    def saveSettings(self):
        settings = QSettings('WaifucCrawler', 'Settings')
        settings.setValue('source', self.source_combo.currentText())
        settings.setValue('search_term', self.search_term.text())
        settings.setValue('resize_size', self.resize_size.value())
        settings.setValue('enable_tagging', str(self.tagging_checkbox.isChecked()).lower())
        settings.setValue('max_count', self.max_count.value())
        settings.setValue('output_path', self.output_path.text())

    def onSourceChanged(self, source):
        if source == 'Danbooru':
            self.search_term.setMaxLength(1000)  # Approximate limit for two words
        else:
            self.search_term.setMaxLength(32767)  # Default max length

    def startCrawling(self):
        self.saveSettings()
        
        if not self.output_path.text():
            QMessageBox.warning(self, 'Warning', 'Please select an output path.')
            return

        source = DanbooruSource if self.source_combo.currentText() == 'Danbooru' else GelbooruSource
        
        if self.source_combo.currentText() == 'Danbooru' and len(self.search_term.text().split()) > 2:
            QMessageBox.warning(self, 'Warning', 'For Danbooru, please use a maximum of 2 words for the search term.')
            return

        self.start_button.setEnabled(False)
        self.crawler_thread = CrawlerThread(
            source,
            self.search_term.text(),
            self.resize_size.value(),
            self.tagging_checkbox.isChecked(),
            self.max_count.value(),
            self.output_path.text()
        )
        self.crawler_thread.finished.connect(self.onCrawlingFinished)
        self.crawler_thread.start()

    def onCrawlingFinished(self):
        self.start_button.setEnabled(True)
        QMessageBox.information(self, 'Information', 'Crawling completed!')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WaifucGUI()
    sys.exit(app.exec_())