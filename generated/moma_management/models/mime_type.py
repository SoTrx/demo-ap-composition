from enum import Enum

class MimeType(str, Enum):
    ApplicationVndMsExcel = "application/vnd.ms-excel",
    ApplicationXIpynb_plus_json = "application/x-ipynb+json",
    ApplicationJson = "application/json",
    ApplicationJsonl = "application/jsonl",
    ApplicationPdf = "application/pdf",
    ApplicationVndOpenxmlformatsOfficedocumentPresentationmlPresentation = "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ApplicationXml = "application/xml",
    ImageJpeg = "image/jpeg",
    ImagePng = "image/png",
    ImageGif = "image/gif",
    ImageWebp = "image/webp",
    ImageBmp = "image/bmp",
    ImageTiff = "image/tiff",
    TextCsv = "text/csv",
    TextSql = "text/sql",
    TextHtml = "text/html",
    TextMarkdown = "text/markdown",
    TextPlain = "text/plain",
    ApplicationVndOpenxmlformatsOfficedocumentSpreadsheetmlSheet = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ApplicationVndOpenxmlformatsOfficedocumentWordprocessingmlDocument = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",

