"""
Generates a list of all .csv files in the input directory, and copies them
into the appropriate folder.
"""

import os

import shutil
# import os


def getAllFilesPaths(directoryIn):
    paths = []
    for root, dirs, files in os.walk(directoryIn):
        for file in files:
            if file.endswith(".csv"):
                relative_path = os.path.relpath(os.path.join(root, file), directoryIn)
                paths.append(relative_path)
    # return [os.path.join(dbName, path) for path in paths]
    return paths

def generate_csv_list(filePaths, output_file, csvTitle, dbName):
    """
    Creates a list of 
    """
    # filePaths = getAllFilesPaths(directory)

    
    with open(output_file, 'w') as f:
        
        f.write(csvTitle + "\n")
        
        f.write(f"{'='*len(csvTitle)}" + "\n")
        f.write("\n")
        
        dbtype = dbName.replace('DB', '')
        f.write(f"The following {dbtype} databases are part of limitstates:\n")

        
        for relative_path in filePaths:
            components = relative_path.split('\\')
            name = components[2].replace('.csv', '')
            outputPath = os.path.join(dbName, relative_path)
            outputPath = outputPath.replace('\\', '/')
            
            f.write(f" - :download:`{components[0]} {components[1]}, {name} <{outputPath}>`.\n")

def copy_files(sourceDir, outputDir, paths):
    for path in paths:
        
        source_file = os.path.join(sourceDir, path)
        dest_file   = os.path.join(outputDir, path)
        
        # if os.path.isfile(source_file)
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        shutil.copy(source_file, dest_file)


if __name__ == "__main__":
    directoryIn = r'C:\Users\Christian\Documents\Python Scripts\localPackage\limitstates\src\limitstates\objects\section\db'
    directoryOut = r'C:\Users\Christian\Documents\Python Scripts\localPackage\limitstates\doc\readthedocs\source\rst\sectionDB'
    output_file = 'objects-section-db.rst'
    
    filePaths = getAllFilesPaths(directoryIn)
    generate_csv_list(filePaths, output_file, 'Section Databases', 'sectionDB')
    copy_files(directoryIn, directoryOut, filePaths)
    
    
    
    directoryIn = r'C:\Users\Christian\Documents\Python Scripts\localPackage\limitstates\src\limitstates\objects\material\db'
    directoryOut = r'C:\Users\Christian\Documents\Python Scripts\localPackage\limitstates\doc\readthedocs\source\rst\matDB'

    output_file = 'objects-material-db.rst'
    filePaths = getAllFilesPaths(directoryIn)
    generate_csv_list(filePaths, output_file, 'Material Databases', 'matDB')
    copy_files(directoryIn, directoryOut, filePaths)
