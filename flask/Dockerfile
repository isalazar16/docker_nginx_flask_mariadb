# Python 2.7 oinarri ofizial batetik abiatuko gara
FROM python:latest
# kontainerra hasten denean, bere lan direktorioa honakoa izango da
WORKDIR /app
# Gure proiektuko fitxategi guztiak kontainerraren /app direktoriora kopiatuko ditugu:
# Uneko direktorioan dauzkagun fitxategiak kopiatuko dira, app.py eta requirements.txt
COPY . /app
# pip erabiliz, "requirements.txt" dauden menpekotasunak instalatuko ditugu.
RUN pip install --trusted-host pypi.python.org -r requirements.txt
# Kontainerra jaurtitzerakoan, honako komandoa exekutatuko da
CMD ["python", "app.py"]
