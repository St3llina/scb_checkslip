import requests
import base64
from bs4 import BeautifulSoup
import re
from bank_code import select_bank
API_ENPOINT = "https://checkslip.scb.co.th/web/api/verify-captcha"
CAPTCHA_ENDPOINT = "https://checkslip.scb.co.th/web/main"

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://checkslip.scb.co.th",
    "Referer": "https://checkslip.scb.co.th/web/main"
}

def get_captcha():
    resp = session.get(
        CAPTCHA_ENDPOINT,
        headers=headers
    )
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")

        img = soup.find("img", alt="CAPTCHA")

        if not img:
            print("CAPTCHA NOT FOUND")
            return

        src = img.get("src")

        if not src.startswith("data:image"):
            print("CAPTCHA src ไม่ใช่ base64")
            return

        base64_data = src.split(",", 1)[1]

        missing_padding = len(base64_data) % 4
        if missing_padding:
            base64_data += "=" * (4 - missing_padding)

        image_data = base64.b64decode(base64_data)

        with open("captcha.png", "wb") as f:
            f.write(image_data)

            print("saved captcha.png")
            match = re.search(
            r'data-style-capcha="([^"]+)"',
            resp.text
        )

        random_value = match.group(1).split("/")
        return {
            "random2": random_value[0],
            "random1": random_value[1],
            "tag": random_value[2]
        }

def checkslip(amount: str, bank: str, tran: str, captchaCode: str, random: dict):
    payload = {
        "amount": amount,
        "bank": bank,
        "tran": tran,
        "captchaCode": captchaCode,
        "random": random
    }

    response = session.post(API_ENPOINT, json=payload, headers=headers)
    return response.json()

def set_form_cookie(amount: str, bank: str, tran: str, captchaCode: str, random_data: dict):
    url = "https://checkslip.scb.co.th/web/api/set-form-cookie"

    payload = {
        "amount": amount,
        "bank": bank,
        "tran": tran,
        "captchaCode": captchaCode,
        "random": random_data
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://checkslip.scb.co.th/web/main",
        "Origin": "https://checkslip.scb.co.th",
        "Content-Type": "application/json"
    }

    response = session.post(
        url,
        json=payload,
        headers=headers
    )

    try:
        return response.json()
    except:
        return response.text



random_code = get_captcha()

tran = input("Enter transaction number: ")
bank = select_bank()
amount = input("Enter amount like 100.00: ")
captcha = input("Enter captcha: ")

props = {
    "tran": tran,
    "bank": bank,
    "amount": amount,
    "captchaCode": captcha,
    "random": random_code
}
checkCaptcha = checkslip(amount, bank, tran, captcha, random_code)
set_cookie_status = set_form_cookie(amount, bank, tran, captcha, random_code)
print(set_cookie_status)
url = f"https://checkslip.scb.co.th/web/__nuxt_island/Tabledetail_LDlVeEWufg1tyOHVlvKhIAK9LmEdpHataTVhQYLi5g.json?props={props}"

def get_table_detail(amount, bank, tran, captchaCode, random_data):
    import urllib.parse
    import json

    payload = {
        "tran": tran,
        "bank": bank,
        "amount": amount,
        "captchaCode": captchaCode,
        "random": random_data
    }

    props = urllib.parse.quote(
        json.dumps(payload, separators=(",", ":"))
    )

    url = f"https://checkslip.scb.co.th/web/__nuxt_island/Tabledetail_LDlVeEWufg1tyOHVlvKhIAK9LmEdpHataTVhQYLi5g.json?props={props}"

    resp = session.get(url, headers=headers)

    data = resp.json()

    if "html" in data:
        soup = BeautifulSoup(data["html"], "html.parser")

        rows = soup.find_all("tr")

        result = []
        for row in rows:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if cols:
                result.append(cols)

        return result

    return data

data = get_table_detail(amount, bank, tran, captcha, random_code)

print(data)