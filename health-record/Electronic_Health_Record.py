import streamlit as st
import pymysql
from datetime import datetime

import bcrypt

def connect_to_db():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            port=3306,
            password="Maurya",  # Update this with your actual MySQL root password
            database="ehr"
        )
        return conn
    except pymysql.MySQLError as e:
        st.error(f"Error connecting to MySQL: {e}")  # Using st.error for better visibility
        return None


# Hash Password
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)


# Verify Password
def verify_password(password, hashed):
    # Check if hashed password is valid
    if not hashed:
        print("No hashed password provided.")
        return False
    
    # Ensure the hash is in bytes format
    hashed = hashed.encode('utf-8') if isinstance(hashed, str) else hashed

    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    except ValueError as e:
        print(f"Error verifying password: {e}")
        return False





def sign_up_patient(first_name, last_name, dob, address, phone, email, password):
    conn = connect_to_db()
    if conn is None:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor()
    hashed_pw = hash_password(password)  # Hash the password for security

    query = """
        INSERT INTO Patient (FirstName, LastName, DOB, Address, PhoneNumber, Email, Password)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (first_name, last_name, dob, address, phone, email, hashed_pw))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def sign_up_doctor(first_name, last_name, specialization,phone, email, password):
    conn = connect_to_db()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)  # Hash the password for security

    query = """
        INSERT INTO Doctor (FirstName, LastName, Specialization,PhoneNumber, Email, Password)
        VALUES (%s, %s,  %s,%s, %s, %s)
    """
    try:
        cursor.execute(query, (first_name, last_name, specialization,phone, email, hashed_pw ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()


def fetch_patient_id(email):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = "SELECT PatientID FROM Patient WHERE Email = %s"
    try:
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        if result:
            return result[0]  # Return the PatientID
        else:
            print("No patient found with this email.")
            return None
    except Exception as e:
        print(f"Error fetching PatientID: {e}")
        return None
    finally:
        conn.close()



def sign_up_patient_ui():
    st.subheader("Patient Sign-Up")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    dob = st.date_input("Date of Birth")
    address = st.text_area("Address")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif not all([first_name, last_name, dob, address, phone, email, password]):
            st.error("All fields are required!")
        else:
            success = sign_up_patient(first_name, last_name, dob, address, phone, email, password)
            if success:
                st.success("Patient account created successfully!")
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = fetch_patient_id(email)  # Fetch the new patient ID
                st.session_state["role"] = "Patient"
                st.session_state["redirect_to_create"] = True  # Set redirection
            else:
                st.error("Failed to create account. Please try again.")



def sign_up_doctor_ui():
    st.subheader("Doctor Sign-Up")

    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    specialization = st.text_input("Specialization")
    phone = st.text_input("PhoneNumber")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif not all([first_name, last_name, specialization,phone,  email, password]):
            st.error("All fields are required!")
        else:
            success = sign_up_doctor(first_name, last_name, specialization,phone, email, password)
            if success:
                st.success("Doctor account created successfully!")
            else:
                st.error("Failed to create account. Please try again.")

def login_user(email, password, role):
    conn = connect_to_db()
    cursor = conn.cursor()

    if role == "Patient":
        query = "SELECT PatientID, Password FROM Patient WHERE Email=%s"
    elif role == "Doctor":
        query = "SELECT DoctorID, Password FROM Doctor WHERE Email=%s"
    elif role == "Admin" :
        query = "SELECT id, password FROM admin WHERE Email=%s"
    else:
        return None, False

    cursor.execute(query, (email,))
    result = cursor.fetchone()
    conn.close()

    if result and verify_password(password, result[1]):  # Compare hashed password
        return result[0], True  # Return user ID and login success
    return None, False

def login_ui():
    st.subheader("Login")
    role = st.radio("Role", ["Patient", "Doctor", "Admin"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_id, success = login_user(email, password, role)
        if success:
            st.success(f"Welcome back, {role}!")
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user_id
            st.session_state["role"] = role
            st.session_state["redirect_to_create"] = True  # Set redirection
        else:
            st.error("Invalid email or password.")


def logout_ui():
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None
        st.session_state["role"] = None
        st.success("You have been logged out.")


def fetch_doctors():
    conn = connect_to_db()
    cursor = conn.cursor()
    query = "SELECT DoctorID, FirstName, LastName, Specialization FROM Doctor"
    try:
        cursor.execute(query)
        doctors = cursor.fetchall()
        return doctors
    except Exception as e:
        print(f"Error fetching doctors: {e}")
        return []
    finally:
        conn.close()


def create_appointment(patient_id, doctor_id, date, time):
    conn = connect_to_db()
    if conn is None:
        return False
        
    cursor = conn.cursor()
    query = """
        INSERT INTO Appointment (PatientID, DoctorID, AppointmentDate, AppointmentTime)
        VALUES (%s, %s, %s, %s)
    """
    try:
        # Convert date and time to strings if they aren't already
        date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else date
        time_str = time.strftime('%H:%M:%S') if hasattr(time, 'strftime') else time
        
        cursor.execute(query, (patient_id, doctor_id, date_str, time_str))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating appointment: {e}")
        return False
    finally:
        cursor.close()
        conn.close()





def create_appointment_ui():
    if not st.session_state.get("logged_in") or st.session_state["role"] != "Patient":
        st.warning("You must log in as a patient to create an appointment.")
        return

    st.subheader("Create an Appointment")

    # Fetch and display doctors
    doctors = fetch_doctors()
    if not doctors:
        st.warning("No doctors available.")
        return

    doctor_options = {f"{doc[1]} {doc[2]} ({doc[3]})": doc[0] for doc in doctors}  # Format: "FirstName LastName (Specialization)"
    selected_doctor = st.selectbox("Select a Doctor", options=list(doctor_options.keys()))
    doctor_id = doctor_options[selected_doctor]

    # Appointment Details
    current_date = datetime.now().date()
    date = st.date_input("Select Appointment Date", 
                        min_value=current_date,
                        value=current_date)
    
    time = st.time_input("Select Appointment Time", 
                        value=datetime.now().time())

    if st.button("Create Appointment"): 
        # Validate date and time
        if date < current_date:
            st.error("Please select a future date.")
            return
            
        try:
            patient_id = st.session_state["user_id"]
            success = create_appointment(patient_id, doctor_id, date, time)
            if success:
                st.success("Appointment created successfully!")
            else:
                st.error("Failed to create appointment. Please try again.")
        except Exception as e:
            st.error(f"Error creating appointment: {str(e)}")
            print(f"Detailed error: {e}")

# Fetch patient appointments
def fetch_patient_appointments(patient_id):
    conn = connect_to_db()
    if conn is None:
        return []

    cursor = conn.cursor()
    query = """
        SELECT 
            a.AppointmentID, 
            a.AppointmentDate, 
            a.AppointmentTime, 
            d.FirstName AS DoctorFirstName, 
            d.LastName AS DoctorLastName, 
            d.Specialization
        FROM 
            Appointment a
        JOIN 
            Doctor d ON a.DoctorID = d.DoctorID
        WHERE 
            a.PatientID = %s
        ORDER BY 
            a.AppointmentDate DESC, a.AppointmentTime DESC
    """
    try:
        cursor.execute(query, (patient_id,))
        appointments = cursor.fetchall()
        return appointments
    except Exception as e:
        st.error(f"Error fetching appointments: {e}")
        return []
    finally:
        conn.close()

def view_patient_appointments_ui():
    st.subheader("Your Appointments")

    # Fetch appointments for the logged-in patient
    patient_id = st.session_state["user_id"]
    appointments = fetch_patient_appointments(patient_id)

    if not appointments:
        st.info("You have no appointments.")
        return

    # Format and display appointments
    st.write("### Your Appointments (Latest at the Top)")
    appointment_data = [
        {
            "Appointment ID": appt[0],
            "Date": appt[1],
            "Time": appt[2],
            "Doctor": f"{appt[3]} {appt[4]}",
            "Specialization": appt[5],
        }
        for appt in appointments
    ]
    st.dataframe(appointment_data)

def fetch_doctor_appointments(doctor_id):
    conn = connect_to_db()
    if conn is None:
        return []

    cursor = conn.cursor()
    query = """
        SELECT 
            a.AppointmentID, 
            a.AppointmentDate, 
            a.AppointmentTime, 
            p.FirstName AS PatientFirstName, 
            p.LastName AS PatientLastName, 
            p.Email AS PatientEmail
        FROM 
            Appointment a
        JOIN 
            Patient p ON a.PatientID = p.PatientID
        WHERE 
            a.DoctorID = %s
        ORDER BY 
            a.AppointmentDate DESC, a.AppointmentTime DESC
    """
    try:
        cursor.execute(query, (doctor_id,))
        appointments = cursor.fetchall()
        return appointments
    except Exception as e:
        st.error(f"Error fetching appointments: {e}")
        return []
    finally:
        conn.close()


def view_doctor_appointments_ui():
    st.subheader("Your Appointments")

    # Fetch appointments for the logged-in doctor
    if not st.session_state.get("logged_in") or st.session_state["role"] != "Doctor":
        st.warning("You must log in as a doctor to view your appointments.")
        return

    doctor_id = st.session_state["user_id"]
    appointments = fetch_doctor_appointments(doctor_id)

    if not appointments:
        st.info("You have no appointments scheduled.")
        return

    # Format and display appointments
    st.write("### Your Appointments (Latest at the Top)")
    appointment_data = [
        {
            "Appointment ID": appt[0],
            "Date": appt[1],
            "Time": appt[2],
            "Patient": f"{appt[3]} {appt[4]}",
            "Patient Email": appt[5],
        }
        for appt in appointments
    ]
    st.dataframe(appointment_data)


# Update Appointment
def update_appointment(appointment_id, new_date, new_time):
    conn = connect_to_db()
    if conn is None:
        return False

    cursor = conn.cursor()
    query = """
        UPDATE Appointment
        SET AppointmentDate = %s, AppointmentTime = %s
        WHERE AppointmentID = %s
    """
    try:
        cursor.execute(query, (new_date, new_time, appointment_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating appointment: {e}")
        return False
    finally:
        conn.close()

def update_appointment_ui():
    if not st.session_state.get("logged_in") or st.session_state["role"] != "Patient":
        st.warning("You must log in as a patient to manage appointments.")
        return

    st.subheader("Update an Appointment")

    # Fetch appointments for the logged-in patient
    patient_id = st.session_state["user_id"]
    appointments = fetch_patient_appointments(patient_id)

    if not appointments:
        st.info("You have no appointments to update.")
        return

    # Create options for the appointment select box
    appointment_options = {
        f"Appointment {appt[0]}: {appt[1]} {appt[2]} with Dr. {appt[3]} {appt[4]} ({appt[5]})": appt[0]
        for appt in appointments
    }
    selected_appointment = st.selectbox("Select an Appointment", list(appointment_options.keys()))
    appointment_id = appointment_options[selected_appointment]

    # Update details
    current_date = datetime.now().date()
    new_date = st.date_input("New Appointment Date", min_value=current_date)
    new_time = st.time_input("New Appointment Time")

    if st.button("Update Appointment"):
        if new_date < current_date:
            st.error("Please select a future date.")
            return

        success = update_appointment(appointment_id, new_date, new_time)
        if success:
            st.success("Appointment updated successfully!")
        else:
            st.error("Failed to update appointment. Please try again.")

# Delete Appointment
def delete_appointment(appointment_id):
    conn = connect_to_db()
    if conn is None:
        return False

    cursor = conn.cursor()
    query = "DELETE FROM Appointment WHERE AppointmentID = %s"
    try:
        cursor.execute(query, (appointment_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting appointment: {e}")
        return False
    finally:
        conn.close()

def delete_appointment_ui():
    if not st.session_state.get("logged_in") or st.session_state["role"] != "Patient":
        st.warning("You must log in as a patient to manage appointments.")
        return

    st.subheader("Delete an Appointment")

    # Fetch appointments for the logged-in patient
    patient_id = st.session_state["user_id"]
    appointments = fetch_patient_appointments(patient_id)

    if not appointments:
        st.info("You have no appointments to delete.")
        return

    # Create options for the appointment select box
    appointment_options = {
        f"Appointment {appt[0]}: {appt[1]} {appt[2]} with Dr. {appt[3]} {appt[4]} ({appt[5]})": appt[0]
        for appt in appointments
    }
    selected_appointment = st.selectbox("Select an Appointment to Delete", list(appointment_options.keys()))
    appointment_id = appointment_options[selected_appointment]

    if st.button("Delete Appointment"):
        success = delete_appointment(appointment_id)
        if success:
            st.success("Appointment deleted successfully!")
        else:
            st.error("Failed to delete appointment. Please try again.")

            st.warning("You must log in as a patient to delete an appointment.")



def fetch_all_appointments():
    conn = connect_to_db()
    if conn is None:
        return []

    cursor = conn.cursor()
    query = """
        SELECT 
            a.AppointmentID, 
            a.AppointmentDate, 
            a.AppointmentTime, 
            p.FirstName AS PatientFirstName, 
            p.LastName AS PatientLastName, 
            p.Email AS PatientEmail, 
            d.FirstName AS DoctorFirstName, 
            d.LastName AS DoctorLastName, 
            d.Specialization
        FROM 
            Appointment a
        JOIN 
            Patient p ON a.PatientID = p.PatientID
        JOIN 
            Doctor d ON a.DoctorID = d.DoctorID
        ORDER BY 
            a.AppointmentDate DESC, a.AppointmentTime DESC
    """
    try:
        cursor.execute(query)
        appointments = cursor.fetchall()
        return appointments
    except Exception as e:
        st.error(f"Error fetching appointments: {e}")
        return []
    finally:
        conn.close()


def admin_view_patient_appointments_ui():
    st.subheader("Admin - All Appointments")
    
    # Fetch all appointments
    appointments = fetch_all_appointments()

    if not appointments:
        st.info("No appointments found.")
        return

    # Format and display appointments
    st.write("### All Appointments (Latest at the Top)")
    appointment_data = [
        {
            "Appointment ID": appt[0],
            "Date": appt[1],
            "Time": appt[2],
            "Patient": f"{appt[3]} {appt[4]}",
            "Patient Email": appt[5],
            "Doctor": f"{appt[6]} {appt[7]}",
            "Specialization": appt[8],
        }
        for appt in appointments
    ]
    st.dataframe(appointment_data)

    # Optional: Add filters for searching by patient, doctor, or date
    with st.expander("Filter Appointments"):
        filter_type = st.selectbox("Filter by", ["None", "Patient Name", "Doctor Name", "Date"])
        if filter_type == "Patient Name":
            patient_name = st.text_input("Enter Patient Name")
            if patient_name:
                filtered_data = [
                    appt for appt in appointment_data
                    if patient_name.lower() in appt["Patient"].lower()
                ]
                st.dataframe(filtered_data)
        elif filter_type == "Doctor Name":
            doctor_name = st.text_input("Enter Doctor Name")
            if doctor_name:
                filtered_data = [
                    appt for appt in appointment_data
                    if doctor_name.lower() in appt["Doctor"].lower()
                ]
                st.dataframe(filtered_data)
        elif filter_type == "Date":
            date = st.date_input("Select Date")
            if date:
                filtered_data = [
                    appt for appt in appointment_data
                    if appt["Date"] == str(date)
                ]
                st.dataframe(filtered_data)



def appointment_operations_ui():
    st.subheader("Manage Your Appointments")

    # Define operations based on user role
    if st.session_state["role"] == "Patient":
        operations = ["Create", "View", "Update"]
    elif st.session_state["role"] == "Admin":
        operations = ["View"]
    elif st.session_state["role"] == "Doctor":
        operations = ["View"]
    else:
        st.warning("Invalid role. Please log in again.")
        return

    # Select CRUD Operation based on role
    operation = st.radio("Select Operation", operations)

    # Perform actions based on the selected operation
    if operation == "Create":
        create_appointment_ui()
    elif operation == "View" and st.session_state["role"] == "Patient" :
        view_patient_appointments_ui()
    elif operation == "View" and st.session_state["role"] == "Admin" :
        admin_view_patient_appointments_ui()   
    elif operation == "View" and st.session_state["role"] == "Doctor" :
        view_doctor_appointments_ui()
    elif operation == "Update":
        update_appointment_ui()
    elif operation == "Delete":
        delete_appointment_ui()




# Function to fetch appointments with patient names for a specific doctor
def get_doctor_appointments(doctor_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        SELECT 
            Appointment.AppointmentID, 
            Patient.FirstName, 
            Appointment.AppointmentDate
        FROM 
            Appointment
        JOIN 
            Patient ON Appointment.PatientID = Patient.PatientID
        WHERE 
            Appointment.DoctorID = %s
    """
    try:
        cursor.execute(query, (doctor_id,))
        appointments = cursor.fetchall()
        return appointments
    except Exception as e:
        print(f"Error fetching doctor appointments: {e}")
        return []
    finally:
        conn.close()

    
def add_medical_record(appointment_id, prescription, diagnosis, test_taken):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        INSERT INTO MedicalRecord (AppointmentID, Prescription, Diagnosis, TestTaken)
        VALUES (%s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (appointment_id, prescription, diagnosis, test_taken))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding medical record: {e}")
        return False
    finally:
        conn.close()

# UI to add a medical record
def add_medical_record_ui():
    if not st.session_state.get("logged_in") or st.session_state["role"] == "Patient":
        st.warning("You must log in as a doctor to create medical records.")
        return

    st.subheader("Create Medical Record")

    # Get doctor ID from session state
    doctor_id = st.session_state.get("user_id")  # Assuming doctor ID is stored in session_state

    # Fetch appointments for the doctor
    appointments = get_doctor_appointments(doctor_id)

    if not appointments:
        st.warning("No appointments found for this doctor.")
        return

    # Display appointments in a dropdown with patient names
    appointment_options = {
        f"Appointment ID: {app[0]}, Patient: {app[1]}, Date: {app[2]}": app[0]
        for app in appointments
    }
    selected_appointment = st.selectbox("Select an Appointment", options=appointment_options.keys())

    # Get the corresponding appointment ID
    appointment_id = appointment_options[selected_appointment]

    # Input fields for prescription, diagnosis, and test taken
    prescription = st.text_area("Prescription")
    diagnosis = st.text_area("Diagnosis")
    test_taken = st.checkbox("Test Taken")

    if st.button("Create Medical Record"):
        success = add_medical_record(appointment_id, prescription, diagnosis, test_taken)
        if success:
            st.success("Medical record created successfully!")
        else:
            st.error("Failed to create medical record.")


# Function to view medical records
def view_medical_records(appointment_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        SELECT RecordID, Prescription, Diagnosis, TestTaken
        FROM MedicalRecord
        WHERE AppointmentID = %s
    """
    try:
        cursor.execute(query, (appointment_id,))
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching medical records: {e}")
        return []
    finally:
        conn.close()

def view_medical_records_for_doctor(doctor_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        SELECT 
            MedicalRecord.RecordID, 
            CONCAT(Patient.FirstName, ' ', Patient.LastName) AS PatientName, 
            Appointment.AppointmentDate, 
            MedicalRecord.Prescription, 
            MedicalRecord.Diagnosis, 
            MedicalRecord.TestTaken
        FROM 
            MedicalRecord
        JOIN 
            Appointment ON MedicalRecord.AppointmentID = Appointment.AppointmentID
        JOIN 
            Patient ON Appointment.PatientID = Patient.PatientID
        WHERE 
            Appointment.DoctorID = %s;
    """
    try:
        cursor.execute(query, (doctor_id,))
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching medical records: {e}")
        return []
    finally:
        conn.close()


# UI to view medical records
def view_medical_records_ui():
    if not st.session_state.get("logged_in") :
        st.warning("You must log in to view medical records.")
        return

    st.subheader("View Medical Records")

    # Get the doctor ID from the session state
    doctor_id = st.session_state.get("user_id")  # Assuming doctor ID is stored in session state

    # Fetch medical records for the doctor
    records = view_medical_records_for_doctor(doctor_id)

    if records:
        st.write("### Medical Records")
        for record in records:
            st.write(f"**Record ID:** {record[0]}")
            st.write(f"**Patient Name:** {record[1]}")
            st.write(f"**Appointment Date:** {record[2]}")
            st.write(f"**Prescription:** {record[3]}")
            st.write(f"**Diagnosis:** {record[4]}")
            st.write(f"**Test Taken:** {'Yes' if record[5] else 'No'}")
            st.write("---")
    else:
        st.warning("No medical records found for this doctor.")


# Function to update a medical record
def update_medical_record(record_id, prescription, diagnosis, test_taken):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        UPDATE MedicalRecord
        SET Prescription = %s, Diagnosis = %s, TestTaken = %s
        WHERE RecordID = %s
    """
    try:
        cursor.execute(query, (record_id, prescription, diagnosis, test_taken))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating medical record: {e}")
        return False
    finally:
        conn.close()


# Function to fetch medical records for a specific doctor
def get_doctor_medical_records(doctor_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        SELECT 
            MedicalRecord.RecordID, 
            CONCAT(Patient.FirstName, ' ', Patient.LastName) AS PatientName, 
            Appointment.AppointmentDate, 
            MedicalRecord.Prescription, 
            MedicalRecord.Diagnosis, 
            MedicalRecord.TestTaken
        FROM 
            MedicalRecord
        JOIN 
            Appointment ON MedicalRecord.AppointmentID = Appointment.AppointmentID
        JOIN 
            Patient ON Appointment.PatientID = Patient.PatientID
        WHERE 
            Appointment.DoctorID = %s;
    """
    try:
        cursor.execute(query, (doctor_id,))
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching medical records: {e}")
        return []
    finally:
        conn.close()



# UI to update a medical record
def update_medical_record_ui():
    if not st.session_state.get("logged_in") or st.session_state["role"] == "Patient":
        st.warning("You must log in as a doctor to update medical records.")
        return

    st.subheader("Update Medical Record")

    # Get doctor ID from session state
    doctor_id = st.session_state.get("user_id")  # Assuming doctor ID is stored in session_state

    # Fetch medical records for the doctor
    medical_records = get_doctor_medical_records(doctor_id)

    if not medical_records:
        st.warning("No medical records found for this doctor.")
        return

    # Display medical records in a dropdown
    record_options = {
        f"Record ID: {rec[0]}, Patient: {rec[1]}, Date: {rec[2]}": rec
        for rec in medical_records
    }
    selected_record = st.selectbox("Select a Medical Record", options=record_options.keys())

    # Get details of the selected record
    record_id, patient_name, appointment_date, existing_prescription, existing_diagnosis, existing_test_taken = record_options[selected_record]

    # Display current details and allow editing
    st.write(f"**Patient Name:** {patient_name}")
    st.write(f"**Appointment Date:** {appointment_date}")
    prescription = st.text_area("Prescription", value=existing_prescription)
    diagnosis = st.text_area("Diagnosis", value=existing_diagnosis)
    test_taken = st.checkbox("Test Taken", value=existing_test_taken)

    if st.button("Update Medical Record"):
        success = update_medical_record(record_id, prescription, diagnosis, test_taken)
        if success:
            st.success("Medical record updated successfully!")
        else:
            st.error("Failed to update medical record.")

# Function to delete a medical record
def delete_medical_record(record_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        DELETE FROM MedicalRecord
        WHERE RecordID = %s
    """
    try:
        cursor.execute(query, (record_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting medical record: {e}")
        return False
    finally:
        conn.close()

# UI to delete a medical record
def delete_medical_record_ui():
    if not st.session_state.get("logged_in") or st.session_state["role"] != "Admin":
        st.warning("You must log in as a admin to delete medical records.")
        return

    st.subheader("Delete Medical Record")

    record_id = st.number_input("Record ID", min_value=1, step=1)

    if st.button("Delete Medical Record"):
        success = delete_medical_record(record_id)
        if success:
            st.success("Medical record deleted successfully!")
        else:
            st.error("Failed to delete medical record.")


def view_medical_records_for_admin():
    conn = connect_to_db()
    if conn is None:
        return []

    cursor = conn.cursor()

    query = """
        SELECT 
            MedicalRecord.RecordID, 
            CONCAT(Patient.FirstName, ' ', Patient.LastName) AS PatientName, 
            Appointment.AppointmentDate, 
            CONCAT(Doctor.FirstName, ' ', Doctor.LastName) AS DoctorName, 
            MedicalRecord.Prescription, 
            MedicalRecord.Diagnosis, 
            MedicalRecord.TestTaken
        FROM 
            MedicalRecord
        JOIN 
            Appointment ON MedicalRecord.AppointmentID = Appointment.AppointmentID
        JOIN 
            Patient ON Appointment.PatientID = Patient.PatientID
        JOIN 
            Doctor ON Appointment.DoctorID = Doctor.DoctorID
        ORDER BY 
            Appointment.AppointmentDate DESC;
    """
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching medical records: {e}")
        return []
    finally:
        conn.close()


def view_medical_records_admin_ui():
    if not st.session_state.get("logged_in") or st.session_state.get("role") != "Admin":
        st.warning("You must log in as an admin to view medical records.")
        return

    st.subheader("Admin - View All Medical Records")

    # Fetch all medical records
    records = view_medical_records_for_admin()

    if records:
        st.write("### Medical Records")
        medical_data = [
            {
                "Record ID": record[0],
                "Patient Name": record[1],
                "Appointment Date": record[2],
                "Assigned Doctor": record[3],
                "Prescription": record[4],
                "Diagnosis": record[5],
                "Test Taken": "Yes" if record[6] else "No",
            }
            for record in records
        ]
        st.dataframe(medical_data)

        # Optional: Add filters for search functionality
        with st.expander("Filter Records"):
            filter_type = st.selectbox("Filter by", ["None", "Patient Name", "Doctor Name", "Appointment Date"])
            if filter_type == "Patient Name":
                patient_name = st.text_input("Enter Patient Name")
                if patient_name:
                    filtered_data = [
                        record for record in medical_data
                        if patient_name.lower() in record["Patient Name"].lower()
                    ]
                    st.dataframe(filtered_data)
            elif filter_type == "Doctor Name":
                doctor_name = st.text_input("Enter Doctor Name")
                if doctor_name:
                    filtered_data = [
                        record for record in medical_data
                        if doctor_name.lower() in record["Assigned Doctor"].lower()
                    ]
                    st.dataframe(filtered_data)
            elif filter_type == "Appointment Date":
                date = st.date_input("Select Appointment Date")
                if date:
                    filtered_data = [
                        record for record in medical_data
                        if record["Appointment Date"] == str(date)
                    ]
                    st.dataframe(filtered_data)
    else:
        st.warning("No medical records found.")


def medical_record_operations_ui():
    st.subheader("Manage Medical Records")

    # Define operations based on user role
    if st.session_state["role"] == "Patient":
        operations = ["View"]
    elif st.session_state["role"] == "Doctor":
        operations = ["Create", "View", "Update"]
    elif st.session_state["role"] == "Admin":
        operations = ["View"]
    else:
        st.warning("Invalid role. Please log in again.")
        return

    # Select CRUD Operation based on role
    operation = st.radio("Select Operation", operations)

    # Perform actions based on the selected operation
    if operation == "Create":
        add_medical_record_ui()
    elif operation == "View"and st.session_state["role"] != "Admin" :
        view_medical_records_ui()
    elif operation == "View" and st.session_state["role"] == "Admin" :
        view_medical_records_admin_ui()
    elif operation == "Update":
        update_medical_record_ui()
    elif operation == "Delete":
        delete_medical_record_ui()



# Function to add a lab test
def add_lab_test(test_name, description, cost):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        INSERT INTO LabTests (TestName, Description, Cost)
        VALUES (%s, %s, %s)
    """
    try:
        cursor.execute(query, (test_name, description, cost))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding lab test: {e}")
        return False
    finally:
        conn.close()

# UI for adding a lab test
def add_lab_test_ui():
    st.subheader("Add Lab Test")

    test_name = st.text_input("Test Name")
    description = st.text_area("Description")
    cost = st.number_input("Cost", min_value=0.0, step=0.01)

    if st.button("Add Lab Test"):
        success = add_lab_test(test_name, description, cost)
        if success:
            st.success("Lab test added successfully!")
        else:
            st.error("Failed to add lab test.")

# Function to view all lab tests
def view_lab_tests():
    conn = connect_to_db()
    cursor = conn.cursor()

    query = "SELECT LabTestID, TestName, Description, Cost, CreatedAt, UpdatedAt FROM LabTests"
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching lab tests: {e}")
        return []
    finally:
        conn.close()

# UI for viewing lab tests
def view_lab_tests_ui():
    st.subheader("View Lab Tests")

    records = view_lab_tests()
    if records:
        for record in records:
            st.write(f"**Lab Test ID:** {record[0]}")
            st.write(f"**Test Name:** {record[1]}")
            st.write(f"**Description:** {record[2]}")
            st.write(f"**Cost:** {record[3]}")
            st.write(f"**Created At:** {record[4]}")
            st.write(f"**Updated At:** {record[5]}")
            st.write("---")
    else:
        st.warning("No lab tests found.")

# Function to update a lab test
def update_lab_test(lab_test_id, test_name, description, cost):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        UPDATE LabTests
        SET TestName = %s, Description = %s, Cost = %s, UpdatedAt = %s
        WHERE LabTestID = %s
    """
    try:
        cursor.execute(query, (test_name, description, cost, datetime.now(), lab_test_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating lab test: {e}")
        return False
    finally:
        conn.close()

# UI for updating a lab test
def update_lab_test_ui():
    st.subheader("Update Lab Test")

    records = view_lab_tests()
    if not records:
        st.warning("No lab tests found to update.")
        return

    lab_test_options = {f"Lab Test ID: {rec[0]}, Name: {rec[1]}": rec for rec in records}
    selected_lab_test = st.selectbox("Select a Lab Test", options=lab_test_options.keys())

    lab_test_id, test_name, description, cost, _, _ = lab_test_options[selected_lab_test]

    test_name = st.text_input("Test Name", value=test_name)
    description = st.text_area("Description", value=description)
    cost = st.number_input("Cost", value=float(cost), min_value=0.0, step=0.01)

    if st.button("Update Lab Test"):
        success = update_lab_test(lab_test_id, test_name, description, cost)
        if success:
            st.success("Lab test updated successfully!")
        else:
            st.error("Failed to update lab test.")

# Function to delete a lab test
def delete_lab_test(lab_test_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = "DELETE FROM LabTests WHERE LabTestID = %s"
    try:
        cursor.execute(query, (lab_test_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting lab test: {e}")
        return False
    finally:
        conn.close()

# UI for deleting a lab test
def delete_lab_test_ui():
    st.subheader("Delete Lab Test")

    records = view_lab_tests()
    if not records:
        st.warning("No lab tests found to delete.")
        return

    lab_test_options = {f"Lab Test ID: {rec[0]}, Name: {rec[1]}": rec[0] for rec in records}
    selected_lab_test = st.selectbox("Select a Lab Test", options=lab_test_options.keys())

    lab_test_id = lab_test_options[selected_lab_test]

    if st.button("Delete Lab Test"):
        success = delete_lab_test(lab_test_id)
        if success:
            st.success("Lab test deleted successfully!")
        else:
            st.error("Failed to delete lab test.")

# Main UI for Lab Test operations
def lab_test_operations_ui():
    st.subheader("Manage Lab Tests")

    operations = ["Create", "View", "Update", "Delete"]
    operation = st.radio("Select Operation", operations)

    if operation == "Create":
        add_lab_test_ui()
    elif operation == "View":
        view_lab_tests_ui()
    elif operation == "Update":
        update_lab_test_ui()
    elif operation == "Delete":
        delete_lab_test_ui()


def add_test_results(record_id, test_name, test_result):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        INSERT INTO TestResults (RecordID, TestName, Result)
        VALUES (%s, %s, %s)
    """
    try:
        cursor.execute(query, (record_id, test_name, test_result))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding test results: {e}")
        return False
    finally:
        conn.close()

def add_test_results_ui():
    if not st.session_state.get("logged_in") or st.session_state["role"] != "Doctor":
        st.warning("You must log in as a doctor to add test results.")
        return

    st.subheader("Add Test Results")

    # Fetch and display medical records
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT MedicalRecord.RecordID, Patient.FirstName, Patient.LastName
            FROM MedicalRecord
            INNER JOIN Patient ON MedicalRecord.PatientID = Patient.PatientID
        """)
        records = cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching medical records: {e}")
        conn.close()
        return
    finally:
        conn.close()

    # Selection inputs
    record_options = {f"Record {r[0]} - {r[1]} {r[2]}": r[0] for r in records}
    selected_record = st.selectbox("Select Medical Record", options=list(record_options.keys()))

    test_name = st.text_input("Enter Test Name")
    test_result = st.text_area("Enter Test Result")

    if st.button("Add Test Results"):
        record_id = record_options[selected_record]
        success = add_test_results(record_id, test_name, test_result)

        if success:
            st.success("Test results added successfully!")
        else:
            st.error("Failed to add test results. Please try again.")









def sign_up_admin(email, password):
    conn = connect_to_db()
    if conn is None:
        print("Failed to connect to database")
        return False
    
    cursor = conn.cursor()
    hashed_pw = hash_password(password)  # Hash the password for security

    # Insert query for admin account
    query = """
        INSERT INTO admin (Email, Password)
        VALUES ( %s, %s)
    """
    try:
        cursor.execute(query, (email, hashed_pw))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def sign_up_admin_ui():
    st.subheader("Admin Sign-Up")
    
    # Admin-specific fields
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    # Button to submit the form
    if st.button("Sign Up"):
        # Validation: Check if passwords match and if all fields are filled
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif not all([email, password]):
            st.error("All fields are required!")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters long!")
        else:
            # Call sign_up_admin function to create admin account
            success = sign_up_admin( email, password)
            
            if success:
                st.success("Admin account created successfully!")
                st.session_state["logged_in"] = True
                st.session_state["role"] = "Admin"
                st.session_state["admin_email"] = email  # Store admin email or ID
                st.session_state["redirect_to_home"] = True  # Set redirection flag
            else:
                st.error("Failed to create account. Please try again.")



# Function to view all appointments with `TestTaken = True`
def get_appointments_with_tests():
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        SELECT AppointmentID, RecordID, TestTaken 
        FROM MedicalRecord WHERE TestTaken = TRUE
    """
    cursor.execute(query)
    records = cursor.fetchall()
    conn.close()
    return records

# Function to add lab tests for an appointment
def add_lab_tests_for_appointment(record_id, lab_tests):
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        for test_id in lab_tests:
            query = """
                INSERT INTO TestResults (LabTestID, RecordID)
                VALUES (%s, %s)
            """
            cursor.execute(query, (test_id, record_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding lab tests: {e}")
        return False
    finally:
        conn.close()

# UI for Doctor to assign tests
def doctor_assign_tests_ui():
    st.subheader("Assign Lab Tests to Patient")

    appointments = get_appointments_with_tests()
    if not appointments:
        st.warning("No appointments with pending tests.")
        return

    appointment_options = {f"Appointment ID: {app[0]}, Record ID: {app[1]}": app[1] for app in appointments}
    selected_record = st.selectbox("Select an Appointment", options=appointment_options.keys())
    record_id = appointment_options[selected_record]

    # Fetch available lab tests
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT LabTestID, TestName FROM LabTests")
    lab_tests = cursor.fetchall()
    conn.close()

    if not lab_tests:
        st.warning("No lab tests available.")
        return

    test_options = {f"{test[1]} (ID: {test[0]})": test[0] for test in lab_tests}
    selected_tests = st.multiselect("Select Lab Tests", options=test_options.keys())

    if st.button("Assign Tests"):
        if selected_tests:
            lab_test_ids = [test_options[test] for test in selected_tests]
            success = add_lab_tests_for_appointment(record_id, lab_test_ids)
            if success:
                st.success("Lab tests assigned successfully!")
        else:
            st.error("No tests selected.")

# Function to add test results
def add_test_result(test_id, result):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = "UPDATE TestResults SET Result = %s WHERE TestID = %s"
    try:
        cursor.execute(query, (result, test_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating test result: {e}")
        return False
    finally:
        conn.close()

# UI for Doctor to add test results
def doctor_add_results_ui():
    st.subheader("Add Lab Test Results")

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TestResults.TestID, LabTests.TestName, TestResults.RecordID, TestResults.Result
        FROM TestResults
        JOIN LabTests ON TestResults.LabTestID = LabTests.LabTestID
        WHERE TestResults.Result IS NULL
    """)
    pending_tests = cursor.fetchall()
    conn.close()

    if not pending_tests:
        st.warning("No pending lab tests.")
        return

    test_options = {f"{test[1]} (Record ID: {test[2]})": test for test in pending_tests}
    selected_test = st.selectbox("Select a Test", options=test_options.keys())
    test_id, test_name, record_id, _ = test_options[selected_test]

    result = st.text_area(f"Enter Result for {test_name}")
    if st.button("Submit Result"):
        if result.strip():
            success = add_test_result(test_id, result)
            if success:
                st.success("Result added successfully!")
        else:
            st.error("Result cannot be empty.")



def view_patient_tests(patient_id):
    """
    Fetches lab test results for a given patient, including appointment ID, appointment date,
    doctor's name, test name, and test results.
    
    Args:
    patient_id (int): The ID of the patient.
    
    Returns:
    list: A list of tuples containing appointment ID, date, doctor's name, test name, and test result.
    """
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        SELECT 
            a.AppointmentID,
            a.AppointmentDate,
            CONCAT(d.FirstName, ' ', d.LastName) AS DoctorName,
            lt.TestName,
            tr.Result
        FROM TestResults tr
        JOIN MedicalRecord mr ON tr.RecordID = mr.RecordID
        JOIN LabTests lt ON tr.LabTestID = lt.LabTestID
        JOIN Appointment a ON mr.AppointmentID = a.AppointmentID
        JOIN Doctor d ON a.DoctorID = d.DoctorID
        WHERE a.PatientID = %s
    """
    cursor.execute(query, (patient_id,))
    records = cursor.fetchall()
    conn.close()
    return records

# UI for patients to view test results
def patient_view_tests_ui():
    """
    Displays the patient's lab test results in the Streamlit UI.
    Ensures the user is logged in as a patient.
    """
    st.subheader("View Lab Test Results")

    # Check if the user is logged in as a patient
    if not st.session_state.get("logged_in") or st.session_state["role"] != "Patient":
        st.warning("You must log in as a patient to view lab test results.")
        return

    patient_id = st.session_state["user_id"]

    if st.button("View Tests"):
        results = view_patient_tests(patient_id)
        if results:
            for record in results:
                st.write(f"**Appointment ID:** {record[0]}")
                st.write(f"**Appointment Date:** {record[1]}")
                st.write(f"**Doctor's Name:** {record[2]}")
                st.write(f"**Test Name:** {record[3]}")
                st.write(f"**Result:** {record[4]}")
                st.write("---")
        else:
            st.warning("No test results found.")


# Admin CRUD operations for LabTests
def admin_lab_tests_ui():
    st.subheader("Manage Lab Tests (Admin)")

    operations = ["Create", "View", "Update", "Delete"]
    operation = st.radio("Select Operation", operations)

    if operation == "Create":
        # Add lab test logic here
        add_lab_test_ui()
    elif operation == "View":
        # View lab tests logic here
        view_lab_tests_ui()
    elif operation == "Update":
        # Update lab tests logic here
        update_lab_test_ui()
    elif operation == "Delete":
        # Delete lab tests logic here
        delete_lab_test_ui()



# Check if wallet exists for a patient
def check_wallet_exists(patient_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = "SELECT WalletID FROM Wallets WHERE PatientID = %s"
    cursor.execute(query, (patient_id,))
    result = cursor.fetchone()
    conn.close()

    return result is not None

# Create wallet for the patient
def create_wallet(patient_id, initial_balance=0.0):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = "INSERT INTO Wallets (PatientID, Balance) VALUES (%s, %s)"
    cursor.execute(query, (patient_id, initial_balance))
    conn.commit()
    conn.close()

# Fetch wallet balance
def fetch_wallet_balance(patient_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = "SELECT Balance FROM Wallets WHERE PatientID = %s"
    cursor.execute(query, (patient_id,))
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None

# Add money to wallet
def add_money_to_wallet(patient_id, amount):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = "UPDATE Wallets SET Balance = Balance + %s WHERE PatientID = %s"
    cursor.execute(query, (amount, patient_id))
    conn.commit()
    conn.close()

# Fetch unpaid bills
def fetch_unpaid_bills(patient_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        SELECT BillingID, TotalAmount, PaymentStatus 
        FROM Billing 
        WHERE PatientID = %s AND PaymentStatus = 'Pending'
    """
    cursor.execute(query, (patient_id,))
    bills = cursor.fetchall()
    conn.close()

    return bills

def pay_bill_with_wallet(patient_id, billing_id, amount):
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        # Start a transaction explicitly
        conn.begin()

        # Deduct from wallet balance
        deduct_query = "UPDATE Wallets SET Balance = Balance - %s WHERE PatientID = %s"
        cursor.execute(deduct_query, (amount, patient_id))

        # Generate a unique transaction ID
        transaction_id = int(datetime.now().timestamp())

        # Update billing status
        update_query = "UPDATE Billing SET PaymentStatus = 'Completed', TransactionID = %s WHERE BillingID = %s"
        cursor.execute(update_query, (transaction_id, billing_id))

        # Update admin wallet balance
        update_admin_query = "UPDATE AdminWallets SET Balance = Balance + %s WHERE WalletID = 1"
        cursor.execute(update_admin_query, (amount,))

        # Commit the transaction if all queries succeed
        conn.commit()

    except pymysql.MySQLError as err:
        # Rollback the transaction in case of an error
        print(f"Error: {err}")
        conn.rollback()

    finally:
        # Ensure the connection is closed
        cursor.close()
        conn.close()
    

# Wallet UI
def wallet_ui():
    st.title("Manage Your Wallet")

    # Assume patient is logged in and their ID is in session
    patient_id = st.session_state.get("user_id", 1)  # Replace with actual session handling
    
    # Check if the wallet exists
    wallet_exists = check_wallet_exists(patient_id)
    if not wallet_exists:
        st.warning("No wallet found for your account.")
        if st.button("Create Wallet"):
            create_wallet(patient_id)
            st.success("Wallet created successfully!")
        return

    # Display current wallet balance
    balance = fetch_wallet_balance(patient_id)
    if balance is not None:
        st.write(f"### Current Wallet Balance: ₹{balance:.2f}")
    else:
        st.error("Failed to fetch wallet balance. Please try again later.")
        return

    # Section to add money to wallet
    st.subheader("Add Money to Wallet")
    add_amount = st.number_input("Enter amount to add:", min_value=0.0, step=100.0)
    if st.button("Add Money"):
        if add_amount > 0:
            add_money_to_wallet(patient_id, add_amount)
            st.success(f"₹{add_amount:.2f} added to your wallet.")
        else:
            st.warning("Please enter a valid amount.")

    # Section to pay bills
    st.subheader("Pay Bills")
    unpaid_bills = fetch_unpaid_bills(patient_id)

    if unpaid_bills:
        for bill in unpaid_bills:
            billing_id, total_amount, payment_status = bill
            st.write(f"**Billing ID:** {billing_id}")
            st.write(f"**Total Amount:** ₹{total_amount:.2f}")
            st.write(f"**Payment Status:** {payment_status}")
            
            if total_amount <= balance:
                if st.button(f"Pay ₹{total_amount:.2f} for Billing ID {billing_id}", key=billing_id):
                    pay_bill_with_wallet(patient_id, billing_id, total_amount)
                    st.success(f"Bill {billing_id} paid successfully!")
            else:
                st.warning(f"Not enough balance to pay Bill {billing_id}. Please add money.")
            st.write("---")
    else:
        st.info("No unpaid bills found.")



# Function to add billing
def add_billing(patient_id, record_id, total_amount, payment_status, transaction_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        INSERT INTO Billing (PatientID, RecordID, TotalAmount, PaymentStatus, TransactionID)
        VALUES (%s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (patient_id, record_id, total_amount, payment_status, transaction_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error creating billing record: {e}")
        return False
    finally:
        conn.close()

# UI for adding billing
def doctor_add_billing_ui():
    st.subheader("Create Billing Record")

    # Get patient and record details for the UI
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Fetch patient details (you can modify the query as needed)
    cursor.execute("SELECT PatientID, FirstName FROM Patient")
    patients = cursor.fetchall()

    # Fetch medical record details (you can modify the query as needed)
    cursor.execute("SELECT RecordID, Diagnosis FROM MedicalRecord")
    records = cursor.fetchall()

    conn.close()

    # Dropdowns for selecting patient and medical record
    patient_options = {f"{patient[1]} (Patient ID: {patient[0]})": patient for patient in patients}
    selected_patient = st.selectbox("Select a Patient", options=patient_options.keys())
    patient_id, _ = patient_options[selected_patient]

    record_options = {f"{record[1]} (Record ID: {record[0]})": record for record in records}
    selected_record = st.selectbox("Select a Medical Record", options=record_options.keys())
    record_id, _ = record_options[selected_record]

    # Input fields for billing
    total_amount = st.number_input("Total Amount", min_value=0.0, format="%.2f")
    payment_status = st.selectbox("Payment Status", options=["Pending", "Completed"])
    transaction_id = st.number_input("Transaction ID", min_value=0, step=1, format="%d", value=0)

    if st.button("Create Billing Record"):
        if total_amount > 0:
            success = add_billing(patient_id, record_id, total_amount, payment_status, transaction_id)
            if success:
                st.success("Billing record created successfully!")
        else:
            st.error("Total amount must be greater than zero.")

# Streamlit UI to process payment
def admin_wallet_ui():
    st.subheader("Admin - Process Payment")

    # Ensure admin ID is correctly set, assuming the admin ID is in session state
    admin_id = st.session_state.get("user_id")  # Replace with actual session handling

    if admin_id is None:
        st.error("Admin ID not found! Please log in first.")
        return

    conn = connect_to_db()
    cursor = conn.cursor()

    # Fetch the admin's wallet balance
    query = "SELECT Balance FROM AdminWallets WHERE id = %s"
    cursor.execute(query, (admin_id,))
    result = cursor.fetchone()

    # If wallet does not exist, prompt to create it
    if result is None:
        st.warning("No wallet found for the admin.")
        if st.button("Create Admin Wallet"):
            create_admin_wallet(admin_id)  # Create the wallet for the admin
            st.success("Admin wallet created successfully!")
    else:
        admin_wallet_balance = result[0]  # Fetch the balance from the result
        st.write(f"### Current Admin Wallet Balance: ₹{admin_wallet_balance:.2f}")

        # Section to add money to the admin's wallet
        st.subheader("Add Money to Admin Wallet")
        add_amount = st.number_input("Enter amount to add:", min_value=0.0, step=100.0)
        if st.button("Add Money"):
            if add_amount > 0:
                add_money_to_admin_wallet(admin_id, add_amount)  # Add money to the wallet
                st.success(f"₹{add_amount:.2f} added to the admin wallet.")
            else:
                st.warning("Please enter a valid amount.")

    conn.close()

# Function to create admin wallet (if not already created)
def create_admin_wallet(admin_id):
    if admin_id is None:
        st.error("Admin ID is not available to create the wallet.")
        return

    conn = connect_to_db()
    cursor = conn.cursor()

    # Make sure admin_id is valid
    query = "INSERT INTO AdminWallets (id, Balance) VALUES (%s, %s)"
    cursor.execute(query, (admin_id, 0.0))  # Initial balance is 0.0
    conn.commit()
    conn.close()

# Function to add money to admin wallet
def add_money_to_admin_wallet(admin_id, amount):
    if admin_id is None:
        st.error("Admin ID is not available to add money to the wallet.")
        return

    conn = connect_to_db()
    cursor = conn.cursor()

    query = "UPDATE AdminWallets SET Balance = Balance + %s WHERE id = %s"
    cursor.execute(query, (amount, admin_id))
    conn.commit()
    conn.close()


def fetch_billing_records_for_admin():
    conn = connect_to_db()
    if conn is None:
        return []

    cursor = conn.cursor()
    query = """
        SELECT 
            b.BillingID,
            CONCAT(p.FirstName, ' ', p.LastName) AS PatientName,
            b.TotalAmount,
            b.PaymentStatus,
            b.TransactionID,
            m.Diagnosis
        FROM 
            Billing b
        JOIN 
            Patient p ON b.PatientID = p.PatientID
        JOIN 
            MedicalRecord m ON b.RecordID = m.RecordID
        ORDER BY 
            b.BillingID DESC
    """
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        return records
    except Exception as e:
        st.error(f"Error fetching billing records: {e}")
        return []
    finally:
        conn.close()


def view_billing_record_ui():
    st.subheader("Admin - View All Billing Records")

    # Fetch billing records
    records = fetch_billing_records_for_admin()

    if records:
        st.write("### Billing Records")
        billing_data = [
            {
                "Billing ID": record[0],
                "Patient Name": record[1],
                "Total Amount": f"${record[2]:,.2f}",
                "Payment Status": record[3],
                "Transaction ID": record[4],
                "Diagnosis": record[5],
            }
            for record in records
        ]

        # Display billing data in a table
        st.dataframe(billing_data)
    else:
        st.info("No billing records found.")


def fetch_lab_tests():
    conn = connect_to_db()
    if conn is None:
        return []

    cursor = conn.cursor()
    query = """
        SELECT LabTestID, TestName, Description, Cost, CreatedAt, UpdatedAt
        FROM LabTests
        ORDER BY CreatedAt DESC
    """
    try:
        cursor.execute(query)
        lab_tests = cursor.fetchall()
        return lab_tests
    except Exception as e:
        st.error(f"Error fetching lab tests: {e}")
        return []
    finally:
        conn.close()

# Function to add a new lab test
def add_lab_test(test_name, description, cost):
    conn = connect_to_db()
    if conn is None:
        return False

    cursor = conn.cursor()
    query = """
        INSERT INTO LabTests (TestName, Description, Cost)
        VALUES (%s, %s, %s)
    """
    try:
        cursor.execute(query, (test_name, description, cost))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding lab test: {e}")
        return False
    finally:
        conn.close()

# Lab Test UI for Admin
def lab_test_ui():
    st.subheader("Admin - Lab Test Management")

    # Fetch lab tests and display them
    lab_tests = fetch_lab_tests()

    if lab_tests:
        st.write("### Lab Test List")
        lab_test_data = [
            {
                "Lab Test ID": test[0],
                "Test Name": test[1],
                "Description": test[2],
                "Cost": f"${test[3]:,.2f}",
                "Created At": test[4],
                "Updated At": test[5],
            }
            for test in lab_tests
        ]
        st.dataframe(lab_test_data)
    else:
        st.info("No lab tests found.")

    # Form to add a new lab test
    st.write("### Add a New Lab Test")

    test_name = st.text_input("Test Name")
    description = st.text_area("Description")
    cost = st.number_input("Cost", min_value=0.0, format="%.2f")

    if st.button("Add Lab Test"):
        if test_name and description and cost > 0:
            success = add_lab_test(test_name, description, cost)
            if success:
                st.success("Lab test added successfully!")
        else:
            st.error("Please fill in all fields and ensure cost is greater than zero.")

#     main()
def main():
    st.title("Health Records Management System")

    # Check for redirection after login or sign-up
    if not st.session_state.get("logged_in"):
        # If not logged in, show login and signup options
        menu = ["Home", "Login", "Sign Up"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Home":
            st.subheader("Welcome to the Health Records System! Please login to access your records.")
        
        elif choice == "Login":
            login_ui()
        
        elif choice == "Sign Up":
            role = st.radio("Sign-Up As", ["Patient", "Doctor", "Admin"])  # Added Admin role option
            if role == "Patient":
                sign_up_patient_ui()
            elif role == "Doctor":
                sign_up_doctor_ui()
            elif role == "Admin":
                sign_up_admin_ui()  # Admin sign-up

    else:
        # If the user is logged in, show appropriate menu based on their role
        if st.session_state["role"] == "Patient":
            menu = ["Home", "Appointment", "Medical Record","LabResults","Wallet", "Logout"]
            choice = st.sidebar.selectbox("Menu", menu)

            if choice == "Home":
                st.subheader(f"Welcome back, {st.session_state['role']}!")
            elif choice == "Appointment":
                appointment_operations_ui()
            elif choice == "Medical Record":
                medical_record_operations_ui()
            # elif choice == "Prescription":
            #     prescription_operations_ui()
            elif choice == "LabResults": 
                patient_view_tests_ui()
            elif choice == "Wallet":
                wallet_ui()
                    
            elif choice == "Logout":
                logout_ui()

        elif st.session_state["role"] == "Doctor":
            menu = ["Home","Medical Record","LabResults","Appointment","Billing", "Logout"]
            choice = st.sidebar.selectbox("Menu", menu)

            if choice == "Home":
                st.subheader(f"Welcome back, Dr. {st.session_state['role']}!")
            elif choice == "Appointment":
                appointment_operations_ui()
            elif choice == "Medical Record":
                medical_record_operations_ui()
            elif choice == "LabResults":
                action = st.sidebar.radio("Choose Action", ["Assign Tests", "Add Results"])
                if action == "Assign Tests":
                    doctor_assign_tests_ui()
                elif action == "Add Results":
                    doctor_add_results_ui()
            elif choice == "Billing":
                doctor_add_billing_ui()
            elif choice == "Logout":
                logout_ui()

        elif st.session_state["role"] == "Admin":
            menu = ["Home", "Appointment", "Medical Record", "View Billing Record","LabTests","LabResults","AdminWallet","Logout"]
            choice = st.sidebar.selectbox("Menu", menu)

            if choice == "Home":
                st.subheader(f"Welcome back, Admin!")
            elif choice == "Appointment":
                appointment_operations_ui()
            elif choice == "Medical Record":
                medical_record_operations_ui()
            elif choice =="View Billing Record":
                view_billing_record_ui()
            elif choice == "LabTests":
                lab_test_ui()
            elif choice == "LabResults":
                admin_lab_tests_ui()
            elif choice == "AdminWallet":
                admin_wallet_ui()
            
            elif choice == "Logout":
                logout_ui()

                

                

if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None
        st.session_state["role"] = None
        st.session_state["admin_email"] = None  # Initialize admin session state

    main()