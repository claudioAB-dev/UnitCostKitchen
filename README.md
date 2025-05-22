# 🍳 UnitCostKitchen 📐✨

**Design and quote kitchens like a pro!**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

UnitCostKitchen is a modular desktop application designed to help kitchen designers and sellers efficiently select furniture, configure options (like doors), and calculate unit costs.

**_(Imagine a cool GIF of the app here!)_**

## 🌟 Key Features

* **🗄️ Dynamic Furniture Catalog:**
    * Explore a database of kitchen furniture, categorized by type (wall cabinets, base cabinets, lockers, etc.).
    * Search for specific furniture by model.
    * View complete details: description, base price, dimensions.
* **🚪 Detailed Door Configuration:**
    * Select and assign different door styles and colors (Type 1 and Type 2) to furniture items.
    * Search a door catalog by line, model, or color.
    * Check prices per m² for frames, door fronts, and mullions.
* **💲 Project and Cost Management:**
    * Create, open, save, and save as... kitchen design projects (in JSON format).
    * Add configured furniture to your current project.
    * Calculate the estimated total project cost. *(Currently, a simplified sum of the base furniture price and selected door frame prices)*.
* **🖥️ Intuitive Graphical Interface:**
    * Welcome screen for a quick start.
    * Three-panel layout for easy navigation: available furniture, individual configuration, and project summary.
    * Comprehensive menu bar for all actions.
* **🛠️ Data Tools:**
    * Includes a script (`src/Data_Creator/csv_to_sql.py`) to convert data from CSV files to SQLite databases, with type inference and name sanitization.

## 🛠️ Tech Stack

* **Language:** Python 3.6+
* **GUI:** PyQt6
* **Database:** SQLite
* **Main Dependencies:** `requests`, `numpy` (see `setup.py` for more details).

## 🚀 Getting Started

Follow these steps to get UnitCostKitchen up and running:

### Prerequisites

* Python 3.6 or higher.
* `pip` to install packages.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/claudioAB-dev/UnitCostKitchen.git](https://github.com/claudioAB-dev/UnitCostKitchen.git)
    cd UnitCostKitchen
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt # Optional: Create a requirements.txt from setup.py
    # Or directly if setup.py is configured for it:
    pip install .
    ```
    *(Note: `setup.py` lists `requests` and `numpy` as dependencies. Ensure PyQt6 is also installed; you might need to add it to `install_requires` in `setup.py` or install it manually: `pip install PyQt6`)*

### 📊 Database Setup

The application uses SQLite databases generated from CSV files.

1.  **Source CSV Files:**
    * `src/Data_Creator/dbKitchen.csv`: Contains furniture data.
    * `src/Data_Creator/db_doors.csv`: Contains door data.

2.  **Generate Databases:**
    Run the `csv_to_sql.py` script to process the CSVs and create the necessary database files (`kitchen_main_db` and `dbdoor`) in the `src/data/` directory.

    The `src/Data_Creator/csv_to_sql.py` script has a `sql_generator_main(csv_file, dbname)` function you can use.
    When run directly (`python src/Data_Creator/csv_to_sql.py`), it processes `db_doors.csv` to create `src/data/dbdoor`.
    You'll need to ensure `dbKitchen.csv` is also processed to create `src/data/kitchen_main_db`. You can temporarily modify the `if __name__ == "__main__":` block in `csv_to_sql.py` or call `sql_generator_main` separately for this file.

    Example to generate `dbdoor` (already configured in the script's `if __name__ == "__main__"` block):
    ```bash
    python src/Data_Creator/csv_to_sql.py
    ```
    Adapt or re-run the script or its `sql_generator_main` function for `dbKitchen.csv`:
    ```python
    # In csv_to_sql.py, you might have:
    # sql_generator_main("src/Data_Creator/dbKitchen.csv", "src/data/kitchen_main_db")
    ```

### ▶️ Run the Application



👨‍💻 Author
Claudio Ariza
GitHub: claudioAB-dev
Email: clarba156@gmail.com
Made with ❤️ and 🐍 by developers for designers.
