# Web Scraper Project

## 📝 Description
This project is a **full-stack web scraper** built using Python. It allows users to scrape data from any website URL, extract specific details like **emails**, **phone numbers**, **social links**, and other information, and store the scraped data in a **local SQLite database**. The project also includes a **Flask-based web interface** for easy interaction and data visualization.

---

## 🚀 Features
- **Scrape Data**: Extract emails, phone numbers, social links, headers, images, and more from any website.
- **Database Storage**: Store scraped data in a SQLite database with a structured schema.
- **Web Interface**: A user-friendly web UI built with Flask and Bootstrap for interacting with the scraper.
- **Logging**: Logs all scrape attempts (success/failure) for debugging and tracking.
- **Export Data**: Export scraped data as CSV for further analysis.

---

## 🛠️ Technologies Used
- **Python**: Core programming language.
- **Flask**: Web framework for the UI.
- **Bootstrap**: Frontend styling for the web interface.
- **BeautifulSoup**: HTML parsing for web scraping.
- **SQLite**: Local database for storing scraped data.
- **Requests**: HTTP requests to fetch website content.
- **Selenium**: For scraping dynamic websites (if needed).
- **Pandas**: Data manipulation and CSV export.

---

## 📂 Project Structure
```
WebScraperProject/
├── app.py                  # Flask application for the web interface
├── scraper.py              # Core web scraping logic
├── database.py             # Database operations (SQLite)
├── requirements.txt        # List of dependencies
├── README.md               # Project documentation
├── templates/              # Flask HTML templates
│   └── index.html          # Main UI template
└── static/                 # Static files (CSS, JS, etc.)
    └── styles.css          # Custom CSS for the UI
```

---

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.6 or higher
- Pip (Python package manager)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/web-scraper-project.git
   cd web-scraper-project
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask application:
   ```bash
   python app.py
   ```

5. Open your browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

---

## 🖥️ Usage
1. **Enter a URL**: On the homepage, enter the URL of the website you want to scrape.
2. **Scrape Data**: Click the "Scrape" button to start scraping. The data will be saved in the database.
3. **View Data**: The scraped data will be displayed in a table on the homepage.
4. **Export Data**: Use the "Export Data as CSV" button to download the scraped data.

---

## 📊 Database Schema
The project uses two tables to store data:

### `scraped_data`
| Column Name      | Data Type | Description                          |
|------------------|-----------|--------------------------------------|
| id               | INTEGER   | Primary key (auto-increment)         |
| url              | TEXT      | URL of the scraped website           |
| emails           | TEXT      | Extracted emails (JSON array)        |
| phone_numbers    | TEXT      | Extracted phone numbers (JSON array) |
| social_links     | TEXT      | Extracted social links (JSON array)  |
| meta_info        | TEXT      | Meta information (JSON object)       |
| headers          | TEXT      | Headers (JSON object)                |
| main_content     | TEXT      | Main content (JSON array)            |
| contact_info     | TEXT      | Contact information (JSON object)    |
| images           | TEXT      | Extracted images (JSON array)        |
| links            | TEXT      | Extracted links (JSON array)         |
| scrape_date      | TIMESTAMP | Timestamp of the scrape              |
| last_updated     | TIMESTAMP | Timestamp of the last update         |

### `scrape_history`
| Column Name      | Data Type | Description                          |
|------------------|-----------|--------------------------------------|
| id               | INTEGER   | Primary key (auto-increment)         |
| url              | TEXT      | URL of the scraped website           |
| scrape_date      | TIMESTAMP | Timestamp of the scrape attempt      |
| status           | TEXT      | Status of the scrape (e.g., success) |
| error_message    | TEXT      | Error message (if any)               |

---

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments
- Thanks to the developers of **BeautifulSoup**, **Flask**, and **Bootstrap** for their amazing libraries.
- Inspired by the need for a simple yet powerful web scraping tool.

---

## 📧 Contact
For questions or feedback, feel free to reach out:
- **Muhammad usman**: [usman853136@gmail.com](mailto:usman853136@gmail.com)
- **GitHub**: [MY GitHub Profile](https://github.com/UsmanMERN)

---

Enjoy using the Web Scraper! 🚀
```