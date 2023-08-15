import re
import tldextract
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import ssl
import socket


def no_of_dots(url):
    # Check for the number of dots in URL
    if url.count(".") >= 4:
        return 1
    else:
        return 0


def specialSymbol(url):
    # Check for '@' symbol in URL
    if "@" in url:
        return 1
    else:
        return 0


def lengthOfURL(url):
    # Check for length of URL
    if len(url) >= 74:
        return 1
    else:
        return 0


def suspiciousWords(url):
    # List of suspicious keywords
    keywords = [
        "security",
        "login",
        "signin",
        "bank",
        "account",
        "update",
        "include",
        "webs",
        "online",
    ]

    # Check for presence of the above keywords in URL
    for keyword in keywords:
        if keyword in url.lower():
            return 1
        else:
            return 0


def prefixSuffix(url):
    if "-" in urlparse(url).netloc:
        return 1
    else:
        return 0


def countOfHttp(url):
    if url.count("http") > 1:
        return 1
    else:
        return 0


# listing shortening services
shortening_services = (
    r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|"
    r"yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|"
    r"short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|"
    r"doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|db\.tt|"
    r"qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|"
    r"po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|"
    r"prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|"
    r"tr\.im|link\.zip\.net"
)


# Checking for Shortening Services in URL (Tiny_URL)
def shorteningService(url):
    match = re.search(shortening_services, url)
    if match:
        return 1
    else:
        return 0


def has_data_uri(url):
    try:
        # Retrieve the website's HTML content
        response = requests.get(url)
        html_content = response.text

        # Use a regular expression to search for data URIs
        pattern = re.compile(r"data:[^;]+;base64,")
        data_uris = pattern.findall(html_content)

        # Print out the data URIs found
        if data_uris:
            return 1
        else:
            return 0
    except:
        return 1


def check_ssl_certificate(url):
    try:
        hostname = url.split("//")[1].split("/")[0]
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                if cert:
                    return 0
                else:
                    return 1
    except Exception:
        return 1


def get_dom_tree(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content of the response using BeautifulSoup
    dom_tree = BeautifulSoup(response.content, "html.parser")

    # Return the DOM tree as a BeautifulSoup object
    return dom_tree


def fake_login_form(url):

    try:
        dom_tree = get_dom_tree(url)

        # Initialize the output variable F9 to 0
        res = 0

        # Get all the form tags in the DOM tree
        forms = dom_tree.find_all("form")

        # Loop through each form tag
        for form in forms:
            # Get the value of the action attribute
            action = form.get("action")

            # If the action attribute is blank, # or javascript:void(0)), set F9 to 1
            if not action or action == "#" or action == "javascript:void(0)":
                res = 1
            # If the action attribute is in the form of "filename.php", set F9 to 1
            elif ".php" in action:
                res = 1
            # If the action attribute contains a foreign base domain, set F9 to 1 and break the loop
            elif "://" in action and not action.startswith(url):
                res = 1
                break

        # Return the output variable F9
        return res
    except:
        return 1


def countPages(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all(["img", "script", "frame", "input", "link"])
        links += soup.find_all("a", href=True)
        page_count = len(links)
        return page_count
    except:
        return 100


def missingHyperlink(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)

        if len(links) > 0:
            return 0
        else:
            return 1
    except:
        return 1


def count_foreign_links(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)
        foreign_links = 0
        for link in links:
            parsed_link = urlparse(link["href"])
            if parsed_link.netloc != "" and parsed_link.netloc != urlparse(url).netloc:
                foreign_links += 1
        total_links = len(links)
        ratio = foreign_links / total_links
        return int(ratio > 0.5)
    except:
        return 1


def count_empty_links(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a")
        empty_links = []
        for link in links:
            href = link.get("href")
            if href in ["#", "#content", "JavaScript::void(0)"]:
                empty_links.append(link)

        ratio = len(empty_links) / len(links)
        if ratio > 0.34:
            return 1
        else:
            return 0
    except:
        return 1


def count_error_links(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a")
        error_links = []
        for link in links:
            try:
                response = requests.get(link.get("href"))
                if response.status_code in [403, 404]:
                    error_links.append(link)

            except requests.exceptions.RequestException as e:
                error_links.append(link)

        ratio = len(error_links) / len(links)

        if ratio > 0.3 and len(links) > 0:
            return 1
        else:
            return 0

    except:
        return 1


def count_redirection_links(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a")
        redirection_links = []
        for link in links:
            response = requests.get(link.get("href"))
            if response.status_code in [301, 302]:
                redirection_links.append(link)

        ratio = len(redirection_links) / len(links)

        if ratio > 0.3:
            return 1
        else:
            return 0
    except:
        return 1


def has_foreign_css(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        css_links = soup.find_all("link", rel="stylesheet")
        for css_link in css_links:
            href = css_link.get("href")
            if href.startswith("http") and not href.startswith(url):
                return 1
        return 0

    except:
        return 1


def check_favicon(url):
    try:
        # extract domain from url
        domain = urlparse(url).netloc

        # send GET request to fetch page content
        response = requests.get(url)

        # parse page content using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # extract favicon link from page
        favicon_link = soup.find("link", rel="shortcut icon")

        # check if favicon link is present and get its href value
        if favicon_link is not None:
            favicon_href = favicon_link.get("href")
        else:
            # if favicon link is not present, assume it is the default favicon
            favicon_href = "/favicon.ico"

        # send GET request to fetch favicon
        favicon_url = domain + favicon_href
        response = requests.get("http://" + favicon_url)

        # check if favicon belongs to same domain as website
        if urlparse(response.url).netloc == domain:
            return 0
        else:
            return 1

    except:
        return 1


def google_index(url):
    try:
        google = "https://www.google.com/search?q=site:" + url + "&hl=en"
        response = requests.get(google, cookies={"CONSENT": "YES+1"})
        soup = BeautifulSoup(response.content, "html.parser")
        not_indexed = re.compile("did not match any documents")

        if soup(text=not_indexed):
            return 1
        else:
            return 0
    except:
        return 1


def httpDomain(url):
    domain = urlparse(url).netloc
    if "https" in domain:
        return 1
    else:
        return 0


def extractFeatures(url, label):
    features = []

    features.append(no_of_dots(url))
    features.append(specialSymbol(url))
    features.append(lengthOfURL(url))
    features.append(suspiciousWords(url))
    features.append(prefixSuffix(url))
    features.append(countOfHttp(url))
    features.append(shorteningService(url))
    features.append(has_data_uri(url))
    features.append(check_ssl_certificate(url))
    features.append(fake_login_form(url))
    features.append(countPages(url))
    features.append(missingHyperlink(url))
    features.append(count_foreign_links(url))
    features.append(count_empty_links(url))
    features.append(count_error_links(url))
    features.append(count_redirection_links(url))
    features.append(has_foreign_css(url))
    features.append(check_favicon(url))
    features.append(google_index(url))
    features.append(httpDomain(url))
    features.append(label)

    return features


print(extractFeatures("http://www.googleapis.com", 0))
