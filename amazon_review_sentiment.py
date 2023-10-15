from bs4 import BeautifulSoup
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

#uses compound score for vader sentiment analysis
def compute_score(sentences):
    sid_obj = SentimentIntensityAnalyzer()
    sent_dict = sid_obj.polarity_scores(sentences)
    return sent_dict['compound']
class Review:
    pos_reviews = {}
    neg_reviews = {}
    images = []
    url = ""
    prod_name = ""
    def __init__(self, url):
        self.prod_name = url.split("/")[3].replace("-", " ")
        self.asin = url.split("/")[5]
        self.url = url
        self.pos_url = "https://www.amazon.com/" + self.prod_name.replace(" ", "-") + "/product-reviews/" + self.asin + "/ref=cm_cr_arp_d_viewopt_sr?filterByStar=positive&pageNumber=1"
        self.neg_url = "https://www.amazon.com/" + self.prod_name.replace(" ", "-") + "/product-reviews/" + self.asin + "/ref=cm_cr_arp_d_viewopt_sr?filterByStar=critical&pageNumber=1"
        self.scrape(self.pos_url, True)
        self.scrape(self.neg_url, False)
    def scrape(self, url, pos):
        HEADERS = ({'User-Agent':
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                        AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/90.0.4430.212 Safari/537.36',
                    'Accept-Language': 'en-US, en;q=0.5'})
        try:
            r = requests.get(url, headers=HEADERS)
        except:
            return
        try:
            soup = BeautifulSoup(r.text, 'html.parser')
        except:
            return
        filter = ["out of 5 stars", "Learn more", "Get it", "FREE", "Best Sellers Rank", "Customer reviews", "Reviewed in", "Wish List", "Start overPage", "Top Brand indicates", "100 million songs", "Amazon.com, Inc.", "To view this video", "To calculate the overall", "Qty:", "shown at checkout", "Eligible for", " | ", "After viewing product detail pages"]
        filter_flag = False
        for item in soup.find_all('span'):
            item = item.get_text().split("\n")
            for i in item:
                i = i.strip()
                if len(i.split()) > 8:
                    for thing in filter:
                        if thing in i:
                            filter_flag = True
                            break
                    if (not filter_flag):
                        if pos:
                            if i not in self.pos_reviews:
                                self.pos_reviews.update({i:0})
                        else:
                            if i not in self.neg_reviews:
                                self.neg_reviews.update({i:0})
                filter_flag = False

    def review_ranker(self):
        for key in self.pos_reviews:
            sentences = key.replace(".", ". ")
            self.pos_reviews[key] = compute_score(sentences)
        for key in self.neg_reviews:
            sentences = key.replace(".", ". ")
            self.neg_reviews[key] = compute_score(sentences)
        inverted_pos = {v:k for k,v in self.pos_reviews.items()}
        inverted_neg = {v:k for k,v in self.neg_reviews.items()}
        sorted_pos = {inverted_pos[k]:k for k in sorted(inverted_pos.keys(), reverse=True)}
        sorted_neg = {inverted_neg[k]:k for k in sorted(inverted_neg.keys())}
        return sorted_pos, sorted_neg

    def output_best_worst(self, k_pos, k_neg):
        pos_str = ""
        neg_str = ""
        i = 0
        p, n = self.review_ranker()
        if k_pos > len(p) or k_neg > len(n):
            print("Maximum number of reviews are", len(p), len(n), "for positive and negative, respectively")
            return None, None
        for k in p:
            if i == k_pos:
                break
            pos_str += "-\t" + k + "\n"
            i += 1
        i = 0
        for k in n:
            if i == k_neg:
                break
            neg_str += "-\t" + k + "\n"
            i += 1
        return pos_str, neg_str
#example test case
url = "https://www.amazon.com/Apple-MacBook-13-inch-256GB-Storage/dp/B08N5KWB9H/ref=sr_1_1_sspa?keywords=macbook&qid=1689808992&sprefix=mac%2Caps%2C278&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1"
m = Review(url)
pos, neg = m.output_best_worst(3,3)
print(pos)
print(neg)