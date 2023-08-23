"""
Let's search through

"""
import re
import pandas as pd
import plotly.express as px
import logging

formatting_access = {
    # Kudos to https://stackoverflow.com/questions/12544510/parsing-apache-log-files
    'regex': '([(\d\.)]+) ([^\s+]) - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"',
    'columns': ("IP", "user", "date", "request", "status", "size", "unknown", "user agent")
}
formatting_error = {
    'regex': '\[(.*?)\] \[(.*?)\] \[(pid.*?)\] (\[client (.*?):(.*?)\])? (.*)',
    'columns': ("date", "error", "pid", "client", "ip", "port", "message")
}

def createDataframeFromFile(filename, formatting):
    df = pd.DataFrame()
    f = open(filename, "r")
    i = 0
    for line in f:
        i += 1
        row = re.match(formatting['regex'], line)
        if row:
            df = pd.concat([df, pd.DataFrame([row.groups()])], ignore_index=True)
        else:
            logging.warn(f"Skipping line {i}: {line}")
    f.close()
    df.columns = formatting['columns']
    return df


logging.info("Parse access.log")
df_access = createDataframeFromFile("logs/access.log", formatting_access)
logging.debug(df_access.iloc[:10].to_markdown())
logging.debug("")

logging.info("Parse error.log")
df_error = createDataframeFromFile("logs/error.log", formatting_error)
logging.debug(df_error.iloc[:10].to_markdown())
logging.debug("")

logging.debug(df_access.value_counts("status").to_markdown() + "\n")
logging.debug(df_access.value_counts("IP")[:10].to_markdown() + "\n")
logging.debug(df_access.value_counts("request")[:10].to_markdown() + "\n")
logging.debug(df_access.value_counts("user agent")[:10].to_markdown() + "\n")

px.scatter(df_access, x="status", y="date", hover_name="request", log_x=True).show()

# import plotly.express as px
# df = px.data.gapminder().query("year == 2007")

# fig = px.scatter(df, x="gdpPercap", y="lifeExp", hover_name="country", log_x=True)
# fig.show()
