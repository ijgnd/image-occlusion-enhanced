# -*- coding: utf-8 -*-
####################################################
##                                                ##
##           Image Occlusion Enhanced             ##
##                                                ##
##        Copyright (c) Glutanimate 2016          ##
##       (https://github.com/Glutanimate)         ##
##                                                ##
##     Original Image Occlusion 2.0 add-on is     ##
##         Copyright (c) 2012-2015 tmbb           ##
##           (https://github.com/tmbb)            ##
##                                                ##
####################################################

from PyQt4 import QtCore, QtGui
from aqt.qt import *

from aqt import mw, webview, deckchooser, tagedit
from aqt.utils import saveGeom, restoreGeom

from config import *
from resources import *

class ImgOccEdit(QDialog):
    """Main Image Occlusion Editor dialog"""
    def __init__(self, mw):
        QDialog.__init__(self, parent=None)
        self.mode = "add"
        loadConfig(self)
        self.setupUi()
        restoreGeom(self, "imgoccedit")

    def closeEvent(self, event):
        if mw.pm.profile is not None:
            self.deckChooser.cleanup()
            saveGeom(self, "imgoccedit")
        self.visible = False
        QWidget.closeEvent(self, event)

    def setupUi(self):
        """Set up ImgOccEdit UI"""
        # Main widgets aside from fields
        self.svg_edit = webview.AnkiWebView()
        self.svg_edit.setCanFocus(True) # focus necessary for hotkeys
        self.tags_hbox = QHBoxLayout()
        self.tags_edit = tagedit.TagEdit(self)
        self.tags_label = QLabel("Tags")
        self.tags_label.setFixedWidth(70)
        self.deck_container = QWidget()
        self.deckChooser = deckchooser.DeckChooser(mw, 
                        self.deck_container, label=True)

        # Button row widgets
        self.bottom_label = QLabel()
        button_box = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal, self)
        button_box.setCenterButtons(False)

        image_btn = QPushButton("Change &Image", clicked=self.changeImage)
        image_btn.setIcon(QIcon(":/icons/new_occlusion.png"))
        image_btn.setIconSize(QSize(16, 16))

        self.occl_tp_select = QComboBox()
        self.occl_tp_select.addItems(["Don't Change", "Hide All, Reveal One",
            "Hide All, Reveal All", "Hide One, Reveal All"])

        self.edit_btn = button_box.addButton("&Edit Cards",
           QDialogButtonBox.ActionRole)
        self.new_btn = button_box.addButton("&Add New Cards",
           QDialogButtonBox.ActionRole)
        self.ao_btn = button_box.addButton(u"Hide &All, Reveal One",
           QDialogButtonBox.ActionRole)
        self.aa_btn = button_box.addButton(u"Hide All, &Reveal All",
           QDialogButtonBox.ActionRole)
        self.oa_btn = button_box.addButton(u"Hide &One, Reveal All",
           QDialogButtonBox.ActionRole)
        close_button = button_box.addButton("&Close", 
            QDialogButtonBox.RejectRole)

        image_tt = "Switch to a different image while preserving all of \
            the shapes and fields"
        dc_tt = "Preserve existing occlusion type"
        edit_tt = "Edit all cards using current mask shapes and field entries"
        new_tt = "Create new batch of cards without editing existing ones"
        ao_tt = "Formerly known as nonoverlapping.<br>\
            Generate cards where all labels are hidden and just one is revealed<br>\
            on the back"
        aa_tt = "A step between nonoverlapping and overlapping.<br>\
            Generate cards where all labels are hidden on the front, but all \
            revealed on the back"
        oa_tt = "Formerly known as overlapping.<br>\
            Generate cards where just one label is hidden on the front and all\
            revealed on the back"
        close_tt = "Close Image Occlusion Editor without generating cards"

        image_btn.setToolTip(image_tt)
        self.edit_btn.setToolTip(edit_tt)
        self.new_btn.setToolTip(new_tt)
        self.ao_btn.setToolTip(ao_tt)
        self.aa_btn.setToolTip(aa_tt)
        self.oa_btn.setToolTip(oa_tt)
        close_button.setToolTip(close_tt)
        self.occl_tp_select.setItemData(0, dc_tt, Qt.ToolTipRole)
        self.occl_tp_select.setItemData(1, ao_tt, Qt.ToolTipRole)
        self.occl_tp_select.setItemData(2, aa_tt, Qt.ToolTipRole)
        self.occl_tp_select.setItemData(3, oa_tt, Qt.ToolTipRole)

        self.connect(self.edit_btn, SIGNAL("clicked()"), self.edit_note)
        self.connect(self.new_btn, SIGNAL("clicked()"), self.new)
        self.connect(self.ao_btn, SIGNAL("clicked()"), self.addAO)
        self.connect(self.aa_btn, SIGNAL("clicked()"), self.addAA)
        self.connect(self.oa_btn, SIGNAL("clicked()"), self.addOA)
        self.connect(close_button, SIGNAL("clicked()"), self.close)

        # Set basic layout up

        ## Button row
        bottom_hbox = QHBoxLayout()
        bottom_hbox.addWidget(image_btn)
        bottom_hbox.insertStretch(1, stretch=1)
        bottom_hbox.addWidget(self.bottom_label)
        bottom_hbox.addWidget(self.occl_tp_select)
        bottom_hbox.addWidget(button_box)

        ## Tab 1
        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.svg_edit, stretch=1)

        ## Tab 2
        self.vbox2 = QVBoxLayout()
        # vbox2 fields are variable and added by setupFields() at a later point

        ## Main Tab Widget
        tab1 = QWidget()
        tab2 = QWidget()
        tab1.setLayout(vbox1)
        tab2.setLayout(self.vbox2)
        self.tab_widget = QtGui.QTabWidget() 
        self.tab_widget.addTab(tab1,"&Masks Editor")
        self.tab_widget.addTab(tab2,"&Fields")
        self.tab_widget.setTabToolTip(1, "Include additional information (optional)")
        self.tab_widget.setTabToolTip(0, "Create image occlusion masks (required)")

        ## Main Window
        vbox_main = QVBoxLayout()
        vbox_main.setMargin(5);
        vbox_main.addWidget(self.tab_widget)
        vbox_main.addLayout(bottom_hbox)
        self.setLayout(vbox_main)
        self.setMinimumWidth(640)
        self.tab_widget.setCurrentIndex(0)
        self.svg_edit.setFocus()

        # Define and connect key bindings

        ## Field focus hotkeys
        for i in range(1,10):
            s = self.connect(QtGui.QShortcut(QtGui.QKeySequence("Ctrl+%i" %i), self), 
                QtCore.SIGNAL('activated()'), 
                lambda f=i-1:self.focusField(f))
        ## Other hotkeys
        self.connect(QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Tab"), self), 
            QtCore.SIGNAL('activated()'), self.switchTabs)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence("Ctrl+r"), self), 
            QtCore.SIGNAL('activated()'), self.resetMainFields)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+r"), self), 
            QtCore.SIGNAL('activated()'), self.resetAllFields)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+t"), self), 
            QtCore.SIGNAL('activated()'), lambda:self.focusField(self.tags_edit))
        self.connect(QtGui.QShortcut(QtGui.QKeySequence("Ctrl+f"), self), 
            QtCore.SIGNAL('activated()'), self.fitImageCanvas)


    # Various actions that act on / interact with the ImgOccEdit UI:

    # Note actions

    def changeImage(self):
        mw.ImgOccAdd.onChangeImage()
    def addAO(self): 
        mw.ImgOccAdd.onAddNotesButton("ao")
    def addAA(self): 
        mw.ImgOccAdd.onAddNotesButton("aa")
    def addOA(self): 
        mw.ImgOccAdd.onAddNotesButton("oa")
    def new(self):
        choice = self.occl_tp_select.currentText()
        mw.ImgOccAdd.onAddNotesButton(choice)
    def edit_note(self):
        choice = self.occl_tp_select.currentText()
        mw.ImgOccAdd.onEditNotesButton(choice)

    # Window state

    def resetFields(self):
        """Reset all window fields. Needed for changes to the note type"""
        layout = self.vbox2
        for i in reversed(range(layout.count())): 
            item = layout.takeAt(i)
            layout.removeItem(item)
            if item.widget():
                item.widget().setParent(None)
            elif item.layout():
                sublayout = item.layout()
                sublayout.setParent(None)
                for i in reversed(range(sublayout.count())):
                    subitem = sublayout.takeAt(i)
                    sublayout.removeItem(subitem)
                    subitem.widget().setParent(None)
        self.tags_hbox.setParent(None)

    def resetWindow(self):
        """Reset window state"""
        self.resetAllFields()
        self.tab_widget.setCurrentIndex(0)
        self.occl_tp_select.setCurrentIndex(0)
        self.tedit[self.ioflds["hd"]].setFocus()
        self.svg_edit.setFocus()

    def setupFields(self, flds):
        """Setup window fields based on note type fields"""
        self.tedit = {}
        self.flds = flds
        for i in flds:
            if i['name'] in self.ioflds_priv:
                continue
            hbox = QHBoxLayout()
            tedit = QPlainTextEdit()
            label = QLabel(i["name"])
            hbox.addWidget(label)
            hbox.addWidget(tedit)
            tedit.setTabChangesFocus(True)
            tedit.setMinimumHeight(40)
            label.setFixedWidth(70) 
            self.tedit[i["name"]] = tedit
            self.vbox2.addLayout(hbox)
        
        self.tags_hbox.addWidget(self.tags_label)
        self.tags_hbox.addWidget(self.tags_edit)
        self.vbox2.addLayout(self.tags_hbox)
        self.vbox2.addWidget(self.deck_container)

    def switchToMode(self, mode):
        """Toggle between add and edit layouts"""
        self.mode = mode
        hide_on_add = [self.occl_tp_select, self.edit_btn, self.new_btn]
        hide_on_edit = [self.ao_btn, self.aa_btn, self.oa_btn]
        if mode == "add":
            for i in hide_on_add:
                i.hide()
            for i in hide_on_edit:
                i.show()
            dl_txt = "Deck"
            ttl = "Image Occlusion Enhanced - Add Mode"
            bl_txt = "Add Cards:"
        else:
            for i in hide_on_add:
                i.show()
            for i in hide_on_edit:
                i.hide()
            dl_txt = "Deck for <i>Add new cards</i>"
            ttl = "Image Occlusion Enhanced - Editing Mode"
            bl_txt = "Type:"
        self.deckChooser.deckLabel.setText(dl_txt)
        self.setWindowTitle(ttl)
        self.bottom_label.setText(bl_txt)

    # Other actions

    def switchTabs(self):
        currentTab = self.tab_widget.currentIndex()
        if currentTab == 0:
          self.tab_widget.setCurrentIndex(1)
          if isinstance(QApplication.focusWidget(), QPushButton):
              self.tedit[self.ioflds["hd"]].setFocus()
        else:
          self.tab_widget.setCurrentIndex(0)

    def focusField(self, idx):
        """Focus field in vbox2 layout by index number"""
        self.tab_widget.setCurrentIndex(1)
        target_item = self.vbox2.itemAt(idx)
        if not target_item:
            return
        target_layout = target_item.layout()
        target_widget = target_item.widget()
        if target_layout:
            target = target_layout.itemAt(1).widget()
        elif target_widget:
            target = target_widget
        target.setFocus()

    def resetMainFields(self):
        for i in self.flds:
            fn = i['name']
            if fn in self.ioflds_priv or fn in self.ioflds_prsv:
                continue
            self.tedit[fn].setPlainText("")

    def resetAllFields(self):
        self.resetMainFields()
        for i in self.ioflds_prsv:
            self.tedit[i].setPlainText("")

    def fitImageCanvas(self):
        command = "svgCanvas.zoomChanged('', 'canvas');"
        self.svg_edit.eval(command)

class ImgOccOpts(QDialog):
    """Main Image Occlusion Options dialog"""
    def __init__(self, mw):
        QDialog.__init__(self, parent=mw)
        loadConfig(self)
        self.ofill = mw.col.conf['imgocc']['ofill']
        self.qfill = mw.col.conf['imgocc']['qfill']
        self.setupUi()

    def getNewMaskColor(self):
        # Remove the # sign from QColor.name():
        choose_color_dialog = QColorDialog()
        color = choose_color_dialog.getColor()
        if color.isValid():
            color_ = color.name()[1:]
            self.qfill = color_
            self.changeButtonColor(self.mask_color_button, color_)

    def getNewOfillColor(self):
        # Remove the # sign from QColor.name():
        choose_color_dialog = QColorDialog()
        color = choose_color_dialog.getColor()
        if color.isValid():
            color_ = color.name()[1:]
            self.ofill = color_
            self.changeButtonColor(self.ofill_button, color_)

    def changeButtonColor(self, button, color):
        pixmap = QPixmap(128,18)
        qcolour = QtGui.QColor(0, 0, 0)
        qcolour.setNamedColor("#" + color)
        pixmap.fill(qcolour)
        button.setIcon(QIcon(pixmap))
        button.setIconSize(QSize(128, 18))

    def setupUi(self):
        ### shape color for questions:
        qfill_label = QLabel('Question shape')
        self.mask_color_button = QPushButton()
        self.mask_color_button.connect(self.mask_color_button,
                                  SIGNAL("clicked()"),
                                  self.getNewMaskColor)
        ### initial shape color:
        ofill_label = QLabel('Initial shape')
        self.ofill_button = QPushButton()
        self.ofill_button.connect(self.ofill_button,
                                SIGNAL("clicked()"),
                                self.getNewOfillColor)

        ### set colors
        self.changeButtonColor(self.ofill_button, self.ofill)
        self.changeButtonColor(self.mask_color_button, self.qfill)

        ### layout
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        colors_heading = QLabel("<b>Colors</b>")
        fields_heading = QLabel("<b>Custom Field Names</b>")

        frame = QFrame()
        frame.setFrameShape(QFrame.HLine)
        frame.setFrameShadow(QFrame.Sunken)

        grid.addWidget(colors_heading, 0, 0, 1, 6)
        grid.addWidget(qfill_label, 1, 1, 1, 2)
        grid.addWidget(self.mask_color_button, 1, 3, 1, 2)
        grid.addWidget(ofill_label, 2, 1, 1, 2)
        grid.addWidget(self.ofill_button, 2, 3, 1, 2)
        grid.addWidget(frame, 3, 0, 1, 6)
        grid.addWidget(fields_heading, 4, 0, 1, 6)

        # Fields

        fields_text = ("Changing any of the entries below will rename "
        "the corresponding default field of the IO Enhanced note type. "
        "This is the only way you can rename any of the default fields. "
        "<br><br><i>Renaming these fields through Anki's regular dialogs "
        "will cause the add-on to fail. So please don't do that.</i>")

        fields_description = QLabel(fields_text)
        fields_description.setWordWrap(True)
        grid.addWidget(fields_description, 5, 0, 1, 6)

        self.lnedit = {}
        nr = 6
        c = 0
        for key in IO_FLDS_IDS:
            if nr == 12: # switch to right columns
                c = 3
                nr = 6
            default_name = IO_FLDS[key]
            current_name = mw.col.conf['imgocc']['flds'][key]
            l = QLabel(default_name)
            l.setTextInteractionFlags(Qt.TextSelectableByMouse)
            t = QLineEdit()
            t.setText(current_name)
            grid.addWidget(l, nr, c, 1, 2)
            grid.addWidget(t, nr, c+1, 1, 2)
            self.lnedit[key] = t
            nr = nr+1
        
        button_box = QtGui.QDialogButtonBox(
                    QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
                )
        defaults_btn = button_box.addButton("Restore &Defaults",
           QDialogButtonBox.ResetRole)

        button_box.accepted.connect(self.onAccept)
        button_box.rejected.connect(self.onReject)
        
        self.connect(defaults_btn, SIGNAL("clicked()"), self.restoreDefaults)

        mainlayout = QVBoxLayout()
        mainlayout.addLayout(grid)
        mainlayout.addWidget(button_box)
        self.setLayout(mainlayout)
        self.setMinimumWidth(640)
        self.setMinimumHeight(520)
        self.setWindowTitle('Image Occlusion Enhanced Options')

    def restoreDefaults(self):
        for key in self.lnedit.keys():
            self.lnedit[key].setText(IO_FLDS[key])
            self.lnedit[key].setModified(True)
        self.changeButtonColor(self.ofill_button, self.sconf_d['ofill'])
        self.changeButtonColor(self.mask_color_button, self.sconf_d['qfill'])
        self.ofill = self.sconf_d['ofill']
        self.qfill = self.sconf_d['qfill']

    def renameFields(self):
        modified = False
        model = mw.col.models.byName(IO_MODEL_NAME)
        for key in self.lnedit.keys():
            if not self.lnedit[key].isModified():
                print "not modified:", key
                continue
            name = self.lnedit[key].text()
            oldname = mw.col.conf['imgocc']['flds'][key]
            if name is None or not name.strip():
                continue
            elif name == oldname:
                print "no change to", oldname
                continue
            idx = mw.col.models.fieldNames(model).index(oldname)
            fld = model['flds'][idx]
            if fld:
                mw.col.models.renameField(model, fld, name)
                mw.col.conf['imgocc']['flds'][key] = name
                modified = True
                print "renamed %s to %s" % (oldname, name)
        if modified:
            pass

    def onAccept(self):
        self.renameFields()
        mw.col.conf['imgocc']['ofill'] = self.ofill
        mw.col.conf['imgocc']['qfill'] = self.qfill
        mw.col.setMod()
        self.close()

    def onReject(self):
        self.close()

def ioAskUser(text, title="Image Occlusion Enhanced", parent=None, 
                    help="", defaultno=False, msgfunc=None):
    """Show a yes/no question. Return true if yes.
                Based on anki/utils.py by Damien Elmes"""
    if not parent:
        parent = mw.app.activeWindow()
    if not msgfunc:
        msgfunc = QMessageBox.question
    sb = QMessageBox.Yes | QMessageBox.No
    if help:
        sb |= QMessageBox.Help
    while 1:
        if defaultno:
            default = QMessageBox.No
        else:
            default = QMessageBox.Yes
        r = msgfunc(parent, title, text, sb, default)
        if r == QMessageBox.Help:
            ioHelp(help, parent=parent)
        else:
            break
    return r == QMessageBox.Yes

def ioHelp(help, title=None, text=None, parent=None):
    """Display an info message or a predefined help section"""
    io_link_wiki = "https://github.com/Glutanimate/image-occlusion-enhanced/wiki"
    io_link_tut = "https://www.youtube.com/playlist?list=PL3MozITKTz5YFHDGB19ypxcYfJ1ITk_6o"
    help_text = {}
    help_text["editing"] = """<center><b>Instructions for editing</b>: \
        <br><br> Each mask shape represents a card.\
        Removing any of the existing shapes will remove the corresponding card.\
        New shapes will generate new cards. You can change the occlusion type\
        by using the dropdown box on the left.<br><br>If you click on the \
        <i>Add new cards</i> button a completely new batch of cards will be \
        generated, leaving your originals untouched.<br><br> \
        <b>Actions performed in Image Occlusion's <i>Editing Mode</i> cannot be\
        easily undone, so please make sure to check your changes twice before\
        applying them.</b><br><br>The only exception to this are purely textual\
        changes to fields like the header or footer of your notes. These can\
        be fully reverted by using Ctrl+Z in the Browser or Reviewer view\
        </center>"""
    help_text["main"] = u"""<h2>Help and Support</h2>
        <p><a href="%s">Image Occlusion Enhanced Wiki</a></p>
        <p><a href="%s">Official Video Tutorial Series</a></p>
        <h2>Credits and License</h2>
        <p style="font-size:12pt;"><em>Copyright © 2016 \
        <a href="https://github.com/Glutanimate">Glutanimate</a></em></p>
        <p style="font-size:12pt;"><em>Copyright © 2012-2015 \
        <a href="https://github.com/tmbb">tmbb</a></em></p>
        <p style="font-size:12pt;"><em>Copyright © 2013 \
        <a href="https://github.com/steveaw">Steve AW</a></em></p>
        <p><em>Image Occlusion Enhanced</em> is licensed under the GNU GPLv3 License.</p>
        <p>Third-party open-source software shipped with <em>Image Occlusion Enhanced</em>:</p>
        <ul><li><p><a href="http://www.pythonware.com/products/pil/">Python Imaging Library</a> \
        (PIL) 1.1.7. Copyright (c) 1997-2011 by Secret Labs AB, Copyright (c) 1995-2011 by Fredrik \
        Lundh. Licensed under the <a href="http://www.pythonware.com/products/pil/license.htm">\
        PIL license</a></p></li>
        <li><p><a href="https://github.com/SVG-Edit/svgedit">SVG Edit</a> 2.6. \
        Copyright (c) 2009-2012 by SVG-edit authors. Licensed under the
        <a href="https://github.com/SVG-Edit/svgedit/blob/master/LICENSE">MIT license</a></p></li>
        </ul>
        """ % (io_link_wiki, io_link_tut)
    if help != "custom":
        text = help_text[help]
    if not title:
        title = "Image Occlusion Enhanced Help"
    if not parent:
        parent = mw.app.activeWindow()
    QMessageBox.about(parent, title, text)