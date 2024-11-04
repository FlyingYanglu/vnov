
import logging
import re
import os
import json

class Book():
    def __init__(self, filename, nochapters=False, stats=False):
        self.filename = filename
        self.nochapters = nochapters
        self.contents = self.getContents()
        self.lines = self.getLines()
        self.headings = self.getHeadings()
        # Alias for historical reasons. FIXME
        self.headingLocations = self.headings
        self.ignoreTOC()
        logging.info('Heading locations: %s' % self.headingLocations)
        headingsPlain = [self.lines[loc] for loc in self.headingLocations]
        logging.info('Headings: %s' % headingsPlain)
        self.chapters = self.getTextBetweenHeadings()
        # logging.info('Chapters: %s' % self.chapters)
        self.numChapters = len(self.chapters)

    def processBook(self, save_dir, stats=False):
        if stats:
            self.getStats(save_dir)
        else:
            self.writeChapters(save_dir)
            self.getStats(save_dir)


    def getContents(self):
        """
        Reads the book into memory.
        """
        with open(self.filename, errors='ignore') as f:
            contents = f.read()
        return contents

    def getLines(self):
        """
        Breaks the book into lines.
        """
        return self.contents.split('\n')

    def getHeadings(self):

        # Form 1: Chapter I, Chapter 1, Chapter the First, CHAPTER 1
        # Ways of enumerating chapters, e.g.
        arabicNumerals = '\d+'
        romanNumerals = '(?=[MDCLXVI])M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})'
        numberWordsByTens = ['twenty', 'thirty', 'forty', 'fifty', 'sixty',
                              'seventy', 'eighty', 'ninety']
        numberWords = ['one', 'two', 'three', 'four', 'five', 'six',
                       'seven', 'eight', 'nine', 'ten', 'eleven',
                       'twelve', 'thirteen', 'fourteen', 'fifteen',
                       'sixteen', 'seventeen', 'eighteen', 'nineteen'] + numberWordsByTens
        numberWordsPat = '(' + '|'.join(numberWords) + ')'
        ordinalNumberWordsByTens = ['twentieth', 'thirtieth', 'fortieth', 'fiftieth', 
                                    'sixtieth', 'seventieth', 'eightieth', 'ninetieth'] + \
                                    numberWordsByTens
        ordinalNumberWords = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 
                              'seventh', 'eighth', 'ninth', 'twelfth', 'last'] + \
                             [numberWord + 'th' for numberWord in numberWords] + ordinalNumberWordsByTens
        ordinalsPat = '(the )?(' + '|'.join(ordinalNumberWords) + ')'
        enumeratorsList = [arabicNumerals, romanNumerals, numberWordsPat, ordinalsPat] 
        enumerators = '(' + '|'.join(enumeratorsList) + ')'
        form1 = 'chapter ' + enumerators

        # Form 2: II. The Mail
        enumerators = romanNumerals
        separators = '(\. | )'
        titleCase = '[A-Z][a-z]'
        form2 = enumerators + separators + titleCase

        # Form 3: II. THE OPEN ROAD
        enumerators = romanNumerals
        separators = '(\. )'
        titleCase = '[A-Z][A-Z]'
        form3 = enumerators + separators + titleCase

        # Form 4: a number on its own, e.g. 8, VIII
        arabicNumerals = '^\d+\.?$'
        romanNumerals = '(?=[MDCLXVI])M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\.?$'
        enumeratorsList = [arabicNumerals, romanNumerals]
        enumerators = '(' + '|'.join(enumeratorsList) + ')'
        form4 = enumerators

        pat = re.compile(form1, re.IGNORECASE)
        # This one is case-sensitive.
        pat2 = re.compile('(%s|%s|%s)' % (form2, form3, form4))

        # TODO: can't use .index() since not all lines are unique.

        headings = []
        for i, line in enumerate(self.lines):
            if pat.match(line) is not None:
                headings.append(i)
            if pat2.match(line) is not None:
                headings.append(i)

        if len(headings) < 3:
            logging.info('Headings: %s' % headings)
            logging.error("Detected fewer than three chapters. This probably means there's something wrong with chapter detection for this book.")
            exit()

        self.endLocation = self.getEndLocation()

        # Treat the end location as a heading.
        headings.append(self.endLocation)

        return headings

    def ignoreTOC(self):
        """
        Filters headings out that are too close together,
        since they probably belong to a table of contents.
        """
        pairs = zip(self.headingLocations, self.headingLocations[1:])
        toBeDeleted = []
        for pair in pairs:
            delta = pair[1] - pair[0]
            if delta < 4:
                if pair[0] not in toBeDeleted:
                    toBeDeleted.append(pair[0])
                if pair[1] not in toBeDeleted:
                    toBeDeleted.append(pair[1])
        logging.debug('TOC locations to be deleted: %s' % toBeDeleted)
        for badLoc in toBeDeleted:
            index = self.headingLocations.index(badLoc)
            del self.headingLocations[index]

    def getEndLocation(self):
        """
        Tries to find where the book ends.
        """
        ends = ["End of the Project Gutenberg EBook",
                "End of Project Gutenberg's",
                "\*\*\*END OF THE PROJECT GUTENBERG EBOOK",
                "\*\*\* END OF THIS PROJECT GUTENBERG EBOOK"]
        joined = '|'.join(ends)
        pat = re.compile(joined, re.IGNORECASE)
        endLocation = None
        for line in self.lines:
            if pat.match(line) is not None:
                endLocation = self.lines.index(line)
                self.endLine = self.lines[endLocation]
                break

        if endLocation is None: # Can't find the ending.
            logging.info("Can't find an ending line. Assuming that the book ends at the end of the text.")
            endLocation = len(self.lines)-1 # The end
            self.endLine = 'None'

        logging.info('End line: %s at line %s' % (self.endLine, endLocation))
        return endLocation

    def getTextBetweenHeadings(self):
        chapters = []
        lastHeading = len(self.headingLocations) - 1
        for i, headingLocation in enumerate(self.headingLocations):
            if i != lastHeading:
                nextHeadingLocation = self.headingLocations[i+1]
                chapters.append(self.lines[headingLocation+1:nextHeadingLocation])
        return chapters

    def zeroPad(self, numbers):
        """
        Takes a list of ints and zero-pads them, returning
        them as a list of strings.
        """
        maxNum = max(numbers)
        maxDigits = len(str(maxNum))
        numberStrs = [str(number).zfill(maxDigits) for number in numbers]
        return numberStrs

    def getStats(self, save_dir):
        """
        Returns statistics about the chapters, like their length, and saves them in a JSON file in save_dir.
        """
        # Ensure the save_dir exists
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Calculate statistics
        numChapters = self.numChapters
        averageChapterLength = sum([len(chapter) for chapter in self.chapters]) / numChapters
        book_name = os.path.basename(self.filename).split('.')[0]

        # Create a dictionary with your desired structure
        stats_dict = {
            "image": None,  # You can replace None with actual image URL if available
            "name": book_name,
            "author": None,  # You can replace None with the actual author if available
            "category": None,  # You can replace None with the actual category if available
            "keywords": [None, None, None, None],  # Replace None with actual keywords if available
            "url": None,  # You can replace None with the actual URL if available
            "description": None,  # You can replace None with the actual description if available
            "filename": self.filename,
            "average_chapter_length": averageChapterLength,
            "number_of_chapters": numChapters
        }

        # Save the dictionary as a JSON file
        json_file_path = os.path.join(save_dir, 'info.json')
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(stats_dict, json_file, ensure_ascii=False, indent=4)
        
        logging.info(f'Statistics saved to {json_file_path}')

    def writeChapters(self, save_dir):
        """
        Writes chapters to files in the specified save_dir and saves chapter metadata in chapters.json.
        """
        # Ensure the save_dir exists
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        chapterNums = list(range(1, len(self.chapters) + 1))
        logging.debug('Writing chapter headings: %s' % chapterNums)
        basename = os.path.basename(self.filename)
        noExt = os.path.splitext(basename)[0]

        chapters_list = []  # List to store metadata for chapters

        if self.nochapters:
            # Join together all the chapters and lines.
            text = ""
            for chapter in self.chapters:
                # Stitch together the lines.
                chapter = '\n'.join(chapter)
                # Stitch together the chapters.
                text += chapter + '\n'
            ext = '-extracted.txt'
            path = os.path.join(save_dir, noExt + ext)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
        else:
            logging.info('Filename: %s' % noExt)
            outDir = save_dir
            if not os.path.exists(outDir):
                os.makedirs(outDir)
            ext = '.txt'

            # Iterate over each chapter and save
            for num, chapter in zip(chapterNums, self.chapters):
                # Construct the file path
                file_name = f"{num}{ext}"
                path = os.path.join(outDir, file_name)
                
                # Write the chapter content to a file
                logging.debug(chapter)
                chapter_text = '\n'.join(chapter)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(chapter_text)

                # Construct metadata for the chapter
                chapter_metadata = {
                    "name": None,  # Replace with actual chapter name if available
                    "url": None,  # Replace with actual URL if available
                    "file_name": file_name
                }
                chapters_list.append(chapter_metadata)

        # Save the chapters_list as chapters.json
        json_file_path = os.path.join(save_dir, 'chapters.json')
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(chapters_list, json_file, ensure_ascii=False, indent=4)
        
        logging.info(f'Chapters metadata saved to {json_file_path}')