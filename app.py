from flask import Flask, render_template, request, send_from_directory
import requests
from datetime import datetime
MIN_YEAR = 1900
app = Flask(__name__, template_folder=".")

def parse_gregorian_date(value):
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Please enter a valid date in YYYY-MM-DD format.")

    if parsed.isoformat() != value:
        raise ValueError("Please enter a valid date in YYYY-MM-DD format.")

    if parsed.year < MIN_YEAR:
        raise ValueError(f"Please enter a date from the year {MIN_YEAR} or later.")

    return parsed

@app.route("/style.css")
def stylesheet():
    return send_from_directory(app.root_path, "style.css")


@app.route("/")
def index():
    hebrew_date = None
    error = None
    selected_date = request.args.get("date", "")

    if selected_date:
        try:
            gregorian_date = parse_gregorian_date(selected_date)
        except ValueError as e:
            error = str(e)
        else:
            url = "https://www.hebcal.com/converter"
            params = {
                "cfg": "json",
                "date": gregorian_date.isoformat(),
                "g2h": 1,
                "strict": 1
            }

            try:
                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    hebrew_date = data["hebrew"]
                elif response.status_code == 400:
                    error = "This date can't be converted."
                else:
                    error = "The conversion service is unavailable. Please try again later."

            except (KeyError, ValueError):
                error = "Invalid response from the conversion service."
            
            except requests.RequestException:
                error = "Unable to connect to the conversion service."


    return render_template(
        "index.html",
        hebrew_date=hebrew_date,
        selected_date=selected_date,
        error=error
    )


if __name__ == "__main__":
    app.run()