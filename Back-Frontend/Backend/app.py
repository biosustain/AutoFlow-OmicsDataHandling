from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow, Schema
from flask_cors import CORS


app = Flask(__name__)
ma = Marshmallow(app)
CORS(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://bfair_user:password@localhost:5432/smart"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class SampleModel(db.Model):
    __tablename__ = "Sample"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Sample_name = db.Column(db.String())

    def __init__(self, Sample_name):
        self.Sample_name = Sample_name

    def __repr__(self):
        return f"<Sample {self.Sample_name}>"


class MethodologyModel(db.Model):
    __tablename__ = "Methodology"

    id = db.Column(db.Integer, primary_key=True)
    Methodology = db.Column(db.String(120), nullable=False)
    Sample_id = db.Column(db.Integer, db.ForeignKey('Sample.id', ondelete="CASCADE"), nullable=False)


class MethodSchema(ma.SQLAlchemySchema):
    class Meta:
        model = MethodologyModel

    id = ma.auto_field()
    Methodology = ma.auto_field()
    Sample_id = ma.auto_field()


class UserSchema(Schema):
    id = ma.auto_field()
    Methodology = ma.auto_field()
    Sample_id = ma.auto_field()


class ASSAYModel(db.Model):
    __tablename__ = "ASSAY"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Assay_Identifier = db.Column(db.String())
    Assay_Measurement_Type = db.Column(db.String())
    Assay_Measurement_Type_Term_Accession_Number = db.Column(db.String())
    Assay_Measurement_Type_Term_Source_REF = db.Column(db.String())
    Assay_Technology_Type = db.Column(db.String())
    Assay_Technology_Type_Term_Accession_Number = db.Column(db.String())
    Assay_Technology_Type_Term_Source_REF = db.Column(db.String())
    Assay_Technology_Platform = db.Column(db.String())

    def __init__(self, Assay_Identifier, Assay_Measurement_Type, Assay_Measurement_Type_Term_Accession_Number,
                 Assay_Measurement_Type_Term_Source_REF, Assay_Technology_Type,
                 Assay_Technology_Type_Term_Accession_Number, Assay_Technology_Type_Term_Source_REF,
                 Assay_Technology_Platform):
        self.Assay_Identifier = Assay_Identifier
        self.Assay_Measurement_Type = Assay_Measurement_Type
        self.Assay_Measurement_Type_Term_Accession_Number = Assay_Measurement_Type_Term_Accession_Number
        self.Assay_Measurement_Type_Term_Source_REF = Assay_Measurement_Type_Term_Source_REF
        self.Assay_Technology_Type = Assay_Technology_Type
        self.Assay_Technology_Type_Term_Accession_Number = Assay_Technology_Type_Term_Accession_Number
        self.Assay_Technology_Type_Term_Source_REF = Assay_Technology_Type_Term_Source_REF
        self.Assay_Technology_Platform = Assay_Technology_Platform

    def __repr__(self):
        return f"<ASSAY {self.Assay_Identifier}>"


class STUDYModel(db.Model):
    __tablename__ = "STUDY"

    id = db.Column(db.Integer, primary_key=True)
    Study_Identifier = db.Column(db.String())
    Study_Title = db.Column(db.String())
    Study_Description = db.Column(db.String())
    Study_Submission_Date = db.Column(db.Date())
    Study_Public_Release_Date = db.Column(db.Date())
    Study_Assays = db.Column(db.Integer)
    Study_Contact = db.Column(db.Integer)
    Study_Design_Descriptors = db.Column(db.Integer)
    Study_Factors = db.Column(db.Integer)
    Study_Protocols = db.Column(db.Integer)
    Study_Publications = db.Column(db.Integer)

    def __init__(self, Study_Identifier, Study_Title, Study_Description, Study_Submission_Date,
                 Study_Public_Release_Date, Study_Assays, Study_Contact, Study_Design_Descriptors,
                 Study_Factors, Study_Protocols,
                 Study_Publications):
        self.Study_Identifier = Study_Identifier
        self.Study_Title = Study_Title
        self.Study_Description = Study_Description
        self.Study_Submission_Date = Study_Submission_Date
        self.Study_Public_Release_Date = Study_Public_Release_Date
        self.Study_Assays = Study_Assays
        self.Study_Contact = Study_Contact
        self.Study_Design_Descriptors = Study_Design_Descriptors
        self.Study_Factors = Study_Factors
        self.Study_Protocols = Study_Protocols
        self.Study_Publications = Study_Publications

    def __repr__(self):
        return f"<STUDY {self.Study_Identifier}>"


class ONTOLOGY_SOURCE_REFERENCEModel(db.Model):
    __tablename__ = 'ONTOLOGY_SOURCE_REFERENCE'

    Ontology_Source_REF_ID = db.Column(db.Integer, primary_key=True)
    Term_Source_Name = db.Column(db.String())
    Term_Source_File = db.Column(db.String())
    Term_Source_Version = db.Column(db.String())
    Term_Source_Description = db.Column(db.String())
    Ontology_REF_Investigation_Identifier = db.Column(db.String())

    def __init__(self, Term_Source_Name, Term_Source_File, Term_Source_Version,
                 Term_Source_Description, Ontology_REF_Investigation_Identifier):
        self.Term_Source_Name = Term_Source_Name
        self.Term_Source_File = Term_Source_File
        self.Term_Source_Version = Term_Source_Version
        self.Term_Source_Description = Term_Source_Description
        self.Ontology_REF_Investigation_Identifier = Ontology_REF_Investigation_Identifier

    def __repr__(self):
        return f"<ONTOLOGY_SOURCE_REFERENCE {self.Term_Source_Name}>"


@app.route('/Assay_api', methods=['POST', 'GET'])
def handle_assay():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_assay = ASSAYModel(Assay_Identifier=data['Assay_Identifier'],
                                   Assay_Measurement_Type=data['Assay_Measurement_Type'],
                                   Assay_Measurement_Type_Term_Accession_Number=data[
                                       'Assay_Measurement_Type_Term_Accession_Number'],
                                   Assay_Measurement_Type_Term_Source_REF=data[
                                       'Assay_Measurement_Type_Term_Source_REF'],
                                   Assay_Technology_Type=data['Assay_Technology_Type'],
                                   Assay_Technology_Type_Term_Accession_Number=data[
                                       'Assay_Technology_Type_Term_Accession_Number'],
                                   Assay_Technology_Type_Term_Source_REF=data['Assay_Technology_Type_Term_Source_REF'],
                                   Assay_Technology_Platform=data['Assay_Technology_Platform'])
            db.session.add(new_assay)
            db.session.commit()
            return {"message": f"Assay {new_assay.Assay_Identifier} has been created successfully. "}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        Assay = ASSAYModel.query.all()
        results = [
            {
                "Assay_Identifier": As.Assay_Identifier,
                "Assay_Measurement_Type": As.Assay_Measurement_Type,
                "Assay_Measurement_Type_Term_Accession_Number": As.Assay_Measurement_Type_Term_Accession_Number,
                "Assay_Measurement_Type_Term_Source_REF": As.Assay_Measurement_Type_Term_Source_REF,
                "Assay_Technology_Type": As.Assay_Technology_Type,
                "Assay_Technology_Type_Term_Accession_Number": As.Assay_Technology_Type_Term_Accession_Number,
                "Assay_Technology_Type_Term_Source_REF": As.Assay_Technology_Type_Term_Source_REF,
                "Assay_Technology_Platform": As.Assay_Technology_Platform
            } for As in Assay]

        return {"count": len(results), "Assay": results}


@app.route('/Study_api', methods=['POST', 'GET'])
def handle_study():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_assay = STUDYModel(Study_Identifier=data['Study_Identifier'],
                                   Study_Title=data['Study_Title'],
                                   Study_Description=data[
                                       'Study_Description'],
                                   Study_Submission_Date=data[
                                       'Study_Submission_Date'],
                                   Study_Public_Release_Date=data['Study_Public_Release_Date'],
                                   Study_Assays=data[
                                       'Study_Assays'],
                                   Study_Contact=data['Study_Contact'],
                                   Study_Factors=data['Study_Factors'],
                                   Study_Protocols=data['Study_Protocols'],
                                   Study_Publications=data['Study_Publications'],
                                   Study_Design_Descriptors=data['Study_Design_Descriptors'])
            db.session.add(new_assay)
            db.session.commit()
            return {"message": f"Study {new_assay.Study_Identifier} has been created successfully."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        Study = STUDYModel.query.all()
        results = [
            {
                "Study_Identifier": As.Study_Identifier,
                "Study_Title": As.Study_Title,
                "Study_Description": As.Study_Description,
                "Study_Submission_Date": As.Study_Submission_Date,
                "Study_Public_Release_Date": As.Study_Public_Release_Date,
                "Study_Assays": As.Study_Assays,
                "Study_Contact": As.Study_Contact,
                "Study_Protocols": As.Study_Protocols,
                "Study_Publications": As.Study_Publications,
                "Study_Design_Descriptors": As.Study_Design_Descriptors,
                "Study_Factors": As.Study_Factors
            } for As in Study]

        return {"count": len(results), "Study": results}


@app.route('/Source_reference_api', methods=['POST', 'GET'])
def handle_source():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_assay = ONTOLOGY_SOURCE_REFERENCEModel(Term_Source_Name=data['Term_Source_Name'],
                                                       Term_Source_File=data['Term_Source_File'],
                                                       Term_Source_Version=data[
                                                           'Term_Source_Version'],
                                                       Term_Source_Description=data['Term_Source_Description'],
                                                       Ontology_REF_Investigation_Identifier=data[
                                                           'Ontology_REF_Investigation_Identifier'])
            db.session.add(new_assay)
            db.session.commit()
            return {"message": f"Source {new_assay.Term_Source_Name} has been created successfully."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        Study = ONTOLOGY_SOURCE_REFERENCEModel.query.all()
        results = [
            {
                "Term_Source_Name": As.Term_Source_Name,
                "Term_Source_File": As.Term_Source_File,
                "Term_Source_Version": As.Term_Source_Version,
                "Term_Source_Description": As.Term_Source_Description,
                "Ontology_REF_Investigation_Identifier": As.Ontology_REF_Investigation_Identifier,
            } for As in Study]

        return {"count": len(results), "Study": results}


@app.route('/Sample_api', methods=['POST', 'GET', 'DELETE'])
def handle_sample_api():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_assay = SampleModel(Sample_name=data['Sample_name'])
            db.session.add(new_assay)
            db.session.commit()
            return {"message": f"Source {new_assay.Sample_name} has been created successfully."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        Study = SampleModel.query.all()
        results = [
            {
                "id": As.id,
                "Sample_name": As.Sample_name,
            } for As in Study]

        return {"count": len(results), "Sample": results}
    elif request.method == 'DELETE':
        data = request.get_json()
        # db.session.query(MethodologyModel).filter_by(Sample_id=data['Sample_id']).all().delete()
        SampleModel.query.filter_by(id=data.get('Sample_id')).delete()
        # SampleModel.query.filter(id=data.get('Sample_id')).delete()
        db.session.commit()
        return "Sample successfully deleted"


@app.route('/Process_sample_api', methods=['POST', 'GET'])
def handle_process_sample_api():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            query = db.session.query(MethodologyModel).filter_by(Sample_id=data['Sample_id']).all()
            return jsonify(MethodSchema(many=True).dump(query))
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        Study = SampleModel.query.all()
        results = [
            {
                "id": As.id,
                "Sample_name": As.Sample_name,
            } for As in Study]

        return {"count": len(results), "Sample": results}


@app.route('/Methodology_api', methods=['POST', 'GET'])
def handle_methodology_api():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_assay = MethodologyModel(Methodology=data['Methodology'], Sample_id=data['Sample_id'])
            db.session.add(new_assay)
            db.session.commit()
            return {"message": f"Source {new_assay.Methodology} has been created successfully."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        Study = MethodologyModel.query.all()
        results = [
            {
                "Methodology_id": As.id,
                "Methodology": As.Methodology,
                "Sample_id": As.Sample_id
            } for As in Study]

        return {"count": len(results), "Methodology": results}


if __name__ == '__main__':
    app.run(debug=False)
