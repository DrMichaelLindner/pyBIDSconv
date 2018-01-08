

pyBIDSconv

version 1.0 beta

User Manual

Table of contents

    1. About pyBIDSconv
          1.1 What is the BIDS structure?
          1.2 Installation
          1.3 Using pyBIDSconv
    2. Dialogs of pyBIDSconv
          2.1 Get Input
                2.1.1 Menubar
                      2.1.1.1 pyBIDSconv TOOLS
                2.1.2   Input Fields
                      2.1.2.1   Subject dicom directory
                      2.1.2.2   Subject number
                      2.1.2.3   Group
                      2.1.2.4   Session number
                      2.1.2.5   Output BIDS directory
                      2.1.2.6  Categorization file
                      2.1.2.7  Configuration file
          2.2 Check Sequences
                2.2.2   Input Fields
                      2.2.2.1 Transfer?
                      2.2.2.2 Folder
                      2.2.2.3 _task-
                      2.2.2.4 _run-
                      2.2.2.5 _acq
                      2.2.2.6 _rec-
                      2.2.2.7 _label
                      2.2.2.8 Ref
    * 3. FAQ
          3.1 What is a .tsv file?
          3.2 What is a .json file?
          3.3 How does a participant.tsv file looks like?
          3.4 How does a dataset_description.json file looks like?
          3.5 What is the catagorisation file?
          3.6 What is the configuration file?
          3.7 What is the task event tsv file?


      


1. About pyBIDSconv

This tool is designed to convert MR dicom files into the BIDS structure.



1.1 What is the BIDS structure?
BIDS was introduces as  a new stadnard for neuroimaging and behavioral data based on a file-system hierarchy, with files containing key metadata, to to describe the data of a human neuroimaing experiment.
In the table below you can find a typical example of the BIDS structure with a short description on the right.
More information about the BIDS Structure can be found on the BIDS homepage, in the BIDS specs and in the BIDS publication.

Example of the BIDS structure
Studyfolder/
    participants.tsv
    dataset_description.json
    README
    CHANGES
    code/
        deface.py
    derivatives/
    sub-01/
        sub-control01_scans.tsv
        anat/
            sub-01_T1w.nii.gz
            sub-01_T1w.json
            sub-01_T2w.nii.gz
            sub-01_T2w.json
        func/
            sub-01_task-nback_bold.nii.gz
            sub-01_task-nback_bold.json
            sub-01_task-nback_events.tsv
            sub-01_task-nback_physio.tsv.gz
            sub-01_task-nback_physio.json
            sub-01_task-nback_sbref.nii.gz
        dwi/
            sub-01_dwi.nii.gz
            sub-01_dwi.bval
            sub-01_dwi.bvec
        fmap/
            sub-01_phasediff.nii.gz
            sub-01_phasediff.json
            sub-01_magnitude1.nii.gz
            sub-01_magnitude1.json

    sub-02/
        ...


	
In this example you can see a typical example of neuroimaging data stored in the BIDS structure. The data is organized in a main studies folder and each subject has an own subfolder. In each subjects subfolder there will be optional subfolders for each session (if multiple session per subject are scanned), otherwise in case of ony one session there are subfolders for each type of scans: anat (structural scans e.g. MPRAGE, T2 weighted images etc), func (functional scans - BOLD, ASL, etc), dwi (diffusion weighted imaged - DTI), and fmap (fieldmaps). Optionally there can be an additional folder beh for behavioral data (with no MRI). Each imaging data file in the folders follows a strict rule of filename and has to have a describing json file. Additional each subject (and or session ) needs to have a .tsv file (What is a .tsv file?) containing the filenames.

In the BIDS folder needs to be a participants.tsv (or .json)  file, containing information about all participants and a dataset_description,json file containing information about the dataset itself. In a form free README file more detailed description about the dataset can be provided and in the CHANGE file all changes to the BIDS structure can be logged. Optionally there can be additional folder: code (for codes and scripts for e.g. the task stimuliation and/or for preprocessing and analysis), and derivatives (e.g. for alternative versions of the data).

All the black files and folders will be generated and updated by using pyBIDSconv. Only the red files can/need to be created from the user manually.



1.2 Installation

Download and unzip the pyBIDSconv folder to a directory of your choice and add this directory to your PYTHONPATH.


Software dependencies

    * dcm2niix

          DICOM to NIfTI conversion is done with dcm2niix converter. See their github for source or NITRC for compiled versions.

    * The following python packages need to be installed:

          dicom, numpy, wx, pandas, json
          os, shutil, glob, datetime, webbrowser, sys, time, re

          pyBIDSconv was developed and tested with the following versions:
          python 2.7.14
          numpy: 1.13.3
          wx: 4.0.0rc1
          dicom: 0.9.9
          json: 2.0.9
          pandas: 0.20.3




1.3 Using pyBIDSconv

You can start pyBIDSconv with the command pyBIDSconv in a terminal window.

For the usage of pyBIDSconv you need to setup a categorization and a configuration file. An example for each of this file is included in the pyBIDSconv folder for a SIEMENS Prisma fit Scanner. See 3.5 (categorization file) and 3.6 (configuration file) for more dfeteails about the content of these files



2. Dialogs of pyBIDSconv

2.1 Get Input
Get Input is the first GUI of pyBIDSconv where the user needs to specify the data folder from where to where the data should be transfered.

2.1.1 Menubar
In the menubar the user can open:

    * The user manual for help
    * The BIDS
          o homepage
          o specifications
          o online validator
    * pyBIDSconv TOOLS
          o dataset_description.json file editor
          o Create pyBIDSconv_default.py files
          o Create/edit pyBIDSconv config file


2.1.1.1 pyBIDSconv TOOLS
1) dataset_description.json file editor
This tool allows to edit the entries of the dataset_description.json file.

2) Create pyBIDSconv_default.py files
With this tool a pyBIDSconv_default.py file can be created to specify the default config and categorization file.

3) Create/edit pyBIDSconv config file
With this tool a new pyBIDSconv config file can be create or an existing one edited.

ReconstructionInfoInImageType:  Specify strings to search in the dicom.ImageType to be used for the rec label of the filenames in the BIDS structure.

PhaseInfoForFmapsBySequenceDescriptionSubstring: Specify substrings of the sequence description which can be used to identify the phase encoding direction of the fieldmap to be used as acq labels of the filenames in the fmap dorectory in the BIDS structure.

ExclusionsBySequenceDescriptionContent: Specify substrings of any part of the sequence description which can be used to exclude the scan from the transfer process.


ExclusionsBySequenceDescriptionEnd: Specify substrings of the end of the sequence description which can be used to exclude the scan from the transfer process.

2.1.2   Input Fields
In the following all input fields of the Get Input Dialog are described in more detail:

2.1.2.1   Subject dicom directory
The subject dicom directory is the input directory. This folder should only contain all dicom file from one subject of one session!

2.1.2.2   Subject number
The subject number needs to be specified and will be used for the subject folder and filenames: E.g. 1 --> sub-001

2.1.2.3   Group
The group info is optional. If a group name is specified, it will be used for the filenames: E.g. control --> sub-control001

2.1.2.4   Session number
If participant will be scanned multiple time in the study, you can specify which session you add to the BIDS structure. In this case the sublect folders will have subfolder for each session (e.g. sub-001\ses-1\). Additionally the session number will appear in the filenames as well (e.g. sub-001_ses-1_.....nii.gz).

2.1.2.5   Output BIDS directory
The BIDS output directory is the directory where the BIDS structure of the study is stored.

2.1.2.6  Categorization file
Here you need to specify your categorization file (see 3.5 for more detail about the content of the file).

2.1.2.7  Configuration file
Here you need to specify your configuration file (see 3.6 for more detail about the content of the file).




2.2 Check Sequences

2.2.2   Input Fields
In general, the naming of files in the BIDS structure followes specific rules.

e.g.
sub-SubjectNumber_sess-SessionNumber_task-TaskName_run-RunNumber_acq-YourAcqInfo_rec-YourReconstrucitonInfo_label

But not all parts of the filename appear in all types of scans and some of the filename parts are optional.
E.g. _task- needs only be specified for functional data and _run-, _acq- and _rec- are optional
pyBIDSconv allows you to add information to all filename parts which are relevant depending on the scan type. If you leave a fleld of an optional filename part empty, the filename part will not be added.

In the following all input fields of the Check Sequences Dialog are described in more detail:

2.2.2.1 Transfer?
Here you can specify if you want to transfer this sequence or not. The automatic detection should have already excluded some. But if you want to exclude more (because of e.g. a stopped sequence, techical problems, etc) than you can select "No". If you want to transfer a sequnce whic was automatically excluded, then change the value to "Yes".

2.2.2.2 Folder
The folder represents the BIDS folder where the data will be copied to. Please check if the automatic detection was working properly. If not please correct it.

2.2.2.3 _task-
For each functional scan a taskname needs to provided. The task name will appear in the filename. In case of restig sta te data as functional run the task name should contain "rest".

Each functional (which is not labeled with "rest") needs to have an additional event tsv file (See 3.7 for more detail)

2.2.2.4 _run-
If you have multiple runs of the same task, then give then the same taskname and spcify the number of the run here.

2.2.2.5 _acq
The acq parameter can be used to distinguish a different set of parameters used for acquiring the same modality. E.g highres and lowres for different structural scans or the different phase incoding directions of fieldmaps etc.

2.2.2.6 _rec-
The rec parameter can be used to distinguish different reconstruction algorithms (e.g. ones using online motion correction or normalization)

2.2.2.7 _label
The label is always the last bit of the filename representing the scan type.

E.g.
structural scans: T1w, T2w, FLAIR, ...
functional scan: bold, asl, ...
DTI scans: dwi
fieldmaps: fieldmap, magnitude, phase, phasediff, etc

Other labels:
event for task evet files
physio for physio data

See  BIDS specs for more details.

2.2.2.8 Ref
In case of a fieldmap sequence the correspocning json file to the nifti file needs to contain the info for which sequence the fieldmap is used for. Therefore you can specify the sequences number from the column "Nr" (seperated by comma) and pyBIDSconv will add the information to the json file for you.



3. FAQ

3.1 What is a .tsv file?
TSV files are essentially text files which can be opened and edited with each text editor. TSV files do have tabs as delimiters for the columns. The first line of a .tsv file typically contains the column headers and the further lines the data for each column. See 3.3 for en axample of a .tsv file for BIDS.

3.2 What is a .json file?
JSON (JavaScript Object Notation) is an open-standard file format taht uses human readable text to transmit data objectss consisting of attribute - value pairs and array data types.
JSON is a data-interchange format, that is easy for humans to read and write and easy for machines to parse and generate. JSON is a text format (bvased on a subset of JavaScript) that is completely language independent but uses conventions that are familiar to programmers of the C-family of languages, including C, C++, C#, Java, JavaScript, Perl, Python, and many others.
attribute - value pairs
In general: In JSON objects (e.g. attribute - value pairs) are stored in curly brackets, seperated by comma. The attributre - vaue pairs are seperated by colon. E.g.:
{
    "attribute1": "ExampleString",
    "attribute2": 2.1234
}

See 3.4 for an example of a .json file for BIDS

More information about the JSON format can be found on www.json.org and https://en.wikipedia.org/wiki/JSON


3.3 How does a participant.tsv file looks like?
Here is an example of a minimal participant.tsv file. It can contain more columns for more information. But be aware, pyBIDSconv only supports these three columns. Additional columns need to be added manually.

participant_id    age    sex
sub-01    M    28
sub-02    F    25
sub-03    M    32
sub-04    F    29
sub-05    F    31
...

3.4 How does a dataset_description.json file looks like?
Here is an example of a dataset_description.json file. Only the first two line (in bold) are the recommended inrmation stored in this file. All other information is optional. pyBIDSconv only created the recommended input. But the user can edit the file easily with the build in dataset_description editor. (Get Input GUI --> Tools --> dataset_description editor)

{
    "Name": "Name of the experiment",
    "BIDSVersion": "1.0.2",
    "License": "CC1",
    "Authors": ["First Author", "Second Author"],
    "Acknowledgements": "say here what are your acknowledgments",
    "HowToAcknowledge": "say here how you would like to be acknowledged",
    "Funding": "list your funding sources",
    "ReferencesAndLinks": ["a paper", "a resource to be cited when using the data", "any other refs"],
    "DatasetDOI": "The DOI of your dataset"
}

3.5 What is the catagorisation file?
The categorisation file is basically .tsv file containing the link between:

Column 	Type			Description
1	BIDS folder 		Where the data with the specs in 2-4 should go to in the BIDS subject folder (e.g. func, anat, etc)
2	sequence name 		substring of sequence name (for SIEMENS in dcm.SequenceName)
3	acquisition type 	2D or 3D
4	sequence description 	substring of name the sequence had on the Scanner console (for SIEMENS in dcm.SequenceDescription)
5	BIDS label 		The label in the BIDS file name format

The categorisation file has now columns headers!

The information in the categorization file is used to automatically catgorize the sequences in the dicom input folder to the BIDS hierarchy. The more complete and accurate the information in the categorixation file the better the automatic categorization will work. pyBIDSconv comes with a categorization file for SIEMENS Prisma scanners but can be extended or replaced by the user for other MR scanners.

3.6 What is the configuration file?
The config file is a python script (.py) that contains user defined information for the automatically detection of 1) different reconstruction types (e.g. Normalized or online motion corrected dicoms) 2) exclusion of sequences by their names (substrings of dicom.SeriesDescription) on the scanner console, and optional  3) catagorize phase encoding direction for the acq from the sequence name.

ReconstructionInfoInImageType
PhaseInfoForFmapsByFilenameSubstring
ExclusionsByFilenameContent

Example:
ReconstructionInfoInImageType = ['NORM','MOCO']
ExclusionsByFilenameContent = ['localizer', 'aah','scout', 'phoenix','_fa','_trace','_colfa']
PhaseInfoForFmapsByFilenameSubstring = ["_pa", "_ap", "_rl", "_lr"]

3.7 What is the task event tsv file?
Each functional (which is not labeled with "rest") needs to have an additional event tsv file. Teh name must be identical to the corresponding functional nifiti file. E.g.:
sub-001_task-MyTask_bold.nii.gz
sub-001_task-MyTask_bold.tsv

The task event file should included at least onsets and durations (and response times if recorded). Additional optional columns are trial_type, stim_file, identifier etc. See  BIDS specs for more details.

Example of a task event file:
onset    duration    trial_type    response_time
1.2        0.6            go            1.435
5.6        0.6            stop         1.739




