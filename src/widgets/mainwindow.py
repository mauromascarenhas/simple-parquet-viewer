import os
import typing
import numpy as np
import pandas as pd

from enum import Enum
from pathlib import Path

from PyQt6.QtGui import QIcon, QPixmap, QCloseEvent
from PyQt6.QtCore import (
    Qt, QObject, QThread, pyqtSignal, QDir, QSettings,
    QAbstractTableModel, QModelIndex, QSize, QTimer
)
from PyQt6.QtWidgets import (
    QMainWindow, QTableView, QWidget, QApplication, QToolBar,
    QVBoxLayout, QToolButton, QStatusBar, QVBoxLayout, QLabel,
    QProgressBar, QFileDialog, QMessageBox, QHBoxLayout, QLineEdit
)

APP_VERSION = (0, 9, 0)

def imgPath(fileName: str) -> str:
    return os.path.join(os.environ["SPV_SD_"], "res", "imgs", fileName)

class ExportType(Enum):
    CSV = 1
    JSON = 2
    PARQUET = 3

class TableModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame,parent: typing.Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._data = np.array(data.astype(str).values)
        self._cols = data.columns
        self.r, self.c = np.shape(self._data)

    def rowCount(self, parent: QModelIndex = None) -> int:
        return self.r

    def columnCount(self, parent: QModelIndex = None) -> int:
        return self.c

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> typing.Any:
        if index.isValid() and role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row(),index.column()]
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> typing.Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._cols[section]
            elif orientation == Qt.Orientation.Vertical:
                return section
        return None

class AsyncWorker(QObject):
    dfReady = pyqtSignal(pd.DataFrame, QObject)
    readFail = pyqtSignal()
    exportComplete = pyqtSignal()

    def readParquet(self, filePath: str) -> None:
        try:
            df = pd.read_parquet(filePath)
            self.dfReady.emit(df, self)
        except: self.readFail.emit()
    
    def exportFile(self, path: str, df: pd.DataFrame, type_: ExportType) -> None:
        if type_ == ExportType.CSV: df.to_csv(path, self.tr(",", "CSV Delimiter"), index = False)
        elif type_ == ExportType.JSON:
            with open(path, "r+") as f: df.to_json(f, "records")
        elif type_ == ExportType.PARQUET: df.to_parquet(path, "pyarrow", "snappy", False)
        self.exportComplete.emit()

class MainWindow(QMainWindow):

    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        args = QApplication.arguments()
        self.fp: typing.Optional[str] = args[1] if len(args) > 1 else None
        self.df: typing.Optional[pd.DataFrame] = None
        self.dfV: typing.Optional[pd.DataFrame] = None
        self.wt = QThread()
        self.wt.start()

        self.__initWindow()
        if self.fp is not None: QTimer.singleShot(500, self.__readParquet)
    
    def closeEvent(self, a0: QCloseEvent) -> None:
        settings = QSettings("spv", "Simple Parquet Viewer")
        settings.setValue("w_state", self.saveState())
        settings.setValue("w_geometry", self.saveGeometry())
        return super().closeEvent(a0)
    
    def __initWindow(self) -> None:
        self.__tb = QToolBar()
        self.__tb.setIconSize(QSize(48, 48))
        self.__tb.setObjectName("toolBar")

        self.__btOpenFile = QToolButton(self)
        self.__btOpenFile.setIcon(QIcon(QPixmap(imgPath("open.png"))))
        self.__btOpenFile.setToolTip(self.tr("Open Parquet file"))
        self.__btOpenFile.clicked.connect(self.__openParquet)

        self.__btSaveParquet = QToolButton(self)
        self.__btSaveParquet.setIcon(QIcon(imgPath("save_parquet.png")))
        self.__btSaveParquet.setToolTip(self.tr("Save current view into a Parquet file"))
        self.__btSaveParquet.setEnabled(False)
        self.__btSaveParquet.clicked.connect(lambda: self.__exportData(ExportType.PARQUET))

        self.__btSaveCSV = QToolButton(self)
        self.__btSaveCSV.setIcon(QIcon(imgPath("save_csv.png")))
        self.__btSaveCSV.setToolTip(self.tr("Save current view into a CSV file"))
        self.__btSaveCSV.setEnabled(False)
        self.__btSaveCSV.clicked.connect(lambda: self.__exportData(ExportType.CSV))

        self.__btSaveJSON = QToolButton(self)
        self.__btSaveJSON.setIcon(QIcon(QPixmap(imgPath("save_json.png"))))
        self.__btSaveJSON.setToolTip(self.tr("Save current view into a JSON file"))
        self.__btSaveJSON.setEnabled(False)
        self.__btSaveJSON.clicked.connect(lambda: self.__exportData(ExportType.JSON))

        self.__btAbout = QToolButton(self)
        self.__btAbout.setIcon(QIcon(QPixmap(imgPath("info.png"))))
        self.__btAbout.setToolTip(self.tr("View information about this application"))
        self.__btAbout.clicked.connect(
            lambda: QMessageBox.about(
                self,
                self.tr("About Simple Parquet Viewer"),
                self.tr(
                    "<b>About Simple Parquet Viewer (SPV)</b><br />"
                    f"v{APP_VERSION[0]}.{APP_VERSION[1]}.{APP_VERSION[2]}<br />"
                    "<br />"
                    "Simple Parquet Viewer is a simple GUI program to visualize and interact with "
                    "data stored in Parquet files.<br />"
                    "<br />"
                    "SPV is distributed under the terms of GPLv3. You should have received a copy "
                    "of the GNU General Public License along with this program.  If not, you can "
                    "find it at <a href=\"https://www.gnu.org/licenses/gpl-3.0.html\">"
                    "<span style=\"color: white; font-weight: bold;\">GNU's website</span></a>.<br />"
                    "<br />"
                )
            )
        )

        self.__btAboutQt = QToolButton(self)
        self.__btAboutQt.setIcon(QIcon(QPixmap(imgPath("info_qt.png"))))
        self.__btAboutQt.setToolTip(self.tr("View information about Qt"))
        self.__btAboutQt.clicked.connect(QApplication.aboutQt)

        self.__tb.addWidget(self.__btOpenFile)
        self.__tb.addWidget(self.__btSaveParquet)
        self.__tb.addWidget(self.__btSaveCSV)
        self.__tb.addWidget(self.__btSaveJSON)
        self.__tb.addSeparator()
        self.__tb.addWidget(self.__btAbout)
        self.__tb.addWidget(self.__btAboutQt)

        self.addToolBar(self.__tb)

        sb = QStatusBar()
        sb.showMessage(self.tr("Ready"))

        self.setStatusBar(sb)

        self.__setupViz()

        settings = QSettings("spv", "Simple Parquet Viewer")
        if (settings.contains("w_geometry")): self.restoreGeometry(settings.value("w_geometry"))
        else:
            self.setMinimumSize(QSize(512, 512))
            self.move(self.screen().geometry().center() - self.frameGeometry().center())
        if (settings.contains("w_state")): self.restoreState(settings.value("w_state"))
    
    def __setupViz(self) -> None:
        cl = QVBoxLayout()
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        cw = QWidget(self)
        cw.setLayout(cl)
        
        if self.fp is None:
            self.__tb.setEnabled(True)
            self.__btSaveCSV.setEnabled(False)
            self.__btSaveJSON.setEnabled(False)
            self.__btSaveParquet.setEnabled(False)
            lbl = QLabel(self.tr("Please, select a valid Parquet file in order to view its content here :)"))
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(lbl)
        elif self.df is None:
            self.__tb.setEnabled(False)
            self.__btSaveCSV.setEnabled(False)
            self.__btSaveJSON.setEnabled(False)
            self.__btSaveParquet.setEnabled(False)
            lbl = QLabel(self.tr("Loading data..."))
            lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

            pb = QProgressBar()
            pb.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            pb.setMaximumWidth(200)
            pb.setRange(0, 0)
            
            cl.addWidget(lbl)
            cl.addWidget(pb)
        else:
            self.__tb.setEnabled(True)
            self.__btSaveCSV.setEnabled(True)
            self.__btSaveJSON.setEnabled(True)
            self.__btSaveParquet.setEnabled(True)
            
            tv = QTableView()
            self.__applyDFToView(self.df, tv)

            lbl = QLabel()
            lbl.setAccessibleName(self.tr("Filter"))
            lbl.setPixmap(QPixmap(imgPath("filter.png")).scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatioByExpanding))

            edt = QLineEdit()
            edt.setToolTip(self.tr("Custom filter compatible with Pandas \"query\""))
            edt.returnPressed.connect(lambda: self.__applyFilter(edt.text(), tv))

            btA = QToolButton()
            btA.setIcon(QIcon(imgPath("apply.png")))
            btA.setToolTip(self.tr("Apply filter"))
            btA.clicked.connect(lambda: self.__applyFilter(edt.text(), tv))

            btC = QToolButton()
            btC.setIcon(QIcon(imgPath("clear.png")))
            btC.setToolTip(self.tr("Clear current filter"))
            btC.clicked.connect(lambda: self.__clearFilters(edt, tv))

            hl = QHBoxLayout()
            hl.addWidget(lbl)
            hl.addWidget(edt)
            hl.addWidget(btA)
            hl.addWidget(btC)

            cl.addLayout(hl)
            cl.addWidget(tv)
        
        ocw = self.centralWidget()
        self.setCentralWidget(cw)
        if ocw is not None: ocw.deleteLater()

    def __applyDFToView(self, df: pd.DataFrame, tv: QTableView) -> None:
        self.dfV = df
        sm = TableModel(df)
        tv.setUpdatesEnabled(False)
        tv.setModel(sm)
        tv.setUpdatesEnabled(True)
    
    def __applyFilter(self, filter: str, tv: QTableView) -> None:
        try:
            if ("@" in filter): raise Exception(self.tr("Filter must not contain \"@\" (no support to query variables)."))
            self.__applyDFToView(self.df.query(filter, inplace = False), tv)
        except Exception as e:
            QMessageBox.critical(self, self.tr("Filter error"), self.tr(f"Error when applying the requested filter. Details:\n{e}"))
    
    def __clearFilters(self, inp: QLineEdit, tv: QTableView) -> None:
        inp.setText("")
        self.__applyDFToView(self.df, tv)
    
    def __readParquet(self) -> None:
        self.df = None
        self.__setupViz()
        QApplication.processEvents()

        aw = AsyncWorker()
        aw.moveToThread(self.wt)
        aw.dfReady.connect(self.__dataFrameReady)
        aw.readFail.connect(self.__readingError)
        QTimer.singleShot(0, lambda: aw.readParquet(self.fp))
    
    def __exportData(self, type_: ExportType) -> None:
        if type_ == ExportType.CSV:
            ext = ".csv"
            title = self.tr("Export CSV")
            filters = self.tr("CSV files (*.csv);;All files (*.*)")
        elif type_ == ExportType.JSON:
            ext = ".json"
            title = self.tr("Export JSON")
            filters = self.tr("JSON files (*.json);;All files (*.*)")
        elif type_ == ExportType.PARQUET:
            ext = ".parquet"
            title = self.tr("Export Parquet")
            filters = self.tr("CSV files (*.parquet);;All files (*.*)")
        
        fn = QFileDialog.getSaveFileName(self, title, os.path.join(os.path.dirname(self.fp), Path(self.fp).stem + ext), filters)
        if len(fn[0]):
            fp = fn[0] if fn[0].endswith(ext) else fn[0] + ext
            self.statusBar().showMessage(self.tr(f"Exporting \"{fp}\"..."))
            QApplication.processEvents()

            aw = AsyncWorker()
            aw.moveToThread(self.wt)
            aw.exportComplete.connect(self.__exportComplete)
            QTimer.singleShot(200, lambda: aw.exportFile(fp, self.dfV, type_))
            QApplication.processEvents()

    def __dataFrameReady(self, df: pd.DataFrame, worker: AsyncWorker) -> None:
        self.df = df
        self.__setupViz()
        worker.deleteLater()
    
    def __exportComplete(self) -> None:
        self.statusBar().showMessage(self.tr(f"The file has been exported successfully."), 5000)
        QTimer.singleShot(5200, lambda: self.statusBar().showMessage(self.tr("Ready!")))
    
    def __readingError(self) -> None:
        QMessageBox.critical(self, self.tr("Reading error"), self.tr("It was not possible to read the given file."), QMessageBox.StandardButton.Ok)
        self.fp = None
        self.__setupViz()
    
    def __openParquet(self) -> None:
        fn = QFileDialog.getOpenFileName(
            self, self.tr("Open Parquet file"),
            QDir.homePath() if self.fp is None else os.path.dirname(self.fp),
            self.tr("Parquet files (*.parquet);;All files (*.*)")
        )
        if len(fn[0]):
            self.fp = fn[0]
            self.__readParquet()