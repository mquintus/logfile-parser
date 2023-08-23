"""
Let's search through

"""
# https://stackoverflow.com/questions/12544510/parsing-apache-log-files
import re
import pandas as pd
import plotly.express as px

# regex = '([(\d\.)]+) ([^\s]*) ([^\s]*) \[(.*?)\] "(.*?)" (\d+) - "(.*?)" "(.*?)"'

formatting_access = {
    'regex': '([(\d\.)]+) ([^\s+]) - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"',
    'columns': ("IP", "user", "date", "request", "status", "size", "unknown", "user agent")
}
formatting_error = {
#    'regex': '\[(.*?)\] \[(.*?)\] \[(pid.*?)\] \[client (.*?):(.*?)\] (.*)',
#    'columns': ("date", "error", "pid", "ip", "port", "message")
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
            print("Skipping line", i, ":", line)
    f.close()
    df.columns = formatting['columns']
    return df


df_access = createDataframeFromFile("logs/access.log", formatting_access)
df_error = createDataframeFromFile("logs/error.log", formatting_error)

print(df_access.iloc[:10].to_markdown())
print()
print(df_error.iloc[:10].to_markdown())
print()

#print(df_access.value_counts("status").to_markdown() + "\n")
#print(df_access.value_counts("IP")[:10].to_markdown() + "\n")
#print(df_access.value_counts("request")[:10].to_markdown() + "\n")
#print(df_access.value_counts("user agent")[:10].to_markdown() + "\n")



px.scatter(df_access, x="status", y="date", hover_name="request", log_x=True).show()



# import plotly.express as px
# df = px.data.gapminder().query("year == 2007")

# fig = px.scatter(df, x="gdpPercap", y="lifeExp", hover_name="country", log_x=True)
# fig.show()
