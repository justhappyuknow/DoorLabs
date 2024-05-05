import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import openai

# Set up Google Sheets API credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/justhappyuknow/Desktop/internship/internship-422407-2130a52c1836.json', scope)
client = gspread.authorize(creds)

# Set up OpenAI API credentials
openai.api_key = ''

# Open the Google Sheet
sheet = client.open('project1').sheet1

# Scrape and clean company homepage data
def scrape_and_clean(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove unwanted elements (e.g., headers, footers, navigation)
    for element in soup(['header', 'footer', 'nav']):
        element.decompose()

    # Get the main content area
    main_content = soup.find('main') or soup.find('div', {'role': 'main'}) or soup.find('body')

    # If main content area is not found, use the entire page content
    if main_content is None:
        main_content = soup

    # Clean and format the text
    cleaned_text = ' '.join(main_content.get_text().split())

    return cleaned_text
# Function to run OpenAI prompts
import openai

def run_prompts(company_data):
    prompt1 = """Here's the raw homepage information of my target company.
I need you to convert this into a 200 word summary that is organized in the following manner:
- Company overview
- Product and service offering recap
- Potential target industries for this company
- What is their core USP
- How many times have they used the word "AI" in their homepage.

Here's the homepage information:
{}"""

    prompt2 = """I will give you the company overview of a target company I'm trying to pitch to.
Can you read through their offering and create a potential sales opportunity for me?

My company offers custom HR training and modules

Your potential sales opportunity analysis should be 150 words
It should have multiple bullet points and tell me how I can posit my solution
Ensure it is highly custom built and includes the target companies industry terminology

Here's the summary:
{}"""

    prompt3 = """I will give you a potential sales opportunity analysis for a company I'm targeting
You have to create a custom 100 word sales email
The email has to look at elements about what the company offers from ###Company overview### and should include potential sales hooks from ###sales opportunity analysis###
Keep the text extremely human and to the point.

###Company overview###
{}

###sales opportunity analysis###
{}"""

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt1.format(company_data)}
    ]

    prompt1_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
    )
    prompt1_output = prompt1_response.choices[0].message.content

    messages.append({"role": "user", "content": prompt2.format(prompt1_output)})
    prompt2_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
    )
    prompt2_output = prompt2_response.choices[0].message.content

    messages.append({"role": "user", "content": prompt3.format(prompt1_output, prompt2_output)})
    prompt3_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
    )
    prompt3_output = prompt3_response.choices[0].message.content

    return prompt1_output, prompt2_output, prompt3_output
# Iterate through each company
row = 2  # Start from row 2 (row 1 is the header)
for company_name, company_url in zip(sheet.col_values(1)[1:], sheet.col_values(2)[1:]):
    cleaned_data = scrape_and_clean(company_url)
    sheet.update_cell(row, 3, cleaned_data)  # Update Column C with cleaned data
    
    prompt1_output, prompt2_output, prompt3_output = run_prompts(cleaned_data)
    
    sheet.update_cell(row, 4, prompt1_output)  # Update Column D with Prompt 1 output
    sheet.update_cell(row, 5, prompt2_output)  # Update Column E with Prompt 2 output
    sheet.update_cell(row, 6, prompt3_output)  # Update Column F with Prompt 3 output
    
    row += 1

print('Task completed successfully!')