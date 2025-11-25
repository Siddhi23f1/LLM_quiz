import os
import time
import base64
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import anthropic

class QuizSolver:
    def __init__(self, email, secret):
        self.email = email
        self.secret = secret
        self.client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        
    def get_browser(self):
        """Initialize headless Chrome browser"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(options=chrome_options)
    
    def fetch_quiz_content(self, url):
        """Fetch and render quiz page content"""
        driver = self.get_browser()
        try:
            driver.get(url)
            # Wait for JavaScript execution
            time.sleep(2)
            
            # Get rendered HTML
            html_content = driver.page_source
            
            # Try to get specific result element
            try:
                result = driver.find_element(By.ID, 'result')
                text_content = result.text
            except:
                text_content = driver.find_element(By.TAG_NAME, 'body').text
            
            return text_content, html_content
        finally:
            driver.quit()
    
    def solve_with_claude(self, question, context=""):
        """Use Claude to solve the quiz question"""
        prompt = f"""You are solving a data analysis quiz. 
        
Question:
{question}

{f"Additional context: {context}" if context else ""}

Analyze the question carefully and provide:
1. What type of task this is (data sourcing, analysis, visualization, etc.)
2. Step-by-step solution approach
3. The final answer in the exact format requested

If the question asks for a number, return just the number.
If it asks for a file, indicate what type of file needs to be created.
If it asks for a JSON object, provide the exact JSON structure.

Be precise and follow instructions exactly."""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    
    def download_file(self, url):
        """Download file from URL"""
        response = requests.get(url)
        return response.content
    
    def submit_answer(self, submit_url, answer):
        """Submit answer to the quiz endpoint"""
        payload = {
            "email": self.email,
            "secret": self.secret,
            "url": submit_url,
            "answer": answer
        }
        
        response = requests.post(submit_url, json=payload)
        return response.json()
    
    def solve_quiz_chain(self, initial_url):
        """Solve a chain of quiz questions"""
        current_url = initial_url
        start_time = time.time()
        max_time = 180  # 3 minutes
        
        while current_url and (time.time() - start_time) < max_time:
            print(f"Solving quiz at: {current_url}")
            
            # Fetch quiz content
            text_content, html_content = self.fetch_quiz_content(current_url)
            
            # Parse to find submit URL and question
            # This is simplified - you'd need to parse the actual structure
            lines = text_content.split('\n')
            
            submit_url = None
            for line in lines:
                if 'submit' in line.lower() and 'http' in line:
                    # Extract URL
                    import re
                    urls = re.findall(r'https?://[^\s<>"]+', line)
                    if urls:
                        submit_url = urls[0]
                        break
            
            # Use Claude to solve
            solution = self.solve_with_claude(text_content)
            
            print(f"Claude's solution: {solution}")
            
            # Extract answer from solution (simplified)
            # You'd need more sophisticated parsing
            answer = self.parse_answer(solution, text_content)
            
            # Submit answer
            if submit_url:
                result = self.submit_answer(submit_url, answer)
                print(f"Submission result: {result}")
                
                if result.get('correct'):
                    print("✓ Answer correct!")
                    current_url = result.get('url')
                else:
                    print(f"✗ Answer incorrect: {result.get('reason')}")
                    # Retry or move to next URL if provided
                    current_url = result.get('url')
            else:
                print("Could not find submit URL")
                break
        
        print("Quiz chain completed or timeout reached")
    
    def parse_answer(self, solution, question):
        """Parse the answer from Claude's solution"""
        # This is highly simplified
        # You need to handle different answer types:
        # - numbers
        # - strings
        # - booleans
        # - base64 files
        # - JSON objects
        
        # Try to extract number
        import re
        numbers = re.findall(r'\d+', solution)
        if numbers:
            return int(numbers[-1])
        
        return solution.strip()
