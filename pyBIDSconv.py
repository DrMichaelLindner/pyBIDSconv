
"""
pyBIDSconv is a GUI based tool to convert MR dicom data into the BIDS structure.

See detailed description about the usage of pyBIDSconv in the User Manual (pyBIDSconv_Manual.html).
More information about the BIDS strucure can be found [here](http://bids.neuroimaging.io/)

The only thing you need to do is to create categorization file for your scanner or institute. An example of the
categorization file for a SIEMENS Prisma can be found in the example files. More information about the content of the
configuration file can be found in the pyBIDSconv_Manual.

In an additional configuration file you can specify specific cases of in- or exclusions of your dicom data to the
transfer process. An example of a configuration file for a SIEMENS Prisma can be found in the example files. More
information about the content of the configuration file can be found int he pyBIDSconv_Manual. An editor for the
configuration file is available in the GUI menu under tools.

Based on these two files pyBIDSconv will do the categorization of the dicom data of one subject at each time to the
appropriate BIDS structure folder automatically and shows you the catagorization on the screen where you can do the
additions (e.g. task names of funcitonal scans) or change manually. Beside the convcersation from the subject dicom
folder to the BIDS structure nearly all sidecar (.json and .txt) files for BIDS are created or updated automatically.
(This only work when you start the BIDS structure with pyBIDSconv).

For help and support feel free to contact: pyBIDSconv@gmx.co.uk

pyBIDSconv by Michael Lindner is licensed under CC BY 4.0

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY;

Version 1.1.1 by Michael Lindner
University of Reading, 2018
School of Psychology and Clinical Language Sciences
Center for Integrative Neuroscience and Neurodynamics

"""

import sys
import os
import numpy as np
import shutil
import glob
from datetime import datetime
import json
import pandas as pd
import webbrowser
import re
import wx
import wx.lib.scrolledpanel
import gzip

try:
    import pydicom as pydicom
except:
    import dicom as pydicom


# #####################################################################################################################
# #####################################################################################################################
#
# GetInput
#
# #####################################################################################################################
# #####################################################################################################################

ver = "1.1.1"
bidsver = "1.1.0"


class GetInput(wx.Frame):
    # This class creates the main GUI for pyBIDSconv

    def __init__(self):
        wx.Frame.__init__(self, None)

        # default colours
        # -------------------------------------
        backgroundcolor = wx.Colour(0, 0, 0)
        fontcolor = wx.Colour(255, 255, 255)
        fontcolor2 = wx.Colour(123, 123, 123)
        bluecolor = wx.Colour(52, 142, 216)
        buttonbackgroundcolor = wx.Colour(100, 100, 100)
        boxbackgroundcolor = wx.Colour(100, 100, 100)
        optboxbackgroundcolor = wx.Colour(60, 60, 60)


        # -------------------------------------
        # load defaults if exists
        # -------------------------------------
        # cwd = os.getcwd()

        defaultfile = "pyBIDSconv_defaults.py"

        if os.path.isfile(defaultfile):
            p, f = os.path.split(defaultfile)

            # os.chdir(p)
            sys.path.insert(0, p)

            try:
                dname = f[:-3]
                defaults = __import__(dname, fromlist=[''])
            except:
                defaults = __import__(f, fromlist=[''])

            catfilename = defaults.default_categorization_file
            cfgfilename = defaults.default_config_file

        else:
            cfgfilename = ""
            catfilename = ""

        # -------------------------------------
        # start creating GUI
        # -------------------------------------

        panel = wx.Panel(self)

        self.SetBackgroundColour(backgroundcolor)

        self.Bind(wx.EVT_CLOSE, self.onclosewindow)

        pp = 200
        textfontby = wx.Font(8, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        textfontdef = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        textfontmax = wx.Font(24, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        guiwidth = 500
        guiheight = 500+pp

        self.SetSize((guiwidth, guiheight))
        self.SetTitle('pyBIDSconv - Get Input')
        self.Centre()
        self.Show(True)
        
        # create emtpy output variable
        self.pathdicom = []
        self.subjectnumber = []
        self.subjectgroup = []
        self.sessionnumber = []
        self.categorizationfile = []
        self.configfile = []
        self.outputdir = []
        self.new = []
        
        # menubar
        # -----------------------------
        menubar = wx.MenuBar()
        filemenu = wx.Menu()
        helpmenu = wx.Menu()
        aboutmenu = wx.Menu()
        checkmenu = wx.Menu()
        toolmenu = wx.Menu()

        BIDS = wx.Menu()
        self.BIDSabout = BIDS.Append(wx.ID_ANY, 'about BIDS')
        self.BIDShome = BIDS.Append(wx.ID_ANY, 'BIDS Homepage')
        self.BIDSspecs = BIDS.Append(wx.ID_ANY, 'BIDS specifications')

        self.fileitem = filemenu.Append(wx.ID_EXIT, '&Quit\tCtrl+W', 'Quit application')
        self.helpitem = helpmenu.Append(wx.ID_ANY, '&Help', 'Help')
        self.aboutitem1 = aboutmenu.Append(wx.ID_ANY, '&About BIDS', BIDS)
        self.aboutitem2 = aboutmenu.Append(wx.ID_ANY, '&About pyBIDSconv', 'About pyBIDSconv')
        self.checkitem = checkmenu.Append(wx.ID_ANY, '&Open BIDS Validator', 'Open BIDS Validator')
        self.DSedititem = toolmenu.Append(wx.ID_ANY, '&Edit dataset_description.json', 'Edit dataset_description.json')
        self.create_def_item = toolmenu.Append(wx.ID_ANY, '&Create pyBIDSconv_defaults.py',
                                               'Create pyBIDSconv_defaults.py')
        self.create_config_item = toolmenu.Append(wx.ID_ANY, '&Create/Edit pyBIDSconv config file',
                                               'Create/Edit pyBIDSconv config file')

        # menubar.Append(filemenu, '&File')
        menubar.Append(helpmenu, '&Help')
        menubar.Append(aboutmenu, '&About')
        menubar.Append(checkmenu, '&Check existing BIDS structure')
        menubar.Append(toolmenu, '&Tools')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.onquit, self.fileitem)
        self.Bind(wx.EVT_MENU, self.on_main_help, self.helpitem)
        self.Bind(wx.EVT_MENU, self.onabout_bids, self.BIDSabout)
        self.Bind(wx.EVT_MENU, self.onbidshome, self.BIDShome)
        self.Bind(wx.EVT_MENU, self.onbidsspecs, self.BIDSspecs)
        self.Bind(wx.EVT_MENU, self.onvalidator, self.checkitem)
        self.Bind(wx.EVT_MENU, self.onedit_ds, self.DSedititem)
        self.Bind(wx.EVT_MENU, self.create_def, self.create_def_item)
        self.Bind(wx.EVT_MENU, self.create_conf, self.create_config_item)

        self.Bind(wx.EVT_MENU, self.onabout_pybidsconv, self.aboutitem2)

        # content
        wx.StaticBitmap(self, -1, wx.Bitmap("pyBIDSconv_logo.png", wx.BITMAP_TYPE_ANY), pos=(0, 0))  # , size=(50, 10))

        #text0 = wx.StaticText(panel, -1, label="pyBIDSconv version: " + ver, pos=(guiwidth / 2 - 80, pp - 40))
        #text0.SetFont(textfontdef)
        #text0.SetForegroundColour(bluecolor)
        text01 = wx.StaticText(panel, -1, label="for BIDS version: " + bidsver, pos=(guiwidth/2-90, pp-50))
        text01.SetFont(textfontdef)
        text01.SetForegroundColour(bluecolor)

        text1 = wx.StaticText(panel, -1, label="Subjects dicom directory:", pos=(20, 10+pp))
        text1.SetFont(textfontdef)
        text1.SetForegroundColour(fontcolor)
        self.inputdir = wx.TextCtrl(panel, pos=(20, 30+pp), size=(300, 25), name='inputdir')
        self.inputdir.SetForegroundColour(fontcolor)
        self.inputdir.SetBackgroundColour(boxbackgroundcolor)
        self.button1 = wx.Button(panel, -1, "Browse", pos=(350, 30+pp), name='button1')
        self.button1.SetFont(textfontdef)
        self.button1.SetForegroundColour(fontcolor)
        self.button1.SetBackgroundColour(buttonbackgroundcolor)
        self.button1.Bind(wx.EVT_BUTTON, self.onbutton1)

        text2 = wx.StaticText(panel, -1, label="Subject number:", pos=(20, 75+pp))
        text2.SetFont(textfontdef)
        text2.SetFont(textfontdef)
        text2.SetForegroundColour(fontcolor)
        self.subjnum = wx.TextCtrl(panel, pos=(130, 70+pp), size=(60, 25), name='subjnum')
        self.subjnum .SetForegroundColour(fontcolor)
        self.subjnum .SetBackgroundColour(boxbackgroundcolor)

        text3 = wx.StaticText(panel, -1, label="Group (optional):", pos=(200, 75+pp))
        text3.SetFont(textfontdef)
        text3.SetFont(textfontdef)
        text3.SetForegroundColour(fontcolor)
        self.group = wx.TextCtrl(panel, pos=(320, 70+pp), size=(120, 25), name='group')
        self.group.SetForegroundColour(fontcolor)
        self.group.SetBackgroundColour(optboxbackgroundcolor)

        text4 = wx.StaticText(panel, -1, label="Session number:", pos=(20, 115+pp))
        text4.SetFont(textfontdef)
        text4.SetFont(textfontdef)
        text4.SetForegroundColour(fontcolor)
        self.sessnum = wx.TextCtrl(panel, pos=(130, 110+pp), size=(60, 25), name='sessnum')
        self.sessnum.SetForegroundColour(fontcolor)
        self.sessnum.SetBackgroundColour(optboxbackgroundcolor)
        text4b = wx.StaticText(panel, -1, label="(Leave empty if only one session will exist)", pos=(200, 115+pp))
        text4b.SetFont(textfontdef)
        text4b.SetFont(textfontdef)
        text4b.SetForegroundColour(fontcolor)

        text5 = wx.StaticText(panel, -1, label="Output BIDS directory:", pos=(20, 150+pp))
        text5.SetFont(textfontdef)
        text5.SetFont(textfontdef)
        text5.SetForegroundColour(fontcolor)
        self.bidsdir = wx.TextCtrl(panel, pos=(20, 170+pp), size=(300, 25), name='bidsdir')
        self.bidsdir.SetForegroundColour(fontcolor)
        self.bidsdir.SetBackgroundColour(boxbackgroundcolor)
        self.button3 = wx.Button(panel, -1, "Browse", pos=(350, 170+pp), name='button3')
        self.button3.SetFont(textfontdef)
        self.button3.SetForegroundColour(fontcolor)
        self.button3.SetBackgroundColour(buttonbackgroundcolor)
        self.button3.Bind(wx.EVT_BUTTON, self.onbutton3)

        text6 = wx.StaticText(panel, -1, label="Configuration file:", pos=(20, 220+pp))
        text6.SetFont(textfontdef)
        text6.SetFont(textfontdef)
        text6.SetForegroundColour(fontcolor)
        self.cfgfile = wx.TextCtrl(panel, pos=(20, 240+pp), size=(300, 25), name='cfgfile')
        self.cfgfile.SetValue(cfgfilename)
        self.cfgfile.SetForegroundColour(fontcolor)
        self.cfgfile.SetBackgroundColour(boxbackgroundcolor)
        self.button4 = wx.Button(panel, -1, "Browse", pos=(350, 240+pp), name='button4')
        self.button4.SetFont(textfontdef)
        self.button4.SetForegroundColour(fontcolor)
        self.button4.SetBackgroundColour(buttonbackgroundcolor)
        self.button4.Bind(wx.EVT_BUTTON, self.onbutton4)

        text7 = wx.StaticText(panel, -1, label="Categorization file:", pos=(20, 280+pp))
        text7.SetFont(textfontdef)
        text7.SetForegroundColour(fontcolor)
        self.catfile = wx.TextCtrl(panel, pos=(20, 300+pp), size=(300, 25), name='catfile')
        self.catfile.SetValue(catfilename)
        self.catfile.SetForegroundColour(fontcolor)
        self.catfile.SetBackgroundColour(boxbackgroundcolor)
        self.button2 = wx.Button(panel, -1, "Browse", pos=(350, 300+pp), name='button2')
        self.button2.SetFont(textfontdef)
        self.button2.SetForegroundColour(fontcolor)
        self.button2.SetBackgroundColour(buttonbackgroundcolor)
        self.button2.Bind(wx.EVT_BUTTON, self.onbutton2)

        self.OKbutton = wx.Button(panel, -1, "Start", pos=(20, 350+pp), size=(450, 60), name='OKbutton')
        self.OKbutton.SetFont(textfontmax)
        self.OKbutton.SetForegroundColour(bluecolor)
        self.OKbutton.SetBackgroundColour(buttonbackgroundcolor)
        self.OKbutton.Bind(wx.EVT_BUTTON, self.onbuttonok)

        by = wx.StaticText(panel, -1,
                           label="pyBIDSconv (version: " + ver + ") by Michael Lindner, 2018",
                           pos=(20, 420+pp))
        by.SetFont(textfontby)
        by.SetForegroundColour(fontcolor2)

    def onbutton1(self, _):
        # app = wx.App()
        dialog = wx.DirDialog(None, "Choose a directory with dicom data of one subject:",
                              style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            pd1 = dialog.GetPath()
            dialog.Destroy()
            self.inputdir.SetValue(pd1)

    def onbutton2(self, _):
        # app = wx.App()
        dialog = wx.FileDialog(None, "Choose a categorization file:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            cf = dialog.GetPath()
            dialog.Destroy()
            self.catfile.SetValue(cf)

    def onbutton3(self, _):
        # app = wx.App()
        dialog = wx.DirDialog(None, "Choose output BIDS directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            od = dialog.GetPath()
            dialog.Destroy()
            self.bidsdir.SetValue(od)

    def onbutton4(self, _):
        # app = wx.App()
        dialog = wx.FileDialog(None, "Choose a configuration file:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            od = dialog.GetPath()
            dialog.Destroy()
            self.cfgfile.SetValue(od)

    def onbuttonok(self, _):
        pathdicom = self.inputdir.GetValue()
        subjectnumber = self.subjnum.GetValue()
        subjectgroup = self.group.GetValue()
        sessionnumber = self.sessnum.GetValue()
        categorizationfile = self.catfile.GetValue()
        configfile = self.cfgfile.GetValue()
        outputdir = self.bidsdir.GetValue()
        self.pathdicom = pathdicom
        self.subjectnumber = subjectnumber
        self.subjectgroup = subjectgroup
        self.sessionnumber = sessionnumber
        self.categorizationfile = categorizationfile
        self.configfile = configfile
        self.outputdir = outputdir

        # self.Close()

        CheckSubject(pathdicom, subjectnumber, subjectgroup, sessionnumber, categorizationfile, configfile, outputdir)

    @staticmethod
    def onquit(self, _):
        self.Close(True)

    def onclosewindow(self, _):
        self.Destroy()

    def onabout_pybidsconv(self, _):
        self.new = AboutpyBIDSconv(parent=None, id=-1)
        self.new.Show()

    def onabout_bids(self, _):
        self.new = AboutBIDS(parent=None, id=-1)
        self.new.Show()

    @staticmethod
    def onbidshome(_):
        BIDShome()

    @staticmethod
    def onbidsspecs(_):
        BIDSspecs()

    @staticmethod
    def onvalidator(_):
        StartValidator()

    @staticmethod
    def onedit_ds(_):
        StartDSedit()

    @staticmethod
    def create_def(_):
        CreateDefaultFile()

    @staticmethod
    def create_conf(_):
        CreateConfigFile()

    @staticmethod
    def on_main_help(_):
        AboutMainHelp()
    

# #####################################################################################################################
# #####################################################################################################################
# 
# GetDCMinfo
# 
# #####################################################################################################################
# #####################################################################################################################

class CheckSubject:
    # This class creates the main GUI for pyBIDSconv

    def __init__(self, pathdicom, subjectnumber, subjectgroup, sessionnumber, 
                 categorizationfile, configfile, outputdir):

        # Check if subject already exists
        # -----------------------------------

        if int(float(subjectnumber)) > 99:
            subjnum = str(subjectnumber)
        else:
            if int(float(subjectnumber)) > 9:
                subjnum = "0" + str(subjectnumber)
            else:
                subjnum = "00" + str(subjectnumber)

        if subjectgroup:
            subjnum = subjectgroup + subjnum

        subject = "sub-" + subjnum
        subjectfolder = os.path.join(outputdir, subject)
        subjexist = os.path.exists(os.path.join(subjectfolder))

        subjtext2log = ""

        if subjexist:  # if subject exists

            # Check if session subfolders exist
            dirs = filter(lambda x: os.path.isdir(os.path.join(subjectfolder, x)), os.listdir(subjectfolder))
            sessindices = [i for i, s in enumerate(dirs) if 'ses' in s]

            if not sessindices:  # if session fubfolders exist

                # Message Dialog
                # f1 = wx.App()
                winfo = "WARNING: Subject " + subject + " already exists in the BIDS directory : " + outputdir + \
                        " \nPlease check if your input was correct!! \n"
                winfo_yes = "Press YES to DELETE " + subject + \
                            " from the BIDS directory and CONTINUE with the conversion. \n"
                winfo_no = "Press NO to KEEP " + subject + " and STOP this conversion process. \n"
                d = wx.MessageDialog(
                    None, winfo + winfo_yes + winfo_no, 
                    "Warning", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                answer = d.ShowModal()
                d.Destroy()

                # If delete (YES) selected
                if answer == wx.ID_YES:

                    # 2. Message Dialog to be sure
                    # f2 = wx.App()
                    winfo2 = "Are you sure that you want to DELETE " + subject + \
                             " \nfrom the BIDS directory: " + outputdir + "?"
                    d2 = wx.MessageDialog(
                        None, winfo2, 
                        "Warning", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                    answer2 = d2.ShowModal()
                    d2.Destroy()

                    # If delete (YES) selected
                    if answer2 == wx.ID_YES:

                        try:
                            # delete folder
                            shutil.rmtree(subjectfolder.encode('ascii', 'ignore'))

                            subjtext2log = subjtext2log + "\t- DELETED " + subject + \
                                           " from the BIDS directory: " + outputdir + " \n\n"

                            GetDCMinfo(pathdicom, subjectnumber, subjectgroup, sessionnumber, categorizationfile, 
                                       configfile, outputdir, subjtext2log)

                        except OSError as ex:
                            print(ex)

            else:  # if a session subfolder exists

                if not sessionnumber:  # if no session was specified

                    # Try to add session to non session subject - Warning and not allow
                    # --------------------------------------------------------------------
                    # f1 = wx.App()
                    winfo = "WARNING: Subject " + subject + \
                            " already exists with Session subfolders in the BIDS directory : " + outputdir + "\n"
                    winfo2 = "You did not specify a session in here. " + \
                             "Transfer to BIDS is not possible with these settings! \n"
                    winfo3 = "Please check if your input was correct!!"

                    d = wx.MessageDialog(
                        None, winfo + winfo2 + winfo3, 
                        "Warning", wx.CANCEL | wx.ICON_QUESTION)
                    d.ShowModal()
                    d.Destroy()

                else:  # if a session was specified

                    # Check if same session already exists
                    # -------------------------------------------
                    sessnum = str(sessionnumber)

                    number = []

                    for ss in range(len(sessindices)):
                        t = dirs[sessindices[ss]]
                        m, n = t.split('-')
                        number.append(n)

                    sessexistindex = [i for i, s in enumerate(number) if sessnum in s]

                    if sessexistindex:  # if session subfolder already exists

                        # if same session already exist, message dialog to delete or skip
                        # ------------------------------------------------------------------
                        # f1 = wx.App()
                        winfo = "WARNING: Subject " + subject + " session " + sessnum + \
                                " already exists in the BIDS directory : " + outputdir + \
                                " \nPlease check if your input was correct!! \n"
                        winfo_yes = "Press YES to DELETE " + subject + " session " + sessnum + \
                                    " from the BIDS directory and CONTINUE with the conversion. \n"
                        winfo_no = "Press NO to KEEP " + subject + " session " + sessnum + \
                                   " and STOP this conversion process. \n"
                        d = wx.MessageDialog(
                            None, winfo + winfo_yes + winfo_no, 
                            "Warning", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                        answer2 = d.ShowModal()
                        d.Destroy()

                        if answer2 == wx.ID_YES:

                            subjectfolder = os.path.join(outputdir, "sub-" + subjnum, "ses-" + sessnum)

                            try:
                                # delete subfolder
                                shutil.rmtree(subjectfolder.encode('ascii', 'ignore'))

                                subjtext2log = subjtext2log + "\t- DELETED " + subject + " session " + \
                                               sessnum + " from the BIDS directory: " + outputdir + " \n\n"

                                GetDCMinfo(pathdicom, subjectnumber, subjectgroup, sessionnumber, categorizationfile, 
                                           configfile, outputdir, subjtext2log)

                            except OSError as ex:
                                print(ex)

                    else:  # if session subfolder does not exist

                        GetDCMinfo(pathdicom, subjectnumber, subjectgroup, sessionnumber, categorizationfile, 
                                   configfile, outputdir, subjtext2log)

        else:
            # if subject does not exist simply go ahead
            # ----------------------------------------------
            GetDCMinfo(pathdicom, subjectnumber, subjectgroup, sessionnumber, categorizationfile, configfile, 
                       outputdir, subjtext2log)


class GetDCMinfo:
    def __init__(self, pathdicom, subjectnumber, subjectgroup, sessionnumber, categorizationfile, configfile, 
                 outputdir, subjtext2log):

        # ---------------------------
        # import config file
        # ---------------------------
        cwd = os.getcwd()

        p, f = os.path.split(configfile)

        # os.chdir(p)
        sys.path.insert(0, p)

        try:
            mname = f[:-3]
            cfg = __import__(mname, fromlist=[''])
        except:
            cfg = __import__(f, fromlist=[''])

        # os.chdir(cwd)

        # -------------------------------------------------
        # get decision rules from categorization file
        # -------------------------------------------------
        rule_seq_type = []
        rule_seq_act = []
        rule_seq_desc = []
        rule_seq_name = []
        rule_label = []

        # with open('/media/michael/SSD/DICOM_to_BIDS_test/CINNrules_DCM2BIDS.txt') as infile:
        with open(categorizationfile) as infile:
            for line in infile:
                tsplit = line.split("\t")
                rule_seq_type.append(tsplit[0])
                rule_seq_name.append(tsplit[1])
                rule_seq_act.append(tsplit[2])
                rule_seq_desc.append(tsplit[3])
                rule_label.append(tsplit[4])

        # get uniques of columns in categorization file
        unique_seq_name = list(set(rule_seq_name))
        unique_seq_act = list(set(rule_seq_act))
        unique_seq_desc = list(set(rule_seq_desc))

        # create empty dict
        dictname = {}
        dictact = {}
        dictdesc = {}

        # create dictionaries of indices
        for ii in range(len(unique_seq_name)):
            indices = [i for i, x in enumerate(rule_seq_name) if x == unique_seq_name[ii]]
            # Fill in the entries one by one
            dictname[unique_seq_name[ii]] = indices

        for ii in range(len(unique_seq_act)):
            indices = [i for i, x in enumerate(rule_seq_act) if x == unique_seq_act[ii]]
            # Fill in the entries one by one
            dictact[unique_seq_act[ii]] = indices

        for ii in range(len(unique_seq_desc)):
            indices = [i for i, x in enumerate(rule_seq_desc) if x == unique_seq_desc[ii]]
            # Fill in the entries one by one
            dictdesc[unique_seq_desc[ii]] = indices

        # ----------------------
        # get dicom info
        # ----------------------
        list_dicom_files = []  # create an empty list
        for dirName, subdirList, fileList in os.walk(pathdicom):
            for filename in fileList:
                if ".dcm" in filename.lower():  # check whether the file's DICOM
                    list_dicom_files.append(os.path.join(dirName, filename))

        if len(list_dicom_files) == 0:
            # f1 = wx.App()
            winfo = "No dicom files found in : " + pathdicom + " \nPlease check if your input was correct!! \n"
            d = wx.MessageDialog(
                None, winfo, 
                "Warning", wx.OK | wx.ICON_QUESTION)
            d.ShowModal()
            d.Destroy()
            return

        sn_array = np.array([])
        seq_array = np.array([])
        seqname_array = np.array([])
        act_array = np.array([])
        acq_time_list = []
        it_val_list = []
        it_len_array = np.array([])
        echotime_array = np.array([])
        echonumber_array = np.array([])

        # multiband_array = np.array([])
        dti_array = np.array([])

        patinfo = [''] * 2

        # ------------------------------------------
        # Loop over dicom files
        # ------------------------------------------
        for ii in range(len(list_dicom_files)):
            dcm = pydicom.read_file(list_dicom_files[ii])

            if patinfo[0] == '':
                try:
                    patinfo[0] = str(int(re.sub("Y", "", dcm.PatientAge)))
                    patinfo[1] = dcm.PatientSex
                except:
                    pass

            sn_array = np.append(sn_array, dcm.SeriesNumber)
            seq_array = np.append(seq_array, dcm.SeriesDescription)
            it_val_list.append(dcm.ImageType)
            it_len_array = np.append(it_len_array, len(dcm.ImageType))

            try:
                a1 = dcm.AcquisitionDate
                a2 = dcm.AcquisitionTime
                dat = a1[0:4] + "-" + a1[4:6] + "-" + a1[6:8] + "T" + a2[0:2] + ":" + a2[2:4] + ":" + a2[4:6]
                acq_time_list.append(dat)
            except:
                acq_time_list.append("")

            try:
                echotime_array = np.append(echotime_array, dcm.EchoTime)
            except:
                echotime_array = np.append(echotime_array, "")
            try:
                echonumber_array = np.append(echonumber_array, dcm.EchoNumber)
            except:
                echonumber_array = np.append(echonumber_array, "")

            try:
                seqname_array = np.append(seqname_array, dcm.SequenceName)
            except:
                seqname_array = np.append(seqname_array, " ")
            try:
                act_array = np.append(act_array, dcm.MRAcquisitionType)
            except:
                act_array = np.append(act_array, " ")

            if dcm.Manufacturer == "SIEMENS":
                # try:
                # if dcm[0x0019, 0x1029]:
                # multiband_array = np.append(multiband_array, 1)
                # else:
                # multiband_array = np.append(multiband_array, 0)
                # except:
                # multiband_array = np.append(multiband_array, 0)

                try:
                    if dcm[0x0019, 0x100C]:
                        dti_array = np.append(dti_array, 1)
                    else:
                        dti_array = np.append(dti_array, 0)
                except:
                    dti_array = np.append(dti_array, 0)

            elif dcm.Manufacturer == "PHILIPS":
                # try:
                # if dcm[0x0019, 0x1029]:  # #################################### needs to be adjusted
                # multiband_array = np.append(multiband_array, 1)
                # else:
                # multiband_array = np.append(multiband_array, 0)
                # except:
                # multiband_array = np.append(multiband_array, 0)

                try:
                    if dcm[0x0018, 0x9089]:
                        dti_array = np.append(dti_array, 1)
                    else:
                        dti_array = np.append(dti_array, 0)
                except:
                    dti_array = np.append(dti_array, 0)
                try:
                    if dcm[0x2001, 0x1004]:
                        dti_array = np.append(dti_array, 1)
                    else:
                        dti_array = np.append(dti_array, 0)
                except:
                    dti_array = np.append(dti_array, 0)

            elif dcm.Manufacturer == "GE":
                # try:
                # if dcm[0x0019, 0x1029]:  # #################################### needs to be adjusted
                # multiband_array = np.append(multiband_array, 1)
                # else:
                # multiband_array = np.append(multiband_array, 0)
                # except:
                # multiband_array = np.append(multiband_array, 0)

                try:
                    if dcm[0x0019, 0x10BC]:
                        dti_array = np.append(dti_array, 1)
                    else:
                        dti_array = np.append(dti_array, 0)
                except:
                    dti_array = np.append(dti_array, 0)

            try:
                if dcm.Manufacturer == "SIEMENS":
                    if dcm[0x0019, 0x100C]:
                        dti_array = np.append(dti_array, 1)
                    else:
                        dti_array = np.append(dti_array, 0)
                elif dcm.Manufacturer == "PHILIPS":
                    if dcm[0x0018, 0x9089]:
                        dti_array = np.append(dti_array, 1)
                    elif dcm[0x2001, 0x1004]:
                        dti_array = np.append(dti_array, 1)
                    else:
                        dti_array = np.append(dti_array, 0)
                elif dcm.Manufacturer == "GE":
                    if dcm[0x0019, 0x10BC]:
                        dti_array = np.append(dti_array, 1)
                    else:
                        dti_array = np.append(dti_array, 0)
            except:
                dti_array = np.append(dti_array, 0)

            # try:
            # if dcm.Private_0019_1029:
            # dti_array = np.append(dtiname_array, 1)
            # else:
            # dti_array = np.append(dtiname_array, 0)
            # except:
            # dti_array = np.append(dtiname_array, 0)

        it_len_array = it_len_array.astype(int)

        # get uniques
        # ----------------------
        uniques = np.unique(sn_array)

        # ----------------------
        # get info from uniques
        # ----------------------
        firstval_array = np.array([])
        nrvols_array = np.array([])
        itl_array = np.array([])
        it_list = []
        it_list2 = []
        it_list_all = []

        # loop over unique sequences and get values for each
        for ii in range(len(uniques)):
            fv = np.nonzero(sn_array == uniques[ii])[0][0]
            firstval_array = np.append(firstval_array, fv)
            a = np.where(sn_array == uniques[ii])
            nrvols_array = np.append(nrvols_array, len(a[0]))
            itl_array = np.append(itl_array, it_len_array[fv])
            it_list.append(it_val_list[fv][int(it_len_array[fv])-1])
            it_list2.append(it_val_list[fv][2])
            it_list_all.append(it_val_list[fv])

        # itl_array = itl_array.astype(int)
        firstval_array = firstval_array.astype(int)
        nrvols_array = nrvols_array.astype(int)
        un_seq = []
        un_seqname = []
        un_act = []
        un_sn = []
        acq_time = []
        # un_mb = []
        un_dti = []

        for ii in range(len(firstval_array)):
            un_seq.append(seq_array[firstval_array[ii]])
            un_seqname.append(seqname_array[firstval_array[ii]])
            un_act.append(act_array[firstval_array[ii]])
            un_sn.append(sn_array[firstval_array[ii]])
            acq_time.append(acq_time_list[firstval_array[ii]])
            # un_mb.append(multiband_array[firstval_array[ii]])
            un_dti.append(dti_array[firstval_array[ii]])

        sn_array = sn_array.astype(int)

        # print(un_mb)
        # print(un_dti)

        sn = sn_array.tolist()

        un_sn = map(int, un_sn)

        # Create list of filenames for each sequence
        dcmfiles = [''] * len(un_sn)
        un_echo = [''] * len(un_sn)

        for ii in range(len(un_sn)):
            index = [i for i, j in enumerate(sn) if j == un_sn[ii]]

            ff = [''] * len(index)

            for nn in range(len(index)):
                ff[nn] = list_dicom_files[index[nn]]

            dcmfiles[ii] = [x.encode('UTF8') for x in ff]

            ect = echotime_array[index]
            un_echo[ii] = np.unique(ect)

        # ----------------------
        # categorize sequences
        # ----------------------

        # create empty lists
        scantype_list = ["None"] * len(uniques)
        label_list = [''] * len(uniques)

        acq_name_list = [''] * len(uniques)
        rec_name_list = [''] * len(uniques)

        # create lower case versions of lists
        un_seq_l = [item.lower() for item in un_seq]
        un_seqname_l = [item.lower() for item in un_seqname]
        un_act_l = [item.lower() for item in un_act]
        # rule_seq_name_l = [item.lower() for item in rule_seq_name]
        # rule_seq_act_l = [item.lower() for item in rule_seq_act]
        # rule_seq_desc_l = [item.lower() for item in rule_seq_desc]

        # loop over unique sequences
        # --------------------------------------
        for ii in range(len(un_seqname_l)):

            # specify acq label of found multiband scans
            # if un_mb[ii] == 1.0:
            #     acq_name_list[ii] = "Grappa"

            # print(un_seqname_l[ii])
            # print(un_seq_l[ii])

            x = [value for key, value in dictname.items() if key.lower() in un_seqname_l[ii]]
            res = [j for i in x for j in i]
            print(res)

            if len(res) > 1:
                x = [value for key, value in dictact.items() if key.lower() in un_act_l[ii].lower()]
                res2 = [j for i in x for j in i]
                res = [value for value in res if value in res2]

            print(res)
            if len(res) > 1:
                x = [value for key, value in dictdesc.items() if key.lower() in un_seq_l[ii].lower()]
                res2 = [j for i in x for j in i]
                res = [value for value in res if value in res2]

            print(res)

            if len(res) == 1:
                label_list[ii] = rule_label[res[0]]
                scantype_list[ii] = rule_seq_type[res[0]]
            else:
                label_list[ii] = '0'
                scantype_list[ii] = '0'

        print(scantype_list)
        print(label_list)

        # create reconstruction and exclude vector
        # --------------------------------------------
        exclusion_array = np.zeros(len(uniques))
        exclusion_array = exclusion_array.astype(int)

        # Check if specific reconstructions are obvious
        for ii in range(len(cfg.ReconstructionInfoInImageType)):
            for jj in range(len(it_list_all)):
                c = [i for i, item in enumerate(it_list_all[jj]) if cfg.ReconstructionInfoInImageType[ii] in item]
                for cc in range(len(c)):
                    rec_name_list[jj] = cfg.ReconstructionInfoInImageType[ii]

        # Check for phase encoding directions in filenames
        try:
            for ii in range(len(un_seq_l)):
                if scantype_list[ii] == "fmap":
                    s = un_seq_l[ii]
                    for jj in range(len(cfg.PhaseInfoForFmapsBySequenceDescriptionSubstring)):
                        if cfg.PhaseInfoForFmapsBySequenceDescriptionSubstring[jj] in s.lower():
                            acq_name_list[ii] = cfg.PhaseInfoForFmapsBySequenceDescriptionSubstring[jj][1:]
        except:
            pass

        # define exclusions based on sequence name parts
        for ii in range(len(cfg.ExclusionsBySequenceDescriptionContent)):
            c = [i for i, item in enumerate(un_seq_l) if cfg.ExclusionsBySequenceDescriptionContent[ii] in item]
            for cc in range(len(c)):
                exclusion_array[c[cc]] = 1
                acq_name_list[c[cc]] = cfg.ExclusionsBySequenceDescriptionContent[ii]

        print(exclusion_array)

        # define exclusions based on sequence name end
        for ii in range(len(cfg.ExclusionsBySequenceDescriptionEnd)):
            c = []
            for sco in range(len(un_seq_l)):
                a = un_seq_l[sco].lower()
                b = cfg.ExclusionsBySequenceDescriptionEnd[ii].lower()

                if a.endswith(b):
                    c.append(sco)
                    print(a + " > " + b)
            # c = [i for i, item in enumerate(un_seq_l) if cfg.ExclusionsBySequenceDescriptionEnd[ii] in item]
            for cc in range(len(c)):
                exclusion_array[c[cc]] = 1
                acq_name_list[c[cc]] = cfg.ExclusionsBySequenceDescriptionEnd[ii]

        exclusion_array = exclusion_array.astype(int)

        print(exclusion_array)

        # go to next step
        # x = wx.App()
        frame = CheckSeqs(un_seq, scantype_list, exclusion_array, nrvols_array, subjectnumber, subjectgroup,
                          sessionnumber, subjtext2log, acq_name_list, rec_name_list, label_list, dcmfiles, pathdicom,
                          outputdir, it_list2, acq_time, patinfo, un_echo)
        frame.Show(True)


# #####################################################################################################################
# #####################################################################################################################
#
# CheckSeqs
#
# #####################################################################################################################
# #####################################################################################################################


class CheckSeqs(wx.Frame):
    def __init__(self, un_seq, scantype_list, exclusion_array, nrvols_array, subjectnumber, subjectgroup, sessionnumber, subjtext2log, acq_name_list, rec_name_list, label_list, dcmfiles, pathdicom, outputdir, it_list2, acq_time, patinfo, un_echo):
        wx.Frame.__init__(self, None)

        # default colours
        # -------------------------------------
        self.backgroundcolor = wx.Colour(0, 0, 0)
        self.fontcolor = wx.Colour(255, 255, 255)
        self.NOfontcolor = wx.Colour(55, 55, 55)
        self.fontcolor2 = wx.RED
        self.bluecolor = wx.Colour(52, 142, 216)
        self.buttonbackgroundcolor = wx.Colour(100, 100, 100)
        self.boxbackgroundcolor = wx.Colour(100, 100, 100)
        self.optboxbackgroundcolor = wx.Colour(60, 60, 60)


        # self.panel = wx.Panel(self)
        # self.panel = wx.lib.scrolledpanel.ScrolledPanel(self)
        self.panel = wx.ScrolledWindow(self, -1)
        self.SetBackgroundColour(self.backgroundcolor)

        self.Bind(wx.EVT_CLOSE, self.onclosewindow)

        labels2 = ['---', 'anat', 'func', 'dwi', 'fmap']
        exctxt = ['Yes', 'No']
        self.exccol = [self.fontcolor, self.NOfontcolor]
        self.fmaplabel = ['fieldmap', 'magnitude', 'magnitude1', 'magnitude2', 'phasediff', 'phase1', 'phase2', 'epi']
        self.anatlabel = ['---', 'T1w', 'T2w', 'T1rho', 'T1map', 'T2map', 'T2star', 'FLAIR', 'FLASH', 'PD', 'PDmap',
                          'PDT2', 'inplaneT1', 'inplaneT2', 'angio', 'defacemask']
        self.funclabel = ['---', 'bold', 'sbref', 'asl']
        self.dwilabel = ['---', 'dwi', 'bvec', 'bval']
        self.alllabel = ['---', 'T1w', 'T2w', 'T1rho', 'T1map', 'T2map', 'T2star', 'FLAIR', 'FLASH', 'PD', 'PDmap',
         'PDT2', 'inplaneT1', 'inplaneT2', 'angio', 'defacemask', 'bold', 'sbref', 'asl', 'dwi', 'bvec', 'bval',
         'fieldmap', 'magnitude', 'magnitude1', 'magnitude2', 'phasediff', 'phase1', 'phase2', 'epi']

        self.acq_name_list = acq_name_list
        self.rec_name_list = rec_name_list
        self.label_list = label_list
        self.exclusion_array = exclusion_array
        self.dcmfiles = dcmfiles
        self.un_seq = un_seq
        self.pathdicom = pathdicom
        self.subjectnumber = subjectnumber
        self.subjectgroup = subjectgroup
        self.sessionnumber = sessionnumber
        self.outputdir = outputdir
        self.acq_time = acq_time
        self.patinfo = patinfo
        self.un_echo = un_echo
        self.subjtext2log = subjtext2log

        scancat = np.array([])
        for jj in range(len(scantype_list)):
            la = [labels2.index(i) for i in labels2 if scantype_list[jj] in i]
            if not la:
                scancat = np.append(scancat, 0)
            else:
                scancat = np.append(scancat, la)

        scancat = scancat.astype(int)

        scancat2 = scancat
        for ii in range(len(scancat2)):
            if exclusion_array[ii] == 1:
                scancat2[ii] = 0

        # guess reference for fmap
        refvalue = [''] * len(un_seq)
        reflab = [''] * len(un_seq)
        mm = [''] * 2
        cc = [2, 3]
        for ii in range(len(scancat2)):
            if scancat2[ii] == 4:
                x = scancat[:ii]
                y = list(reversed(x))
                for jj in range(len(cc)):
                    try:
                        mm[jj] = len(y) - y.index(cc[jj]) - 1
                    except:
                        mm[jj] = 0
                if mm[0] > mm[1]:
                    refvalue[ii] = mm[0]
                else:
                    refvalue[ii] = mm[1]

                if it_list2[ii] == "M":
                    reflab[ii] = 1

                    if it_list2[ii-1] == "M" and scancat2[ii-1] == 4:
                        reflab[ii] = 3
                        reflab[ii-1] = 2

                elif it_list2[ii] == "P":
                    reflab[ii] = 4

                    if it_list2[ii-1] == "P" and scancat2[ii-1] == 4:
                        reflab[ii] = 6
                        reflab[ii-1] = 5
                else:
                    reflab[ii] = 1

        # specify taskname list
        c = [i for i, item in enumerate(scantype_list) if "func" in item]
        self.taskname_list = [""] * len(scantype_list)
        ic = 1
        for iii in range(len(c)):
            self.taskname_list[c[iii]] = "Taskname" + str(ic)
            ic += 1

        # Specify GUI size
        screenSize = wx.DisplaySize()
        # screenWidth = screenSize[0]
        screenHeight = screenSize[1]

        guiwidth = 1200
        self.vertshift = 100
        guiheight = len(un_seq)*40+self.vertshift+120

        if guiheight >= screenHeight*0.7:
            # self.SetSize((guiwidth, floor(screenHeight*0.9)))
            self.SetSize((guiwidth, screenHeight * 0.7))
            self.panel.SetScrollbars(0, 10, 0, guiheight /10)
            self.panel.SetScrollRate(1, 1)
        else:
            self.SetSize((guiwidth, guiheight))

        self.SetTitle('pyBIDSconv - Check sequence categorization')
        self.Centre()
        # self.panel.SetupScrolling()
        self.panel.SetSize((guiwidth, guiheight))
        self.Show(True)


        # app = wx.App()

        # menubar
        # -----------------------------
        menubar = wx.MenuBar()
        filemenu = wx.Menu()
        helpmenu = wx.Menu()
        aboutmenu = wx.Menu()

        BIDS = wx.Menu()
        self.BIDSabout = BIDS.Append(wx.ID_ANY, 'about BIDS')
        self.BIDShome = BIDS.Append(wx.ID_ANY, 'BIDS Homepage')
        self.BIDSspecs = BIDS.Append(wx.ID_ANY, 'BIDS specifications')

        self.fileitem = filemenu.Append(wx.ID_EXIT, '&Quit\tCtrl+W', 'Quit application')

        self.helpitem = helpmenu.Append(wx.ID_ANY, '&Help', 'Help')
        self.manualitem = helpmenu.Append(wx.ID_ANY, '&Manual', 'Manual')

        self.aboutitem1 = aboutmenu.Append(wx.ID_ANY, '&About BIDS', BIDS)
        self.aboutitem2 = aboutmenu.Append(wx.ID_ANY, '&About', 'About pyBIDSconv')

        menubar.Append(helpmenu, '&Help')
        menubar.Append(aboutmenu, '&About')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.onquit, self.fileitem)
        self.Bind(wx.EVT_MENU, self.on_label_help, self.helpitem)
        self.Bind(wx.EVT_MENU, self.on_main_help, self.manualitem)
        self.Bind(wx.EVT_MENU, self.onabout_bids, self.aboutitem1)
        self.Bind(wx.EVT_MENU, self.onabout_pybidsconv, self.aboutitem2)
        self.Bind(wx.EVT_MENU, self.onabout_bids, self.BIDSabout)
        self.Bind(wx.EVT_MENU, self.onbidshome, self.BIDShome)
        self.Bind(wx.EVT_MENU, self.onbidsspecs, self.BIDSspecs)

        # title subject text
        textfonttitle = wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        headerfont = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        if int(float(subjectnumber)) > 99:
            subjnum = str(subjectnumber)
        else:
            if int(float(subjectnumber)) > 9:
                subjnum = "0" + str(subjectnumber)
            else:
                subjnum = "00" + str(subjectnumber)

        if subjectgroup:
            subjnum = subjectgroup + subjnum

        # Check output folder (add subj folder and subfolders)
        if not sessionnumber == "":
            sessnum = str(sessionnumber)

        subjectinfo = 'sub-' + subjnum
        infoshift = 150

        if not sessionnumber == '':
            subjectinfo = subjectinfo + '_ses-' + sessnum
            infoshift += 100

        subjtext = wx.StaticText(self.panel, -1, label=subjectinfo, pos=(guiwidth/2-infoshift, self.vertshift/4))
        subjtext.SetFont(textfonttitle)
        subjtext.SetForegroundColour(self.bluecolor)

        # column headers
        t = wx.StaticText(self.panel, -1, label="Transfer?", pos=(20, self.vertshift*2/3))
        t.SetFont(headerfont)
        t.SetForegroundColour(self.fontcolor)
        t = wx.StaticText(self.panel, -1, label="Folder", pos=(100, self.vertshift*2/3))
        t.SetFont(headerfont)
        t.SetForegroundColour(self.fontcolor)
        t = wx.StaticText(self.panel, -1, label="_task-", pos=(180, self.vertshift*2/3))
        t.SetFont(headerfont)
        t.SetForegroundColour(self.bluecolor)
        t = wx.StaticText(self.panel, -1, label="_run-", pos=(300, self.vertshift*2/3))
        t.SetFont(headerfont)
        t.SetForegroundColour(self.bluecolor)
        t = wx.StaticText(self.panel, -1, label="_acq-", pos=(380, self.vertshift*2/3))
        t.SetFont(headerfont)
        t.SetForegroundColour(self.bluecolor)
        t = wx.StaticText(self.panel, -1, label="_rec-", pos=(480, self.vertshift*2/3))
        t.SetFont(headerfont)
        t.SetForegroundColour(self.bluecolor)
        t = wx.StaticText(self.panel, -1, label="_label", pos=(580, self.vertshift*2/3))
        t.SetFont(headerfont)
        t.SetForegroundColour(self.bluecolor)

        t = wx.StaticText(self.panel, -1, label="Ref", pos=(690, self.vertshift*2/3))
        t.SetFont(headerfont)
        t.SetForegroundColour(self.fontcolor)
        t = wx.StaticText(self.panel, -1, label="Nr", pos=(780, self.vertshift*2/3))
        t.SetFont(headerfont)
        t.SetForegroundColour(self.fontcolor)
        t = wx.StaticText(self.panel, -1, label="NrVols", pos=(850, self.vertshift*2/3))
        t.SetFont(headerfont)
        t.SetForegroundColour(self.fontcolor)
        t = wx.StaticText(self.panel, -1, label="Sequence name", pos=(900, self.vertshift*2/3))
        t.SetFont(headerfont)
        t.SetForegroundColour(self.fontcolor)


        line = wx.StaticLine(self.panel, id=-1, pos=(10, self.vertshift*2/3+20), size=(guiwidth-40, 1), style=wx.LI_HORIZONTAL)
        line.SetForegroundColour(self.bluecolor)
        line.SetBackgroundColour(self.bluecolor)

        # ic = 0
        self.combo1 = {}
        self.combo2 = {}
        self.task = {}
        self.run = {}
        self.acq = {}
        self.rec = {}
        self.label = {}
        self.ref = {}
        self.new = []

        self.nrvols = {}
        self.seqnr = {}
        self.seqlabel = {}

        self.reflabel = {}

        indices = np.where(scancat == 0)
        indices = list(indices)
        # print(indices)
        print(scantype_list)
        for index in range(len(indices)):
            scantype_list[indices[0][index]] = 'None'
        print(scantype_list)




        ix = 0
        for i in range(len(un_seq)):

            ix = i

            self.seqnr[i] = wx.StaticText(self.panel, -1, label=str(i), pos=(780, self.vertshift+40*i), 
                                          name='seq'+str(i))
            self.seqnr[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
            self.nrvols[i] = wx.StaticText(self.panel, -1, label=str(nrvols_array[i]), pos=(850, self.vertshift+40*i), 
                                           name='nvol'+str(i))
            self.nrvols[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
            self.seqlabel[i] = wx.StaticText(self.panel, -1, label=un_seq[i], pos=(900, self.vertshift+40*i), 
                                             name='scan'+str(i))
            self.seqlabel[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])

            self.combo1[i] = wx.ComboBox(self.panel, choices=exctxt, pos=(20, self.vertshift+40*i-5), name='ex'+str(i))
            self.combo1[i].SetSelection(self.exclusion_array[i])
            self.combo1[i].Bind(wx.EVT_COMBOBOX, self.oncombo1)
            self.combo1[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
            self.combo1[i].SetBackgroundColour(self.boxbackgroundcolor)

            self.combo2[i] = wx.ComboBox(self.panel, choices=labels2, pos=(100, self.vertshift+40*i-5), 
                                         name='st'+str(i))
            self.combo2[i].SetSelection(scancat[i])
            self.combo2[i].Bind(wx.EVT_COMBOBOX, self.oncombo2)
            self.combo2[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
            self.combo2[i].SetBackgroundColour(self.boxbackgroundcolor)

            reflist = range(len(un_seq))
            del reflist[i]
            self.reflabel[i] = [str(k) for k in reflist]

            if scantype_list[i] == "func":
                self.task[i] = wx.TextCtrl(self.panel, pos=(180, self.vertshift+40*i-5), size=(100, 25),
                                           name='task'+str(i))
                self.task[i].SetValue(self.taskname_list[i])
                self.task[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.task[i].SetBackgroundColour(self.boxbackgroundcolor)

                self.run[i] = wx.TextCtrl(self.panel, pos=(300, self.vertshift+40*i-5), size=(30, 25),
                                          name='run'+str(i))
                self.run[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.run[i].SetBackgroundColour(self.optboxbackgroundcolor)

                self.acq[i] = wx.TextCtrl(self.panel, pos=(380, self.vertshift+40*i-5), size=(80, 25),
                                          name='acq'+str(i))
                self.acq[i].SetValue(self.acq_name_list[i])
                self.acq[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.acq[i].SetBackgroundColour(self.optboxbackgroundcolor)

                self.rec[i] = wx.TextCtrl(self.panel, pos=(480, self.vertshift+40*i-5), size=(80, 25),
                                          name='rec'+str(i))
                self.rec[i].SetValue(self.rec_name_list[i])
                self.rec[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.rec[i].SetBackgroundColour(self.optboxbackgroundcolor)

                self.label[i] = wx.ComboBox(self.panel, pos=(580, self.vertshift + 40 * i - 5),
                                            size=(90, 30), name='lab' + str(i))
                self.label[i].SetItems(self.funclabel)
                self.label[i].SetValue(self.label_list[i])
                self.label[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.label[i].SetBackgroundColour(self.boxbackgroundcolor)

                self.ref[i] = wx.TextCtrl(self.panel, pos=(690, self.vertshift+40*i-5), size=(40, 25), name='r'+str(i))
                self.ref[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.ref[i].SetBackgroundColour(self.boxbackgroundcolor)
                self.ref[i].Hide()

            elif scantype_list[i] == "anat":
                self.task[i] = wx.TextCtrl(self.panel, pos=(180, self.vertshift+40*i-5), size=(100, 25),
                                           name='task'+str(i))
                self.task[i].Hide()
                self.task[i].Clear()
                self.task[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.task[i].SetBackgroundColour(self.boxbackgroundcolor)

                self.run[i] = wx.TextCtrl(self.panel, pos=(300, self.vertshift+40*i-5), size=(30, 25),
                                          name='run'+str(i))
                self.run[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.run[i].SetBackgroundColour(self.optboxbackgroundcolor)

                self.acq[i] = wx.TextCtrl(self.panel, pos=(380, self.vertshift+40*i-5), size=(80, 25),
                                          name='acq'+str(i))
                self.acq[i].SetValue(self.acq_name_list[i])
                self.acq[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.acq[i].SetBackgroundColour(self.optboxbackgroundcolor)

                self.rec[i] = wx.TextCtrl(self.panel, pos=(480, self.vertshift+40*i-5), size=(80, 25),
                                          name='rec'+str(i))
                self.rec[i].SetValue(self.rec_name_list[i])
                self.rec[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.rec[i].SetBackgroundColour(self.optboxbackgroundcolor)

                # self.label[i] = wx.TextCtrl(self.panel, pos=(580, self.vertshift+40*i-5), size=(90, 25),
                #                             name='lab'+str(i))
                self.label[i] = wx.ComboBox(self.panel, pos=(580, self.vertshift + 40 * i - 5),
                                            size=(90, 30), name='lab' + str(i))
                self.label[i].SetItems(self.anatlabel)
                self.label[i].SetValue(self.label_list[i])
                self.label[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.label[i].SetBackgroundColour(self.boxbackgroundcolor)

                self.ref[i] = wx.TextCtrl(self.panel, pos=(690, self.vertshift+40*i-5), size=(40, 25), name='r'+str(i))
                self.ref[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.ref[i].SetBackgroundColour(self.boxbackgroundcolor)
                self.ref[i].Hide()

            elif scantype_list[i] == "dwi":
                self.task[i] = wx.TextCtrl(self.panel, pos=(180, self.vertshift+40*i-5), size=(100, 25),
                                           name='task'+str(i))
                self.task[i].Hide()
                self.task[i].Clear()
                self.task[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.task[i].SetBackgroundColour(self.boxbackgroundcolor)

                self.run[i] = wx.TextCtrl(self.panel, pos=(300, self.vertshift+40*i-5), size=(30, 25),
                                          name='run'+str(i))
                self.run[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.run[i].SetBackgroundColour(self.optboxbackgroundcolor)

                self.acq[i] = wx.TextCtrl(self.panel, pos=(380, self.vertshift+40*i-5), size=(80, 25),
                                          name='acq'+str(i))
                self.acq[i].SetValue(self.acq_name_list[i])
                self.acq[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.acq[i].SetBackgroundColour(self.optboxbackgroundcolor)

                self.rec[i] = wx.TextCtrl(self.panel, pos=(480, self.vertshift+40*i-5), size=(80, 25),
                                          name='rec'+str(i))
                self.rec[i].SetValue(self.rec_name_list[i])
                self.rec[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.rec[i].SetBackgroundColour(self.optboxbackgroundcolor)

                self.label[i] = wx.ComboBox(self.panel, pos=(580, self.vertshift + 40 * i - 5),
                                            size=(90, 30), name='lab' + str(i))
                self.label[i].SetItems(self.dwilabel)
                self.label[i].SetValue(self.label_list[i])
                self.label[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.label[i].SetBackgroundColour(self.boxbackgroundcolor)

                self.ref[i] = wx.TextCtrl(self.panel, pos=(690, self.vertshift+40*i-5), size=(40, 25), name='r'+str(i))
                self.ref[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.ref[i].SetBackgroundColour(self.boxbackgroundcolor)
                self.ref[i].Hide()

            elif scantype_list[i] == "fmap":
                self.task[i] = wx.TextCtrl(self.panel, pos=(180, self.vertshift+40*i-5), size=(100, 25),
                                           name='task'+str(i))
                self.task[i].Hide()
                self.task[i].Clear()
                self.task[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.task[i].SetBackgroundColour(self.boxbackgroundcolor)

                self.run[i] = wx.TextCtrl(self.panel, pos=(300, self.vertshift+40*i-5), size=(30, 25),
                                          name='run'+str(i))
                self.run[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.run[i].SetBackgroundColour(self.optboxbackgroundcolor)

                self.acq[i] = wx.TextCtrl(self.panel, pos=(380, self.vertshift+40*i-5), size=(80, 25),
                                          name='acq'+str(i))
                self.acq[i].SetValue(self.acq_name_list[i])
                self.acq[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.acq[i].SetBackgroundColour(self.optboxbackgroundcolor)

                self.rec[i] = wx.TextCtrl(self.panel, pos=(480, self.vertshift+40*i-5), size=(80, 25),
                                          name='rec'+str(i))
                self.rec[i].Hide()
                self.rec[i].Clear()
                self.rec[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.rec[i].SetBackgroundColour(self.optboxbackgroundcolor)

                self.label[i] = wx.ComboBox(self.panel, pos=(580, self.vertshift+40*i-5),
                                            size=(90, 30), name='lab'+str(i))
                self.label[i].SetItems(self.fmaplabel)
                self.label[i].SetSelection(reflab[i])
                self.label[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.label[i].SetBackgroundColour(self.boxbackgroundcolor)

                self.ref[i] = wx.TextCtrl(self.panel, pos=(690, self.vertshift+40*i-5), size=(40, 25), name='r'+str(i))
                self.ref[i].Show()
                self.ref[i].SetValue(str(refvalue[i]))
                self.ref[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.ref[i].SetBackgroundColour(self.boxbackgroundcolor)

            else:
                self.task[i] = wx.TextCtrl(self.panel, pos=(180, self.vertshift+40*i-5), size=(100, 25),
                                           name='task'+str(i))
                self.task[i].SetBackgroundColour(self.boxbackgroundcolor)
                self.task[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.task[i].Hide()
                self.task[i].Clear()

                self.run[i] = wx.TextCtrl(self.panel, pos=(300, self.vertshift+40*i-5), size=(30, 25),
                                          name='run'+str(i))
                self.run[i].SetBackgroundColour(self.optboxbackgroundcolor)
                self.run[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.run[i].Hide()
                self.run[i].Clear()

                self.acq[i] = wx.TextCtrl(self.panel, pos=(380, self.vertshift+40*i-5), size=(80, 25),
                                          name='acq'+str(i))
                self.acq[i].SetBackgroundColour(self.optboxbackgroundcolor)
                self.acq[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.acq[i].Hide()
                self.acq[i].Clear()

                self.rec[i] = wx.TextCtrl(self.panel, pos=(480, self.vertshift+40*i-5), size=(80, 25),
                                          name='rec'+str(i))
                self.rec[i].SetBackgroundColour(self.optboxbackgroundcolor)
                self.rec[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.rec[i].Hide()
                self.rec[i].Clear()

                # self.label[i] = wx.TextCtrl(self.panel, pos=(580, self.vertshift+40*i-5), size=(90, 25),
                #                             name='lab'+str(i))
                self.label[i] = wx.ComboBox(self.panel, pos=(580, self.vertshift + 40 * i - 5),
                                            size=(90, 25), name='lab' + str(i))
                self.label[i].SetItems(self.alllabel)
                self.label[i].SetBackgroundColour(self.boxbackgroundcolor)
                self.label[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.label[i].Clear()
                self.label[i].Hide()

                self.ref[i] = wx.TextCtrl(self.panel, pos=(690, self.vertshift+40*i-5), size=(40, 25), name='r'+str(i))
                self.ref[i].SetBackgroundColour(self.boxbackgroundcolor)
                self.ref[i].SetForegroundColour(self.exccol[self.exclusion_array[i]])
                self.ref[i].Hide()
                self.ref[i].Clear()

        self.labelcombocol()
        self.foldercombocol()

        self.button = wx.Button(self.panel, -1, "TRANSFER", pos=(600, self.vertshift+40+40*ix), size=(500, 40),
                                name='gobutton')
        self.button.Bind(wx.EVT_BUTTON, self.onbutton)
        self.button.SetFont(wx.Font(20, wx.SCRIPT, wx.NORMAL, wx.BOLD))
        self.button.SetBackgroundColour(self.buttonbackgroundcolor)
        self.button.SetForegroundColour(self.bluecolor)

        self.checkbutton = wx.Button(self.panel, -1, "Check output filenames here before pressing the TRANSFER button!!", pos=(100, self.vertshift + 40 + 40 * ix), size=(400, 40),
                            name='gobutton')
        self.checkbutton.Bind(wx.EVT_BUTTON, self.oncheckbutton)
        self.checkbutton.SetBackgroundColour(self.buttonbackgroundcolor)
        self.checkbutton.SetForegroundColour(self.fontcolor)

        self.helpbutton = wx.Button(self.panel, -1, "?", pos=(guiwidth-100, self.vertshift/4), size=(50, 50),
                                name='helpbutton',style=0)
        self.helpbutton.SetFont(wx.Font(28, wx.SCRIPT, wx.NORMAL, wx.BOLD))
        self.helpbutton.SetBackgroundColour((52, 142, 216))
        self.helpbutton.SetForegroundColour('white')
        self.helpbutton.Bind(wx.EVT_BUTTON, self.on_label_help)

    def onquit(self, event):
        self.Close(True)

    def onclosewindow(self, event):
        self.Destroy()

    def onabout_pybidsconv(self, e):
        self.new = AboutpyBIDSconv(parent=None, id=-1)
        self.new.Show()

    def onabout_bids(self, e):
        self.new = AboutBIDS(parent=None, id=-1)
        self.new.Show()

    @staticmethod
    def onbidshome(self):
        BIDShome()

    @staticmethod
    def onbidsspecs(self):
        BIDSspecs()

    @staticmethod
    def on_main_help(self):
        AboutMainHelp()

    @staticmethod
    def on_label_help(self):
        AboutLabelHelp()

    def getvalue(self):
        return self.input.GetValue()

    def labelcombocol(self):
        for i in range(len(self.un_seq)):
            selection = self.label[i].GetSelection()
            if selection == 0:
                self.label[i].SetForegroundColour(wx.RED)
            else:
                self.label[i].SetForegroundColour(self.exccol[0])
        self.panel.Refresh()

    def foldercombocol(self):
        for i in range(len(self.un_seq)):
            tr = self.combo1[i].GetCurrentSelection()
            fold = self.combo2[i].GetCurrentSelection()
            if tr == 0:
                if fold == 0:
                    self.combo2[i].SetForegroundColour(wx.RED)
                else:
                    self.combo2[i].SetForegroundColour(self.bluecolor)
        self.panel.Refresh()

    def oncombo1(self, event):
        b = event.GetEventObject().GetName()
        nr = int(float(b[2:]))

        selection = event.GetSelection()

        # app = wx.App()
        if selection == 0:
            self.task[nr].SetForegroundColour(self.exccol[0])
            self.run[nr].SetForegroundColour(self.exccol[0])
            self.acq[nr].SetForegroundColour(self.exccol[0])
            self.rec[nr].SetForegroundColour(self.exccol[0])
            self.ref[nr].SetForegroundColour(self.exccol[0])
            self.label[nr].SetForegroundColour(self.exccol[0])
            self.seqlabel[nr].SetForegroundColour(self.exccol[0])
            self.nrvols[nr].SetForegroundColour(self.exccol[0])
            self.seqnr[nr].SetForegroundColour(self.exccol[0])
            self.panel.Refresh()
        elif selection == 1:
            self.combo2[nr].SetForegroundColour(self.exccol[1])
            self.task[nr].SetForegroundColour(self.exccol[1])
            self.run[nr].SetForegroundColour(self.exccol[1])
            self.rec[nr].SetForegroundColour(self.exccol[1])
            self.acq[nr].SetForegroundColour(self.exccol[1])
            self.ref[nr].SetForegroundColour(self.exccol[1])
            self.label[nr].SetForegroundColour(self.exccol[1])
            self.seqlabel[nr].SetForegroundColour(self.exccol[1])
            self.nrvols[nr].SetForegroundColour(self.exccol[1])
            self.seqnr[nr].SetForegroundColour(self.exccol[1])
            self.panel.Refresh()

        self.foldercombocol()

    def oncombo2(self, event):
        b = event.GetEventObject().GetName()
        nr = int(float(b[2:]))

        selection = event.GetSelection()
        self.foldercombocol()

        # app = wx.App()
        if selection == 2:
            self.task[nr].Show()
            self.task[nr].SetValue(self.taskname_list[nr])

            self.run[nr].Show()

            self.acq[nr].Show()
            self.acq[nr].SetValue(self.acq_name_list[nr])

            self.rec[nr].Show()
            self.rec[nr].SetValue(self.rec_name_list[nr])

            self.label[nr].SetItems(self.funclabel)
            self.label[nr].SetSelection(0)
            self.label[nr].SetForegroundColour(self.exccol[self.exclusion_array[nr]])
            self.label[nr].SetBackgroundColour(self.boxbackgroundcolor)
            self.label[nr].Show()

            self.ref[nr].Hide()
            self.ref[nr].Clear()

        elif selection == 1:
            self.task[nr].Hide()
            self.task[nr].Clear()

            self.run[nr].Show()

            self.acq[nr].Show()
            self.acq[nr].SetValue(self.acq_name_list[nr])

            self.rec[nr].Show()
            self.rec[nr].SetValue(self.rec_name_list[nr])

            self.label[nr].SetItems(self.anatlabel)
            self.label[nr].SetSelection(0)
            self.label[nr].SetForegroundColour(self.exccol[self.exclusion_array[nr]])
            self.label[nr].SetBackgroundColour(self.boxbackgroundcolor)
            self.label[nr].Show()

            self.ref[nr].Hide()
            self.ref[nr].Clear()

        elif selection == 3:
            self.task[nr].Hide()
            self.task[nr].Clear()

            self.run[nr].Show()

            self.acq[nr].Show()
            self.acq[nr].SetValue(self.acq_name_list[nr])

            self.rec[nr].Show()
            self.rec[nr].SetValue(self.rec_name_list[nr])

            self.label[nr].SetItems(self.dwilabel)
            self.label[nr].SetSelection(0)
            self.label[nr].SetForegroundColour(self.exccol[self.exclusion_array[nr]])
            self.label[nr].Show()

            self.ref[nr].Hide()
            self.ref[nr].Clear()


        elif selection == 4:
            self.task[nr].Hide()
            self.task[nr].Clear()

            self.run[nr].Show()

            self.acq[nr].Show()
            self.acq[nr].SetValue(self.acq_name_list[nr])

            self.rec[nr].Hide()
            self.rec[nr].Clear()

            self.label[nr].SetItems(self.fmaplabel)
            self.label[nr].SetSelection(0)
            self.label[nr].SetBackgroundColour(self.boxbackgroundcolor)
            self.label[nr].Show()

            self.ref[nr].Show()

        else:

            self.task[nr].Hide()
            self.task[nr].Clear()

            self.run[nr].Hide()
            self.run[nr].Clear()

            self.acq[nr].Hide()
            self.acq[nr].Clear()

            self.rec[nr].Hide()
            self.rec[nr].Clear()

            self.label[nr].Hide()
            self.label[nr].Clear()

            self.ref[nr].Hide()
            self.ref[nr].Clear()

        self.labelcombocol()
        self.panel.Refresh()

    def oncheckbutton(self, event):
        b = event.GetEventObject().GetName()

        data2conv = []
        folder2conv = []
        folderindex = []
        task2conv = []
        run2conv = []
        acq2conv = []
        rec2conv = []
        label2conv = []
        echo2conv = []
        fmapref = []

        for i in range(len(self.un_seq)):

            if self.combo1[i].GetValue() == 'Yes':
                data2conv.append(i)
                if self.combo2[i].GetValue() == '---':
                    infomsg = "Sequence Nr " + str(i) + " is selected to transfer but BIDS folder is not selected." + \
                              "\nPlease check your input!"
                    d = wx.MessageDialog(None, infomsg, "INPUT ERROR!", wx.OK)
                    d.ShowModal()
                    d.Destroy()
                    return
                else:
                    folder2conv.append(self.combo2[i].GetValue())
                folderindex.append(i)
                echo2conv.append(self.un_echo[i])

                try:
                    task2conv.append(self.task[i].GetValue())
                except:
                    task2conv.append('')

                try:
                    rr = self.run[i].GetValue()
                    if rr > 10:
                        run2conv.append(str(rr))
                    else:
                        run2conv.append("0"+str(rr))
                except:
                    run2conv.append('')

                try:
                    acq2conv.append(self.acq[i].GetValue())
                except:
                    acq2conv.append('')

                try:
                    rec2conv.append(self.rec[i].GetValue())
                except:
                    rec2conv.append('')

                try:
                    label2conv.append(self.label[i].GetValue())
                except:
                    label2conv.append('')

                if self.combo2[i].GetValue() == 'fmap':
                    if not self.ref[i].GetValue():
                        # app = wx.App()
                        msg = "References for fmap (Seq: " + str(self.un_seq[i]) + ") is not specified!"
                        wx.MessageBox(msg, "Input error!", wx.CANCEL)
                    else:
                        try:
                            a = self.ref[i].GetValue()
                            a = a.replace(', ', ', ')
                            a = a.replace(' , ', ', ')
                            a = a.replace(', ', ' ')
                            b = a.split()
                            b = list(map(int, b))
                            fmapref.append(b)
                        except:
                            fmapref.append('')

        folder2conv = [x.encode('UTF8') for x in folder2conv]
        task2conv = [x.encode('UTF8') for x in task2conv]
        run2conv = [x.encode('UTF8') for x in run2conv]
        acq2conv = [x.encode('UTF8') for x in acq2conv]
        rec2conv = [x.encode('UTF8') for x in rec2conv]
        label2conv = [x.encode('UTF8') for x in label2conv]

        CheckFilename(folder2conv, self.subjectnumber, self.sessionnumber, task2conv, acq2conv, run2conv, rec2conv,
                      label2conv)

    def onbutton(self, event):
        b = event.GetEventObject().GetName()

        data2conv = []
        folder2conv = []
        folderindex = []
        task2conv = []
        run2conv = []
        acq2conv = []
        rec2conv = []
        label2conv = []
        echo2conv = []
        fmapref = []

        for i in range(len(self.un_seq)):

            if self.combo1[i].GetValue() == 'Yes':
                data2conv.append(i)
                if self.combo2[i].GetValue() == '---':
                    infomsg = "Sequence Nr " + str(i) + " is selected to transfer but BIDS folder is not selected." + \
                              "\nPlease check your input!"
                    d = wx.MessageDialog(None, infomsg, "INPUT ERROR!", wx.OK)
                    d.ShowModal()
                    d.Destroy()
                    return
                else:
                    folder2conv.append(self.combo2[i].GetValue())

                folderindex.append(i)
                echo2conv.append(self.un_echo[i])

                try:
                    task2conv.append(self.task[i].GetValue())
                except:
                    task2conv.append('')

                try:
                    rr = self.run[i].GetValue()
                    if rr > 10:
                        run2conv.append(str(rr))
                    else:
                        run2conv.append("0"+str(rr))
                except:
                    run2conv.append('')

                try:
                    acq2conv.append(self.acq[i].GetValue())
                except:
                    acq2conv.append('')

                try:
                    rec2conv.append(self.rec[i].GetValue())
                except:
                    rec2conv.append('')

                try:
                    label2conv.append(self.label[i].GetValue())
                except:
                    label2conv.append('')

                if self.combo2[i].GetValue() == 'fmap':
                    if not self.ref[i].GetValue():
                        # app = wx.App()
                        msg = "References for fmap (Seq: " + str(self.un_seq[i]) + ") is not specified!"
                        wx.MessageBox(msg, "Input error!", wx.CANCEL)
                    else:
                        try:
                            a = self.ref[i].GetValue()
                            a = a.replace(', ', ', ')
                            a = a.replace(' , ', ', ')
                            a = a.replace(', ', ' ')
                            b = a.split()
                            b = list(map(int, b))
                            fmapref.append(b)
                        except:
                            fmapref.append('')

        folder2conv = [x.encode('UTF8') for x in folder2conv]
        task2conv = [x.encode('UTF8') for x in task2conv]
        run2conv = [x.encode('UTF8') for x in run2conv]
        acq2conv = [x.encode('UTF8') for x in acq2conv]
        rec2conv = [x.encode('UTF8') for x in rec2conv]
        label2conv = [x.encode('UTF8') for x in label2conv]

        self.Close()

        Convert2BIDS(self.pathdicom, self.subjectnumber, self.subjectgroup, self.sessionnumber, self.subjtext2log,
                     self.outputdir, self.dcmfiles, folder2conv, folderindex, task2conv, run2conv, acq2conv, rec2conv,
                     label2conv, fmapref, self.un_seq, self.acq_time, self.patinfo, echo2conv)


# ################################################################################################################################
# ################################################################################################################################
#
# Convert2BIDS
#
# ################################################################################################################################
# ################################################################################################################################

class Convert2BIDS:
    def __init__(self, pathdicom, subjectnumber, subjectgroup, sessionnumber, subjtext2log, outputdir, dcmfiles, 
                 folder2conv, folderindex, task2conv, run2conv, acq2conv, rec2conv, label2conv, fmapref, seqlabel2conv, 
                 acq_time, patinfo, echo2conv):

        # create subject number
        if int(float(subjectnumber)) > 99:
            subjnum = str(subjectnumber)
        else:
            if int(float(subjectnumber)) > 9:
                subjnum = "0" + str(subjectnumber)
            else:
                subjnum = "00" + str(subjectnumber)

        # Check BIDS labels
        # -------------------------------------
        validBIDSlabels =["FLAIR", "FLASH", "T1w", "T2w", "T1rho", "T1map", "T2map", "T2star", "PD", "PDmap",
                          "PDT2", "inplaneT1", "inplaneT2", "angio", "defacemask", "bold", "sbref",
                          "asl", "dwi", "fieldmap", "magnitude", "magnitude1", "magnitude2", "phasediff",
                          "phase1", "phase2","epi'"]

        for ii in range(len(folder2conv)):
            c = [i for i, item in enumerate(validBIDSlabels) if label2conv[ii] in item]
            if not c:
                # oo = wx.App()
                infomsg = "The specified label " + label2conv[ii] + " seems not to be a valid BIDS label." + \
                          "\nPlease check your input!\nPress YES to go further or NO to stop the transfer"
                d = wx.MessageDialog( None, infomsg, "IMPORTANT!", wx.YES_NO)
                answer = d.ShowModal()

                if (answer == wx.ID_NO):
                    return

        # Check new filenames for duplicates
        # -------------------------------------
        nf_list = []
        for ii in range(len(folder2conv)):
            # create new filenames
            sub1 = "sub-" + subjnum

            if sessionnumber == "":
                sess1 = ""
            else:
                sess1 = "_ses-" + str(sessionnumber)

            if task2conv[ii] == "":
                if folder2conv == "func":
                    # oo = wx.App()
                    infomsg = "Transfer stopped!\nA task name needs to be specified for each functional session." + \
                              "\n Taskname missing for sequence " + str(ii)
                    d = wx.MessageDialog( None, infomsg, "INPUT ERROR!", wx.OK)
                    d.ShowModal()
                    d.Destroy()
                    return
                else:
                    task1 = ""
            else:
                task2conv[ii] = re.sub(" ", "", task2conv[ii])
                task1 = "_task-" + task2conv[ii]

            if acq2conv[ii] == "":
                acq1 = ""
            else:
                acq1 = "_acq-" + acq2conv[ii]

            if run2conv[ii] == "":
                run1 = ""
            else:
                run1 = "_run-" + run2conv[ii]

            if rec2conv[ii] == "":
                rec1 = ""
            else:
                rec1 = "_rec-" + rec2conv[ii]

            nf_list.append(sub1 + sess1 + task1 + acq1 + run1 + rec1 + "_" + label2conv[ii])

        dup = [x for n, x in enumerate(nf_list) if x in nf_list[:n]]
        if len(dup) > 0:
            dialogtext = "Transfer stopped, because input leads to duplicate filenames! :\n"
            for ii in range(len(dup)):
                dialogtext = dialogtext + dup[ii] + "\n"

            # oo = wx.App()
            d = wx.MessageDialog(
                None, dialogtext, "IMPORTANT", wx.OK)
            d.ShowModal()
            return
        else:
            print "\n\nFilenames checked"

        # Create subfolders
        # ----------------------------
        subfolderlist = list(set(folder2conv))
        # subjrawnum = subjnum

        if subjectgroup:
            subjnum = subjectgroup + subjnum

        # Check output folder (add subj folder and subfolders)
        if sessionnumber == "":
            subjectfolder = os.path.join(outputdir, "sub-" + subjnum)
            subjectfolderrel = os.path.join("sub-" + subjnum)
            # subjid4out = "Subject: " + subjnum
        else:
            sessnum = str(sessionnumber)

            subjectfolder = os.path.join(outputdir, "sub-" + subjnum, "ses-" + sessnum)
            subjectfolderrel = os.path.join("sub-" + subjnum, "ses-" + sessnum)
            # subjid4out = "Subject: " + subjnum, "Session: " + sessnum

        tempfolder1 = os.path.join(subjectfolder, "temp")
        tempfolder2 = os.path.join(subjectfolder, "temp2")

        try:
            shutil.rmtree(tempfolder1)
        except:
            pass

        try:
            shutil.rmtree(tempfolder2)
        except:
            pass

        subjexist = os.path.exists(subjectfolder)
        if not subjexist:
            os.makedirs(subjectfolder)
            # os.makedirs(tempfolder1)
            # os.makedirs(tempfolder2)
            for ss in range(len(subfolderlist)):
                os.makedirs(os.path.join(subjectfolder, subfolderlist[ss]))
        else:
            # if not os.path.exists(tempfolder1):
            # os.makedirs(tempfolder1)
            # if not os.path.exists(tempfolder2):
            # os.makedirs(tempfolder2)
            for ss in range(len(subfolderlist)):
                if not os.path.exists(os.path.join(subjectfolder, subfolderlist[ss])):
                    os.makedirs(os.path.join(subjectfolder, subfolderlist[ss]))

        logfolder = os.path.join(outputdir, "pyBIDSconv_logs")
        logfolderexist = os.path.exists(logfolder)
        if not logfolderexist:
            os.makedirs(logfolder)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # procedure existing folder missing
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # get time string
        t = datetime.now()
        strg = t.strftime('%B_%d_%Y_%H_%M')
        strg2 = t.strftime('%Y-%m-%dT%H:%M:%S')

        # Check / create CHANGE file
        # -----------------------------------------
        cfilename = os.path.join(outputdir, "CHANGES")
        cexist = os.path.exists(cfilename)
        if not cexist:
            cfile = open(cfilename, "w")
            cfile.write("0.01 "+ strg2 + "\n\n\t- Initial release.\n\n")
            cfile.close()
            changenumber = 0.02
        else:
            infile = open(cfilename, 'r')
            firstline = infile.readline()
            x = firstline.split()
            changenumber = float(x[0]) + 0.01

        # start log file
        # -----------------------------------------
        if sessionnumber == "":
            logfilename = os.path.join(logfolder, "log_pyBIDSconv_sub-" + subjnum + "_" + strg + ".txt")
            scantsvfilename = os.path.join(subjectfolder, "sub-" + subjnum + "_scans.tsv")
        else:
            logfilename = os.path.join(logfolder, "log_pyBIDSconv_sub-" + subjnum + "_ses-" + sessnum + 
                                       "_" + strg + ".txt")
            scantsvfilename = os.path.join(subjectfolder, "sub-" + subjnum + "_ses-" + sessnum + "_scans.tsv")
        logfile = open(logfilename, "w")

        # add first line
        logfile.write(str(changenumber) + " " + strg2 + "\n\n")

        # add deletion of subject
        if not subjtext2log == "":
            logfile.write(subjtext2log)

        # add adding of subject
        if not sessionnumber:
            logfile.write("\t- ADD sub-" + subjnum + " to the BIDS directory: " + outputdir + 
                          " (by pyBIDSconv version " + ver + " : \n\n")
        else:
            logfile.write("\t- ADD sub-" + subjnum + " ses-" + sessnum + " to the BIDS directory: " + outputdir + 
                          " (by pyBIDSconv version " + ver + " : \n\n")

        # Check if scan tsv file exist otherwise start it
        # -------------------------------------------------
        scantsvexistexist = os.path.exists(scantsvfilename)
        if not scantsvexistexist:
            scantsvfile = open(scantsvfilename, "w")
            scantsvfile.write("filename")

        # Check existance / Create dataset_description.json file
        # -----------------------------------------
        # app = wx.App()
        dsfile = "dataset_description.json"
        dsfilename = os.path.join(outputdir, dsfile)
        dsexist = os.path.exists(dsfilename)
        if not dsexist:

            logfile.write("\t- Create dataset_description.json file in: " + outputdir + "\n\n")

            pathx, defname = os.path.split(outputdir)
            # Empty dict
            d = {}
            dialog = wx.TextEntryDialog(None, "Name of the dataset:", 
                                        "Input Name of Dataset for dataset_description.json file", defname)
            if dialog.ShowModal() == wx.ID_OK:
                dataname = dialog.GetValue()
            else:
                d = wx.MessageDialog(
                    None, "Transfer stopped!", 
                    "IMPORTANT", wx.OK)
                d.ShowModal()
                return

            d["Name"] = dataname
            d["BIDSVersion"] = bidsver

            # write json file
            with open(dsfilename, 'w') as f:
                f.write(json.dumps(d, indent=4, separators=(', ', ': ')))

        scanjson = [""] * len(folder2conv)
        scannii = [""] * len(folder2conv)
        scanstsv = []

        nrfuncfiles = 0
        funcfilenames = []

        # Loop over sequences to convert
        # -----------------------------------------
        for ii in range(len(folder2conv)):

            if ii > 1:
                logfile.write("\n")

            logfile.write("\t- Convert data: " + seqlabel2conv[folderindex[ii]] + " to " + folder2conv[ii] + "\n")

            os.makedirs(tempfolder1)
            os.makedirs(tempfolder2)

            # copy file to tempfolder1
            print "\n\nCOPY FILES " + seqlabel2conv[folderindex[ii]] + "\n"
            for files in range(len(dcmfiles[folderindex[ii]])):
                shutil.copy2(dcmfiles[folderindex[ii]][files], tempfolder1)

            # convert dcm in temfolder1 to nii in tempfolder2
            print "CONVERT DICOM TO NIFTI \n"
            # options = "-b y -ba y -z y -f %s"
            options = "-b y -ba y -z i -f %s"
            commandstr = "dcm2niix {} -o {} {}"
            command = commandstr.format(options, tempfolder2, tempfolder1)
            print command
            logfile.write("\t\t" + command + "\n")
            os.system(command)

            # delete dcm files from tempfolder1
            filelist = glob.glob(os.path.join(tempfolder1, "*.dcm"))
            try:
                for f in filelist:
                    os.remove(f)
            except:
                for f in filelist:
                    os.chmod(f, 666)
                    os.remove(f)

            # Rename files
            print "\nRENAME FILES \n"
            logfile.write("\t- Rename files: " + "\n")

            # detect multi echos
            onlyfiles = glob.glob(os.path.join(tempfolder2, "*.json"))
            try:
                nrecho = sum(any(m in L for m in '_e') for L in onlyfiles)
            except:
                nrecho = 1

            # create new filenames
            sub1 = "sub-" + subjnum

            if sessionnumber == "":
                sess1 = ""
            else:
                sess1 = "_ses-" + str(sessionnumber)

            if task2conv[ii] == "":
                task1 = ""
            else:
                task1 = "_task-" + task2conv[ii]

            if acq2conv[ii] == "":
                acq1 = ""
            else:
                acq1 = "_acq-" + acq2conv[ii]

            if run2conv[ii] == "":
                run1 = ""
            else:
                run1 = "_run-" + run2conv[ii]

            if rec2conv[ii] == "":
                rec1 = ""
            else:
                rec1 = "_rec-" + rec2conv[ii]

            if nrecho > 1:
                echocount = 1

            # rename all files
            filetypes = ['.nii.gz', '.json']

            if folder2conv[ii] == 'dwi':
                filetypes = filetypes + ['.bval', '.bvec']

            # loop over files to rename
            sc1 = []
            sc2 = []
            for filename in onlyfiles:

                if nrecho > 1:
                    echo1 = "_echo-" + str(echocount)
                    if folder2conv[ii] == 'fmap':
                        newfilename = sub1 + sess1 + task1 + acq1 + rec1 + run1 + "_" + label2conv[ii] + str(echocount)
                    else:
                        newfilename = sub1 + sess1 + task1 + acq1 + rec1 + run1  + echo1 + "_" + label2conv[ii]

                    echocount += 1
                else:
                    newfilename = sub1 + sess1 + task1 + acq1 + rec1 + run1 + "_" + label2conv[ii]

                fn = os.path.splitext(os.path.basename(filename))

                # loop over file types (json vs nii.gz)
                for ftype in filetypes:

                    source = os.path.join(tempfolder2, fn[0] + ftype)
                    dest = os.path.join(subjectfolder, folder2conv[ii], newfilename + ftype)
                    if ftype == '.nii.gz':
                        if not os.path.isfile(source):
                            source = os.path.join(tempfolder2, fn[0] + '.nii')
                            dest = os.path.join(subjectfolder, folder2conv[ii], newfilename + '.nii')
                            winfo = "The following file was not been gzip form dcm2niix:\n" + dest + " \nPlease gzip it manuallzy afterwards!! \n"
                            d = wx.MessageDialog(
                                None, winfo,
                                "Warning", wx.OK | wx.ICON_QUESTION)
                            d.ShowModal()
                            d.Destroy()


                    if ftype == '.json':
                        x = os.path.join(folder2conv[ii], newfilename + ftype)
                        x = x.replace('\\', '/')
                        sc1.append(x)
                    else:


                        x1 = os.path.join(subjectfolderrel, folder2conv[ii], newfilename + ftype)
                        x1 = x1.replace('\\', '/')
                        scanstsv.append(x1)
                        scantsvfile.write("\r\n" + x1)

                        if sessionnumber == "":
                            x2 = os.path.join(folder2conv[ii], newfilename + ftype)
                        else:
                            x2 = os.path.join("ses-"+sessnum, folder2conv[ii], newfilename + ftype)
                        x2 = x2.replace('\\', '/')
                        sc2.append(x2)

                    logfile.write("\t\t" + source + " ---> " + dest + "\n")

                    # try:
                    os.rename(source, dest)
                    # except:
                    #     if ftype == '.nii.gz':




                    if folder2conv[ii] == 'func':
                        if ftype == ".nii.gz":
                            funcfilenames.append(dest)
                            nrfuncfiles += 1

            scanjson[ii] = sc1
            scannii[ii] = sc2

            # remove temp folder
            try:
                shutil.rmtree(tempfolder1)
            except:
                pass
            try:
                shutil.rmtree(tempfolder2)
            except:
                pass

        logfile.write("\n\t- Create scan tsv file: " + scantsvfilename + "\n\n")

        scantsvfile.close()

        # Add infos json files
        logfile.write("\t- Add info to .json files: \n")

        fmc = -1
        for ii in range(len(folder2conv)):

            # add Add taskname to func json files
            if folder2conv[ii] == 'func':

                for yy in range(len(scanjson[ii])):

                    filename = subjectfolder.replace('\\', '/') + "/" + scanjson[ii][yy]

                    logfile.write("\t\tAdd to " + scanjson[ii][yy] + ":\n" )
                    logfile.write("\t\tTaskName: " + task2conv[ii] + "\n")

                    print filename
                    with open(filename) as f:
                        data = f.read()

                    # Add IntendedFor
                    d = json.loads(data)
                    d["TaskName"] = task2conv[ii]

                    # write json file
                    with open(filename, 'w') as f:
                        f.write(json.dumps(d, indent=4, separators=(', ', ': ')))

            # add IntendedFor to fmap json files
            if folder2conv[ii] == 'fmap':
                fmc += 1

                # loop over json files
                for yy in range(len(scanjson[ii])):
                    print "\nAdd IntendedFor to fmap .json file:  \n" + scanjson[ii][yy]

                    # create indendedfor content
                    intendedfor = []
                    if len(fmapref[fmc]) > 1:
                        intendedfor.append('[')

                    for jj in range(len(fmapref[fmc])):
                        intendedfor.append( str(scannii[jj][0]) + ', ')

                    if len(fmapref[fmc]) > 1:
                        intendedfor.append(']')

                    intendedfor = ''.join(map(str, intendedfor))
                    if len(fmapref[fmc]) > 1:
                        intendedfor = intendedfor.replace(', ]', ']')
                    else:
                        intendedfor = intendedfor.replace(', ', '')

                    print "IntendedFor: " + intendedfor

                    logfile.write("\n\t\tAdd IntendedFor to fmap .json file: " + scanjson[ii][yy] + ":\n")
                    logfile.write("\t\tIntendedFor: " + intendedfor + "\n")

                    # load json file
                    filename = subjectfolder.replace('\\', '/') + "/" + scanjson[ii][yy]

                    with open(filename) as f:
                        data = f.read()

                    # add IntendedFor
                    d = json.loads(data)
                    d["IntendedFor"] = intendedfor

                    if label2conv[ii] == "phasediff":
                        if folder2conv[ii-1] == 'fmap':
                            if len(echo2conv[ii-1]) > 1:

                                logfile.write("\n\t\tAdd both echo times to phasediff fmap .json file: " +
                                              scanjson[ii][0] + " \n")
                                print "Add both echo times to phasediff fmap json file: " + scanjson[ii][0]

                                try:
                                    del d['EchoTime']
                                except:
                                    pass

                                for jj in range(len(echo2conv[ii-1])):
                                    d["EchoTime"+str(jj+1)] = float(echo2conv[ii-1][jj])/1000

                    with open(filename, 'w') as f:
                        f.write(json.dumps(d, indent=4, separators=(', ', ': ')))

        # Participant file
        # -----------------------------------
        pfilename = os.path.join(outputdir, 'participants.tsv')

        subjid = "sub-" + subjnum

        # check if participant file exists
        if os.path.isfile(pfilename):  # if yes

            # check if subject is alreeady included
            df = pd.read_csv(pfilename, delimiter='\t')
            x = df['participant_id'].tolist()
            index1 = [i for i, c in enumerate(x) if c == "sub-" + subjnum]

            if index1:  # if yes, as for replacement

                winfo1 = "Subject " + subjid + " already exists in the participant.tsv file!\n"
                winfo2 = "Do you want to replace the entry in the participant.tsv file.\n"
                winfo3 = "Press YES, to replace, or NO to keep the old entry. "
                d = wx.MessageDialog(
                    None, winfo1 + winfo2 + winfo3, 
                    "Warning", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                answer = d.ShowModal()
                d.Destroy()

                if answer == wx.ID_YES:

                    df = df[df.participant_id != "sub-" + subjnum]
                    df.to_csv(pfilename, sep='\t', index=False)
                    pfile = open(pfilename, 'ab')
                    pfile.write( subjid + "\t" + str(patinfo[0]) + "\t" + str(patinfo[1]) + "\n")
                    pfile.close()

            else:  # if not add

                pfile = open(pfilename, 'ab')
                pfile.write( subjid + "\t" + str(patinfo[0]) + "\t" + str(patinfo[1]) + "\n")
                pfile.close()

        else:  # create if participant file does not exist
            pfile = open(pfilename, "w")
            pfile.write("participant_id\tage\tsex\n")

            pfile.write(subjid + "\t" + str(patinfo[0]) + "\t" + str(patinfo[1]) + "\n")
            pfile.close()

        logfile.write("\n\t- Load participant.tsv file and add/replace: " +
                      subjid + "\t" + str(patinfo[0]) + "\t" + str(patinfo[1]) )
        print "\n\n- Load participant.tsv file and add/replace: \nparticipant_id\tage\tsex\n" + \
              subjid + "\t" + str(patinfo[0]) + "\t" + str(patinfo[1])

        logfile.write("\n\n\n")
        logfile.close()

        # concat logfile to change
        print "\n\nUpdate CHANGE log file"
        cfiles = [logfilename, cfilename]
        concat = ''.join([open(f).read() for f in cfiles])

        with open(cfilename, 'w') as fout:
            for line in concat:
                fout.write(line)
            fout.close()

        try:
            shutil.rmtree(logfolder)
        except:
            pass

        StartValidator()

        # Present final message dialog
        # ------------------------------
        winfo1 = "Transfer completed for:\t " + subjid

        # add task event.tsv file
        if nrfuncfiles > 0:
            winfo1a = "\n\nTo finalize the BIDS structure for this subject, you need to do the following:" + \
                      "\n\nYou need to create a event.tsv file for each of the functional files " + \
                      "\n(if not labeled with '_task-rest' for restingstate):\n"
            winfo1b = "\n"
            for xx in range(len(funcfilenames)):
                winfo1b = winfo1b + funcfilenames[xx] + "\n"
        else:
            winfo1a = ""
            winfo1b = ""

        # add README file
        pfilename = os.path.join(outputdir, 'README')
        if not os.path.isfile(pfilename): # if yes
            winfo1c = "\n\nPlease add a README file (in the BIDS source directory) containing " + \
                      "\na detailed description of the dataset."
        else:
            winfo1c = ""

        # add info to dataset_description.json file
        winfo2 = "\n\nPlease add information to the dataset_description.json file." + \
                 "\n(You can use the build in editor in pyBIDSconv in the menubar in the main GUI!)"

        # Validator
        winfo3 = "\n\nPlease use the online BIDS validation tool to check" + \
                 "\nyour BIDS structure after adding each subject!"

        winfo4 = "\n\nThank you for using pyBIDSconv version" + str(ver) + "!"
        winfo5 = '\n\nby Michael Lindner\nm.lindner@reading.ac.uk\nUniversity of Reading, 2017' \
                 '\nCenter for Integrative Neuroscience and Neurodynamics' \
                 '\nhttps://www.reading.ac.uk/cinn/cinn-home.aspx'
        d = wx.MessageDialog(
            None, winfo1 + winfo1a + winfo1b + winfo1c + winfo2 + winfo3 + winfo4 + winfo5, 
            "IMPORTANT", wx.OK)
        d.ShowModal()

        # close program
        # sys.exit(0)


# ################################################################################################################################
# ################################################################################################################################
#
# Helper Classes
#
# ################################################################################################################################
# ################################################################################################################################

class AboutpyBIDSconv(wx.Frame):
    def __init__(self, parent, id):
        # wx.App()
        wx.Frame.__init__(self, parent, id, 'About pyBIDSconv', size=(400, 300))
        wx.Frame.CenterOnScreen(self)
        # panel = wx.Panel(self)

        s = '		pyBIDSconv '
        s += (os.linesep + '')
        s += (os.linesep + '	   version: ' + str(ver))
        s += (os.linesep + '')
        s += (os.linesep + 'This tool is designed to convert dicom files of one')
        s += (os.linesep + 'subject into a subject subfolder in a BIDS structure.')
        s += (os.linesep + '')
        s += (os.linesep + 'pyBIDS helps you to do the conversion in a automated manor')
        s += (os.linesep + 'by automatically detecting the allocation of the different')
        s += (os.linesep + 'file types (e.g. DTI, anatomical or functional scans, etc) ')
        s += (os.linesep + 'to the appropriate subfolders in the BIDS structore. ')
        s += (os.linesep + 'The detection can be visually inspected and if neccessarry ')
        s += (os.linesep + 'corrected in a GUI.')
        s += (os.linesep + '')
        s += (os.linesep + 'Enjoy playing around with this tool!')
        s += (os.linesep + '')
        s += (os.linesep + 'pyBIDSconv by Michael Lindner is licensed')
        s += (os.linesep + 'under CC BY 4.0.')
        s += (os.linesep + '')
        s += (os.linesep + 'This program is distributed in the hope that it will be useful, ')
        s += (os.linesep + 'but WITHOUT ANY WARRANTY!')
        s += (os.linesep + '')
        s += (os.linesep + 'by Michael Lindner')
        s += (os.linesep + 'm.lindner@reading.ac.uk')
        s += (os.linesep + 'University of Reading, 2017')
        s += (os.linesep + 'Center for Integrative Neuroscience and Neurodynamics')
        s += (os.linesep + 'https://www.reading.ac.uk/cinn/cinn-home.aspx')

        statxt = wx.StaticText(self, -1, s, (-1, -1), (-1, -1))
        staline = wx.StaticLine(self, -1, (-1, -1), (-1, -1), wx.LI_HORIZONTAL)

        b = 5
        vsizer1 = wx.BoxSizer(wx.VERTICAL)
        vsizer1.Add(statxt, 1, wx.EXPAND | wx.ALL, b)
        vsizer1.Add(staline, 0, wx.GROW | wx.ALL, b)
        vsizer1.SetMinSize((200, -1))
        self.SetSizerAndFit(vsizer1)


class AboutBIDS(wx.Frame):
    def __init__(self, parent, id):
        # wx.App()
        wx.Frame.__init__(self, parent, id, 'About BIDS', size=(400, 300))
        wx.Frame.CenterOnScreen(self)
        # panel = wx.Panel(self)

        s = '		BIDS'
        s += (os.linesep + 'Brain Imaging Data Structure')
        s += (os.linesep + '')
        s += (os.linesep + 'BIDS is a simple and intuitive way to organize')
        s += (os.linesep + 'neuroimaging and behavioral data inspired by')
        s += (os.linesep + 'OpenfMRI.org.')
        s += (os.linesep + '')
        s += (os.linesep + 'More information about BIDS can be found here: ')
        s += (os.linesep + 'http://bids.neuroimaging.io/')
        s += (os.linesep + 'https://www.nature.com/articles/sdata201644')
        s += (os.linesep + '')

        statxt = wx.StaticText(self, -1, s, (-1, -1), (-1, -1))
        staline = wx.StaticLine(self, -1, (-1, -1), (-1, -1), wx.LI_HORIZONTAL)

        b = 5
        vsizer1 = wx.BoxSizer(wx.VERTICAL)
        vsizer1.Add(statxt, 1, wx.EXPAND | wx.ALL, b)
        vsizer1.Add(staline, 0, wx.GROW | wx.ALL, b)
        vsizer1.SetMinSize((200, -1))
        self.SetSizerAndFit(vsizer1)


class AboutMainHelp:

    def __init__(self):
        # webbrowser.open('pyBIDSconv_Manual', new=2)
        try:
            from urllib import pathname2url         # Python 2.x
        except:
            from urllib.request import pathname2url # Python 3.x

        cwd = os.getcwd()

        url = 'file:{}'.format(pathname2url(os.path.abspath(os.path.join(cwd, 'pyBIDSconv_Manual.html'))))
        webbrowser.open(url)


class AboutLabelHelp:
    def __init__(self):

        dialogtext = "In general, the naming of files in the BIDS structure followes\n" + \
                        "specific rules.\n\n" + \
                        "e.g.\n" + \
                        "sub-4_sess-1_task-ABC_run-1_acq-highres_rec-NORM_bold\n\n" + \
                        "But not all parts of the filename appear in all types of scans and\n" + \
                        "some of the filename parts are optional.\n" + \
                        "E.g. _task- needs only be specified for functional data and _run-,\n" \
                        "_acq- and _rec- are optional\n\n" + \
                        "pyBIDSconv allows you to add information to all filename parts which \n" + \
                        "are relevant depending on the scan type. If you leave a fleld of an \n" + \
                        "optional filename part empty, the" "filename part will not be added.\n\n" + \
                        "The following file name parts can be specified:.\n\n" + \
                        "Folder\n" + \
                        "  The folder represents the BIDS folder where the data will be\n" + \
                        "  copied to. Please check if the automatic detection was working \n" + \
                        "  properly. If not please correct it!!\n\n" + \
                        "_task-\n" + \
                        "  For each functional scan a taskname needs to be provided.\n" + \
                        "  The task name will appear in the filename. In case of resting\n" + \
                        "  state data as functional run the task name should contain\n" + \
                        "  'rest'. Each functional (which is not labeled with 'rest') needs\n" + \
                        "  to have an additional event tsv file (See Manual for more detail)\n\n" + \
                        "_run-\n" + \
                        "  If you have multiple runs of the same task, then give then the\n" + \
                        "  same taskname and specify the number of the run here.\n\n" + \
                        "_acq\n" + \
                        "  The acq parameter can be used to distinguish a different set of\n" + \
                        "  parameters used for acquiring the same modality. E.g highres\n" + \
                        "  and lowres for different structural scans or the different phase\n" + \
                        "  incoding directions of fieldmaps etc.\n\n" + \
                        "_rec-\n" + \
                        "  The rec parameter can be used to distinguish different\n" + \
                        "  reconstruction algorithms (e.g. ones using online motion correction\n" + \
                        "  or normalization)\n\n" + \
                        "_label\n" + \
                        "  The label is always the last bit of the filename representing the\n" + \
                        "  scan type.\n\n" + \
                        "  E.g.\n" + \
                        "  structural scans: T1w, T2w, FLAIR, ...\n" + \
                        "  functional scan: bold, asl, ...\n" + \
                        "  DTI scans: dwi\n" + \
                        "  fieldmaps: fieldmap, magnitude, phase, phasediff, etc\n\n" + \
                        "  Other labels:\n" + \
                        "  event for task evet files\n" + \
                        "  physio for physio data\n\n" + \
                        "Ref\n" + \
                        "  In case of a fieldmap sequence the correspoding json file to the nifti" + \
                        "  file needs to contain the info for which sequence the fieldmap is used" + \
                        "  for. Therefore you can specify the sequences number from the column 'Nr'" + \
                        "  (seperated by comma) and pyBIDSconv will add the information to the json" + \
                        "  file for you.\n\n" + \
                        "NrVols\n" + \
                        "  Number of volumes found for this sequence.\n\n" + \
                        "Sequence name\n" + \
                        "  Names of the sequences as specified on the Scanner console.\n\n\n" + \
                        "See BIDS specifications for more details."

        d = wx.MessageDialog(
            None, dialogtext, "OK", wx.OK)
        d.ShowModal()

class StartDSedit(wx.Frame):
    def __init__(self):
        # app4 = wx.App()
        wx.Frame.__init__(self, None)
        self.panel = wx.Panel(self)

        DSkeys=['Name', 'BIDSVersion', 'License', 'Authors', 'Acknowledgements', 'HowToAcknowledge', 'Funding',
                'ReferencesAndLinks', 'DatasetDOI']

        # app56 = wx.App()
        dialog = wx.FileDialog(None, "Choose a dataset description file:",
                               style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            cf = dialog.GetPath()
            dialog.Destroy()
        else:
            cf = ""

        self.dsfilename = cf

        with open(self.dsfilename) as data_file:
            data = json.load(data_file)

        keys = []
        idxs = []
        defkeys = DSkeys
        for key, value in data.items():
            x = key.encode('utf-8')
            keys.append(x)
            indices = [i for i, s in enumerate(DSkeys) if x in s]
            if indices:
                idxs.append(indices[0])
            else:
                print("Warning unknow key found in dataset_description.json file")
                idxs.append(len(defkeys))
                defkeys.append(x)

        vals = []
        for ii in range(len(keys)):
            x = data[keys[ii]]
            vals.append(x.encode('utf-8'))

        # Specify GUI size
        self.NrKeys = len(defkeys)
        guiwidth = 900
        vertshift = 120
        guiheight = self.NrKeys*40+vertshift+220

        self.SetSize((guiwidth, guiheight))
        self.SetTitle('pyBIDSconv - Edit dataset_description.json')
        self.Centre()
        self.Show(True)

        self.DSkey = {}
        self.DSval = {}

        textfonttitle = wx.Font(24, wx.DECORATIVE, wx.NORMAL, wx.BOLD)

        # title
        title = wx.StaticText(self.panel, -1, label="Edit dataset_description.json file", pos=(120, 10))
        title.SetFont(textfonttitle)
        wx.StaticText(self.panel, -1, label="Keys", pos=(20, 80))
        wx.StaticText(self.panel, -1, label="Values", pos=(300, 80))

        for ii in range(0, self.NrKeys+1):
            self.DSkey[ii] = wx.TextCtrl(self.panel, pos=(20, vertshift+40*ii-5), size=(200, 30), name='DSkey'+str(ii))
            if ii < 2:
                self.DSkey[ii].SetForegroundColour(wx.RED)

            try:
                self.DSkey[ii].SetValue(defkeys[ii])
            except:
                pass

            wx.StaticText(self.panel, -1, label=" : ", pos=(250, vertshift+40*ii))
            self.DSval[ii] = wx.TextCtrl(self.panel, pos=(300, vertshift+40*ii-5), size=(560, 30), name='DSval'+str(ii))
            if ii < 2:
                self.DSval[ii].SetForegroundColour(wx.RED)

            try:
                self.DSval[ii].SetValue(vals[idxs[ii]])
            except:
                pass

        wx.StaticText(self.panel, -1, label="Keep value field empty to not include the keys to the file.",
                      pos=(300, guiheight-180))
        rf = wx.StaticText(self.panel, -1, label="red = required fields ", pos=(300, guiheight-160))
        rf.SetForegroundColour(wx.RED)
        wx.StaticText(self.panel, -1, label="black = optional fields.", pos=(300, guiheight-140))

        self.button = wx.Button(self.panel, -1, "Save dataset_description.json file", pos=(100, guiheight-100),
                                size=(guiwidth-200, 40), name='gobutton')
        self.button.Bind(wx.EVT_BUTTON, self.onbutton)

    def onbutton(self, event):
        dsdata = {}

        # Check first two keys
        if not self.DSval[0].GetValue():
            # a1 = wx.App()
            d = wx.MessageDialog(
                None, "Name is empty but is a required field. Please fill in a name for the dataset!", 
                "IMPORTANT", wx.OK)
            d.ShowModal()

        if not self.DSval[1].GetValue():
            # a2 = wx.App()
            d = wx.MessageDialog(
                None, "BIDSversion is empty but is a required field. Please specify used BIDS version!", 
                "IMPORTANT", wx.OK)
            d.ShowModal()

        # Get values
        for i in range(len(self.DSkey)):
            if self.DSval[i].GetValue():
                dsdata[self.DSkey[i].GetValue()] = self.DSval[i].GetValue()

        # write json file
        with open(self.dsfilename, 'w') as f:
            f.write(json.dumps(dsdata, indent=4, separators=(', ', ': ')))


class CreateConfigFile(wx.Frame):
    def __init__(self):
        # app5 = wx.App()
        wx.Frame.__init__(self, None)
        self.panel = wx.Panel(self)

        guiwidth = 550
        guiheight = 550
        self.SetSize((guiwidth, guiheight))
        self.SetTitle('pyBIDSconv - Create/Edit pyBIDSconv config file')
        self.Centre()
        self.Show(True)

        rectext = ""
        phasetext = ""
        contenttext = ""
        endtext = ""

        self.input = [''] * 5

        textfonttitle = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)

        title = wx.StaticText(self.panel, -1, label="Create/Edit pyBIDSconv_defaults.py file", pos=(100, 10))
        title.SetFont(textfonttitle)

        self.button0 = wx.Button(self.panel, -1, "Load a pyBIDSconv config file", pos=(100, 50),
                                size=(300, 40), name='gobutton')
        self.button0.Bind(wx.EVT_BUTTON, self.onbuttonload)

        wx.StaticText(self.panel, -1, label="Detect reconstruction info in dicom.ImageType:", pos=(20, 110))
        self.input[0] = wx.TextCtrl(self.panel, pos=(20, 130), size=(500, 30), name='catfile')
        self.input[0].SetValue(rectext)

        wx.StaticText(self.panel, -1, label='Detect phase info for fieldmaps by content (substring) of '
                                       'dicom.SequenceDescription:', pos=(20, 180))
        self.input[1] = wx.TextCtrl(self.panel, pos=(20, 200), size=(500, 30), name='catfile')
        self.input[1].SetValue(phasetext)

        wx.StaticText(self.panel, -1, label="Exclusions of transfer by content (substring) of "
                                       "dicom.SequenceDescription:", pos=(20, 250))
        self.input[2] = wx.TextCtrl(self.panel, pos=(20, 270), size=(500, 30), name='catfile')
        self.input[2].SetValue(contenttext)

        wx.StaticText(self.panel, -1, label="Exclusions of transfer by dicom.SequenceDescription ending with:",
                      pos=(20, 320))
        self.input[3] = wx.TextCtrl(self.panel, pos=(20, 340), size=(500, 30), name='catfile')
        self.input[3].SetValue(endtext)

        wx.StaticText(self.panel, -1, label="file name for pyBIDSconv config file:", pos=(20, 390))
        self.fn = wx.TextCtrl(self.panel, pos=(20, 410), size=(500, 30), name='catfile')
        self.fn.SetValue("pyBIDSconv_config.py")

        self.button = wx.Button(self.panel, -1, "Save pyBIDSconv config file", pos=(100, 470),
                                size=(300, 40), name='gobutton')
        self.button.Bind(wx.EVT_BUTTON, self.onbuttonok)

    def onbuttonload(self, _):

        # app = wx.App()
        dialog = wx.FileDialog(None, "Choose a categorization file:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            configfile = dialog.GetPath()
            dialog.Destroy()
            
        p, f = os.path.split(configfile)

        # os.chdir(p)
        sys.path.insert(0, p)

        try:
            mname = f[:-3]
            cfg = __import__(mname, fromlist=[''])
        except:
            cfg = __import__(f, fromlist=[''])

        rectext = cfg.ReconstructionInfoInImageType
        phasetext = cfg.PhaseInfoForFmapsBySequenceDescriptionSubstring
        contenttext = cfg.ExclusionsBySequenceDescriptionContent
        endtext = cfg.ExclusionsBySequenceDescriptionEnd

        # print(rectext)
        # print(type(rectext))

        self.input[0].SetValue("'" + "', '".join(rectext) + "'")
        self.input[1].SetValue("'" + "', '".join(phasetext) + "'")
        self.input[2].SetValue("'" + "', '".join(contenttext) + "'")
        self.input[3].SetValue("'" + "', '".join(endtext) + "'")

    def onbuttonok(self, _):

        names = ['ReconstructionInfoInImageType = ', 'PhaseInfoForFmapsBySequenceDescriptionSubstring = ',
                 'ExclusionsBySequenceDescriptionContent = ', 'ExclusionsBySequenceDescriptionEnd = ']
        data = [''] * 4
        for ii in range(4):
            x = self.input[ii].GetValue()
            data[ii] = names[ii] + "'" + x.encode("utf-8" + "'")

        dialog = wx.TextEntryDialog(None, "Name of the dataset:",
                                    "Input Name of Dataset for dataset_description.json file", "pyBIDSconv_config.py")
        if dialog.ShowModal() == wx.ID_OK:
            filename = dialog.GetValue()

        outfile = open(filename, 'w')

        outfile.write("\n")
        for item in data:
            outfile.write("%s\n" % item)

        self.Close()


class CreateDefaultFile(wx.Frame):
    def __init__(self):
        # app4 = wx.App()
        wx.Frame.__init__(self, None)
        panel = wx.Panel(self)
       
        guiwidth = 700
        guiheight = 300
        self.SetSize((guiwidth, guiheight))
        self.SetTitle('pyBIDSconv - Create pyBIDSconv_defaults.py file')
        self.Centre()
        self.Show(True)

        self.file = [''] * 2

        textfonttitle = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)

        title = wx.StaticText(panel, -1, label="Create pyBIDSconv_defaults.py file", pos=(100, 10))
        title.SetFont(textfonttitle)

        wx.StaticText(panel, -1, label="Categorization file:", pos=(20, 110))
        self.file[0] = wx.TextCtrl(panel, pos=(20, 130), size=(500, 30), name='catfile')
        self.button1 = wx.Button(panel, -1, "Browse", pos=(550, 130), name='button2')
        self.button1.Bind(wx.EVT_BUTTON, self.onbutton1)

        wx.StaticText(panel, -1, label="Configuration file:", pos=(20, 40))
        self.file[1] = wx.TextCtrl(panel, pos=(20, 60), size=(500, 30), name='cfgfile')
        self.button2 = wx.Button(panel, -1, "Browse", pos=(550, 60), name='button4')
        self.button2.Bind(wx.EVT_BUTTON, self.onbutton2)

        self.button = wx.Button(panel, -1, "Save pyBIDSconv_defaults.py file", pos=(100, 200),
                                size=(500, 40), name='gobutton')
        self.button.Bind(wx.EVT_BUTTON, self.onbuttonok)

    def onbutton1(self, _):
        # app = wx.App()
        dialog = wx.FileDialog(None, "Choose a categorization file:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            cf = dialog.GetPath()
            dialog.Destroy()
            self.file[0].SetValue(cf)

    def onbutton2(self, _):
        # app = wx.App()
        dialog = wx.FileDialog(None, "Choose a configuration file:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            od = dialog.GetPath()
            dialog.Destroy()
            self.file[1].SetValue(od)
            
    def onbuttonok(self, _):
        # Check entries
        if not self.file[0].GetValue():
            # a2 = wx.App()
            d = wx.MessageDialog(
                None, "Please specify a categorization file!",
                "IMPORTANT", wx.OK)
            d.ShowModal()
        if not self.file[1].GetValue():
            # a1 = wx.App()
            d = wx.MessageDialog(
                None, "Please specify a configuration file!",
                "IMPORTANT", wx.OK)
            d.ShowModal()

        names = ['default_categorization_file = ', 'default_config_file = ']
        data = [''] * 2
        for ii in range(2):
            x = self.file[ii].GetValue()
            data[ii] = names[ii] + "'" + x.encode("utf-8") + "'"

        filename = 'pyBIDSconv_defaults.py'
        outfile = open(filename, 'w')

        outfile.write("\n")
        for item in data:
            outfile.write("%s\n" % item)

        self.Close()


class StartValidator:
    def __init__(self):
        webbrowser.open('http://incf.github.io/bids-validator/', new=2)


class BIDShome:
    def __init__(self):
        webbrowser.open('http://bids.neuroimaging.io/', new=1)


class BIDSspecs:
    def __init__(self):
        webbrowser.open('http://bids.neuroimaging.io/bids_spec1.1.0.pdf', new=1)


class CheckFilename:
    def __init__(self, folder2conv, subjnum, sessionnumber, task2conv, acq2conv, run2conv, rec2conv, label2conv):

        # Check new filenames for duplicates
        # -------------------------------------
        nf_list = []
        nf_list2 = []

        for ii in range(len(folder2conv)):
            # create new filenames
            sub1 = "sub-" + subjnum

            if sessionnumber == "":
                sess1 = ""
            else:
                sess1 = "_ses-" + str(sessionnumber)

            if task2conv[ii] == "":
                if folder2conv == "func":
                    # oo = wx.App()
                    infomsg = "A task name needs to be specified for each functional session." + \
                              "\n Taskname missing for sequence " + str(ii)
                    d = wx.MessageDialog(None, infomsg, "INPUT ERROR!", wx.OK)
                    d.ShowModal()
                    d.Destroy()
                    return
                else:
                    task1 = ""
            else:
                task2conv[ii] = re.sub(" ", "", task2conv[ii])
                task1 = "_task-" + task2conv[ii]

            if acq2conv[ii] == "":
                acq1 = ""
            else:
                acq1 = "_acq-" + acq2conv[ii]

            if run2conv[ii] == "":
                run1 = ""
            else:
                run1 = "_run-" + run2conv[ii]

            if rec2conv[ii] == "":
                rec1 = ""
            else:
                rec1 = "_rec-" + rec2conv[ii]

            nf_list.append(sub1 + sess1 + task1 + acq1 + run1 + rec1 + "_" + label2conv[ii])
            nf_list2.append("...\\" + folder2conv[ii] + "\\" + sub1 + sess1 + task1 + acq1 + run1 + rec1 + "_" +
                            label2conv[ii])

        dup = [x for n, x in enumerate(nf_list2) if x in nf_list2[:n]]
        if len(dup) > 0:
            dialogtext = "Duplicate filenames detected!\nTransfer not possible until filenames are unique " \
                         "in output folders. \n"
            for ii in range(len(dup)):
                dialogtext = dialogtext + dup[ii] + "\n"

            dialogtext = dialogtext + "\n Suggestion: Add run numbers for equal scans or rec or acq labels: " \
                                      "\n (e.g. rec: ""empty field"" for raw vs norm for normaliyed images or \n" \
                                      "acq: singleband vs multiband)"
            # oo = wx.App()
            d = wx.MessageDialog(
                None, dialogtext, "IMPORTANT", wx.OK)
            d.ShowModal()

        else:
            # oo2 = wx.App()

            dialogtext = "Filenames are ok!\n\nThe following files will be transfered:\n\n"

            for ii in range(len(nf_list2)):
                dialogtext = dialogtext + nf_list2[ii] + "\n"

            dialogtext = dialogtext + "\n\nIf you are ready to transfer, press the OK and then the TRANSFER button!"

            d = wx.MessageDialog(
                None, dialogtext, "OK", wx.OK)


            d.ShowModal()


# #####################################################################################################################
# #####################################################################################################################
#
# Main
#
# #####################################################################################################################
# #####################################################################################################################

def main():
    x = wx.App()
    # dcm = GetDCMinfo()
    # dcm = GetInput()
    GetInput()
    x.MainLoop()


if __name__ == '__main__':
    main()