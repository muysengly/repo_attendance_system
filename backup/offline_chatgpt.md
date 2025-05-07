To build a Python project for **offline installation** on a new computer, follow these steps:

---

### **1. Prepare Your Python Project**

Ensure your project has:

- A `requirements.txt` file (for dependencies) or a `pyproject.toml` (if using Poetry)
- A `setup.py` (if making an installable package)
- Any necessary scripts, models, or data

---

### **2. Freeze Dependencies**

To ensure your project has the correct dependencies:

```bash
pip freeze > requirements.txt
```

If you use a virtual environment, activate it first:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip freeze > requirements.txt
```

---

### **3. Download Dependencies for Offline Use**

On a computer with internet access, run:

```bash
mkdir offline_packages
pip download -r requirements.txt -d offline_packages
```

This will download `.whl` and `.tar.gz` files for all dependencies.

---

### **4. Package Your Project**

Option 1: **Zip Everything**  
Create a zip file containing:

- Your project source code
- The `offline_packages` folder
- `requirements.txt`

Option 2: **Build a Wheel**  
If you want to install your project as a package:

```bash
python setup.py bdist_wheel
```

Or using Poetry:

```bash
poetry build
```

Your package will be in `dist/`.

---

### **5. Transfer to the Offline Computer**

Copy the zip or built package to the new computer using:

- USB drive
- External HDD/SSD
- Local network transfer

---

### **6. Install Dependencies Offline**

On the offline computer, navigate to the folder and install:

```bash
pip install --no-index --find-links=offline_packages -r requirements.txt
```

Or install a built package:

```bash
pip install --no-index --find-links=dist yourpackage.whl
```

---

### **7. Verify Installation**

Check if the project runs:

```bash
python your_script.py
```

Or if installed as a package:

```bash
python -m yourpackage
```

---

#### **Optional: Create an Executable**

If you want to make an executable:

```bash
pip install pyinstaller
pyinstaller --onefile your_script.py
```

This will generate an executable in the `dist/` folder.

---

Would you like to bundle any additional dependencies like pre-trained models?
