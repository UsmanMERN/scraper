# app.py
from flask import Flask, render_template, request, jsonify, flash
from scraper import WebScraper
from database import Database
import validators
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this in production

@app.route('/', methods=['GET', 'POST'])
def index():
    db = Database()
    
    if request.method == 'POST':
        url = request.form.get('url')
        
        if not validators.url(url):
            flash('Please enter a valid URL', 'danger')
            return render_template('index.html', data=db.fetch_all_data())

        try:
            scraper = WebScraper(url)
            data = scraper.extract_all_data()
            
            if db.fetch_data(url):
                db.update_data(url, data)
                db.log_scrape_attempt(url, 'updated')
                flash(f'Data updated for {url}', 'success')
            else:
                db.insert_data(data)
                db.log_scrape_attempt(url, 'inserted')
                flash(f'Data inserted for {url}', 'success')
                
        except Exception as e:
            db.log_scrape_attempt(url, 'error', str(e))
            flash(f'Error scraping {url}: {str(e)}', 'danger')

    data = db.fetch_all_data()
    db.close()
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)