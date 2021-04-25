CREATE TABLE public."ASSAY" (
    "Assay_ID" integer NOT NULL,
    "Assay_Identifier" text,
    "Assay_Measurement_Type" text,
    "Assay_Measurement_Type_Term_Accession_Number" text,
    "Assay_Measurement_Type_Term_Source_REF" text,
    "Assay_Technology_Type" text,
    "Assay_Technology_Type_Term_Accession_Number" text,
    "Assay_Technology_Type_Term_Source_REF" text,
    "Assay_Technology_Platform" text
);

CREATE TABLE public."STUDY" (
    "Study_ID" integer NOT NULL,
    "Study_Identifier" text NOT NULL,
    "Study_Title" text,
    "Study_Description" text,
    "Study_Submission_Date" date,
    "Study_Public_Release_Date" date,
    "Study_File_Name" text,
    "Study_Assays" integer,
    "Study_Contact" integer,
    "Study_Design_Descriptors" integer,
    "Study_Factors" integer,
    "Study_Protocols" integer,
    "Study_Publications" integer
);

CREATE TABLE public."ONTOLOGY_SOURCE_REFERENCE" (
    "Ontology_Source_REF_ID" integer NOT NULL,
    "Term_Source_Name" text NOT NULL,
    "Term_Source_File" text NOT NULL,
    "Term_Source_Version" text NOT NULL,
    "Term_Source_Description" text NOT NULL,
    "Ontology_REF_Investigation_Identifier" text NOT NULL
);

CREATE TABLE public."ISA_model_graph_structure"
(
id integer NOT NULL,
isa_json json NOT NULL,
"Investigation_id_REF" integer NOT NULL,
CONSTRAINT "ISA_model_graph_structure_pkey" PRIMARY KEY (id)
)