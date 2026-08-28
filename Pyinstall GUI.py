#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, json, subprocess, threading, time, shutil
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                               QTabWidget, QWidget, QLabel, QLineEdit, QCheckBox,
                               QPushButton, QTextEdit, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")
PYINST = [sys.executable, "-m", "PyInstaller"]


class PackThread(QThread):
    log = Signal(str)

    def __init__(self, cmd, temp_dir):
        super().__init__()
        self.cmd = cmd
        self.temp_dir = temp_dir

    def run(self):
        proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True,
                                bufsize=1, encoding="utf-8")
        for line in proc.stdout:
            self.log.emit(line)
        proc.wait()
        self.log.emit("\n✅ 打包完成！\n")
        if os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("基于Pyinstaller制作的图形化打包程序")
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
        """)
        self.vars = {}
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        title = QLabel("Cyber PyInstaller Pro")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Consolas", 20, QFont.Bold))
        main_layout.addWidget(title)
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        self.build_tabs(tabs)
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        main_layout.addWidget(self.log_edit)
        btn_layout = QHBoxLayout()
        for txt, func in [("开始打包", self.start_pack),
                          ("生成命令", self.gen_cmd),
                          ("保存配置", self.save_cfg),
                          ("加载配置", self.load_cfg)]:
            btn = QPushButton(txt)
            btn.clicked.connect(func)
            btn_layout.addWidget(btn)
        main_layout.addLayout(btn_layout)
        self.load_cfg()

    def build_tabs(self, tabs):
        for name, creator in [("基本", self.create_basic), ("打包", self.create_package),
                              ("资源", self.create_resource), ("安全", self.create_security),
                              ("高级", self.create_advanced)]:
            w = QWidget()
            tabs.addTab(w, f"  {name}  ")
            creator(w)

    def create_basic(self, parent):
        lay = QVBoxLayout(parent)
        self.add_entry(lay, "主脚本", "script", pick="file")
        self.add_entry(lay, "输出目录", "outdir", pick="dir")

    def create_package(self, parent):
        lay = QVBoxLayout(parent)
        self.add_entry(lay, "图标(.ico)", "icon", pick="file")
        for txt, key in [("单文件(--onefile)", "onefile"), ("窗口程序(--noconsole)", "noconsole"),
                         ("UPX 压缩", "upx"), ("调试(--debug)", "debug")]:
            self.add_check(lay, txt, key)
        for txt, key in [("公司名称", "company"), ("产品名称", "product"), ("文件版本", "file_ver"),
                         ("产品版本", "prod_ver"), ("文件描述", "desc"), ("版权", "copyright")]:
            self.add_entry(lay, txt, key)

    def create_resource(self, parent):
        lay = QVBoxLayout(parent)
        self.add_entry(lay, "附加数据", "data", pick="multi")
        self.add_entry(lay, "附加二进制", "bin", pick="multi")
        self.add_entry(lay, "隐藏导入(逗号分隔)", "hidden")

    def create_security(self, parent):
        lay = QVBoxLayout(parent)
        self.add_check(lay, "加密字节码(--key)", "encrypt")
        self.add_entry(lay, "加密密钥(留空则不加密)", "encrypt_key")

    def create_advanced(self, parent):
        lay = QVBoxLayout(parent)
        self.add_entry(lay, "钩子目录", "hooks", pick="dir")
        self.add_entry(lay, "额外参数", "extra")
        self.add_check(lay, "构建后清理(--clean)", "clean")

    def add_entry(self, parent, label, key, pick=None):
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setFixedWidth(140)
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

    def add_check(self, parent, text, key):
        chk = QCheckBox(text)
        self.vars[key] = chk
        parent.addWidget(chk)

    def pick_file(self, key):
        f, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if f:
            self.vars[key].setText(os.path.abspath(f))

    def pick_dir(self, key):
        d = QFileDialog.getExistingDirectory(self, "选择目录")
        if d:
            self.vars[key].setText(os.path.abspath(d))

    def pick_multi(self, key):
        files, _ = QFileDialog.getOpenFileNames(self, "选择多个文件")
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
        return vf

    def start_pack(self):
        script = self.vars["script"].text()
        if not script:
            QMessageBox.critical(self, "错误", "请选择主脚本")
            return
        outdir, cmd = self.build_cmd(script)
        self.vars["outdir"].setText(outdir)
        self.log(" ".join(cmd) + "\n\n")
        self.log("⚙ 开始打包，请稍候...\n")
        temp_dir = os.path.abspath("temp_build")
        self.thread = PackThread(cmd, temp_dir)
        self.thread.log.connect(self.log)
        self.thread.start()

    def gen_cmd(self):
        script = self.vars["script"].text()
        if script:
            outdir, cmd = self.build_cmd(script)
            self.vars["outdir"].setText(outdir)
            QMessageBox.information(self, "生成的命令", " ".join(cmd))

    def save_cfg(self):
        cfg = {k: (v.text() if hasattr(v, "text") else v.isChecked()) for k, v in self.vars.items()}
        with open("cyber_gui.json", "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "提示", "配置已保存")

    def load_cfg(self):
        try:
            with open("cyber_gui.json", encoding="utf-8") as f:
                cfg = json.load(f)
            for k, v in cfg.items():
                if k in self.vars:
                    w = self.vars[k]
                    if hasattr(w, "setText"):
                        w.setText(str(v))
                    elif hasattr(w, "setChecked"):
                        w.setChecked(bool(v))
        except FileNotFoundError:
            pass
        default_out = os.path.join(os.getcwd(), "output")
        self.vars["outdir"].setText(default_out)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())