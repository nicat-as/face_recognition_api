import os
from imutils import paths
import cv2
import face_recognition as fr
import pickle
import urllib.request
from app import app
from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename
from .models import (User, OwnerType, db, Raspberry)
from .tasks import (recognition, sendMessage)
from sqlalchemy import exc
from sqlalchemy.sql import text

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config["UPLOAD_FOLDER"] = ''


sql = text("""select u.id, u.name, u.lastname, u.email, r.name raspberry_name
			from user u
			inner join raspberry r
			on r.user_id=u.id
			where r.token= :token""")

getUserById = text("""select u.id, u.name, u.lastname, d.id dataset_id, d.name dataset_name
					from user u
					inner join dataset d
					on d.user_id=u.id
					where u.id=:user_id """)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


@app.route('/multiple-files-upload', methods=['POST'])
def upload_multiple_file():
    # check if the post request has the file part
    if 'files' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp

    files = request.files.getlist('files')
    token = request.form.get("token")
    try:
        search_token = db.session.query(
            Raspberry).filter_by(token=token).first()
        rs = db.engine.execute(sql, token=token)
        path_data = {}
        for r in rs:
            path_data['name'] = r.name
            path_data['lastname'] = r.lastname
            path_data['rpi_name'] = r.raspberry_name
            path_data['email'] = r.email

        print(path_data)

    except exc.SQLAlchemyError:
        pass

    errors = {}
    message = ''
    success = False
    if search_token:
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                fileDir = os.path.join(app.config["UPLOAD_FOLDER"], path_data["name"] +
                                       path_data["lastname"], 'raspberry', path_data["rpi_name"])

                pickleDir = os.path.join(app.config["UPLOAD_FOLDER"], path_data["name"] +
                                         path_data["lastname"], 'dataset')
                print(fileDir)
                create_directory(fileDir)
                fileDir = os.path.join(fileDir, filename)
                file.save(fileDir)
                data, name = recognition(
                    fileDir, os.path.join(pickleDir, 'encodings'))
                print(name)
                sendMessage(path_data["email"], name, fileDir)
                message = name
                success = True
            else:
                errors[file.filename] = 'File type is not allowed'

        if success and errors:
            errors['message'] = 'File(s) successfully uploaded'
            resp = jsonify(errors)
            resp.status_code = 206
            return resp
        if success:
            resp = jsonify({'message': 'Files successfully uploaded',
                            'name': message})
            resp.status_code = 201

            return resp
        else:
            resp = jsonify(errors)
            resp.status_code = 400
            return resp
    else:
        errors['message'] = 'Token is not true'
        resp = jsonify(errors)
        return resp


@app.route('/encode/<user_id>', methods=['POST'])
def encode_face(user_id):
    try:
        rs = db.engine.execute(getUserById, user_id=user_id)
        path_data = {}
        for r in rs:
            path_data["name"] = r.name
            path_data["lastname"] = r.lastname
            path_data["dataset_name"] = r.dataset_name

        searching_path = os.path.join(app.config["UPLOAD_FOLDER"], path_data["name"] +
                                      path_data["lastname"], "dataset")

        print("[INFO] quantifying faces...")
        imagePaths = list(paths.list_images(searching_path))
        knownEncodings = []
        knownNames = []

        for i, imagePath in enumerate(imagePaths):
            print(f"[INFO] processing image {i + 1}/{len(imagePaths)}")
            name = imagePath.split(os.path.sep)[-2]
            images = cv2.imread(imagePath)
            rgb = cv2.cvtColor(images, cv2.COLOR_BGR2RGB)
            boxes = fr.face_locations(rgb, model="hog")
            encodings = fr.face_encodings(rgb, boxes)

            for encoding in encodings:
                knownEncodings.append(encoding)
                knownNames.append(name)

        print("[INFO] serializing encodings...")
        data = {"encodings": knownEncodings, "names": knownNames}
        f = open(os.path.join(searching_path, "encodings"), "wb")
        pickle.dump(data, f)
        f.close()

        return jsonify({"message": "encode is doing"})

    except exc.SQLAlchemyError:
        return jsonify({"message": "Bad request"})
