from typing import Union
from fastapi import FastAPI, File, UploadFile
from Bio.PBD import * 

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/upload")
def upload_file(file: UploadFile = File(...)): 
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("")
    return {"File has been uploaded"}