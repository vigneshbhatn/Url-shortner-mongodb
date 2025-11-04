import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from pymongo import MongoClient
import shortuuid
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId  # Import this

# --- 1. App & DB Setup ------------------------------------------------
app = FastAPI(title="URL Shortener API")

origins = [
    "http://localhost",
    "http://localhost:8501",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["url_shortener_db"]
    collection = db["urls"]
    collection.create_index("short_code", unique=True)
    print("✅ Successfully connected to MongoDB.")
except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}")
    client = None
    collection = None


# --- 3. Pydantic Models -----------------------------------------------

class URLCreate(BaseModel):
    target_url: HttpUrl


class URLUpdate(BaseModel):
    """Model for updating a URL. Only the target_url can be changed."""
    target_url: HttpUrl


class URLInfo(BaseModel):
    short_url: str
    target_url: HttpUrl


class URLInfoDB(BaseModel):
    """Full URL model for data coming from the database."""
    # We use this to properly handle the MongoDB '_id'
    id: str
    short_code: str
    target_url: str


# Helper to convert MongoDB's ObjectId
def document_helper(doc) -> dict:
    return {
        "id": str(doc["_id"]),
        "short_code": doc["short_code"],
        "target_url": doc["target_url"],
    }


# --- 4. API Endpoints (Core) -------------------------------------------

@app.get("/", summary="Root Endpoint")
def read_root():
    if collection is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    return {"message": "Welcome! URL Shortener API is running."}


@app.post("/shorten", response_model=URLInfo, summary="Create a new short URL")
def create_short_url(url: URLCreate, request: Request):
    if collection is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    short_code = shortuuid.uuid()[:7]
    while collection.find_one({"short_code": short_code}):
        short_code = shortuuid.uuid()[:7]

    base_url = str(request.base_url)
    url_document = {
        "short_code": short_code,
        "target_url": str(url.target_url),
    }

    try:
        collection.insert_one(url_document)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return URLInfo(
        short_url=f"{base_url}{short_code}",
        target_url=url.target_url
    )


@app.get("/{short_code}", response_class=RedirectResponse, summary="Redirect to Target URL")
def redirect_to_url(short_code: str):
    if collection is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    document = collection.find_one({"short_code": short_code})

    if document:
        return RedirectResponse(url=document["target_url"], status_code=307)
    else:
        raise HTTPException(status_code=404, detail="Short URL not found")


# --- 5. NEW: Admin Endpoints (CRUD) -----------------------------------

@app.get("/admin/links", response_model=List[URLInfoDB], summary="Get all stored URLs")
def get_all_links():
    """
    Retrieves a list of all URL documents from the database.
    """
    if collection is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    links = []
    for doc in collection.find():
        links.append(document_helper(doc))
    return links


@app.put("/admin/{short_code}", response_model=URLInfoDB, summary="Update a short URL")
def update_link(short_code: str, url: URLUpdate):
    """
    Updates the target_url for a given short_code.
    """
    if collection is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    # Find the document and update it
    result = collection.update_one(
        {"short_code": short_code},
        {"$set": {"target_url": str(url.target_url)}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"URL with short_code '{short_code}' not found.")

    # Get the newly updated document to return it
    updated_doc = collection.find_one({"short_code": short_code})
    return document_helper(updated_doc)


@app.delete("/admin/{short_code}", summary="Delete a short URL")
def delete_link(short_code: str):
    """
    Deletes a URL document by its short_code.
    """
    if collection is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    result = collection.delete_one({"short_code": short_code})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"URL with short_code '{short_code}' not found.")

    return {"message": "URL successfully deleted."}


# --- 6. Run the App ---------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)