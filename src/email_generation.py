import re, json
from src.read_emails import ReadEmails
from src.genai_client import GenAIClient

class EmailGenerator:
    def __init__(self) -> None:
        ''' 
        CONSTANTS
        '''      
        self.READ_EMAIL = True
        self.OPENAI = True
        self.personal_email = ""

        with open("data/rubric.txt", "r") as file:
            self.GRADING_RUBRIC = file.read()
        
        with open("data/backend_input.json", "r") as file:
            self.BACKEND = json.load(file)

        with open("data/fit_score.txt", "r") as file:
            self.FIT_SCORE_RUBRIC = file.read()

    def read_email(self):
        if self.READ_EMAIL:
            read_mail = ReadEmails()
            read_mail.read_email()

    def call_genai_client(self, prompt, description):
        client = GenAIClient()
        email = client.get_completions_openai(prompt, description)
        return email

    def generate_email_response(self):
        self.read_email()
        self.score_emails()
        self.create_email_response()
        return self.email_responses, self.scores

    def create_email_response(self):
        with open('data/emails.json') as f:
            emails = json.load(f)
        description = "You are a venture capitalist who gives advice to startups regarding market research, and cold emailing for support"
        prompt = "This is your company info: " + json.dumps(self.BACKEND) + "These are your emails: " + json.dumps(emails) + ". NEXT, take these scores: " + self.scores + ". Based on these scores, write a response to each email in order of highest score to lowest. VERY IMPORTANT: Give results in the format: 'STARTMAIL Company Name: 5 sentence thorough response ENDMAIL'. Do not include any other information in your response."
        self.email_responses = self.call_genai_client(prompt, description)

    def score_emails(self):
        with open('data/emails.json') as f:
            emails = json.load(f)
        description = "You are a venture capitalist who gives advice to startups regarding market research, and cold emailing for support"
        prompt = "This is your company info: " + json.dumps(self.BACKEND) + "These are your emails: " + json.dumps(emails) + "\n\nNEXT, here is your rubric: " + self.GRADING_RUBRIC + "\n\nTHEN, score each of the emails based on the rubric. VERY IMPORTANT: Give results in the format: 'STARTSCORE Company Name: Score with 2-sentence reasoning'. Do not include any other information in your response."
        self.scores = self.call_genai_client(prompt, description)

    def market_research(self):
        description = "You are a market researcher at a startup that is looking for companies to sell your product to."
        prompt = "This is your company info: " + json.dumps(self.BACKEND) + ". Do research on the internet to find companies that would benefit from using your product. Provide a list of 10 companies with a brief description of each. Use the following rubric to determine a fit score for each: " + self.FIT_SCORE_RUBRIC + " Also, give the following information for the company on different lines: CEO of company, email of CEO, sector/industry of the company, annual revenue, and approximate number of employees, location. THEN, VERY IMPORTANT: Give results in the format: 'STARTRESEARCH Company Name: CEO NAME: CEO EMAIL: Company Sector: Annual Revenue: Employee Count: Location: Score: Brief description'. Do not include any other information in your response and ensure each is on a new line."
        self.companies = self.call_genai_client(prompt, description)
        return self.companies

    def generate_emails(self):
        description = "You are the CEO at a startup that is looking to sell their product to companies."
        prompt = "This is your company info: " + json.dumps(self.BACKEND) + ". These are the companies you found: " + self.companies + ". NEXT, write a cold email to each company. VERY IMPORTANT: Give results in a formal letter format: 'STARTMAIL Company Name CEO Name (5-10 sentence extremely thorough and personalized for the company cold email)'. Do not include any other information in your response."
        self.generated_emails = self.call_genai_client(prompt, description)
        return self.generated_emails
    
    def generate_rec_and_email(self):
        raw_companies = self.market_research()
        companies = re.split(r'STARTRESEARCH ', raw_companies)[1:]
        raw_emails = self.generate_emails()
        emails = re.split(r'STARTMAIL ', raw_emails)[1:]
        reccomendation_data = [{"company": company, "email": email} for company, email in zip(companies, emails)]

        with open("data/backend_output.json", "w") as file:
            json.dump(reccomendation_data, file, indent=4)

    def generate_metrics(self):
        pass

if __name__ == '__main__':
    # Create a new email generator
    email_generator = EmailGenerator()
    # Generate a cold email
    email_generator.generate_rec_and_email()