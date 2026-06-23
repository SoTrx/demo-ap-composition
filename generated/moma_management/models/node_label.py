from enum import Enum

class NodeLabel(str, Enum):
    CrFileObject = "cr:FileObject",
    CrFileSet = "cr:FileSet",
    CrField = "cr:Field",
    TextSet = "TextSet",
    ImageSet = "ImageSet",
    CSV = "CSV",
    Table = "Table",
    RelationalDatabase = "RelationalDatabase",
    PDFSet = "PDFSet",
    JSONSet = "JSONSet",
    JSON = "JSON",
    XMLSet = "XMLSet",
    XML = "XML",
    Text = "Text",
    Image = "Image",
    VideoSet = "VideoSet",
    Column = "Column",

