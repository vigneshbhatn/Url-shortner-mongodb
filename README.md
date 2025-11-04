# 🔗 Full-Stack URL Shortener

This is a complete URL shortener application built with a FastAPI backend, a Streamlit frontend, and a MongoDB database.

It provides a simple web interface to create, manage, and delete short URLs, and a fast API-driven backend to handle the redirects.



## 🚀 Features

* **Create Short URLs:** Enter a long URL and get a short, random 7-character link.
* **Fast Redirects:** Use the short link to instantly redirect to the original long URL.
* **Link Management Dashboard:** The Streamlit frontend provides a full "admin" panel.
* **View All Links:** See a table of all created short URLs and their destinations.
* **Update Links:** Edit the destination URL for any existing short link.
* **Delete Links:** Instantly remove any short link.

## 🛠️ Tech Stack

* **Backend:** **FastAPI** (for a high-performance REST API)
* **Frontend:** **Streamlit** (for a fast, interactive web UI)
* **Database:** **MongoDB** (a NoSQL database to store the links)
* **Python Libraries:** `pymongo`, `uvicorn`, `requests`, `shortuuid`
* **Environment:** **Mamba / Conda** (for managing Python packages and dependencies)

---

## 🔧 Setup & Installation

This project uses Mamba (which comes with Miniforge) to manage its environment and complex dependencies like `pyarrow`.

1.  **Install Mamba:**
    Follow the official guide to install [Miniforge3](https://github.com/conda-forge/miniforge) (which includes Mamba).

2.  **Create the Environment:**
    Open your terminal and create a new environment for the project. We use Python 3.11 for maximum compatibility.
    ```bash
    mamba create -n url_env python=3.11
    ```

3.  **Activate the Environment:**
    You must do this every time you work on the project.
    ```bash
    mamba activate url_env
    ```

4.  **Install Dependencies:**
    With your `(url_env)` active, install all required packages in one command:
    ```bash
    mamba install fastapi uvicorn pymongo shortuuid pydantic streamlit requests
    ```

5.  **Start MongoDB:**
    Ensure your MongoDB server is running on its default port (`mongodb://localhost:27017/`).

---

## 🏃‍♂️ How to Run the Project

You must have **three** components running: the Database, the Backend, and the Frontend.

1.  **Terminal 1: Run the Backend (FastAPI)**
    * Activate the environment: `mamba activate url_env`
    * Navigate to the project's root folder.
    * Run uvicorn:
    ```bash
    uvicorn backend.backend:app --reload
    ```
    * Your API is now running at `http://127.0.0.1:8000`.
    * You can see the API docs at `http://127.0.0.1:8000/docs`.

2.  **Terminal 2: Run the Frontend (Streamlit)**
    * Activate the environment: `mamba activate url_env`
    * Navigate to the project's root folder.
    * Run Streamlit:
    ```bash
    streamlit run frontend/frontend.py
    ```
    * Your web app will automatically open in your browser at `http://localhost:8501`.

---

## API Endpoints

The FastAPI backend provides the following endpoints:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/shorten` | Creates a new short URL. |
| `GET` | `/{short_code}` | Redirects to the original target URL. |
| `GET` | `/admin/links` | **(Admin)** Gets a list of all stored URLs. |
| `PUT` | `/admin/{short_code}` | **(Admin)** Updates a short URL's destination. |
| `DELETE` | `/admin/{short_code}` | **(Admin)** Deletes a short URL. |

---

## Mongo Shell Queries (for Presentation)

You can interact with the database directly using the MongoDB Shell (`mongosh`) to demonstrate the core CRUD (Create, Read, Update, Delete) operations.

1.  **Connect to the shell:**
    ```bash
    mongosh
    ```

2.  **Switch to the project database:**
    ```javascript
    use url_shortener_db
    ```

### 1. CREATE (Insert)
Manually inserts a new document into the `urls` collection.

```javascript
db.urls.insertOne({
  "short_code": "demo123",
  "target_url": "[https://www.github.com](https://www.github.com)"
})
```
2. READ (Find)
Reads data from the urls collection.

Find all documents:

```javaScript

db.urls.find()
```
Find a specific document by its short_code:

```javaScript

db.urls.findOne({ "short_code": "demo123" })
```
3. UPDATE (Modify)
Changes the target_url of an existing document.

```javaScript

db.urls.updateOne(
  { "short_code": "demo123" }, // The filter (which document to find)
  { $set: { "target_url": "[https://www.mongodb.com](https://www.mongodb.com)" } } // The operation (what to change)
)
```
4. DELETE (Remove)
Removes a document from the urls collection.

```JavaScript
db.urls.deleteOne({ "short_code": "demo123" })
```
