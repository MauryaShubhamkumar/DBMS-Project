CREATE DATABASE EHR;
USE  EHR;
-- create table
CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Patient (
    PatientID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) Not Null,
    LastName VARCHAR(50) Not Null,
    Password VARCHAR(255) NOT NULL,
    Email  VARCHAR(50) unique  Not NULL,
    PhoneNumber INT(10) NOT NULL,
    DOB DATE,
    Address VARCHAR(200) Not Null
);


CREATE TABLE Doctor (
    DoctorID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) Not Null,
    LastName VARCHAR(50) Not Null,
    Email VARCHAR(50) unique Not NULL,
    Password VARCHAR(255) NOT NULL,
    PhoneNumber INT(10) NOT NULL,
    ConsltationFee decimal(6,2),
    Specialization VARCHAR(50)
);

--  create view to store complete address, concat to merge them


CREATE TABLE Appointment (
    AppointmentID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT,
    DoctorID INT,
    AppointmentDate DATE Not Null,
    AppointmentTime TIME Not Null,
    -- FollowUp BOOLEAN,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID)
);


CREATE TABLE MedicalRecord (
    RecordID INT AUTO_INCREMENT PRIMARY KEY,
    AppointmentID INT,
    Prescription TEXT,
    Diagnosis text,
    TestTaken boolean,
    FOREIGN KEY (AppointmentID) REFERENCES Appointment(AppointmentID)
);

CREATE TABLE Billing (
    BillingID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT,
    RecordID INT,	
    TotalAmount DECIMAL(10, 2),
    PaymentStatus ENUM('Pending', 'Completed') NOT NULL,
    TransactionID INT Null,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    FOREIGN KEY (RecordID) REFERENCES MedicalRecord(RecordID)
);

CREATE TABLE LabTests (
    LabTestID INT AUTO_INCREMENT PRIMARY KEY,
    TestName VARCHAR(100) UNIQUE NOT NULL,
    Description VARCHAR(255),
    Cost DECIMAL(10,2) NOT NULL,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
CREATE TABLE TestResults(
    TestID INT AUTO_INCREMENT PRIMARY KEY,
    LabTestID INT,
    RecordID INT,
    Result TEXT,
    FOREIGN KEY (RecordID) REFERENCES MedicalRecord(RecordID),
    FOREIGN KEY (LabTestID) REFERENCES LabTests(LabTestID)
);

CREATE TABLE Wallets (
    WalletID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT UNIQUE NOT NULL,
    Balance DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID) ON DELETE CASCADE
);

CREATE TABLE AdminWallets (
    WalletID INT AUTO_INCREMENT PRIMARY KEY,
    id INT UNIQUE NOT NULL,
    Balance DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (id) REFERENCES Admin(id) ON DELETE CASCADE
);


-- WalletTransactions Table
CREATE TABLE WalletTransactions (
    TransactionID INT AUTO_INCREMENT PRIMARY KEY,
    WalletID INT NOT NULL,
    Amount DECIMAL(10,2) NOT NULL,
    Description VARCHAR(255),
    TransactionDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (WalletID) REFERENCES Wallets(WalletID) ON DELETE CASCADE
);
ALTER TABLE Patient
DROP COLUMN PhoneNumber;

ALTER TABLE Doctor
ADD COLUMN PhoneNumber VARCHAR(15) NOT NULL;

ALTER TABLE Billing
DROP COLUMN ModeOfPayment;

ALTER TABLE Billing MODIFY 
COLUMN TransactionID INT Null;
ALTER TABLE Billing MODIFY
COLUMN RecordId INT UNIQUE;





