# tess

An extremely basic python script for converting PDFs to TIFFs and 
performing OCR with tesseract.

To run the script, first ensure that ImageMagick 7 and Tesseract 4 are 
installed and can be run from the command line. (Later versions may work but
this has only been tested with the above versions.)

You'll also need to ensure that the correct language models are installed.
[The tesseract wiki](https://github.com/tesseract-ocr/tesseract/wiki)
has installation instructions for various operating systems.

Once you have the software installed, you can run the script:

    tess.py [--language LANGUAGE] files [files ...]

    ---------

    files:          One or more PDF files to process
    --language:     The tesseract language ID code for the language model
                        to use. E.g. eng (English), deu (German) or 
                        ita (Italian). The default is eng.

An Italian-language sample file is provided in the `testdata` folder. To 
process it, run the below command:

    tess.py --language ita testdata/1961_Alessandria.pdf
