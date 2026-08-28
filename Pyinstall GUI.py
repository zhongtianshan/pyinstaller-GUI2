#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, json, subprocess, threading, time, shutil
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                               QTabWidget, QWidget, QLabel, QLineEdit, QCheckBox,
                               QPushButton, QTextEdit, QFileDialog, QMessageBox,
                               QComboBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")
PYINST = [sys.executable, "-m", "PyInstaller"]

STRINGS = {
    "en": {
        "title": "PyInstaller GUI Packager",
        "tab_basic": "Basic", "tab_package": "Package", "tab_resource": "Resources",
        "tab_security": "Security", "tab_advanced": "Advanced",
        "script": "Main script", "outdir": "Output directory",
        "icon": "Icon (.ico)",
        "onefile": "One-file (--onefile)", "noconsole": "Window app (--noconsole)",
        "upx": "UPX compression", "debug": "Debug (--debug)",
        "company": "Company name", "product": "Product name", "file_ver": "File version",
        "prod_ver": "Product version", "desc": "File description", "copyright": "Copyright",
        "data": "Additional data", "bin": "Additional binaries",
        "hidden": "Hidden imports (comma separated)",
        "encrypt": "Encrypt bytecode (--key)",
        "encrypt_key": "Encryption key (blank to disable)",
        "hooks": "Hooks directory", "extra": "Extra arguments", "clean": "Clean build (--clean)",
        "btn_pack": "Start Packing", "btn_cmd": "Generate Command",
        "btn_save": "Save Config", "btn_load": "Load Config",
        "pick_file": "Select file", "pick_dir": "Select directory",
        "pick_multi": "Select multiple files",
        "err_title": "Error", "err_script": "Please select a main script",
        "cmd_title": "Generated command", "info": "Info", "cfg_saved": "Configuration saved",
        "log_start": "Packing started, please wait...", "log_done": "\nPacking done!\n",
        "lang_label": "Language:",
    },
    "zh": {
        "title": "基于 Pyinstaller 制作的图形化打包程序",
        "tab_basic": "基本", "tab_package": "打包", "tab_resource": "资源",
        "tab_security": "安全", "tab_advanced": "高级",
        "script": "主脚本", "outdir": "输出目录",
        "icon": "图标(.ico)",
        "onefile": "单文件(--onefile)", "noconsole": "窗口程序(--noconsole)",
        "upx": "UPX 压缩", "debug": "调试(--debug)",
        "company": "公司名称", "product": "产品名称", "file_ver": "文件版本",
        "prod_ver": "产品版本", "desc": "文件描述", "copyright": "版权",
        "data": "附加数据", "bin": "附加二进制",
        "hidden": "隐藏导入(逗号分隔)",
        "encrypt": "加密字节码(--key)",
        "encrypt_key": "加密密钥(留空则不加密)",
        "hooks": "钩子目录", "extra": "额外参数", "clean": "构建后清理(--clean)",
        "btn_pack": "开始打包", "btn_cmd": "生成命令",
        "btn_save": "保存配置", "btn_load": "加载配置",
        "pick_file": "选择文件", "pick_dir": "选择目录",
        "pick_multi": "选择多个文件",
        "err_title": "错误", "err_script": "请选择主脚本",
        "cmd_title": "生成的命令", "info": "提示", "cfg_saved": "配置已保存",
        "log_start": "⚙ 开始打包，请稍候...", "log_done": "\n✅ 打包完成！\n",
        "lang_label": "语言：",
    },
}

TAB_KEYS = ["tab_basic", "tab_package", "tab_resource", "tab_security", "tab_advanced"]


class PackThread(QThread):
    log = Signal(str)

    def __init__(self, cmd, temp_dir, done_msg):
        super().__init__()
        self.cmd = cmd
        self.temp_dir = temp_dir
        self.done_msg = done_msg

    def run(self):
        proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True,
                                bufsize=1, encoding="utf-8")
        for line in proc.stdout:
            self.log.emit(line)
        proc.wait()
        self.log.emit(self.done_msg)
        if os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "en"
        self.strings = STRINGS[self.lang]
        self.vars = {}
        self.labels = {}
        self.checks = {}
        self.buttons = []
        self.resize(1050, 780)
        self.setStyleSheet("""
            QMainWindow{background:#000000;}
            QLabel{color:#00ffff;font-family:Consolas;font-size:14px;}
            QLineEdit{background:#111111;color:#00ffff;border:1px solid #00ffff;font-size:14px;}
            QTextEdit{background:#111111;color:#00ffff;border:1px solid #00ffff;font-size:14px;}
            QCheckBox{color:#00ffff;font-family:Consolas;font-size:14px;}
            QPushButton{background:#00ffff;color:#000000;border:none;padding:6px 12px;font-size:14px;}
            QTabWidget::pane{border:0;}
            QTabBar::tab{background:#111111;color:#00ffff;padding:8px 16px;font-size:14px;}
            QTabBar::tab:selected{background:#00ffff;color:#000000;}
            QComboBox{background:#111111;color:#00ffff;border:1px solid #00ffff;font-size:14px;}
        """)
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        title = QLabel("Cyber PyInstaller Pro")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Consolas", 20, QFont.Bold))
        main_layout.addWidget(title)

        lang_row = QHBoxLayout()
        lang_row.addStretch()
        lang_lbl = QLabel(self.s("lang_label"))
        self.labels["lang_label"] = lang_lbl
        lang_row.addWidget(lang_lbl)
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("中文", "zh")
        self.lang_combo.currentIndexChanged.connect(self.on_lang_change)
        lang_row.addWidget(self.lang_combo)
        main_layout.addLayout(lang_row)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        self.build_tabs(self.tabs)
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        main_layout.addWidget(self.log_edit)
        btn_layout = QHBoxLayout()
        for key, func in [("btn_pack", self.start_pack), ("btn_cmd", self.gen_cmd),
                          ("btn_save", self.save_cfg), ("btn_load", self.load_cfg)]:
            btn = QPushButton(self.s(key))
            btn.clicked.connect(func)
            self.buttons.append((btn, key))
            btn_layout.addWidget(btn)
        main_layout.addLayout(btn_layout)
        self.apply_lang()
        self.load_cfg()

    def s(self, key):
        return self.strings.get(key, key)

    def on_lang_change(self):
        self.lang = self.lang_combo.currentData()
        self.strings = STRINGS[self.lang]
        self.apply_lang()

    def apply_lang(self):
        self.setWindowTitle(self.s("title"))
        for i, key in enumerate(TAB_KEYS):
            self.tabs.setTabText(i, f"  {self.s(key)}  ")
        for key, lbl in self.labels.items():
            lbl.setText(self.s(key))
        for key, chk in self.checks.items():
            chk.setText(self.s(key))
        for btn, key in self.buttons:
            btn.setText(self.s(key))

    def build_tabs(self, tabs):
        for key, creator in [("tab_basic", self.create_basic), ("tab_package", self.create_package),
                             ("tab_resource", self.create_resource), ("tab_security", self.create_security),
                             ("tab_advanced", self.create_advanced)]:
            w = QWidget()
            tabs.addTab(w, f"  {self.s(key)}  ")
            creator(w)

    def create_basic(self, parent):
        lay = QVBoxLayout(parent)
        self.add_entry(lay, "script", pick="file")
        self.add_entry(lay, "outdir", pick="dir")

    def create_package(self, parent):
        lay = QVBoxLayout(parent)
        self.add_entry(lay, "icon", pick="file")
        for key in ["onefile", "noconsole", "upx", "debug"]:
            self.add_check(lay, key)
        for key in ["company", "product", "file_ver", "prod_ver", "desc", "copyright"]:
            self.add_entry(lay, key)

    def create_resource(self, parent):
        lay = QVBoxLayout(parent)
        self.add_entry(lay, "data", pick="multi")
        self.add_entry(lay, "bin", pick="multi")
        self.add_entry(lay, "hidden")

    def create_security(self, parent):
        lay = QVBoxLayout(parent)
        self.add_check(lay, "encrypt")
        self.add_entry(lay, "encrypt_key")

    def create_advanced(self, parent):
        lay = QVBoxLayout(parent)
        self.add_entry(lay, "hooks", pick="dir")
        self.add_entry(lay, "extra")
        self.add_check(lay, "clean")

    def add_entry(self, parent, key, pick=None):
        row = QHBoxLayout()
        lbl = QLabel(self.s(key))
        lbl.setFixedWidth(240)
        self.labels[key] = lbl
        row.addWidget(lbl)
        line = QLineEdit()
        self.vars[key] = line
        row.addWidget(line)
        if pick == "file":
            btn = QPushButton("...")
            btn.clicked.connect(lambda: self.pick_file(key))
            row.addWidget(btn)
        elif pick == "dir":
            btn = QPushButton("...")
            btn.clicked.connect(lambda: self.pick_dir(key))
            row.addWidget(btn)
        elif pick == "multi":
            btn = QPushButton("+")
            btn.clicked.connect(lambda: self.pick_multi(key))
            row.addWidget(btn)
        parent.addLayout(row)

    def add_check(self, parent, key):
        chk = QCheckBox(self.s(key))
        self.vars[key] = chk
        self.checks[key] = chk
        parent.addWidget(chk)

    def pick_file(self, key):
        f, _ = QFileDialog.getOpenFileName(self, self.s("pick_file"))
        if f:
            self.vars[key].setText(os.path.abspath(f))

    def pick_dir(self, key):
        d = QFileDialog.getExistingDirectory(self, self.s("pick_dir"))
        if d:
            self.vars[key].setText(os.path.abspath(d))

    def pick_multi(self, key):
        files, _ = QFileDialog.getOpenFileNames(self, self.s("pick_multi"))
        if files:
            extra = ";".join(os.path.abspath(f) for f in files)
            current = self.vars[key].text()
            self.vars[key].setText(current + (";" if current else "") + extra)

    def log(self, txt):
        self.log_edit.append(txt.rstrip())
        self.log_edit.ensureCursorVisible()

    def build_cmd(self, script):
        cmd = PYINST.copy()
        if self.vars["onefile"].isChecked():
            cmd.append("--onefile")
        if self.vars["noconsole"].isChecked():
            cmd.append("--noconsole")
        if self.vars["upx"].isChecked():
            cmd.append("--upx-dir=upx")
        if self.vars["debug"].isChecked():
            cmd.append("--debug=all")
        cmd.extend(["--clean", "--workpath", "temp_build", "--specpath", "temp_build"])
        icon = self.vars["icon"].text()
        if icon:
            cmd.extend(["--icon", icon])
        vf = self.build_version_file()
        if vf:
            cmd.extend(["--version-file", vf])
        data = self.vars["data"].text()
        for f in data.split(";"):
            if f.strip():
                cmd.extend(["--add-data", f"{f}{os.pathsep}."])
        bin_files = self.vars["bin"].text()
        for f in bin_files.split(";"):
            if f.strip():
                cmd.extend(["--add-binary", f"{f}{os.pathsep}."])
        hidden = self.vars["hidden"].text()
        for m in hidden.split(","):
            if m.strip():
                cmd.extend(["--hidden-import", m.strip()])
        if self.vars["encrypt"].isChecked():
            key = self.vars["encrypt_key"].text().strip()
            if key:
                cmd.extend(["--key", key])
        hooks = self.vars["hooks"].text()
        if hooks:
            cmd.extend(["--additional-hooks-dir", hooks])
        outdir = os.path.join(os.getcwd(), "output")
        cmd.extend(["--distpath", outdir])
        extra = self.vars["extra"].text()
        if extra.strip():
            cmd.extend(extra.split())
        cmd.append(script)
        return outdir, cmd

    def _parse_version(self, raw):
        """把版本字符串安全解析成 4 元组。

        空串、非法字符、超长都不会崩：非法处截断，缺失补 0，多余截断。
        """
        parts = []
        for seg in raw.split("."):
            seg = seg.strip()
            if not seg.isdigit():
                break
            parts.append(int(seg))
        return tuple((parts + [0] * 4)[:4])

    def build_version_file(self):
        c = self.vars["company"].text()
        p = self.vars["product"].text()
        fv = self.vars["file_ver"].text()
        pv = self.vars["prod_ver"].text()
        d = self.vars["desc"].text()
        cp = self.vars["copyright"].text()
        if not any([c, p, fv]):
            return None
        fv_t = self._parse_version(fv)
        pv_t = self._parse_version(pv)
        txt = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(filevers={fv_t}, prodvers={pv_t}, mask=0x3f, flags=0x0, OS=0x4, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[StringFileInfo([StringTable('040904B0', [
    StringStruct('CompanyName', '{c}'),
    StringStruct('FileDescription', '{d}'),
    StringStruct('FileVersion', '{fv}'),
    StringStruct('ProductName', '{p}'),
    StringStruct('ProductVersion', '{pv}'),
    StringStruct('LegalCopyright', '{cp}')
  ])])]
)"""
        os.makedirs("temp_build", exist_ok=True)
        vf = os.path.join("temp_build", "version_file.txt")
        with open(vf, "w", encoding="utf-8") as f:
            f.write(txt)
        # PyInstaller 会把 --version-file 相对 spec 目录（即 temp_build/）解析，
        # 所以必须返回绝对路径，否则会拼出 temp_build\temp_build\version_file.txt。
        return os.path.abspath(vf)

    def start_pack(self):
        script = self.vars["script"].text()
        if not script:
            QMessageBox.critical(self, self.s("err_title"), self.s("err_script"))
            return
        outdir, cmd = self.build_cmd(script)
        self.vars["outdir"].setText(outdir)
        self.log(" ".join(cmd) + "\n\n")
        self.log(self.s("log_start") + "\n")
        temp_dir = os.path.abspath("temp_build")
        self.thread = PackThread(cmd, temp_dir, self.s("log_done"))
        self.thread.log.connect(self.log)
        self.thread.start()

    def gen_cmd(self):
        script = self.vars["script"].text()
        if script:
            outdir, cmd = self.build_cmd(script)
            self.vars["outdir"].setText(outdir)
            QMessageBox.information(self, self.s("cmd_title"), " ".join(cmd))

    def save_cfg(self):
        cfg = {k: (v.text() if hasattr(v, "text") else v.isChecked()) for k, v in self.vars.items()}
        cfg["lang"] = self.lang
        with open("cyber_gui.json", "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, self.s("info"), self.s("cfg_saved"))

    def load_cfg(self):
        try:
            with open("cyber_gui.json", encoding="utf-8") as f:
                cfg = json.load(f)
        except FileNotFoundError:
            cfg = {}
        lang = cfg.pop("lang", None)
        if lang in ("en", "zh"):
            idx = self.lang_combo.findData(lang)
            if idx != -1:
                self.lang_combo.setCurrentIndex(idx)
        for k, v in cfg.items():
            if k in self.vars:
                w = self.vars[k]
                if hasattr(w, "setText"):
                    w.setText(str(v))
                elif hasattr(w, "setChecked"):
                    w.setChecked(bool(v))
        default_out = os.path.join(os.getcwd(), "output")
        self.vars["outdir"].setText(default_out)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
