
# ![Alt text](pyBIDSconv_logo.png?raw=true "Title")

##   pyBIDSconv

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


*Install*  
You can use either the prebuild binaries for Windows 64bit or you can use the python source code. 

For using pyBIDSconv source code:
Copy the pyBIDSconv folder in a folder of your choice on your system and add the directory to your PYTHONPATH.
For For the Windows 7 binary file:
Extract the pyBIDSconv\_win\_64bit.zip into a folder of your choice on your system 


*Dependencies*  
- For using pyBIDSconv you need to have [dcm2niix](https://github.com/rordenlab/dcm2niix/releases) installed.

- For using pyBIDSconv source code: pyBIDSconv is developed in python 2.7 and the following packages need to be installed: pydicom, numpy, wxpython, pandas. (pyBIDSconv was developed and tested with the following versions: python: 2.7.14, numpy: 1.13.3, wx: 4.0.0rc1, dicom: 0.9.9, pandas: 0.20.3)


*Licence*  
pyBIDSconv by Michael Lindner is licensed under CC BY 4.0
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;


**[Download pyBIDSconv](https://github.com/pyBIDSconv/pyBIDSconv)**

Author:  
Michael Lindner  
University of Reading, 2018  
School of Psychology and Clinical Language Sciences  
Contact: ![contact email](contact.png?raw=true "contact email")
