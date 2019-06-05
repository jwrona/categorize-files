# File Categorization Utility
Create a categorized image of an unorganized directory (e.g. disk dump).
Each contained file is classified according to its suffix or MIME type and
moved/copied/linked to a corresponding directory in the output directory.

## Quick Example
If you want to organize a directory which looks like this (or possibly a
thousand times worse):
```
big_mess
├── definitely_not_porn
│   ├── cool.mkv
│   ├── omg.mkv
│   └── secret
│       ├── nice.jpg
│       └── wow.mkv
├── documents
│   ├── even_more_important
│   │   ├── not_a_doc.doc
│   │   └── untitled.ods
│   ├── important
│   │   ├── document.odt
│   │   └── untitled.ods
│   └── recording.mp3
├── random_stuff
│   ├── document.docx
│   ├── howto.pdf
│   └── paper.docx
└── song.mp3
```
you can run `categorize_files.py -c mime_content -p copy -i flat_name input` to
get it done:
```
big_mess_categorized_by_mime_content
├── application
│   ├── pdf
│   │   └── howto.pdf
│   ├── vnd.oasis.opendocument.spreadsheet
│   │   ├── untitled.ods
│   │   └── untitled.ods.1
│   ├── vnd.oasis.opendocument.text
│   │   ├── document.odt
│   │   └── not_a_doc.doc
│   └── vnd.openxmlformats-officedocument.wordprocessingml.document
│       ├── document.docx
│       └── paper.docx
├── audio
│   └── mpeg
│       ├── recording.mp3
│       └── song.mp3
├── image
│   └── jpeg
│       └── nice.jpg
└── video
    └── x-matroska
        ├── cool.mkv
        ├── omg.mkv
        └── wow.mkv
```

## Parameters
There are three essential parameters: classification criterion, file system
operation used to create the categorized files, and output image structure.
Several other parameters are available, for more information see the built-in
help (`-h/--help argument`).
To demonstrate how these parameters affect the output, the following directory
tree will be used as input:
```
input
├── app1
│   ├── python_bytecode.pyc
│   ├── python_script.py
│   └── shell_script
└── app2
    ├── python_bytecode.pyc
    ├── python_script.py
    └── shell_script
```

### Classification Criterion
A criterion by which files are classified.
Set by the `-c/--criterion` argument with one of the following options:

- `suffix` -- the file suffix (extension)
```
input_categorized_by_suffix
├── py
│   ├── python_script.py
│   └── python_script.py.1
├── pyc
│   ├── python_bytecode.pyc
│   └── python_bytecode.pyc.1
└── unknown
    ├── shell_script
    └── shell_script.1
```
- `mime_name` -- guess the MIME type of the file based on its filename
```
input_categorized_by_mime_name
├── application
│   └── x-python-code
│       ├── python_bytecode.pyc
│       └── python_bytecode.pyc.1
├── text
│   └── x-python
│       ├── python_script.py
│       └── python_script.py.1
└── unknown
    ├── shell_script
    └── shell_script.1
```
- `mime_content` -- guess the MIME type of the file based on its content
```
input_categorized_by_mime_content
├── application
│   └── octet-stream
│       ├── python_bytecode.pyc
│       └── python_bytecode.pyc.1
└── text
    ├── x-python
    │   ├── python_script.py
    │   └── python_script.py.1
    └── x-shellscript
        ├── shell_script
        └── shell_script.1
```

### File System Operation
A file system operation used to create the categorized file.
Set by the `-p/--operation` argument with one of the following options:

- `move` -- move (rename) the file
- `copy` -- copy the file
- `hard_link` -- create a hard link pointing to the file
- `symbolic_link` -- create a symbolic link (symlink) pointing to the file
```
input_categorized_by_suffix
├── py
│   ├── python_script.py -> /path/to/the/input/app2/python_script.py
│   └── python_script.py.1 -> /path/to/the/input/app1/python_script.py
├── pyc
│   ├── python_bytecode.pyc -> /path/to/the/input/app2/python_bytecode.pyc
│   └── python_bytecode.pyc.1 -> /path/to/the/input/app1/python_bytecode.pyc
└── unknown
    ├── shell_script -> /path/to/the/input/app2/shell_script
    └── shell_script.1 -> /path/to/the/input/app1/shell_script
```

### Output Image Structure
Determines file names and a directory structure of the output image directory.
Set by the `-i/--image-structure` argument with one of the following options:

- `flat_name` -- input directories are not preserved.
  Collisions are possible.
```
input_categorized_by_suffix
├── py
│   ├── python_script.py
│   └── python_script.py.1
├── pyc
│   ├── python_bytecode.pyc
│   └── python_bytecode.pyc.1
└── unknown
    ├── shell_script
    └── shell_script.1
```
- `flat_path` -- input directories encoded in the file name (path separator
  characters are replaced with underscores).
  Collisions are possible.
```
input_categorized_by_suffix
├── py
│   ├── app1_python_script.py
│   └── app2_python_script.py
├── pyc
│   ├── app1_python_bytecode.pyc
│   └── app2_python_bytecode.pyc
└── unknown
    ├── app1_shell_script
    └── app2_shell_script
```
- `nested` -- input directories are preserved.
  Collisions are not possible.
```
input_categorized_by_suffix
├── py
│   ├── app1
│   │   └── python_script.py
│   └── app2
│       └── python_script.py
├── pyc
│   ├── app1
│   │   └── python_bytecode.pyc
│   └── app2
│       └── python_bytecode.pyc
└── unknown
    ├── app1
    │   └── shell_script
    └── app2
        └── shell_script
```

## Known Bugs and TODOs
- Using the `flat_path` output image structure may create file names longer than
  the file system can handle.
  - Currently `[Errno 36] File name too long: 'filename'` is reported and the
    affected file is skipped.
  - In POSIX, the limis is defined by `NAME_MAX` which is usually set to 255
    chars.
  - To eliminate this, some kind of name ellipsization would be necessary.
