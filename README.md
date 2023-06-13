### This is a pretty basic [Twitter Bot](https://twitter.com/ProxFeriadoAR) that posts a daily tweet, reporting how many days are left until the next holiday in Argentina.
### For that i make use of:
- Free tier [Twitter API](https://developer.twitter.com/en/docs/twitter-api)
- [No Laborables API](https://pjnovas.gitbooks.io/no-laborables/content/)

## 1. Installation

### 1.1 Libraries
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install al libraries listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```
### 1.2 Twitter App Keys
Rename `.env_template` to `.env` and fill _TW_CONSUMER_KEY_ and _TW_CONSUMER_SECRET_ with your apps Consumer Key and Secret.

### 1.3 OAuth Tokens
Modify the keys in `get_oauth_tokens.py` and run it, after entering the code, you will get your own Oauth Tokens.
Finally add them to `.env`.

## 2. Usage

Just run `botardo.py` 🍻

# 🇦🇷
