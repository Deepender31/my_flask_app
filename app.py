from flask import Flask, render_template, request, jsonify , make_response
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from io import BytesIO
import os
import time
from collections import Counter
from datetime import datetime
import re  # For salary parsing
import json  # For sending structured data to the frontend

app = Flask(__name__)

def get_chrome_driver():
    # Setup Chrome WebDriver using WebDriver Manager
    options = Options()
    #options.add_argument('--headless')  # Run Chrome in headless mode (without GUI)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Minimize the window
    driver.set_window_position(-2000, 0)  # Move the window out of view
    
    return driver

# Function to fetch all job details from a given job link
def fetch_job_details(driver, link):
    driver.execute_script(f"window.open('{link}', '_blank');")
    
    jd_content, key_skills_str, role, industry_type, department, employment_type, role_category, education = "", "", "", "", "", "", "", ""
    
    # Switch to the new tab
    driver.switch_to.window(driver.window_handles[-1])
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'section.styles_job-desc-container__txpYf'))) # Wait for the job description page to load
    except Exception as e:
        driver.close()
        try:
    # Switch back to the first tab
            driver.switch_to.window(driver.window_handles[0])
    
    # Wait until the page is fully loaded (adjust the condition based on the page)
            WebDriverWait(driver, 10).until(
                 EC.presence_of_element_located((By.CSS_SELECTOR, '.cust-job-tuple.layout-wrapper'))
            )
        except Exception as e:
            print(f"Failed to switch back to the previous page: {str(e)}")
        print('Error In fetching JD {e}')
        return{
        'description': jd_content,
        'key_skills': key_skills_str,
        'role': role,
        'industry_type': industry_type,
        'department': department,
        'employment_type': employment_type,
        'role_category': role_category,
        'education': education
    }
        
    # Initialize variables to store data
    jd_content, key_skills_str, role, industry_type, department, employment_type, role_category, education = "", "", "", "", "", "", "", ""
    
    try:
        # Locate and extract the job description
        jd_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'section.styles_job-desc-container__txpYf'))
        )
        jd_content = jd_element.find_element(By.CSS_SELECTOR, 'div.styles_JDC__dang-inner-html__h0K4t').text
    except Exception as e:
        print(f"Failed to fetch job description:")
    
    try:
        # Locate the key skills section and extract all key skills
        key_skills_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.styles_key-skill__GIPn_'))
        )
        key_skills = key_skills_element.find_elements(By.CSS_SELECTOR, 'a > span')
        key_skills_text = [skill.text for skill in key_skills]
        key_skills_str = ', '.join(key_skills_text)
    except Exception as e:
        print(f"Failed to fetch key skills:")
    
    try:
        # Extract role information
        role_element = driver.find_element(By.CSS_SELECTOR, '#root > div > main > div.styles_jdc__content__EZJMQ > div.styles_left-section-container__btAcB > section.styles_job-desc-container__txpYf > div:nth-child(2) > div.styles_other-details__oEN4O > div:nth-child(1) > span > a')
        role = role_element.text
    except Exception as e:
        print(f"Failed to fetch role")
    
    try:
        # Extract industry type information
        industry_element = driver.find_element(By.CSS_SELECTOR, '#root > div > main > div.styles_jdc__content__EZJMQ > div.styles_left-section-container__btAcB > section.styles_job-desc-container__txpYf > div:nth-child(2) > div.styles_other-details__oEN4O > div:nth-child(2) > span > a')
        industry_type = industry_element.text
    except Exception as e:
        print(f"Failed to fetch industry type")
    
    try:
        # Extract department information
        department_element = driver.find_element(By.CSS_SELECTOR, '#root > div > main > div.styles_jdc__content__EZJMQ > div.styles_left-section-container__btAcB > section.styles_job-desc-container__txpYf > div:nth-child(2) > div.styles_other-details__oEN4O > div:nth-child(3) > span > a')
        department = department_element.text
    except Exception as e:
        print(f"Failed to fetch department")
    
    try:
        # Extract employment type information
        employment_type_element = driver.find_element(By.CSS_SELECTOR, '#root > div > main > div.styles_jdc__content__EZJMQ > div.styles_left-section-container__btAcB > section.styles_job-desc-container__txpYf > div:nth-child(2) > div.styles_other-details__oEN4O > div:nth-child(4) > span > span')
        employment_type = employment_type_element.text
    except Exception as e:
        print(f"Failed to fetch employment type")
    
    try:
        # Extract role category information
        role_category_element = driver.find_element(By.CSS_SELECTOR, '#root > div > main > div.styles_jdc__content__EZJMQ > div.styles_left-section-container__btAcB > section.styles_job-desc-container__txpYf > div:nth-child(2) > div.styles_other-details__oEN4O > div:nth-child(5) > span')
        role_category = role_category_element.text
    except Exception as e:
        print(f"Failed to fetch role category:")
    
    try:
        # Extract education information
        education_element = driver.find_element(By.CSS_SELECTOR, '#root > div > main > div.styles_jdc__content__EZJMQ > div.styles_left-section-container__btAcB > section.styles_job-desc-container__txpYf > div:nth-child(2) > div.styles_education__KXFkO > div:nth-child(2) > span')
        education = education_element.text
    except Exception as e:
        print(f"Failed to fetch education")

    # Go back to the previous page
    driver.close()
    try:
    # Switch back to the first tab
        driver.switch_to.window(driver.window_handles[0])
    
    # Wait until the page is fully loaded (adjust the condition based on the page)
        WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.cust-job-tuple.layout-wrapper'))
    )
    except Exception as e:
        print(f"Failed to switch back to the previous page: {str(e)}")
    
    return {
        'description': jd_content,
        'key_skills': key_skills_str,
        'role': role,
        'industry_type': industry_type,
        'department': department,
        'employment_type': employment_type,
        'role_category': role_category,
        'education': education
    }


# Function to extract job listings from a search results page
def extract_jobs_from_page(driver):
    job_cards = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.cust-job-tuple.layout-wrapper'))
    )
    jobs = []
    for card in job_cards:
        try:
            job_title = card.find_element(By.CSS_SELECTOR, '.title').text
        except Exception as e:
            job_title = "Job title not found"
        
        try:
            company_name = card.find_element(By.CSS_SELECTOR, '.comp-name').text
        except Exception as e:
            company_name = "Company name not found"
        
        try:
            experience = card.find_element(By.CSS_SELECTOR, '.exp').text
        except Exception as e:
            experience = "Experience not found"
        
        try:
            location = card.find_element(By.CSS_SELECTOR, '.loc').text
        except Exception as e:
            location = "Location not found"
        
        try:
            salary = card.find_element(By.CSS_SELECTOR, '.sal').text
        except Exception as e:
            salary = "Salary not found"
        
        try:
            job_link = card.find_element(By.CSS_SELECTOR, '.title').get_attribute('href')
        except Exception as e:
            job_link = "Link not found"
        
        job_details = {
            'title': job_title,
            'company': company_name,
            'experience': experience,
            'location': location,
            'salary': salary,
            'link': job_link
        }
        jobs.append(job_details)
    
    return jobs


@app.route('/')
def index():
    return render_template('index.html')

# Route to scrape job data
@app.route('/scrape', methods=['POST'])
def scrape():
    skill = request.form['skill']
    sort_by = request.form['sort']
    pages_nums=int(int(request.form['num_jobs'])/20)
    
    # Set up WebDriver and open Naukri.com
    driver = get_chrome_driver()
    all_jobs = []
    all_skills = []
    all_locations = []
    all_industries = []
    all_salaries = []


    try:
        driver.get('https://www.naukri.com')
        print("Page title is:", driver.title)
    except Exception as e:
        print(f"Error accessing the page: {str(e)}")
        driver.quit()
        return jsonify({'status': 'error', 'message':"Error "})
    
    try:
        # Search for the job title or skill
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter skills / designations / companies"]'))
        )
        search_box.send_keys(skill)
        
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="qsbSubmit"]'))
        )
        search_button.click()
         
        # Handle sorting based on the selected option
        sort_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'filter-sort'))
        )
        sort_button.click()

        if sort_by == "Date":
            # Select "Date" option
            date_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//li[@title="Date"]/a'))
            )
            date_option.click()
        else:
            # Default is "Relevance", so no action needed as it might be pre-selected.

            relevance_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//li[@title="Relevance"]/a'))
            )
            relevance_option.click()
        

      
        # Iterate through pages
        for page in range(1, pages_nums+1):  # Adjust the range as needed to go through more pages
            print(f"Scraping page {page}")
            
            # Extract jobs from the current page
            
            job_list = extract_jobs_from_page(driver)
            
            for job in job_list:
                link = job.get('link')
    
                if isinstance(link, str) and link.startswith(("http://", "https://")):
                    # Fetch all job details
                    job_details = fetch_job_details(driver, link)
        
                    # Append each variable separately
                    job['description'] = job_details.get('description', '')
                    job['key_skills'] = job_details.get('key_skills', '')
                    job['role'] = job_details.get('role', '')
                    job['industry_type'] = job_details.get('industry_type', '')
                    job['department'] = job_details.get('department', '')
                    job['employment_type'] = job_details.get('employment_type', '')
                    job['role_category'] = job_details.get('role_category', '')
                    job['education'] = job_details.get('education', '')
        
                    # Append the updated job to all_jobs
                    all_jobs.append(job)
        
                    # Add the key skills to the overall skill list
                    all_skills.extend(job_details.get('key_skills', '').split(', '))
                    all_locations.append(job.get('location', ''))
                    all_industries.append(job.get('industry_type', ''))
                    all_salaries.append(job.get('salary', ''))
                else:
                     print("Invalid or missing link, skipping job.")
            
            try:
                # Locate and click the "Next" button to go to the next page
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//a/span[text()="Next"]'))
                )
                next_button.click()

                # Wait for the next page to load
                time.sleep(5)
            except Exception as e:
                print(f"Failed to navigate to the next page:")
                break

        # Analyze skill frequency
        skill_count = Counter(all_skills)
        location_count = Counter(all_locations)
        industry_count = Counter(all_industries)
        most_required_skill = skill_count.most_common(1)[0]  # Get the most common skill

        salary_ranges = {
            'Less than 3 LPA': 0,
            '3-6 LPA': 0,
            '6-10 LPA': 0,
            '10-20 LPA': 0,
            'More than 20 LPA': 0,
            'Not specified': 0
        }
        salary_pattern = re.compile(r'(\d+)[KML]')
        for salary in all_salaries:
            match = salary_pattern.search(salary)
            if match:
                salary_amount = int(match.group(1))
                if 'K' in salary:
                    salary_amount /= 100
                if salary_amount < 3:
                    salary_ranges['Less than 3 LPA'] += 1
                elif salary_amount < 6:
                    salary_ranges['3-6 LPA'] += 1
                elif salary_amount < 10:
                    salary_ranges['6-10 LPA'] += 1
                elif salary_amount < 20:
                    salary_ranges['10-20 LPA'] += 1
                else:
                    salary_ranges['More than 20 LPA'] += 1
            else:
                salary_ranges['Not specified'] += 1

        # Generate a dynamic file name based on the current date and time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f'static/jobs_{timestamp}.xlsx'
        
        # Convert the jobs to a DataFrame and save as Excel
        df = pd.DataFrame(all_jobs)
        output = BytesIO()
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        # Create a response with insights and file download
        response = make_response(
            jsonify({
                'status': 'success',
                'message': 'Jobs scraped successfully',
                'most_required_skill': skill_count.most_common(1)[0][0],
                'top_skills': skill_count.most_common(5),
                'top_locations': location_count.most_common(5),
                'top_industries': industry_count.most_common(5),
                'salary_ranges': salary_ranges
            })
        )

        # Add the file as an attachment for download
        response.headers['Content-Disposition'] = f'attachment; filename=jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        return response

        
    except WebDriverException as e:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f'static/jobs_{timestamp}.xlsx'
        
        # Convert the jobs to a DataFrame and save as Excel
        df = pd.DataFrame(all_jobs)
        df.to_excel(file_name, index=False)
        print(f"WebDriverException occurred: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        driver.quit()

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if 'job_file' is in the request
    if 'job_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400

    file = request.files['job_file']

    # Validate if the file is an Excel file (MIME type check)
    if not file.filename.endswith(('.xls', '.xlsx')):
        return jsonify({'status': 'error', 'message': 'Unsupported file format. Please upload an Excel file.'}), 400

    # Save the file temporarily in a static directory
    file_path = os.path.join('static', file.filename)
    file.save(file_path)

    try:
        # Read the Excel file using pandas
        df = pd.read_excel(file_path)

        # Normalize column names (optional but recommended)
        df.columns = df.columns.str.strip().str.lower()

        # Ensure relevant columns exist in the file
        required_columns = ['title', 'company', 'experience', 'location', 'key_skills', 'industry_type', 'salary']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return jsonify({'status': 'error', 'message': f'Missing required columns: {", ".join(missing_columns)}'}), 400

        # Clean the data (removing NaN values for relevant columns)
        df = df.dropna(subset=required_columns)

        # **Step 1**: Process key_skills by splitting each row and flattening the list
        # Split each key_skills string into a list of individual skills (separated by commas)
        all_skills = df['key_skills'].str.split(',').explode().str.strip().tolist()

        # Count the occurrences of each skill
        skill_counts = Counter(all_skills)

        # Get the top 5 most common skills
        top_skills = skill_counts.most_common(5)

        # **Step 2**: Other insights like locations, industries, and companies

        # Top 5 job locations
        top_locations = df['location'].value_counts().head(5).reset_index().values.tolist()

        # Top 5 industries
        top_industries = df['industry_type'].value_counts().head(5).reset_index().values.tolist()

        # Top 5 companies by job posting
        top_companies = df['company'].value_counts().head(5).reset_index().values.tolist()

        # Average salary information (optional, depending on the salary format)
        try:
            salary_info = df['salary'].value_counts().head(5).reset_index().values.tolist()
        except:
            salary_info = "Salary information is in non-standard format."

        # Prepare the response
        response = {
            'status': 'success',
            'message': f'Jobs insights generated from {file.filename}',
            'top_locations': top_locations,
            'top_industries': top_industries,
            'top_skills': top_skills,
            'top_companies': top_companies,
            'salary_info': salary_info
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

    finally:
        # Clean up the uploaded file to avoid unnecessary storage
        if os.path.exists(file_path):
            os.remove(file_path)


if __name__ == '__main__':
    app.run(debug=True)