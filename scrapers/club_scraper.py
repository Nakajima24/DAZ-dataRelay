import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import json
import time
import random

def scrape_and_categorize_clubs(url):
    """
    Scrape and categorize club data including:
    - Public email (non-fhda.edu)
    - Officers' emails (fhda.edu)
    - Basic club information
    Returns categorized dictionary of clubs
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Random delay to prevent blocking
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        categorized_clubs = defaultdict(list)
        club_cards = soup.find_all('div', class_='club-card')
        
        for card in club_cards:
            # Extract category from class attributes
            classes = card.get('class', [])
            category = next(
                (c.split('c-')[-1] for c in classes if c.startswith('c-')),
                'Uncategorized'
            )
            
            # Extract all club data
            club_data = {
                'title': extract_h3_title(card),
                'description': extract_description(card),
                'public_email': extract_public_email(card),
                'officers': extract_officers_info(card),
                'websites': extract_websites(card)
            }
            
            categorized_clubs[category].append(club_data)
        
        return dict(categorized_clubs)
    
    except Exception as e:
        print(f"Scraping failed: {e}")
        return None

def extract_h3_title(element):
    """Extract text from <h3> tag excluding pull-right content"""
    h3_tag = element.find('h3')
    if not h3_tag:
        return 'N/A'
    
    # Remove unwanted elements
    for unwanted in h3_tag.find_all(class_='pull-right'):
        unwanted.decompose()
    
    return h3_tag.get_text(strip=True)

def extract_description(element):
    """Extract club description"""
    desc = element.find('div', class_='club-card-description')
    return desc.text.strip() if desc else 'N/A'

def extract_public_email(element):
    """
    Extract public email (non-fhda.edu) from envelope icon
    Locates: <i class="far fa-envelope mr-1 fa-fw"> followed by email
    """
    email_tag = element.find('a', href=lambda x: x and 'mailto:' in x)
    return email_tag['href'].replace('mailto:', '') if email_tag else 'N/A'

def extract_officers_info(element):
    """Extract all officers' info (name, email, phone), each from their own contact section"""
    officers = []
    
    # Find ALL contact sections (each officer has their own p.club-contact)
    contact_sections = element.find_all('p', class_='mb-3 pl-2 club-contact')
    
    if not contact_sections:
        return [{'name': 'N/A', 'email': 'N/A', 'phone': 'N/A'}]
    
    for contact_section in contact_sections:
        officer_data = {
            'name': 'N/A',
            'email': 'N/A',
            'phone': 'N/A'
        }
        
        # Extract name (from <strong> tag)
        name_tag = contact_section.find('strong')
        if name_tag:
            officer_data['name'] = ' '.join(name_tag.get_text().split())
        
        # Extract email (from mailto link)
        email_tag = contact_section.find('a', href=lambda href: href and 'mailto:' in href)
        if email_tag:
            email = email_tag['href'].replace('mailto:', '').strip()
            if email.endswith(('fhda.edu', 'deanza.edu')):
                officer_data['email'] = email
        
        # Extract phone (look for "408" in text)
        phone_text = contact_section.find(string=lambda text: '408' in str(text))
        if phone_text:
            officer_data['phone'] = phone_text.strip()
        
        officers.append(officer_data)
    
    return officers if officers else [{'name': 'N/A', 'email': 'N/A', 'phone': 'N/A'}]

def extract_websites(element):
    """Extract all website URLs"""
    websites = element.find_all('a', href=lambda x: x and x.startswith('http') and 'mailto:' not in x)
    return [site['href'] for site in websites] if websites else ['N/A']

def save_to_json(data, filename='clubs_by_category.json'):
    """Save data to JSON file with proper formatting"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    URL = "https://www.deanza.edu/clubs/club-list.html"
    
    print("Starting club data scraping...")
    clubs_data = scrape_and_categorize_clubs(URL)
    
    if clubs_data:
        save_to_json(clubs_data)
        print(f"Successfully saved data. Found {len(clubs_data)} categories.")
        
        # Print summary statistics
        for category, clubs in clubs_data.items():
            print(f"\n[{category}] {len(clubs)} clubs")
            print("First club example:")
            club = clubs[0]
            print(f"Name: {club['title']}")
            print(f"Public Email: {club['public_email']}")
            print(f"Officers: {len(club['officers'])} found")
            for i, officer in enumerate(club['officers'][:3], 1):
                print(f"  {i}. {officer['name']} ({officer['email']})")
    else:
        print("Scraping failed. Please check the website structure or network connection.")