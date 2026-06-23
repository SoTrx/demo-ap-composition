from enum import Enum

class DatasetSortField(str, Enum):
    Id = "id",
    Name = "name",
    DatePublished = "datePublished",
    Version = "version",
    Status = "status",
    Headline = "headline",
    UploadedBy = "uploadedBy",

