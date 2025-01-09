# app.py
from flask import Flask, render_template, request, jsonify, flash
from scraper import WebScraper
from database import Database
import validators
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this in production

@app.route('/', methods=['GET', 'POST'])
def index():
    db = Database()
    data = []
    product_data = []
    
    try:
        if request.method == 'POST':
            url = request.form.get('url')
            scrape_type = request.form.get('scrape_type', 'general')
            
            logger.debug(f"Received request - URL: {url}, Type: {scrape_type}")
            
            if not validators.url(url):
                flash('Please enter a valid URL', 'danger')
                return render_template('index.html', data=[], product_data=[])

            try:
                scraper = WebScraper(url, scrape_type)
                
                if scrape_type == "products":
                    logger.debug("Extracting product data...")
                    scraped_data = scraper.extract_product_data()
                    
                    if scraped_data and scraped_data.get("products"):
                        if db.fetch_product_data(url):
                            db.update_product_data(url, scraped_data)
                            flash(f'Product data updated for {url}', 'success')
                        else:
                            db.insert_product_data(scraped_data)
                            flash(f'Product data inserted for {url}', 'success')
                    else:
                        flash('No product data found on the page', 'warning')
                
                else:
                    logger.debug("Extracting general data...")
                    scraped_data = scraper.extract_all_data()
                    
                    if scraped_data:
                        if db.fetch_data(url):
                            db.update_data(url, scraped_data)
                            flash(f'Data updated for {url}', 'success')
                        else:
                            db.insert_data(scraped_data)
                            flash(f'Data inserted for {url}', 'success')
                    else:
                        flash('No data found on the page', 'warning')
                
                db.log_scrape_attempt(url, 'success')
                
            except Exception as e:
                logger.error(f"Scraping error: {str(e)}", exc_info=True)
                db.log_scrape_attempt(url, 'error', str(e))
                flash(f'Error scraping {url}: {str(e)}', 'danger')

        # Fetch all data
        logger.debug("Fetching all data from database...")
        data = db.fetch_all_data() or []
        product_data = db.fetch_all_product_data() or []
        
        logger.debug(f"Found {len(data)} general records and {len(product_data)} product records")
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        flash(f'Application error: {str(e)}', 'danger')
    finally:
        db.close()

    return render_template('index.html', 
                         data=data, 
                         product_data=product_data,
                         debug_info={
                             'general_count': len(data),
                             'product_count': len(product_data)
                         })

@app.route('/debug-info')
def debug_info():
    """Endpoint for checking database content"""
    db = Database()
    try:
        general_data = db.fetch_all_data()
        product_data = db.fetch_all_product_data()
        return jsonify({
            'general_data_count': len(general_data) if general_data else 0,
            'product_data_count': len(product_data) if product_data else 0,
            'general_data_sample': general_data[0] if general_data else None,
            'product_data_sample': product_data[0] if product_data else None
        })
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)