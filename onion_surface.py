from flask import Flask, render_template, request, redirect, url_for, send_file
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import urllib.parse
import os
import json
import csv

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
HISTORY_FILE = "history.json"
CSV_FILE = "results.csv"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


async def search_duckduckgo(session, term):
    query = term.replace(" ", "+")
    url = f"https://html.duckduckgo.com/html/?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    results = []

    try:
        async with session.get(url, headers=headers) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")

            for a in soup.select(".result__url")[:10]:
                raw_link = a.get("href")

                if raw_link and "uddg=" in raw_link:
                    parsed = urllib.parse.parse_qs(
                        urllib.parse.urlparse(raw_link).query
                    )
                    link = parsed.get("uddg", [None])[0]

                    if link:
                        results.append(urllib.parse.unquote(link))

    except Exception as e:
        print("ERROR:", e)

    return term, results


async def run_search(keywords):
    async with aiohttp.ClientSession() as session:
        tasks = [search_duckduckgo(session, kw) for kw in keywords]
        results = await asyncio.gather(*tasks)

    return dict(results)


def save_history(keywords):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)

    history.insert(0, keywords)

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_csv(results):
    print("Saving CSV...")

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Keyword", "Link"])

        for keyword, links in results.items():
            for link in links:
                writer.writerow([keyword, link])

    print("CSV saved!")


@app.route("/", methods=["GET", "POST"])
def index():
    results = {}
    history = load_history()

    if request.method == "POST":
        file = request.files.get("file")

        if file:
            path = os.path.join(UPLOAD_FOLDER, "keywords.txt")
            file.save(path)

            with open(path, "r", encoding="utf-8") as f:
                keywords = [line.strip() for line in f if line.strip()]

            print("KEYWORDS:", keywords)

            results = asyncio.run(run_search(keywords))

            print("RESULTS:", results)

            save_history(keywords)
            save_csv(results)
            history = load_history()

    return render_template("index.html", results=results, history=history)


@app.route("/download_csv")
def download_csv():
    if not os.path.exists(CSV_FILE):
        return "No CSV file found. Run a search first."

    return send_file(os.path.abspath(CSV_FILE), as_attachment=True)


@app.route("/clear_history", methods=["POST"])
def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
