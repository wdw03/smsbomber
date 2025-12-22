from flask import Flask, request, jsonify, abort
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from bson.errors import InvalidId
import json

# MongoDB Connection
MONGO_URI = "mongodb+srv://savanlovw123:v2WEuCWEiyy2iwrK@lovesavan.055jfvj.mongodb.net/testdb?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client.testdb
    collection = db.items  # Collection name - aap isko change kar sakte hain
    print("✅ MongoDB Successfully Connected!")
except ConnectionFailure as e:
    print("❌ MongoDB Connection Failed")
    print(e)
    client = None
    db = None
    collection = None

# Flask App
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Helper function to convert ObjectId to string
def convert_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    return obj

# POST Request - Create New Document
@app.route("/api/create", methods=["POST"])
def create_document():
    """
    POST request to create a new document in MongoDB
    Body me JSON data bhejo
    """
    if collection is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400
        
        result = collection.insert_one(data)
        inserted_doc = collection.find_one({"_id": result.inserted_id})
        inserted_doc = convert_objectid(inserted_doc)
        
        return jsonify({
            "success": True,
            "message": "Document created successfully",
            "data": inserted_doc,
            "id": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error creating document: {str(e)}"}), 400

# GET Request - Get All Documents
@app.route("/api/get", methods=["GET"])
def get_all_documents():
    """
    GET request to retrieve all documents
    Query parameters: skip (default 0), limit (default 100)
    """
    if collection is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    
    try:
        # Get query parameters
        skip = request.args.get("skip", default=0, type=int)
        limit = request.args.get("limit", default=100, type=int)
        
        documents = list(collection.find().skip(skip).limit(limit))
        documents = convert_objectid(documents)
        
        return jsonify({
            "success": True,
            "message": "Documents retrieved successfully",
            "count": len(documents),
            "data": documents
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error retrieving documents: {str(e)}"}), 400

# GET Request - Get Single Document by ID
@app.route("/api/get/<document_id>", methods=["GET"])
def get_document_by_id(document_id):
    """
    GET request to retrieve a single document by ID
    """
    if collection is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    
    try:
        if not ObjectId.is_valid(document_id):
            return jsonify({"success": False, "error": "Invalid document ID format"}), 400
        
        document = collection.find_one({"_id": ObjectId(document_id)})
        
        if not document:
            return jsonify({"success": False, "error": "Document not found"}), 404
        
        document = convert_objectid(document)
        
        return jsonify({
            "success": True,
            "message": "Document retrieved successfully",
            "data": document
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error retrieving document: {str(e)}"}), 400

# PUT Request - Update Document by ID
@app.route("/api/edit/<document_id>", methods=["PUT"])
def update_document(document_id):
    """
    PUT request to update/edit a document by ID
    Body me JSON data bhejo jo update karna hai
    """
    if collection is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    
    try:
        if not ObjectId.is_valid(document_id):
            return jsonify({"success": False, "error": "Invalid document ID format"}), 400
        
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400
        
        # Remove _id from update data if present
        if "_id" in data:
            del data["_id"]
        
        result = collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": data}
        )
        
        if result.matched_count == 0:
            return jsonify({"success": False, "error": "Document not found"}), 404
        
        # Get updated document
        updated_doc = collection.find_one({"_id": ObjectId(document_id)})
        updated_doc = convert_objectid(updated_doc)
        
        return jsonify({
            "success": True,
            "message": "Document updated successfully",
            "data": updated_doc,
            "modified_count": result.modified_count
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error updating document: {str(e)}"}), 400

# PATCH Request - Partial Update Document by ID
@app.route("/api/edit/<document_id>", methods=["PATCH"])
def partial_update_document(document_id):
    """
    PATCH request to partially update/edit a document by ID
    Body me sirf wahi fields bhejo jo update karni hain
    """
    if collection is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    
    try:
        if not ObjectId.is_valid(document_id):
            return jsonify({"success": False, "error": "Invalid document ID format"}), 400
        
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400
        
        # Remove _id from update data if present
        if "_id" in data:
            del data["_id"]
        
        result = collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": data}
        )
        
        if result.matched_count == 0:
            return jsonify({"success": False, "error": "Document not found"}), 404
        
        # Get updated document
        updated_doc = collection.find_one({"_id": ObjectId(document_id)})
        updated_doc = convert_objectid(updated_doc)
        
        return jsonify({
            "success": True,
            "message": "Document partially updated successfully",
            "data": updated_doc,
            "modified_count": result.modified_count
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error updating document: {str(e)}"}), 400

# DELETE Request - Delete Document by ID (Bonus)
@app.route("/api/delete/<document_id>", methods=["DELETE"])
def delete_document(document_id):
    """
    DELETE request to delete a document by ID
    """
    if collection is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    
    try:
        if not ObjectId.is_valid(document_id):
            return jsonify({"success": False, "error": "Invalid document ID format"}), 400
        
        result = collection.delete_one({"_id": ObjectId(document_id)})
        
        if result.deleted_count == 0:
            return jsonify({"success": False, "error": "Document not found"}), 404
        
        return jsonify({
            "success": True,
            "message": "Document deleted successfully",
            "deleted_count": result.deleted_count
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error deleting document: {str(e)}"}), 400

# Root endpoint
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "message": "MongoDB REST API",
        "endpoints": {
            "POST /api/create": "Create new document",
            "GET /api/get": "Get all documents",
            "GET /api/get/<id>": "Get document by ID",
            "PUT /api/edit/<id>": "Update document by ID",
            "PATCH /api/edit/<id>": "Partially update document by ID",
            "DELETE /api/delete/<id>": "Delete document by ID"
        }
    }), 200

# Health check
@app.route("/health", methods=["GET"])
def health_check():
    if collection is None:
        return jsonify({"status": "unhealthy", "database": "disconnected"}), 503
    return jsonify({"status": "healthy", "database": "connected"}), 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
