import os
import sys
import json
from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QAction, QKeySequence, QFileSystemModel, QColor
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
    QTextEdit,
    QTreeView,
    QSplitter,
    QMenu,
    QInputDialog,
    QTabWidget,
    QGraphicsView,
    QGraphicsScene
)


class KuvixStudio(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("KuvixStudio - IDE")
        self.resize(1200, 750)

        # --- Modern Koyu Tema (Dark Palette Styling) ---
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11pt;
            }
            QMenuBar {
                background-color: #2d2d2d;
                color: #f1f1f1;
            }
            QMenuBar::item {
                background-color: #2d2d2d;
                color: #f1f1f1;
                padding: 6px 10px;
            }
            QMenuBar::item:selected {
                background-color: #3d3d3d;
            }
            QMenu {
                background-color: #2d2d2d;
                color: #f1f1f1;
                border: 1px solid #3d3d3d;
            }
            QMenu::item:selected {
                background-color: #007acc;
                color: white;
            }
            QTreeView {
                background-color: #252526;
                color: #cccccc;
                border: none;
                font-family: 'Segoe UI', sans-serif;
                font-size: 10pt;
            }
            QTreeView::item:selected {
                background-color: #37373d;
                color: white;
            }
            QTabWidget::pane {
                border: none;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #969696;
                padding: 8px 16px;
                border-top: 2px solid transparent;
                border-right: 1px solid #1e1e1e;
                font-family: 'Segoe UI', sans-serif;
                font-size: 9.5pt;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                color: #ffffff;
                border-top: 2px solid #007acc;
            }
            QTabBar::tab:hover {
                background-color: #333333;
                color: #cccccc;
            }
            QStatusBar {
                background-color: #007acc;
                color: white;
            }
        """)

        # --- Ana Widget ve Bölücü (Splitter) ---
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        main_layout.addWidget(self.splitter)

        # --- Sol Taraf: Dosya Gezgini ---
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())

        self.tree_view = QTreeView(self)
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(QDir.currentPath()))
        
        self.tree_view.setHeaderHidden(True)
        for i in range(1, self.model.columnCount()):
            self.tree_view.hideColumn(i)

        self.tree_view.doubleClicked.connect(self.open_file_from_tree)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)

        self.splitter.addWidget(self.tree_view)

        # --- Sağ Taraf: Sekme Sistemi (Tab Widget) ve Üst Bilgi ---
        right_container = QWidget(self)
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Dosya Yolu Göstergesi (Breadcrumb)
        self.path_label = QLabel("  [ Hoş Geldiniz - Sekme Açılmadı ]", self)
        self.path_label.setFixedHeight(28)
        self.path_label.setStyleSheet("""
            background-color: #2d2d2d;
            color: #858585;
            font-family: 'Consolas', monospace;
            font-size: 9.5pt;
            border-bottom: 1px solid #333333;
            padding-left: 5px;
        """)
        right_layout.addWidget(self.path_label)

        # Sekme Widget'ı (Tab Widget)
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        right_layout.addWidget(self.tab_widget)

        self.splitter.addWidget(right_container)
        self.splitter.setSizes([250, 950])

        # --- Menü Çubuğu ---
        menubar = self.menuBar()

        file_menu = menubar.addMenu("Dosya")

        new_action = QAction("Yeni", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Dosya Aç...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        open_folder_action = QAction("Klasör Aç...", self)
        open_folder_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_folder_action.triggered.connect(self.open_folder_dialog)
        file_menu.addAction(open_folder_action)

        file_menu.addSeparator()

        save_action = QAction("Kaydet", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Farklı Kaydet...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("Çıkış", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tools_menu = menubar.addMenu("Araçlar")
        validate_action = QAction("Layout Doğrula (JSON)", self)
        validate_action.triggered.connect(self.validate_layout)
        tools_menu.addAction(validate_action)

        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Hazır - KuvixStudio v0.1")

    def get_current_editor(self):
        """Aktif sekmedeki QTextEdit bileşenini döndürür."""
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            return current_widget.findChild(QTextEdit)
        return None

    def tab_changed(self, index):
        """Sekme değiştirildiğinde pencere başlığını ve yol etiketini günceller."""
        current_widget = self.tab_widget.widget(index)
        if current_widget and hasattr(current_widget, "file_path"):
            file_path = current_widget.file_path
            if file_path:
                self.setWindowTitle(f"KuvixStudio - {os.path.basename(file_path)}")
                self.path_label.setText(f"  {file_path}")
                self.path_label.setStyleSheet("""
                    background-color: #2d2d2d;
                    color: #cccccc;
                    font-family: 'Consolas', monospace;
                    font-size: 9.5pt;
                    border-bottom: 1px solid #333333;
                    padding-left: 5px;
                """)
            else:
                self.setWindowTitle(f"KuvixStudio - {self.tab_widget.tabText(index)}")
                self.path_label.setText("  [ Yeni Sekme - Kaydedilmedi ]")
        else:
            self.setWindowTitle("KuvixStudio - IDE")
            self.path_label.setText("  [ Hoş Geldiniz - Sekme Açılmadı ]")

    def close_tab(self, index):
        """Sekmeyi kapatır."""
        self.tab_widget.removeTab(index)

    def new_file(self):
        """Yeni bir boş sekme açar."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        editor = QTextEdit(container)
        layout.addWidget(editor)
        
        container.file_path = None  # Henüz kaydedilmemiş
        
        tab_index = self.tab_widget.addTab(container, "Adsız")
        self.tab_widget.setCurrentIndex(tab_index)
        self.status_bar.showMessage("Yeni sekme açıldı.", 3000)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Dosya Aç", "", "Tüm Desteklenenler (*.json *.cpp *.hpp *.kef);;JSON Dosyaları (*.json);;C/C++ Kaynak (*.cpp *.hpp);;Tüm Dosyalar (*.*)"
        )
        if file_path:
            self.load_file_to_tab(file_path)

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Klasör Seç", "")
        if folder_path:
            self.tree_view.setRootIndex(self.model.index(folder_path))
            self.model.setRootPath(folder_path)
            self.status_bar.showMessage(f"Açılan Proje Klasörü: {folder_path}", 4000)

    def open_file_from_tree(self, index):
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):
            self.load_file_to_tab(file_path)

    def load_file_to_tab(self, file_path):
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if hasattr(widget, "file_path") and widget.file_path == file_path:
                self.tab_widget.setCurrentIndex(i)
                return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # --- YENİ EKLENTİ: JSON ise Görsel Sekme Oluştur ---
            if file_path.endswith(".json"):
                # Hem düzenleyiciyi hem görseli koymak için bir splitter veya tab kullanabiliriz
                # Şimdilik basitçe editörü koyalım, yanına görsel sekmesi ekleyeceğiz:
                editor = QTextEdit(container)
                editor.setPlainText(content)
                layout.addWidget(editor)
                
                # Görsel önizleme sekmesini oluştur
                self.add_preview_tab(file_path, content)
            else:
                editor = QTextEdit(container)
                editor.setPlainText(content)
                layout.addWidget(editor)

            container.file_path = file_path
            tab_name = os.path.basename(file_path)
            tab_index = self.tab_widget.addTab(container, tab_name)
            self.tab_widget.setCurrentIndex(tab_index)

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya açılamadı:\n{e}")

    def add_preview_tab(self, file_path, content):
        scene = QGraphicsScene()
        view = QGraphicsView(scene)
        view.setStyleSheet("background-color: #1e1e1e;") # IDE arka planı ile uyumlu koyu gri
        
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                window_data = data.get("window", {})
                win_title = window_data.get("title", "KuvixWindow")
                win_w = window_data.get("width", 800)
                win_h = window_data.get("height", 600)
                
                # Tuval boyutunu pencereden biraz daha büyük tutalım ki etrafında boşluk kalısın
                scene.setSceneRect(0, 0, win_w + 100, win_h + 100)
                
                # Pencere başlangıç konumu (Ortalamak veya belirli bir boşluk bırakmak için)
                start_x = 50
                start_y = 50
                
                # 1. Sanal Pencere Arka Planı (Gövde)
                window_bg = scene.addRect(start_x, start_y, win_w, win_h)
                window_bg.setBrush(QColor("#2d2d2d"))
                window_bg.setPen(QColor("#555555"))
                
                # 2. Sanal Pencere Başlık Çubuğu
                title_bar_height = 30
                title_bar = scene.addRect(start_x, start_y, win_w, title_bar_height)
                title_bar.setBrush(QColor("#3c3c3c"))
                title_bar.setPen(QColor("#555555"))
                
                # Başlık Metni
                text_item = scene.addText(win_title)
                text_item.setDefaultTextColor(QColor("#cccccc"))
                text_item.setPos(start_x + 10, start_y + 4)
                
                # 3. Elements dizisindeki bileşenleri pencere koordinatına göre çiz
                elements = data.get("elements", [])
                for elem in elements:
                    # Eleman koordinatlarını pencerenin içine göre (start_x, start_y + title_bar_height) kaydırıyoruz
                    x = start_x + elem.get("x", 0)
                    y = start_y + title_bar_height + elem.get("y", 0)
                    w = elem.get("width", 100)
                    h = elem.get("height", 100)
                    
                    rect = scene.addRect(x, y, w, h)
                    rect.setBrush(QColor("#007acc")) # KuvixStudio mavisi
                    rect.setPen(QColor("#ffffff"))
                        
        except Exception as e:
            print(f"Önizleme yüklenirken hata oluştu: {e}")
            
        self.tab_widget.addTab(view, f"Önizleme: {os.path.basename(file_path)}")
        
    def save_file(self):
        editor = self.get_current_editor()
        current_widget = self.tab_widget.currentWidget()
        
        if not current_widget:
            return

        file_path = getattr(current_widget, "file_path", None)

        if file_path:
            try:
                content = editor.toPlainText()
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.status_bar.showMessage("Dosya başarıyla kaydedildi.", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Kaydedilemedi:\n{e}")
        else:
            self.save_as()

    def save_as(self):
        current_widget = self.tab_widget.currentWidget()
        if not current_widget:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Farklı Kaydet", "", "JSON Dosyaları (*.json);;C/C++ Kaynak (*.cpp *.hpp);;Tüm Dosyalar (*.*)"
        )
        if file_path:
            current_widget.file_path = file_path
            tab_index = self.tab_widget.currentIndex()
            self.tab_widget.setTabText(tab_index, os.path.basename(file_path))
            self.save_file()
            self.tab_changed(tab_index)

    def show_context_menu(self, position):
        index = self.tree_view.indexAt(position)
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: #f1f1f1;
                border: 1px solid #3d3d3d;
            }
            QMenu::item:selected {
                background-color: #007acc;
                color: white;
            }
        """)

        new_file_action = menu.addAction("Yeni Dosya Oluştur")
        new_folder_action = menu.addAction("Yeni Klasör Oluştur")

        action = menu.exec(self.tree_view.viewport().mapToGlobal(position))

        if action == new_file_action:
            self.create_new_item(index, is_file=True)
        elif action == new_folder_action:
            self.create_new_item(index, is_file=False)

    def create_new_item(self, index, is_file=True):
        if index.isValid():
            dir_path = self.model.filePath(index)
            if os.path.isfile(dir_path):
                dir_path = os.path.dirname(dir_path)
        else:
            dir_path = self.model.rootPath()

        item_type = "Dosya" if is_file else "Klasör"
        name, ok = QInputDialog.getText(self, f"Yeni {item_type}", f"Yeni {item_type} Adı:")

        if ok and name:
            target_path = os.path.join(dir_path, name)
            try:
                if is_file:
                    with open(target_path, "w", encoding="utf-8") as f:
                        f.write("")
                    self.load_file_to_tab(target_path)
                else:
                    os.makedirs(target_path, exist_ok=True)
                
                self.status_bar.showMessage(f"Başarıyla oluşturuldu: {target_path}", 4000)
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"{item_type} oluşturulamadı:\n{e}")

    def validate_layout(self):
        QMessageBox.information(self, "KuvixStudio", "Layout doğrulama aracı yakında eklenecek!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = KuvixStudio()
    editor.show()
    sys.exit(app.exec())