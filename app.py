import os
import sqlite3
import pandas as pd
import re

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

############################################################
# Flask Configuration
############################################################

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = "drug_recommendation_secret_key"

############################################################
# Paths
############################################################

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DATASET_FOLDER = os.path.join(BASE_DIR, "dataset")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATASET_FOLDER, exist_ok=True)

CSV_PATH = os.path.join(
    DATASET_FOLDER,
    "drugs_side_effects_drugs_com.csv"
)

DATABASE = os.path.join(
    BASE_DIR,
    "drug_history.db"
)

############################################################
# Load Dataset
############################################################

drug_data = pd.DataFrame()

try:

    if os.path.isfile(CSV_PATH):

        drug_data = pd.read_csv(
            "dataset/drugs_side_effects_drugs_com.csv",
            low_memory=False
        )

        drug_data.columns = (
            drug_data.columns
            .str.strip()
            .str.lower()
            .str.replace(" ","_")
        )

        print("="*60)
        print("Dataset Loaded Successfully")
        print("Total Records :",len(drug_data))
        print("Columns :")
        print(drug_data.columns.tolist())
        print("="*60)

    else:

        print("Dataset Not Found")
        print(CSV_PATH)

except Exception as e:

    print("CSV Loading Error")
    print(e)

############################################################
# Database
############################################################

def init_db():

    conn = sqlite3.connect(DATABASE)

    cur = conn.cursor()

    cur.execute("""

    CREATE TABLE IF NOT EXISTS history(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        drug_name TEXT,

        medical_condition TEXT,

        generic_name TEXT,

        drug_class TEXT,

        rating TEXT,

        activity TEXT,

        search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    conn.commit()

    conn.close()

init_db()

############################################################
# Save Search History
############################################################

def save_history(

    drug_name,

    medical_condition,

    generic_name,

    drug_class,

    rating,

    activity

):

    conn=sqlite3.connect(DATABASE)

    cur=conn.cursor()

    cur.execute("""

    INSERT INTO history(

    drug_name,

    medical_condition,

    generic_name,

    drug_class,

    rating,

    activity

    )

    VALUES(?,?,?,?,?,?)

    """,(

        str(drug_name),

        str(medical_condition),

        str(generic_name),

        str(drug_class),

        str(rating),

        str(activity)

    ))

    conn.commit()

    conn.close()

############################################################
# Login
############################################################

############################################################
# Login
############################################################

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Username Validation
        if username == "":
            flash("Username cannot be empty.")
            return redirect(url_for("login"))

        # Password Validation
        if len(password) < 8:
            flash("Password must be at least 8 characters long.")
            return redirect(url_for("login"))

        if not re.search(r"[A-Z]", password):
            flash("Password must contain at least one uppercase letter.")
            return redirect(url_for("login"))

        if not re.search(r"[0-9]", password):
            flash("Password must contain at least one number.")
            return redirect(url_for("login"))

        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
            flash("Password must contain at least one special character.")
            return redirect(url_for("login"))

        # Login Success
        session["admin"] = True
        session["username"] = username

        flash(f"Welcome {username}")

        return redirect(url_for("index"))

    return render_template("admin.html")

############################################################
# Logout
############################################################

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged Out Successfully")

    return redirect(url_for("login"))

############################################################
# Home
############################################################

@app.route("/index")
def index():

    if not session.get("admin"):

        return redirect(url_for("login"))

    total_records=len(drug_data)

    return render_template(

        "index.html",

        total_records=total_records

    )

############################################################
# Upload CSV
############################################################

@app.route("/upload_csv",methods=["POST"])
def upload_csv():

    global drug_data

    if not session.get("admin"):

        return redirect(url_for("login"))

    file=request.files.get("csvfile")

    if file is None or file.filename=="":

        flash("Please Select CSV File")

        return redirect(url_for("index"))

    filepath=os.path.join(

        UPLOAD_FOLDER,

        file.filename

    )

    file.save(filepath)

    try:

        drug_data=pd.read_csv(

            filepath,

            low_memory=False

        )

        drug_data.columns=(

            drug_data.columns

            .str.strip()

            .str.lower()

            .str.replace(" ","_")

        )

        flash("Dataset Uploaded Successfully")

    except Exception as e:

        flash(str(e))

    return redirect(url_for("index"))


############################################################
# Search Drug / Disease
############################################################

@app.route("/search", methods=["POST"])
def search():

    global drug_data

    if drug_data.empty:
        flash("Dataset not loaded")
        return redirect(url_for("index"))

    keyword = request.form.get("keyword", "").strip().lower()

    if keyword == "":
        flash("Enter keyword")
        return redirect(url_for("index"))

    # CLEAN ALL TEXT FIRST (IMPORTANT FIX)
    df = drug_data.copy()

    for col in df.columns:
        df[col] = df[col].astype(str).str.lower()

    # SEARCH ALL POSSIBLE COLUMNS
    mask = (
        df.get("drug_name", "").str.contains(keyword, na=False) |
        df.get("medical_condition", "").str.contains(keyword, na=False) |
        df.get("generic_name", "").str.contains(keyword, na=False) |
        df.get("brand_names", "").str.contains(keyword, na=False)
    )

    result = df[mask]

    if result.empty:
        flash("No results found")
        return redirect(url_for("index"))

    records = result.to_dict(orient="records")

    first = records[0]

    save_history(
        first.get("drug_name", ""),
        first.get("medical_condition", ""),
        first.get("generic_name", ""),
        first.get("drug_classes", ""),
        first.get("rating", ""),
        first.get("activity", "")
    )

    return render_template(
        "result.html",
        found=True,
        keyword=keyword,
        results=records
    )

############################################################
# Search History
############################################################

@app.route("/history")
def history():

    if not session.get("admin"):
        flash("Please login first.")
        return redirect(url_for("login"))

    conn = sqlite3.connect(DATABASE)

    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM history
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    conn.close()

    return render_template(
        "history.html",
        history=rows
    )



############################################################
# Dashboard
############################################################

@app.route("/dashboard")
def dashboard():

    if not session.get("admin"):
        flash("Please login first.")
        return redirect(url_for("login"))

    if drug_data.empty:
        flash("Dataset Not Loaded")
        return redirect(url_for("index"))

    ########################################################
    # Statistics
    ########################################################

    total_drugs = len(drug_data)

    total_conditions = (
        drug_data["medical_condition"].nunique()
        if "medical_condition" in drug_data.columns
        else 0
    )

    if "rating" in drug_data.columns:

        avg_rating = round(
            pd.to_numeric(
                drug_data["rating"],
                errors="coerce"
            ).mean(),
            2
        )

    else:

        avg_rating = 0

    if "no_of_reviews" in drug_data.columns:

        total_reviews = int(

            pd.to_numeric(

                drug_data["no_of_reviews"],

                errors="coerce"

            ).fillna(0).sum()

        )

    else:

        total_reviews = 0

    ########################################################
    # Top Medical Conditions
    ########################################################

    if "medical_condition" in drug_data.columns:

        condition_data = (

            drug_data["medical_condition"]

            .value_counts()

            .head(10)

        )

        condition_labels = condition_data.index.tolist()

        condition_values = condition_data.values.tolist()

    else:

        condition_labels = []

        condition_values = []

    ########################################################
    # Top Drug Classes
    ########################################################

    if "drug_classes" in drug_data.columns:

        class_data = (

            drug_data["drug_classes"]

            .value_counts()

            .head(10)

        )

        class_labels = class_data.index.tolist()

        class_values = class_data.values.tolist()

    else:

        class_labels = []

        class_values = []

    ########################################################
    # Rating Distribution
    ########################################################

    if "rating" in drug_data.columns:

        rating_data = (

            drug_data["rating"]

            .fillna(0)

            .astype(str)

            .value_counts()

            .sort_index()

        )

        rating_labels = rating_data.index.tolist()

        rating_values = rating_data.values.tolist()

    else:

        rating_labels = []

        rating_values = []

    ########################################################
    # Recent History
    ########################################################

    conn = sqlite3.connect(DATABASE)

    cur = conn.cursor()

    cur.execute("""

        SELECT *

        FROM history

        ORDER BY id DESC

        LIMIT 10

    """)

    recent_history = cur.fetchall()

    conn.close()

    ########################################################
    # Render Dashboard
    ########################################################

    return render_template(

        "dashboard.html",

        total_drugs=total_drugs,

        total_conditions=total_conditions,

        avg_rating=avg_rating,

        total_reviews=total_reviews,

        condition_labels=condition_labels,

        condition_values=condition_values,

        class_labels=class_labels,

        class_values=class_values,

        rating_labels=rating_labels,

        rating_values=rating_values,

        recent_history=recent_history

    )


############################################################
# About
############################################################

@app.route("/about")
def about():

    if not session.get("admin"):
        return redirect(url_for("login"))

    return render_template("about.html")


############################################################
# Contact
############################################################

@app.route("/contact")
def contact():

    if not session.get("admin"):
        return redirect(url_for("login"))

    return render_template("contact.html")


############################################################
# Error Handlers
############################################################

@app.errorhandler(404)
def page_not_found(error):

    return "404 Page Not Found",404


@app.errorhandler(500)
def internal_server_error(error):

    return "500 Internal Server Error",500


############################################################
# Run Flask
############################################################

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5111,

        debug=True,

        threaded=True

    )